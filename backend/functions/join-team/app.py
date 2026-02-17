import json
import boto3
import os
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
TEAMS_TABLE = os.environ['TEAMS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Content-Type': 'application/json'
}

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        claims = event['requestContext']['authorizer']['claims']
        user_id = claims['sub']
        user_email = claims.get('email', '')
        
        body = json.loads(event.get('body') or '{}')
        invite_code = body.get('inviteCode', '').strip().upper()
        
        if not invite_code:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invite code is required'})
            }
        
        table = dynamodb.Table(TEAMS_TABLE)
        
        # Find team by invite code using GSI
        response = table.query(
            IndexName='inviteCode-index',
            KeyConditionExpression='inviteCode = :code',
            ExpressionAttributeValues={':code': invite_code}
        )
        
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invalid invite code'})
            }
        
        team = items[0]
        team_id = team['teamId']
        members = team.get('members', [])
        
        # Check if user is already a member
        if any(m['userId'] == user_id for m in members):
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'You are already a member of this team'})
            }
        
        # Add user to team
        new_member = {
            'userId': user_id,
            'email': user_email,
            'role': 'member',
            'joinedAt': datetime.now(timezone.utc).isoformat()
        }
        members.append(new_member)
        
        table.update_item(
            Key={'teamId': team_id},
            UpdateExpression='SET members = :members',
            ExpressionAttributeValues={':members': members}
        )
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'teamId': team_id,
                'teamName': team['teamName']
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
