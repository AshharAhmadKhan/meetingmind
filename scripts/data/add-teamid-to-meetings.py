#!/usr/bin/env python3
"""Add teamId to meetings that are missing it"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# V2 team ID
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

# Get all meetings
response = table.scan()
meetings = response['Items']

print(f'Total meetings: {len(meetings)}\n')

# Find meetings without teamId
meetings_without_teamid = [m for m in meetings if not m.get('teamId')]

print(f'Meetings WITHOUT teamId: {len(meetings_without_teamid)}')
print('-' * 80)

for m in meetings_without_teamid:
    title = m.get('title', 'Untitled')
    meeting_id = m.get('meetingId')
    user_id = m.get('userId')
    
    print(f"Updating: {title}")
    print(f"  meetingId: {meeting_id}")
    print(f"  userId: {user_id}")
    print(f"  Adding teamId: {V2_TEAM_ID}")
    
    # Update the meeting with teamId
    table.update_item(
        Key={
            'userId': user_id,
            'meetingId': meeting_id
        },
        UpdateExpression='SET teamId = :tid',
        ExpressionAttributeValues={
            ':tid': V2_TEAM_ID
        }
    )
    
    print(f"  ✅ Updated\n")

print('-' * 80)
print(f'\n✅ Successfully added teamId to {len(meetings_without_teamid)} meetings')
