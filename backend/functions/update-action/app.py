import json
import boto3
import os
from datetime import datetime, timezone

dynamodb   = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']


def lambda_handler(event, context):
    user_id    = event['requestContext']['authorizer']['claims']['sub']
    meeting_id = event['pathParameters']['meetingId']
    action_id  = event['pathParameters']['actionId']
    body       = json.loads(event.get('body') or '{}')
    completed  = body.get('completed', False)

    table    = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    item     = response.get('Item')

    if not item:
        return _response(404, {'error': 'Meeting not found'})

    actions = item.get('actionItems', [])
    updated = False
    for action in actions:
        if action.get('id') == action_id:
            action['completed'] = completed
            action['completedAt'] = datetime.now(timezone.utc).isoformat() if completed else None
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

    return _response(200, {'success': True, 'actionId': action_id, 'completed': completed})


def _response(code, body):
    return {
        'statusCode': code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(body)
    }
