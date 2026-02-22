#!/usr/bin/env python3
"""
Fix Weekly Check-In completion to 4/5
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get Weekly Check-In meeting
response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

checkin = next((m for m in response['Items'] if m.get('title') == 'Weekly Check-In'), None)

if not checkin:
    print("❌ Weekly Check-In not found")
    exit(1)

print("Current action items:")
actions = checkin.get('actionItems', [])
for i, action in enumerate(actions):
    status = action.get('status', 'UNKNOWN')
    text = action.get('text', 'NO TEXT')
    owner = action.get('owner', 'Unassigned')
    print(f"{i+1}. [{status}] {text} (Owner: {owner})")

print("\n" + "=" * 80)
print("FIXING COMPLETION STATUS")
print("=" * 80)

# Fix: 4 should be DONE, 1 should be TODO
for action in actions:
    text = action.get('text', '')
    
    # These 4 should be DONE
    if any(keyword in text.lower() for keyword in ['auth bug', 'job browse', 'email notification', 'load testing']):
        if action.get('status') != 'DONE':
            print(f"✅ Marking DONE: {text}")
            action['status'] = 'DONE'
            action['completed'] = True
    
    # This 1 should be TODO
    elif 'launch beta' in text.lower() or '10 colleges' in text.lower():
        if action.get('status') == 'DONE':
            print(f"⬜ Marking TODO: {text}")
            action['status'] = 'TODO'
            action['completed'] = False

# Update the meeting
meetings_table.update_item(
    Key={
        'userId': demo_user_id,
        'meetingId': checkin['meetingId']
    },
    UpdateExpression='SET actionItems = :actions',
    ExpressionAttributeValues={
        ':actions': actions
    }
)

print("\n✅ Updated Weekly Check-In")
print("\nNew status:")
done_count = sum(1 for a in actions if a.get('status') == 'DONE')
print(f"Completion: {done_count}/{len(actions)}")
