import json
import boto3
import os
import uuid
from datetime import datetime, timezone
import random
import string

dynamodb = boto3.resource('dynamodb')
TEAMS_TABLE = os.environ['TEAMS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Content-Type': 'application/json'
}

def generate_invite_code():
    """Generate a 6-character alphanumeric invite code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        claims = event['requestContext']['authorizer']['claims']
        user_id = claims['sub']
        user_email = claims.get('email', '')
        
        body = json.loads(event.get('body') or '{}')
        team_name = body.get('teamName', '').strip()
        
        if not team_name:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Team name is required'})
            }
        
        team_id = str(uuid.uuid4())
        invite_code = generate_invite_code()
        
        table = dynamodb.Table(TEAMS_TABLE)
        table.put_item(Item={
            'teamId': team_id,
            'teamName': team_name,
            'inviteCode': invite_code,
            'createdBy': user_id,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'members': [
                {
                    'userId': user_id,
                    'email': user_email,
                    'role': 'owner',
                    'joinedAt': datetime.now(timezone.utc).isoformat()
                }
            ]
        })
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'teamId': team_id,
                'teamName': team_name,
                'inviteCode': invite_code
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
