#!/usr/bin/env python3
"""
Verify the resurrected action
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get the meeting
user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
meeting_id = '27c1d9c8-0aee-46aa-9e10-887d599b71fc'

response = table.get_item(
    Key={'userId': user_id, 'meetingId': meeting_id}
)

meeting = response.get('Item')
if not meeting:
    print("❌ Meeting not found")
    exit(1)

print(f"Meeting: {meeting['title']}")
print(f"Meeting ID: {meeting['meetingId']}")
print(f"\nAction Items:")

# Find the resurrected action
action_id = '6c3c4215-3783-47f5-b2b0-967c1cc4b16a'
found = False

for action in meeting.get('actionItems', []):
    if action.get('id') == action_id:
        found = True
        print(f"\n✅ Found resurrected action:")
        print(f"   Task: {action.get('task')}")
        print(f"   Status: {action.get('status')}")
        print(f"   Owner: {action.get('owner')}")
        print(f"   Deadline: {action.get('deadline')}")
        print(f"   Completed: {action.get('completed')}")
        print(f"   Created: {action.get('createdAt')}")
        
        # Check if it's in the correct state
        if action.get('status') == 'todo' and not action.get('completed'):
            print(f"\n✅ Action successfully resurrected!")
            print(f"   - Status changed to 'todo'")
            print(f"   - Marked as incomplete")
            print(f"   - Should appear in Kanban 'To Do' column")
        else:
            print(f"\n⚠️  Action state unexpected:")
            print(f"   - Status: {action.get('status')} (expected: todo)")
            print(f"   - Completed: {action.get('completed')} (expected: False)")
        break

if not found:
    print(f"\n❌ Action {action_id} not found in meeting")
