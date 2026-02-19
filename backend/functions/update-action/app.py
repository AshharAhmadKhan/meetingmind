import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    user_id    = event['requestContext']['authorizer']['claims']['sub']
    meeting_id = event['pathParameters']['meetingId']
    action_id  = event['pathParameters']['actionId']
    
    # Parse body - handle both string and dict
    body_raw = event.get('body', '{}')
    if isinstance(body_raw, str):
        body = json.loads(body_raw)
    else:
        body = body_raw or {}
    
    completed  = body.get('completed', False)
    status     = body.get('status')  # New: support status field

    table    = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    item     = response.get('Item')

    if not item:
        return _response(404, {'error': 'Meeting not found'})

    actions = item.get('actionItems', [])
    updated = False
    for action in actions:
        if action.get('id') == action_id:
            # Update completed field
            action['completed'] = completed
            action['completedAt'] = datetime.now(timezone.utc).isoformat() if completed else None
            
            # Update status field if provided
            if status:
                valid_statuses = ['todo', 'in_progress', 'blocked', 'done']
                if status in valid_statuses:
                    action['status'] = status
                    # Sync completed field with status
                    if status == 'done':
                        action['completed'] = True
                        action['completedAt'] = datetime.now(timezone.utc).isoformat()
                    elif action.get('completed'):
                        # If moving away from done, mark as incomplete
                        action['completed'] = False
                        action['completedAt'] = None
            
            updated = True
            break

    if not updated:
        return _response(404, {'error': f'Action item {action_id} not found'})

    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression='SET actionItems = :a, updatedAt = :t',
        ExpressionAttributeValues={
            ':a': actions,
            ':t': datetime.now(timezone.utc).isoformat()
        }
    )

    return _response(200, {'success': True, 'actionId': action_id, 'completed': completed, 'status': status})


def _response(code, body):
    return {
        'statusCode': code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, default=decimal_to_float)
    }
