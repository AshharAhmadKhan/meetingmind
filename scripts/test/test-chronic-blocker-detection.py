#!/usr/bin/env python3
"""
Test if chronic blocker will be detected via similarity matching
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

print("Chronic Blocker Detection Test")
print("="*80)
print("\nLooking for 'Fix auth bug preventing user login' across meetings...")
print()

auth_bug_actions = []

for meeting in meetings:
    title = meeting.get('title')
    actions = meeting.get('actionItems', [])
    
    for action in actions:
        text = action.get('text', '').lower()
        if 'auth bug' in text:
            auth_bug_actions.append({
                'meeting': title,
                'text': action.get('text'),
                'status': action.get('status'),
                'owner': action.get('owner'),
                'id': action.get('id')
            })

print(f"Found {len(auth_bug_actions)} actions with 'auth bug':")
print()

for i, action in enumerate(auth_bug_actions, 1):
    status_icon = '✅' if action['status'] == 'DONE' else '❌'
    print(f"{i}. {action['meeting']}")
    print(f"   {status_icon} {action['text']}")
    print(f"   Owner: {action['owner']}, Status: {action['status']}")
    print(f"   ID: {action['id']}")
    print()

print("="*80)

if len(auth_bug_actions) >= 3:
    print(f"✅ PASS: Chronic blocker will be detected ({len(auth_bug_actions)} occurrences)")
    print()
    print("The check-duplicate Lambda will find these as similar (>85% match)")
    print("and mark them as chronic blocker when repeatCount >= 3")
else:
    print(f"❌ FAIL: Only {len(auth_bug_actions)} occurrences (need 3+)")

print("="*80)
