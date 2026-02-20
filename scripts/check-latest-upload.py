#!/usr/bin/env python3
"""Check the latest upload to see what teamId it has"""

import boto3
from datetime import datetime

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'

# User who just uploaded
KELDEO_USER_ID = 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table(MEETINGS_TABLE)

# Get all meetings for this user
response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': KELDEO_USER_ID}
)

meetings = response.get('Items', [])

if not meetings:
    print("No meetings found for Keldeo")
else:
    # Sort by createdAt
    meetings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    
    print("\n" + "="*80)
    print("LATEST UPLOADS BY KELDEO (ashkagakoko@gmail.com)")
    print("="*80)
    
    for i, meeting in enumerate(meetings[:3], 1):
        print(f"\n{i}. {meeting.get('title')}")
        print(f"   MeetingId: {meeting.get('meetingId')}")
        print(f"   Status: {meeting.get('status')}")
        print(f"   CreatedAt: {meeting.get('createdAt')}")
        
        team_id = meeting.get('teamId')
        if team_id:
            print(f"   ✅ TeamId: {team_id}")
        else:
            print(f"   ❌ TeamId: NONE - Personal meeting")
        
        print(f"   Email: {meeting.get('email')}")
