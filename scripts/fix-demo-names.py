#!/usr/bin/env python3
"""Fix incorrect owner names in demo meetings."""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Demo user ID
user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Name corrections
name_fixes = {
    'Ahar': 'Ashhar',
    'Aliba': 'Alishba',
    'Aishba': 'Alishba',
    'Ayosh': 'Ayush',
    'Usher': 'Ashhar'
}

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

meetings = response.get('Items', [])

print("=" * 80)
print("FIXING OWNER NAMES IN DEMO MEETINGS")
print("=" * 80)

total_fixed = 0

for meeting in meetings:
    meeting_id = meeting['meetingId']
    title = meeting.get('title', 'Untitled')
    action_items = meeting.get('actionItems', [])
    
    fixed_count = 0
    
    for item in action_items:
        owner = item.get('owner', '')
        if owner in name_fixes:
            old_name = owner
            new_name = name_fixes[owner]
            item['owner'] = new_name
            fixed_count += 1
            print(f"   {title}: {old_name} → {new_name}")
    
    if fixed_count > 0:
        # Update the meeting with fixed names
        table.update_item(
            Key={'userId': user_id, 'meetingId': meeting_id},
            UpdateExpression='SET actionItems = :ai',
            ExpressionAttributeValues={':ai': action_items}
        )
        total_fixed += fixed_count
        print(f"   ✅ Updated {title} ({fixed_count} names fixed)")

print("=" * 80)
print(f"✅ Fixed {total_fixed} owner names across all meetings!")
print("\nCorrect names now: Ashhar, Alishba, Ayush")
