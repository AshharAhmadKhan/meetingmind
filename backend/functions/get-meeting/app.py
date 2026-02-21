import json
import boto3
import os
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
    # Return unchanged for non-Decimal objects (let JSON encoder handle it)
    return obj


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    user_id    = event['requestContext']['authorizer']['claims']['sub']
    meeting_id = event['pathParameters']['meetingId']
    table      = dynamodb.Table(TABLE_NAME)

    # First try to get meeting by userId (uploader)
    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    item     = response.get('Item')

    # If not found, scan for the meeting (for team members)
    # This is less efficient but works without adding a new GSI
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
                            return {
                                'statusCode': 403,
                                'headers': CORS_HEADERS,
                                'body': json.dumps({'error': 'Not authorized to view this meeting'})
                            }
                    else:
                        # Team not found - deny access
                        return {
                            'statusCode': 403,
                            'headers': CORS_HEADERS,
                            'body': json.dumps({'error': 'Team not found'})
                        }
        except Exception as e:
            print(f"Error scanning for meetingId: {e}")

    if not item:
        return {
            'statusCode': 404,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Meeting not found'}, default=decimal_to_float)
        }

    # Remove raw transcript from response (too large for UI, keep structured data)
    item.pop('transcript', None)

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps(item, default=decimal_to_float)
    }
