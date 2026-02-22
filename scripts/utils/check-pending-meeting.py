#!/usr/bin/env python3
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

print('All meetings for demo user:')
print('='*80)
for item in response['Items']:
    title = item.get('title', 'N/A')
    status = item.get('status', 'N/A')
    created = item.get('createdAt', 'N/A')[:19]
    print(f'\n{title}')
    print(f'  Status: {status}')
    print(f'  Created: {created}')
    
    if title == 'HELLO' or status == 'pending':
        print(f'  Meeting ID: {item.get("meetingId")}')
        print(f'  Has transcript: {"transcript" in item}')
        print(f'  Has summary: {"summary" in item}')
        print(f'  Action items: {len(item.get("actionItems", []))}')
        print(f'  Audio URL: {item.get("audioUrl", "N/A")[:50]}...')
        
        # Check if there's an error
        if 'error' in item:
            print(f'  ERROR: {item["error"]}')

print('\n' + '='*80)
