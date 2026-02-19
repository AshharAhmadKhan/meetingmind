import json
import boto3
import os
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from botocore.config import Config

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}

# Configure Bedrock with retry logic for throttling
bedrock_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'ap-south-1'), config=bedrock_config)


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def generate_epitaph(action, days_old):
    """
    Generate AI epitaph for graveyard action item.
    Uses multi-model fallback: Haiku → Nova Lite → Nova Micro
    Returns epitaph string or None if all models fail.
    """
    task = action.get('task', 'Unknown task')
    owner = action.get('owner', 'nobody')
    
    # Truncate task if too long
    task_short = task[:80] + '...' if len(task) > 80 else task
    
    prompt = f"""Generate a dramatic, darkly humorous tombstone epitaph for this abandoned task.
Max 15 words. Be creative and slightly sarcastic.

Task: {task_short}
Owner: {owner}
Days abandoned: {days_old}

Format: "Here lies [task summary]. [fate in 5 words]."

Return ONLY the epitaph text, no quotes or extra formatting."""

    models = [
        ('anthropic.claude-3-haiku-20240307-v1:0', 'anthropic'),
        ('apac.amazon.nova-lite-v1:0', 'nova'),
        ('apac.amazon.nova-micro-v1:0', 'nova'),
    ]

    for model_id, model_type in models:
        max_retries = 2
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                if model_type == 'anthropic':
                    body = json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': 100,
                        'messages': [{'role': 'user', 'content': prompt}]
                    })
                else:
                    body = json.dumps({
                        'messages': [{'role': 'user', 'content': [{'text': prompt}]}],
                        'inferenceConfig': {'maxTokens': 100, 'temperature': 0.7}
                    })

                resp = bedrock.invoke_model(modelId=model_id, body=body)
                result = json.loads(resp['body'].read())

                if model_type == 'anthropic':
                    epitaph = result['content'][0]['text'].strip()
                else:
                    epitaph = result['output']['message']['content'][0]['text'].strip()

                # Clean up any quotes or extra formatting
                epitaph = epitaph.strip('"\'').strip()
                
                print(f"Generated epitaph with {model_id}")
                return epitaph
                
            except Exception as e:
                error_str = str(e)
                
                if 'ThrottlingException' in error_str or 'TooManyRequestsException' in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Epitaph generation throttled, retrying in {delay}s")
                        time.sleep(delay)
                        continue
                else:
                    print(f"Epitaph generation failed with {model_id}: {e}")
                    break

    # All models failed - return generic epitaph
    print("All Bedrock models failed for epitaph, using fallback")
    return get_fallback_epitaph(task_short, owner, days_old)


def get_fallback_epitaph(task, owner, days_old):
    """Generate a generic epitaph when Bedrock fails."""
    templates = [
        f"Here lies {task[:40]}. Mentioned often, completed never.",
        f"Here lies {task[:40]}. {days_old} days of silence, zero progress.",
        f"Here lies {task[:40]}. Assigned to {owner}, forgotten by all.",
        f"Here lies {task[:40]}. Born in a meeting, died in neglect.",
        f"Here lies {task[:40]}. Survived {days_old} days, perished from apathy.",
    ]
    # Use task hash to pick consistent template for same task
    import hashlib
    task_hash = int(hashlib.md5(task.encode()).hexdigest(), 16)
    return templates[task_hash % len(templates)]


