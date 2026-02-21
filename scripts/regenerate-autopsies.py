#!/usr/bin/env python3
"""
Regenerate autopsies for demo meetings with the updated logic.
This removes the old autopsy so it gets regenerated on next view.
"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("Removing old autopsies to trigger regeneration...")
print("=" * 80)

for meeting in response['Items']:
    meeting_id = meeting['meetingId']
    title = meeting['title']
    
    # Check if meeting has an autopsy
    if 'autopsy' in meeting:
        print(f"📋 {title}")
        print(f"   Old autopsy: {meeting['autopsy'][:80]}...")
        
        # Remove autopsy and autopsyGeneratedAt
        table.update_item(
            Key={'userId': user_id, 'meetingId': meeting_id},
            UpdateExpression='REMOVE autopsy, autopsyGeneratedAt'
        )
        print(f"   ✅ Removed - will regenerate with new logic")
        print()

print("=" * 80)
print("✅ Autopsies removed!")
print()
print("NOTE: Autopsies are only generated for failed meetings (F grade).")
print("They will be regenerated when you view each meeting in the UI.")
print("Or you can trigger processing manually with scripts/trigger-processing.py")
