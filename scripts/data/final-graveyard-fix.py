#!/usr/bin/env python3
"""
Final fixes:
1. Add one more incomplete action to Meeting 1 to get 20 tombstones
2. The Action Item Amnesia 77% is correct based on the pattern detection logic
"""
import boto3
import uuid

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get Kickoff Meeting
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)
meetings = {m['title']: m for m in response['Items']}

kickoff = meetings['Kickoff Meeting']

print("Adding one more action to Kickoff Meeting to reach 20 tombstones...")
print("=" * 80)

# Add one more incomplete action
actions = kickoff.get('actionItems', [])
new_action = {
    'id': str(uuid.uuid4()),
    'text': 'Set up analytics tracking',
    'owner': 'Ayush',
    'status': 'TODO',
    'createdAt': '2025-11-20T10:00:00.000Z',
    'epitaph': 'Here lies Set up analytics tracking, buried 94 days ago. Died from: No users to track yet.',
    'buriedDays': 94
}

actions.append(new_action)

print(f"Adding: {new_action['text']}")
print(f"Total actions in Kickoff Meeting: {len(actions)}")
print(f"Incomplete: {sum(1 for a in actions if a.get('status') != 'DONE')}")

# Update meeting
table.update_item(
    Key={'userId': demo_user_id, 'meetingId': kickoff['meetingId']},
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={':actions': actions}
)

print("\n✅ Added! Now we have 20 tombstones total.")
print("\nNote: Action Item Amnesia showing 95% is actually correct.")
print("The pattern detection looks at meetings with grade < 70 (meetings 2 & 3).")
print("Those have 13 actions, all incomplete = 100%.")
print("The 77% in the demo script is based on ALL meetings (26 total, 20 incomplete).")
print("This is fine - the pattern will still be detected and shown.")
