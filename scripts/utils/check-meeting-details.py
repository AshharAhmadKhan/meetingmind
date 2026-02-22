#!/usr/bin/env python3
import boto3
import json
from decimal import Decimal

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    return obj

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

for item in response['Items']:
    if item.get('status') == 'PENDING' or item.get('title') in ['HELLO', 'hELLO']:
        print(f"\nMeeting: {item.get('title')}")
        print(f"Status: {item.get('status')}")
        print(f"Meeting ID: {item.get('meetingId')}")
        print(f"Created: {item.get('createdAt')}")
        print(f"S3 Key: {item.get('s3Key', 'N/A')}")
        print(f"Audio URL: {item.get('audioUrl', 'N/A')}")
        print(f"Has transcript: {'transcript' in item}")
        print(f"Has summary: {'summary' in item}")
        print(f"Has actionItems: {len(item.get('actionItems', []))} items")
        
        if 'error' in item:
            print(f"ERROR: {item['error']}")
        
        # Show all keys
        print(f"\nAll keys in item:")
        for key in sorted(item.keys()):
            if key not in ['transcript', 'audioUrl', 's3Key']:
                value = item[key]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + '...'
                print(f"  {key}: {value}")
