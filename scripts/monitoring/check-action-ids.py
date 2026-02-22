#!/usr/bin/env python3
"""
Check actual action IDs in the database
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get cyber user's meetings
user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

meetings = response.get('Items', [])

# Find the V1 Meeting 1 that has "Design the UI mockups"
for meeting in meetings:
    if 'V1 Meeting 1' in meeting.get('title', ''):
        print(f"Meeting: {meeting['title']}")
        print(f"Meeting ID: {meeting['meetingId']}")
        print(f"\nAction Items:")
        
        for action in meeting.get('actionItems', []):
            task = action.get('task') or action.get('text', '')
            if 'Design' in task or 'UI' in task:
                print(f"\n  Task: {task}")
                print(f"  Action ID: {action.get('id')}")
                print(f"  Action ID (repr): {repr(action.get('id'))}")
                print(f"  Action ID (bytes): {action.get('id').encode('utf-8')}")
                print(f"  Owner: {action.get('owner')}")
                print(f"  Completed: {action.get('completed')}")
                print(f"  Created: {action.get('createdAt')}")
