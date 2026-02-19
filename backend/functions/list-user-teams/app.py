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
        
        table = dynamodb.Table(TEAMS_TABLE)
        
        # Scan all teams and filter by membership (inefficient but simple for MVP)
        # TODO: Add userId-teamId GSI for efficient queries
        response = table.scan()
        
        user_teams = []
        for team in response.get('Items', []):
            members = team.get('members', [])
            if any(m['userId'] == user_id for m in members):
                user_teams.append({
                    'teamId': team['teamId'],
                    'teamName': team['teamName'],
                    'memberCount': len(members),
                    'role': next((m['role'] for m in members if m['userId'] == user_id), 'member')
                })
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'teams': user_teams})
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
