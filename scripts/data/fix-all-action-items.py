#!/usr/bin/env python3
"""
Completely fix all action items with correct text, status, and completion.
Based on DEMO_STORY_FINAL.md specifications.
"""
import boto3
import uuid
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)
meetings = {m['title']: m for m in response['Items']}

print("Fixing all action items with correct data...")
print("=" * 80)

# Meeting 1: Kickoff Meeting (1/7 completed = 14%)
print("\n1. Kickoff Meeting")
meeting1_actions = [
    {"text": "Register the company", "owner": "Zeeshan", "status": "DONE"},
    {"text": "Design all 15 screens", "owner": "Alishba", "status": "TODO"},
    {"text": "Build the complete backend", "owner": "Ayush", "status": "TODO"},
    {"text": "Get 50 beta signups", "owner": "Zeeshan", "status": "TODO"},
    {"text": "Write an investor pitch", "owner": "Zeeshan", "status": "TODO"},
    {"text": "Create social media accounts", "owner": "Zeeshan", "status": "TODO"},
    {"text": "Build a landing page", "owner": "Zeeshan", "status": "TODO"}
]

actions1 = []
for action_data in meeting1_actions:
    action = {
        'id': str(uuid.uuid4()),
        'text': action_data['text'],
        'owner': action_data['owner'],
        'status': action_data['status'],
        'createdAt': '2025-11-20T10:00:00.000Z'
    }
    actions1.append(action)
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"  {status_icon} {action['text']} ({action['owner']})")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meetings['Kickoff Meeting']['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions1}
)

# Meeting 2: Mid-Project Crisis (0/7 completed = 0%)
print("\n2. Mid-Project Crisis")
meeting2_actions = [
    {"text": "Fix auth bug preventing user login", "owner": "Ayush", "status": "TODO"},
    {"text": "Complete landing page", "owner": "Alishba", "status": "TODO"},
    {"text": "Finish API endpoints", "owner": "Ayush", "status": "TODO"},
    {"text": "Email 20 colleges", "owner": "Zeeshan", "status": "TODO"},
    {"text": "Write pricing page copy", "owner": "Zeeshan", "status": "TODO"},
    {"text": "Design pricing page", "owner": "Alishba", "status": "TODO"},
    {"text": "Create beta sign-up form", "owner": "Alishba", "status": "TODO"}
]

actions2 = []
for action_data in meeting2_actions:
    action = {
        'id': str(uuid.uuid4()),
        'text': action_data['text'],
        'owner': action_data['owner'],
        'status': action_data['status'],
        'createdAt': '2025-12-05T14:00:00.000Z'
    }
    actions2.append(action)
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"  {status_icon} {action['text']} ({action['owner']})")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meetings['Mid-Project Crisis']['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions2}
)

# Meeting 3: Last Attempt Before Pivot (0/6 completed = 0%)
print("\n3. Last Attempt Before Pivot")
meeting3_actions = [
    {"text": "Fix auth bug preventing user login", "owner": "Ayush", "status": "TODO"},
    {"text": "Redesign profile page", "owner": "Alishba", "status": "TODO"},
    {"text": "Finish job browse page", "owner": "Alishba", "status": "TODO"},
    {"text": "Set up load testing", "owner": "Ayush", "status": "TODO"},
    {"text": "Recruit 5 beta testers", "owner": "Ayush", "status": "TODO"},
    {"text": "Write landing page copy", "owner": "Zeeshan", "status": "TODO"}
]

actions3 = []
for action_data in meeting3_actions:
    action = {
        'id': str(uuid.uuid4()),
        'text': action_data['text'],
        'owner': action_data['owner'],
        'status': action_data['status'],
        'createdAt': '2025-12-20T16:00:00.000Z'
    }
    actions3.append(action)
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"  {status_icon} {action['text']} ({action['owner']})")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meetings['Last Attempt Before Pivot']['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions3}
)

# Meeting 4: Should We Pivot (1/1 completed = 100%)
print("\n4. Should We Pivot")
meeting4_actions = [
    {"text": "Discuss target user, core feature, and business model in group chat", "owner": "Zeeshan", "status": "DONE"}
]

actions4 = []
for action_data in meeting4_actions:
    action = {
        'id': str(uuid.uuid4()),
        'text': action_data['text'],
        'owner': action_data['owner'],
        'status': action_data['status'],
        'createdAt': '2026-02-02T11:00:00.000Z'
    }
    actions4.append(action)
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"  {status_icon} {action['text']} ({action['owner']})")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meetings['Should We Pivot']['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions4}
)

# Meeting 5: Weekly Check-In (4/5 completed = 80%)
print("\n5. Weekly Check-In")
meeting5_actions = [
    {"text": "Fix auth bug preventing user login", "owner": "Ayush", "status": "DONE"},
    {"text": "Finish job browse page", "owner": "Alishba", "status": "DONE"},
    {"text": "Check email notifications in production", "owner": "Ayush", "status": "DONE"},
    {"text": "Set up load testing", "owner": "Ayush", "status": "DONE"},
    {"text": "Redesign profile page", "owner": "Alishba", "status": "TODO"}
]

actions5 = []
for action_data in meeting5_actions:
    action = {
        'id': str(uuid.uuid4()),
        'text': action_data['text'],
        'owner': action_data['owner'],
        'status': action_data['status'],
        'createdAt': '2026-02-11T10:00:00.000Z'
    }
    actions5.append(action)
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"  {status_icon} {action['text']} ({action['owner']})")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meetings['Weekly Check-In']['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions5}
)

print("\n" + "=" * 80)
print("✅ All action items fixed!")
print("\nNow run: python scripts/utils/verify-demo-checklist.py")
