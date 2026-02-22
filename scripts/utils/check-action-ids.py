#!/usr/bin/env python3
"""Check if demo meetings have action item IDs"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

print("\nChecking action item IDs in demo meetings:\n")

for meeting in meetings:
    print(f"Meeting: {meeting['title']}")
    actions = meeting.get('actionItems', [])
    print(f"  Total actions: {len(actions)}")
    
    for i, action in enumerate(actions, 1):
        has_id = 'id' in action
        action_id = action.get('id', 'MISSING')
        task = action.get('task', 'N/A')[:50]
        print(f"    {i}. ID: {action_id if has_id else '❌ MISSING'} | {task}")
    
    print()
