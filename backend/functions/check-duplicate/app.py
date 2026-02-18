import json
import boto3
import os
import hashlib
from decimal import Decimal

REGION = os.environ.get('REGION', 'ap-south-1')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')

dynamodb = boto3.resource('dynamodb', region_name=REGION)
bedrock = boto3.client('bedrock-runtime', region_name=REGION)

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def _generate_embedding(text):
    """
    Generate embedding vector for text using Bedrock Titan Embeddings.
    Falls back to TF-IDF-based embedding if Bedrock unavailable.
    """
    try:
        # Try Bedrock Titan Embeddings
        body = json.dumps({"inputText": text})
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=body
        )
        result = json.loads(response['body'].read())
        embedding = result['embedding']
        print(f"Generated Bedrock embedding: {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        print(f"Bedrock embedding failed: {e} — using TF-IDF fallback")
        # Fallback: TF-IDF-based embedding (1536 dimensions to match Titan)
        # Simple word-based vector using character n-grams
        words = text.lower().split()
        # Create a sparse vector based on word presence and position
        vector = [0.0] * 1536
        for i, word in enumerate(words[:100]):  # Limit to first 100 words
            # Use word hash to determine positions in vector
            word_hash = hash(word)
            for j in range(5):  # Each word affects 5 positions
                pos = (word_hash + j) % 1536
                # TF-IDF-like weighting: position matters (earlier words weighted more)
                weight = 1.0 / (i + 1)
                vector[pos] += weight
        
        # Normalize to unit vector
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        # Convert to Decimal for DynamoDB compatibility
        vector = [Decimal(str(x)) for x in vector]
        
        return vector

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    import math
    
    # Convert to lists of floats (handle Decimal from DynamoDB)
    if not isinstance(vec1, list):
        vec1 = list(vec1)
    if not isinstance(vec2, list):
        vec2 = list(vec2)
    
    # Convert Decimal to float
    vec1 = [float(x) for x in vec1]
    vec2 = [float(x) for x in vec2]
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Calculate magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def find_duplicates(user_id, new_task, threshold=0.85):
    """
    Find duplicate action items across all user's meetings.
    Returns list of similar actions with similarity scores.
    """
    table = dynamodb.Table(TABLE_NAME)
    
    # Generate embedding for new task
    new_embedding = _generate_embedding(new_task)
    
    # Get all meetings for user
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id}
    )
    
    duplicates = []
    history = []
    
    for meeting in response.get('Items', []):
        meeting_id = meeting.get('meetingId')
        meeting_title = meeting.get('title', 'Untitled Meeting')
        
        for action in meeting.get('actionItems', []):
            # Skip completed actions
            if action.get('completed'):
                continue
            
            task_text = action.get('task', '')
            if not task_text:
                continue
            
            # Get or generate embedding
            existing_embedding = action.get('embedding')
            if not existing_embedding:
                existing_embedding = _generate_embedding(task_text)
            
            # Calculate similarity
            similarity = cosine_similarity(new_embedding, existing_embedding)
            
            # Track all similar items for history
            if similarity >= 0.70:  # Lower threshold for history
                history.append({
                    'task': task_text,
                    'date': action.get('createdAt', ''),
                    'meetingTitle': meeting_title,
                    'similarity': round(similarity * 100, 1)
                })
            
            # Track high-similarity duplicates
            if similarity >= threshold:
                duplicates.append({
                    'id': action.get('id'),
                    'task': task_text,
                    'owner': action.get('owner', 'Unassigned'),
                    'deadline': action.get('deadline'),
                    'meetingId': meeting_id,
                    'meetingTitle': meeting_title,
                    'createdAt': action.get('createdAt', ''),
                    'riskScore': action.get('riskScore', 0),
                    'riskLevel': action.get('riskLevel', 'LOW'),
                    'similarity': round(similarity * 100, 1)
                })
    
    # Sort by similarity (highest first)
    duplicates.sort(key=lambda x: x['similarity'], reverse=True)
    history.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Determine if chronic blocker (repeated >3 times)
    is_chronic = len(history) >= 3
    
    # Get best match
    best_match = duplicates[0] if duplicates else None
    
    return {
        'isDuplicate': len(duplicates) > 0,
        'similarity': duplicates[0]['similarity'] if duplicates else 0,
        'bestMatch': best_match,
        'allDuplicates': duplicates,
        'history': history[:10],  # Limit to 10 most similar
        'isChronicBlocker': is_chronic,
        'repeatCount': len(history)
    }

def lambda_handler(event, context):
    """
    Check if action item is duplicate.
    
    POST /check-duplicate
    Body: {"task": "Finalize API documentation"}
    """
    print("Event:", json.dumps(event, default=str))
    
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        task = body.get('task', '').strip()
        
        if not task:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Task text required'})
            }
        
        # Get user ID from Cognito token
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Find duplicates
        result = find_duplicates(user_id, task)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=decimal_to_float)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
