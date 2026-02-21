#!/usr/bin/env python3
"""Check for any tasks assigned to 'Team' instead of individuals."""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("Checking for 'Team' assignments...")
print("=" * 80)

for meeting in response['Items']:
    action_items = meeting.get('actionItems', [])
    team_tasks = []
    
    for i, action in enumerate(action_items):
        owner = action.get('owner', '')
        if owner.lower() == 'team':
            team_tasks.append((i, action.get('task', 'Unknown task')))
    
    if team_tasks:
        print(f"\n📋 {meeting['title']}")
        print(f"   Meeting ID: {meeting['meetingId']}")
        for idx, task in team_tasks:
            print(f"   [{idx}] {task}")

print("\n" + "=" * 80)
