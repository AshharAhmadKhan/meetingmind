import json
import boto3
import os
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):
    user_id    = event['requestContext']['authorizer']['claims']['sub']
    meeting_id = event['pathParameters']['meetingId']
    table      = dynamodb.Table(TABLE_NAME)

    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    item     = response.get('Item')

    if not item:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Meeting not found'})
        }

    # Remove raw transcript from response (too large for UI, keep structured data)
    item.pop('transcript', None)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(item, cls=DecimalEncoder)
    }