def lambda_handler(event, context):
    """
    Get all action items from all meetings for authenticated user
    Returns action items with meeting context
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    try:
        # Extract user ID from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Get query parameters for filtering
        params = event.get('queryStringParameters') or {}
        status_filter = params.get('status', 'all')  # all, incomplete, complete
        owner_filter = params.get('owner')  # filter by owner name
        team_id = params.get('teamId')  # optional team filter
        
        # Get all meetings for user or team
        table = dynamodb.Table(TABLE_NAME)
        
        if team_id:
            # Validate user is member of the team
            teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
            team_response = teams_table.get_item(Key={'teamId': team_id})
            
            if 'Item' not in team_response:
                return {
                    'statusCode': 404,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'Team not found'})
                }
            
            team = team_response['Item']
            members = team.get('members', [])
            
            # Check if user is a member of the team
            # Members can be either strings (old format) or dicts (new format)
            member_ids = []
            for member in members:
                if isinstance(member, dict):
                    member_ids.append(member.get('userId'))
                else:
                    member_ids.append(member)
            
            if user_id not in member_ids:
                return {
                    'statusCode': 403,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'You are not a member of this team'})
                }
            
            # Query by teamId using GSI
            response = table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': team_id}
            )
        else:
            # Query by userId (personal meetings)
            response = table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
        
        meetings = response.get('Items', [])
        
        # Extract all action items with meeting context
        all_actions = []
        
        for meeting in meetings:
            meeting_id = meeting.get('meetingId')
            meeting_title = meeting.get('title', 'Untitled Meeting')
            meeting_date = meeting.get('createdAt') or meeting.get('updatedAt')
            action_items = meeting.get('actionItems', [])
            
            for action in action_items:
                # Apply status filter
                is_complete = action.get('completed', False)
                if status_filter == 'incomplete' and is_complete:
                    continue
                if status_filter == 'complete' and not is_complete:
                    continue
                
                # Apply owner filter
                if owner_filter and action.get('owner') != owner_filter:
                    continue
                
                # Add meeting context to action
                action_with_context = {
                    'id': action.get('id'),
                    'task': action.get('task'),
                    'owner': action.get('owner', 'Unassigned'),
                    'deadline': action.get('deadline'),
                    'completed': is_complete,
                    'completedAt': action.get('completedAt'),
                    'status': action.get('status', 'done' if is_complete else 'todo'),
                    'riskScore': action.get('riskScore', 0),
                    'riskLevel': action.get('riskLevel', 'LOW'),
                    'createdAt': action.get('createdAt'),
                    'epitaph': action.get('epitaph'),  # Include cached epitaph if exists
                    'epitaphGeneratedAt': action.get('epitaphGeneratedAt'),
                    # Meeting context (ALWAYS included)
                    'meetingId': meeting_id,
                    'meetingTitle': meeting_title,
                    'meetingDate': meeting_date
                }
                
                all_actions.append(action_with_context)
        
        # Sort by deadline (soonest first), then by risk score (highest first)
        all_actions.sort(key=lambda x: (
            x.get('deadline') or '9999-12-31',  # No deadline goes to end
            -x.get('riskScore', 0)  # Higher risk first
        ))
        
        # Generate epitaphs for graveyard items (>30 days old, incomplete)
        # Only generate if epitaph is missing or stale (>7 days old)
        now = datetime.now(timezone.utc)
        epitaph_ttl_days = 7
        
        for action in all_actions:
            if action['completed']:
                continue
                
            # Calculate days old
            created_at = action.get('createdAt')
            if not created_at:
                continue
                
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (now - created_dt).days
                
                # Only generate for graveyard items (>30 days)
                if days_old <= 30:
                    continue
                
                # Check if epitaph needs generation
                needs_epitaph = False
                
                if not action.get('epitaph'):
                    needs_epitaph = True
                elif action.get('epitaphGeneratedAt'):
                    try:
                        gen_dt = datetime.fromisoformat(action['epitaphGeneratedAt'].replace('Z', '+00:00'))
                        days_since_gen = (now - gen_dt).days
                        if days_since_gen > epitaph_ttl_days:
                            needs_epitaph = True
                    except:
                        needs_epitaph = True
                
                # Generate epitaph if needed
                if needs_epitaph:
                    epitaph = generate_epitaph(action, days_old)
                    if epitaph:
                        action['epitaph'] = epitaph
                        action['epitaphGeneratedAt'] = now.isoformat()
                        
                        # Update DynamoDB with new epitaph (async, don't block response)
                        try:
                            # Find the meeting and update the specific action item
                            meeting_id = action['meetingId']
                            action_id = action['id']
                            
                            # Get the meeting
                            meeting_response = table.get_item(
                                Key={'userId': user_id, 'meetingId': meeting_id}
                            )
                            
                            if 'Item' in meeting_response:
                                meeting = meeting_response['Item']
                                action_items = meeting.get('actionItems', [])
                                
                                # Update the specific action item
                                for idx, item in enumerate(action_items):
                                    if item.get('id') == action_id:
                                        action_items[idx]['epitaph'] = epitaph
                                        action_items[idx]['epitaphGeneratedAt'] = now.isoformat()
                                        break
                                
                                # Save back to DynamoDB
                                table.update_item(
                                    Key={'userId': user_id, 'meetingId': meeting_id},
                                    UpdateExpression='SET actionItems = :items',
                                    ExpressionAttributeValues={':items': action_items}
                                )
                                print(f"Saved epitaph for action {action_id}")
                        except Exception as e:
                            print(f"Failed to save epitaph to DynamoDB: {e}")
                            # Don't fail the request, epitaph is still in response
                            
            except Exception as e:
                print(f"Error processing epitaph for action: {e}")
                continue
        
        # Calculate stats
        total = len(all_actions)
        completed = len([a for a in all_actions if a['completed']])
        incomplete = total - completed
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'actions': all_actions,
                'stats': {
                    'total': total,
                    'completed': completed,
                    'incomplete': incomplete,
                    'completionRate': round(completed / total, 2) if total > 0 else 0
                }
            }, default=decimal_to_float)
        }
        
    except Exception as e:
        print(f"Error getting all actions: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)}, default=decimal_to_float)
        }
