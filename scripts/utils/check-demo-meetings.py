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

print('Demo User Meetings:')
print('=' * 80)
for i, item in enumerate(response['Items'], 1):
    print(f"\n{i}. {item.get('title', 'N/A')}")
    print(f"   Grade: {item.get('healthScore', 'N/A')}")
    print(f"   Date: {item.get('createdAt', 'N/A')}")
    summary = item.get('summary', 'N/A')
    if len(summary) > 150:
        summary = summary[:150] + '...'
    print(f"   Summary: {summary}")
    print(f"   Actions: {len(item.get('actionItems', []))}")
    print(f"   Decisions: {len(item.get('decisions', []))}")
    
    # Show action items
    actions = item.get('actionItems', [])
    if actions:
        print(f"   Action Items:")
        for action in actions[:3]:  # Show first 3
            status = '✅' if action.get('status') == 'DONE' else '❌'
            print(f"     {status} {action.get('text', 'N/A')}")
        if len(actions) > 3:
            print(f"     ... and {len(actions) - 3} more")

print('\n' + '=' * 80)
print(f"Total meetings: {len(response['Items'])}")
