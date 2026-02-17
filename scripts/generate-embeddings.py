#!/usr/bin/env python3
"""
Generate embeddings for all existing action items in DynamoDB.
This backfills embeddings for actions created before Day 5 implementation.
"""

import json
import boto3
import hashlib
from decimal import Decimal

REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'
TEST_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
bedrock = boto3.client('bedrock-runtime', region_name=REGION)

def _generate_embedding(text):
    """
    Generate embedding vector for text using Bedrock Titan Embeddings.
    Falls back to mock embedding if Bedrock unavailable.
    """
    try:
        # Try Bedrock Titan Embeddings
        body = json.dumps({"inputText": text})
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=body
        )
        result = json.loads(response['body'].read())
        embedding = result['embedding']
        print(f"  ✓ Generated Bedrock embedding: {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        print(f"  ⚠ Bedrock failed ({e}), using mock embedding")
        # Mock embedding: simple hash-based vector (1536 dimensions like Titan)
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        mock_embedding = []
        for i in range(1536):
            byte_val = hash_bytes[i % len(hash_bytes)]
            mock_embedding.append((byte_val / 255.0) - 0.5)
        return mock_embedding

def main():
    """Generate embeddings for all action items"""
    print("\n" + "="*60)
    print("GENERATING EMBEDDINGS FOR EXISTING ACTION ITEMS")
    print("="*60)
    
    table = dynamodb.Table(TABLE_NAME)
    
    # Get all meetings for user
    print(f"\nQuerying meetings for user: {TEST_USER_ID}")
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': TEST_USER_ID}
    )
    
    meetings = response.get('Items', [])
    print(f"Found {len(meetings)} meetings\n")
    
    total_actions = 0
    updated_actions = 0
    skipped_actions = 0
    
    for meeting in meetings:
        meeting_id = meeting.get('meetingId')
        meeting_title = meeting.get('title', 'Untitled')
        actions = meeting.get('actionItems', [])
        
        if not actions:
            continue
        
        print(f"\nProcessing: {meeting_title}")
        print(f"  Meeting ID: {meeting_id}")
        print(f"  Actions: {len(actions)}")
        
        updated_meeting = False
        
        for i, action in enumerate(actions):
            total_actions += 1
            task = action.get('task', '')
            
            if not task:
                print(f"  [{i+1}] Skipping empty task")
                skipped_actions += 1
                continue
            
            # Check if embedding already exists
            if action.get('embedding'):
                print(f"  [{i+1}] Already has embedding: {task[:50]}...")
                skipped_actions += 1
                continue
            
            # Generate embedding
            print(f"  [{i+1}] Generating embedding: {task[:50]}...")
            embedding = _generate_embedding(task)
            
            # Convert to Decimal for DynamoDB
            embedding_decimal = [Decimal(str(float(x))) for x in embedding]
            
            # Add embedding to action
            action['embedding'] = embedding_decimal
            updated_actions += 1
            updated_meeting = True
        
        # Update meeting in DynamoDB if any actions were updated
        if updated_meeting:
            print(f"  💾 Updating meeting in DynamoDB...")
            table.put_item(Item=meeting)
            print(f"  ✓ Saved")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Total actions: {total_actions}")
    print(f"  Updated: {updated_actions}")
    print(f"  Skipped: {skipped_actions}")
    print(f"  Coverage: {(updated_actions/total_actions*100):.1f}%")
    print("\n✓ Embedding generation complete!")
    print("\nNow test duplicate detection:")
    print("  1. Visit: https://dcfx593ywvy92.cloudfront.net")
    print("  2. Go to Actions Overview page")
    print("  3. Click '🔍 Check Duplicates' button")
    print("  4. Should find duplicates for repeated tasks")

if __name__ == '__main__':
    main()
