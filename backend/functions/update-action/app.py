import json
import boto3
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from constants import VALID_ACTION_STATUSES

# Add Lambda layer paths
sys.path.append('/opt/python')
from health_calculator import calculate_health_score, generate_autopsy

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

    # FIX #1: Find action index for atomic update (prevents race condition)
    actions = item.get('actionItems', [])
    action_index = None
    for i, action in enumerate(actions):
        if action.get('id') == action_id:
            action_index = i
            break

    if action_index is None:
        return _response(404, {'error': f'Action item {action_id} not found'})

    # Prepare update values
    now = datetime.now(timezone.utc).isoformat()
    completed_at = now if completed else None
    
    # Determine final status
    final_status = status if status and status in VALID_ACTION_STATUSES else ('done' if completed else 'todo')
    
    # FIX #1: Use atomic update expression (NO RACE CONDITION!)
    # This updates only the specific action by index, not the entire array
    try:
        update_expr_parts = []
        expr_attr_values = {':ut': now}
        expr_attr_names = {}
        
        # Always update completed, completedAt, status, updatedAt
        update_expr_parts.append(f'actionItems[{action_index}].completed = :c')
        update_expr_parts.append(f'actionItems[{action_index}].completedAt = :ca')
        update_expr_parts.append(f'actionItems[{action_index}].#status = :s')
        update_expr_parts.append('updatedAt = :ut')
        
        expr_attr_values[':c'] = completed
        expr_attr_values[':ca'] = completed_at
        expr_attr_values[':s'] = final_status
        expr_attr_names['#status'] = 'status'
        
        # Optionally update owner
        if owner is not None:
            update_expr_parts.append(f'actionItems[{action_index}].#owner = :o')
            expr_attr_values[':o'] = owner
            expr_attr_names['#owner'] = 'owner'
        
        # Optionally update deadline
        if deadline is not None:
            update_expr_parts.append(f'actionItems[{action_index}].deadline = :d')
            expr_attr_values[':d'] = deadline
        
        update_expression = 'SET ' + ', '.join(update_expr_parts)
        
        # Execute atomic update
        table.update_item(
            Key={'userId': meeting_owner_id, 'meetingId': meeting_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None
        )
        
        print(f"✅ Atomic update successful for action {action_id}")
        
    except Exception as e:
        print(f"❌ Atomic update failed: {e}")
        return _response(500, {'error': f'Failed to update action: {str(e)}'})

    # FIX #2: Recalculate health score after action update
    try:
        # Fetch updated meeting to get current state
        response = table.get_item(Key={'userId': meeting_owner_id, 'meetingId': meeting_id})
        updated_meeting = response.get('Item')
        
        if updated_meeting:
            actions = updated_meeting.get('actionItems', [])
            decisions = updated_meeting.get('decisions', [])
            created_at = updated_meeting.get('createdAt')
            
            # Calculate new health metrics
            health = calculate_health_score(actions, decisions, created_at)
            autopsy = generate_autopsy(actions, decisions, updated_meeting.get('transcript', ''), float(health['score']))
            
            # Update health metrics in DynamoDB
            table.update_item(
                Key={'userId': meeting_owner_id, 'meetingId': meeting_id},
                UpdateExpression='SET healthScore = :hs, healthGrade = :hg, healthLabel = :hl, autopsy = :a',
                ExpressionAttributeValues={
                    ':hs': health['score'],
                    ':hg': health['grade'],
                    ':hl': health['label'],
                    ':a': autopsy
                }
            )
            
            print(f"✅ Health score recalculated: {health['score']} ({health['grade']})")
        
    except Exception as e:
        # Don't fail the request if health calculation fails
        print(f"⚠️  Health score recalculation failed (non-fatal): {e}")

    return _response(200, {'success': True, 'actionId': action_id, 'completed': completed, 'status': final_status})


def _response(code, body):
    return {
        'statusCode': code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, default=decimal_to_float)
    }
