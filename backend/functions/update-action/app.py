import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal
from constants import VALID_ACTION_STATUSES

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
    owner      = body.get('owner')   # New: support owner update
    deadline   = body.get('deadline')  # New: support deadline update

    table    = dynamodb.Table(TABLE_NAME)
    
    # First try to get meeting by userId (uploader)
    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    item     = response.get('Item')
    meeting_owner_id = user_id  # Assume current user is owner

    # If not found, scan for the meeting (for team members)
    if not item:
        try:
            # Scan for the meeting by meetingId
            response = table.scan(
                FilterExpression='meetingId = :mid',
                ExpressionAttributeValues={':mid': meeting_id}
            )
            items = response.get('Items', [])
            if items:
                item = items[0]
                meeting_owner_id = item['userId']  # Store actual owner's userId
                
                # Verify user is a team member if meeting has teamId
                if item.get('teamId'):
                    teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
                    team_response = teams_table.get_item(
                        Key={'teamId': item['teamId']}
                    )
                    if 'Item' in team_response:
                        team = team_response['Item']
                        members = team.get('members', [])
                        
                        # Check if user is a member
                        # Members can be either strings (old format) or dicts (new format)
                        member_ids = []
                        for member in members:
                            if isinstance(member, dict):
                                member_ids.append(member.get('userId'))
                            else:
                                member_ids.append(member)
                        
                        if user_id not in member_ids:
                            return _response(403, {'error': 'Not authorized to update this meeting'})
                    else:
                        # Team not found - deny access
                        return _response(403, {'error': 'Team not found'})
        except Exception as e:
            print(f"Error scanning for meetingId: {e}")

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
                if status in VALID_ACTION_STATUSES:
                    action['status'] = status
                    # Sync completed field with status
                    if status == 'done':
                        action['completed'] = True
                        action['completedAt'] = datetime.now(timezone.utc).isoformat()
                    elif action.get('completed'):
                        # If moving away from done, mark as incomplete
                        action['completed'] = False
                        action['completedAt'] = None
            
            # Update owner if provided
            if owner is not None:
                action['owner'] = owner
            
            # Update deadline if provided
            if deadline is not None:
                action['deadline'] = deadline
            
            updated = True
            break

    if not updated:
        return _response(404, {'error': f'Action item {action_id} not found'})

    # Use meeting owner's userId for the update (not current user's)
    table.update_item(
        Key={'userId': meeting_owner_id, 'meetingId': meeting_id},
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
