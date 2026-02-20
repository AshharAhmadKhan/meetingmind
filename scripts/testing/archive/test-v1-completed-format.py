#!/usr/bin/env python3
"""
Test if V1 completed items have 'completed' field or just 'status' field
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

response = meetings_table.scan()
meetings = response.get('Items', [])

print("Checking completed action item formats:\n")

for meeting in meetings:
    title = meeting.get('title', 'Untitled')
    action_items = meeting.get('actionItems', [])
    
    for action in action_items:
        is_completed = action.get('completed', False)
        status = action.get('status', '')
        
        if is_completed or status == 'DONE' or status == 'done':
            task = (action.get('task') or action.get('text', ''))[:50]
            print(f"Meeting: {title}")
            print(f"  Task: {task}")
            print(f"  completed field: {action.get('completed')}")
            print(f"  status field: {action.get('status')}")
            print(f"  is_complete check: {is_completed}")
            print()
