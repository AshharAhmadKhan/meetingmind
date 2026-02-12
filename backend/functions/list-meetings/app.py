import json
import boto3
import os

dynamodb   = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']


def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    table   = dynamodb.Table(TABLE_NAME)

    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id},
        ScanIndexForward=False,   # newest first
        ProjectionExpression='meetingId, title, #st, createdAt, updatedAt, summary',
        ExpressionAttributeNames={'#st': 'status'}
    )

    meetings = response.get('Items', [])
    # Sort newest first by createdAt
    meetings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'meetings': meetings})
    }
