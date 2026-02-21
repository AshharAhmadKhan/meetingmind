import json
import boto3
import os
import time
from datetime import datetime, timezone
from botocore.config import Config
import sys
sys.path.append('/opt/python')  # Lambda layer path
from constants import GRAVEYARD_THRESHOLD_DAYS, EPITAPH_TTL_DAYS, EPITAPH_TASK_TRUNCATION

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

# Configure Bedrock with retry logic for throttling
bedrock_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'ap-south-1'), config=bedrock_config)


def generate_epitaph(action, days_old):
    """
    Generate AI epitaph for graveyard action item.
    Uses multi-model fallback: Haiku → Nova Lite → Nova Micro
    Returns epitaph string or None if all models fail.
    """
    task = action.get('task') or action.get('text', 'Unknown task')  # V1 uses 'text', V2 uses 'task'
    owner = action.get('owner', 'nobody')
    
    # Truncate task if too long
    task_short = task[:EPITAPH_TASK_TRUNCATION] + '...' if len(task) > EPITAPH_TASK_TRUNCATION else task
    
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
    Nightly job to pre-generate epitaphs for graveyard items.
    Runs at 3 AM UTC (9 AM IST) daily via EventBridge.
    """
    print("=" * 60)
    print("EPITAPH GENERATION JOB STARTED")
    print("=" * 60)
    
    table = dynamodb.Table(TABLE_NAME)
    now = datetime.now(timezone.utc)
    
    # Scan all meetings (with pagination)
    print("Scanning DynamoDB for all meetings...")
    meetings = []
    scan_kwargs = {}
    
    while True:
        response = table.scan(**scan_kwargs)
        meetings.extend(response.get('Items', []))
        
        if 'LastEvaluatedKey' not in response:
            break
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
    
    print(f"✓ Scanned {len(meetings)} meetings")
    
    # Find graveyard actions needing epitaphs
    print("Finding graveyard actions needing epitaphs...")
    actions_to_process = []
    
    for meeting in meetings:
        user_id = meeting.get('userId')
        meeting_id = meeting.get('meetingId')
        action_items = meeting.get('actionItems', [])
        
        for action in action_items:
            # Skip completed actions
            if action.get('completed'):
                continue
            
            # Calculate days old
            created_at = action.get('createdAt')
            if not created_at:
                continue
            
            try:
                # Parse created_at - handle both timezone-aware and naive formats
                created_at_str = created_at.replace('Z', '+00:00')
                try:
                    created_dt = datetime.fromisoformat(created_at_str)
                except ValueError:
                    # Try parsing without timezone
                    created_dt = datetime.fromisoformat(created_at)
                    # Make it timezone-aware (assume UTC)
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                
                days_old = (now - created_dt).days
                
                # Only process graveyard items (>GRAVEYARD_THRESHOLD_DAYS days)
                if days_old <= GRAVEYARD_THRESHOLD_DAYS:
                    continue
                
                # Check if epitaph needs generation
                needs_epitaph = False
                reason = ""
                
                if not action.get('epitaph'):
                    needs_epitaph = True
                    reason = "missing"
                elif action.get('epitaphGeneratedAt'):
                    try:
                        gen_dt = datetime.fromisoformat(action['epitaphGeneratedAt'].replace('Z', '+00:00'))
                        days_since_gen = (now - gen_dt).days
                        if days_since_gen > EPITAPH_TTL_DAYS:
                            needs_epitaph = True
                            reason = f"stale ({days_since_gen} days old)"
                    except:
                        needs_epitaph = True
                        reason = "invalid timestamp"
                
                if needs_epitaph:
                    actions_to_process.append({
                        'userId': user_id,
                        'meetingId': meeting_id,
                        'action': action,
                        'daysOld': days_old,
                        'reason': reason
                    })
            except Exception as e:
                print(f"✗ Error processing action: {e}")
                continue
    
    print(f"✓ Found {len(actions_to_process)} actions needing epitaphs")
    
    if len(actions_to_process) == 0:
        print("No epitaphs to generate. Job complete.")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'totalMeetings': len(meetings),
                'actionsProcessed': 0,
                'successCount': 0,
                'failureCount': 0,
                'timestamp': now.isoformat()
            })
        }
    
    # Generate epitaphs with throttling protection
    print("Generating epitaphs...")
    success_count = 0
    failure_count = 0
    
    for idx, item in enumerate(actions_to_process):
        try:
            action = item['action']
            days_old = item['daysOld']
            action_id = action.get('id', 'unknown')
            
            print(f"[{idx+1}/{len(actions_to_process)}] Generating epitaph for action {action_id} ({item['reason']})")
            
            # Generate epitaph
            epitaph = generate_epitaph(action, days_old)
            
            if epitaph:
                # Update DynamoDB
                meeting_response = table.get_item(
                    Key={'userId': item['userId'], 'meetingId': item['meetingId']}
                )
                
                if 'Item' in meeting_response:
                    meeting = meeting_response['Item']
                    action_items = meeting.get('actionItems', [])
                    
                    # Update the specific action item
                    updated = False
                    for i, a in enumerate(action_items):
                        if a.get('id') == action_id:
                            action_items[i]['epitaph'] = epitaph
                            action_items[i]['epitaphGeneratedAt'] = now.isoformat()
                            updated = True
                            break
                    
                    if updated:
                        # Save back to DynamoDB
                        table.update_item(
                            Key={'userId': item['userId'], 'meetingId': item['meetingId']},
                            UpdateExpression='SET actionItems = :items',
                            ExpressionAttributeValues={':items': action_items}
                        )
                        
                        success_count += 1
                        print(f"  ✓ Saved epitaph: {epitaph[:60]}...")
                    else:
                        failure_count += 1
                        print(f"  ✗ Action {action_id} not found in meeting")
                else:
                    failure_count += 1
                    print(f"  ✗ Meeting not found: {item['meetingId']}")
            else:
                failure_count += 1
                print(f"  ✗ Failed to generate epitaph")
            
            # Throttling protection: sleep between requests
            if idx < len(actions_to_process) - 1:
                time.sleep(1)  # 1 second between epitaphs
                
        except Exception as e:
            failure_count += 1
            print(f"  ✗ Error: {e}")
            continue
    
    result = {
        'totalMeetings': len(meetings),
        'actionsProcessed': len(actions_to_process),
        'successCount': success_count,
        'failureCount': failure_count,
        'timestamp': now.isoformat()
    }
    
    print("=" * 60)
    print("EPITAPH GENERATION JOB COMPLETE")
    print(f"Total meetings scanned: {result['totalMeetings']}")
    print(f"Actions processed: {result['actionsProcessed']}")
    print(f"Success: {result['successCount']}")
    print(f"Failures: {result['failureCount']}")
    print("=" * 60)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
