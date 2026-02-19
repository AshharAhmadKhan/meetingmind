#!/usr/bin/env python3
"""Add createdAt to V2 meetings that are missing it"""

import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

print("=" * 80)
print("FIXING V2 MEETINGS - Adding createdAt")
print("=" * 80)
print()

# Get all meetings
response = table.scan()
meetings = response['Items']

# Find V2 meetings without createdAt
v2_meetings = [m for m in meetings if m.get('teamId') == V2_TEAM_ID and not m.get('createdAt')]

print(f"Found {len(v2_meetings)} V2 meetings without createdAt")
print()

# Add createdAt to each meeting (use recent dates for V2)
# V2 meetings should be recent (last 2 weeks)
base_date = datetime.now() - timedelta(days=10)

for idx, m in enumerate(v2_meetings):
    title = m.get('title', 'Untitled')
    meeting_id = m.get('meetingId')
    user_id = m.get('userId')
    
    # Stagger the dates by a few days
    created_at = (base_date + timedelta(days=idx * 2)).isoformat()
    
    print(f"Updating: {title}")
    print(f"  meetingId: {meeting_id}")
    print(f"  Adding createdAt: {created_at}")
    
    # Update the meeting
    table.update_item(
        Key={
            'userId': user_id,
            'meetingId': meeting_id
        },
        UpdateExpression='SET createdAt = :ca, updatedAt = :ua',
        ExpressionAttributeValues={
            ':ca': created_at,
            ':ua': created_at
        }
    )
    
    print(f"  ✅ Updated\n")

print("=" * 80)
print(f"✅ Successfully added createdAt to {len(v2_meetings)} meetings")
print()
print("IMPORTANT: GSI updates are eventually consistent.")
print("Wait 30-60 seconds before testing team filtering.")
print("=" * 80)
