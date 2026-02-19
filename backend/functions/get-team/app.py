import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TEAMS_TABLE = os.environ['TEAMS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
    'Content-Type': 'application/json'
}

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        claims = event['requestContext']['authorizer']['claims']
        user_id = claims['sub']
        
        team_id = event['pathParameters']['teamId']
        
        table = dynamodb.Table(TEAMS_TABLE)
        response = table.get_item(Key={'teamId': team_id})
        
        team = response.get('Item')
        if not team:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Team not found'})
            }
        
        # Check if user is a member
        members = team.get('members', [])
        if not any(m['userId'] == user_id for m in members):
            return {
                'statusCode': 403,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'You are not a member of this team'})
            }
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'teamId': team['teamId'],
                'teamName': team['teamName'],
                'inviteCode': team['inviteCode'],
                'members': members,
                'createdAt': team.get('createdAt', '')
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
