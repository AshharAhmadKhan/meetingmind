#!/usr/bin/env python3
"""Check the D3D3 meeting to see if it has teamId"""

import boto3

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'

# User who just uploaded (thehiddenif)
USER_ID = 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'
MEETING_ID = '5474cb4d-03fc-49bd-8126-bed8c32216d5'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table(MEETINGS_TABLE)

# Get the specific meeting
response = meetings_table.get_item(
    Key={'userId': USER_ID, 'meetingId': MEETING_ID}
)

meeting = response.get('Item')

if not meeting:
    print(f"❌ Meeting not found: {MEETING_ID}")
else:
    print("\n" + "="*80)
    print(f"MEETING: {meeting.get('title')}")
    print("="*80)
    print(f"MeetingId: {meeting.get('meetingId')}")
    print(f"Status: {meeting.get('status')}")
    print(f"CreatedAt: {meeting.get('createdAt')}")
    
    team_id = meeting.get('teamId')
    if team_id:
        print(f"✅ TeamId: {team_id}")
    else:
        print(f"❌ TeamId: NONE - Personal meeting")
    
    print(f"Email: {meeting.get('email')}")
    print(f"\nFull item: {meeting}")
