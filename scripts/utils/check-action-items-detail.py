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

print('Checking action items in detail:')
print('=' * 80)

for meeting in response['Items']:
    title = meeting.get('title')
    print(f"\n{title}")
    print(f"Grade: {meeting.get('healthScore')}")
    
    actions = meeting.get('actionItems', [])
    print(f"Total actions: {len(actions)}")
    
    if actions:
        print("Action items:")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. Text: {action.get('text', 'MISSING')}")
            print(f"     Status: {action.get('status', 'MISSING')}")
            print(f"     Owner: {action.get('owner', 'MISSING')}")
            print(f"     ID: {action.get('id', 'MISSING')}")
            print(f"     Epitaph: {action.get('epitaph', 'MISSING')[:50]}...")
            print()
