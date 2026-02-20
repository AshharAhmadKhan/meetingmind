#!/usr/bin/env python3
"""
Test that teamId is preserved during meeting processing.

This script:
1. Checks the latest meeting uploaded to a team
2. Verifies teamId is present in the database
3. Confirms the fix for the teamId preservation bug
"""

import boto3
from datetime import datetime

# Configuration
REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
USER_ID = 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'  # thehiddenif@gmail.com

# Team IDs
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(MEETINGS_TABLE)

def check_latest_meetings():
    """Check the latest meetings for this user."""
    print(f"\n{'='*80}")
    print(f"CHECKING LATEST MEETINGS FOR USER: {USER_ID}")
    print(f"{'='*80}\n")
    
    # Query all meetings for this user
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': USER_ID},
        ScanIndexForward=False,  # Sort by createdAt descending
        Limit=10
    )
    
    meetings = response.get('Items', [])
    
    if not meetings:
        print("❌ No meetings found for this user")
        return
    
    print(f"Found {len(meetings)} recent meetings:\n")
    
    for i, meeting in enumerate(meetings, 1):
        meeting_id = meeting.get('meetingId', 'N/A')
        title = meeting.get('title', 'Untitled')
        status = meeting.get('status', 'UNKNOWN')
        team_id = meeting.get('teamId')
        created_at = meeting.get('createdAt', 'N/A')
        
        # Determine team name
        if team_id == V1_TEAM_ID:
            team_name = "V1 - Legacy"
        elif team_id == V2_TEAM_ID:
            team_name = "V2 - Active"
        elif team_id:
            team_name = f"Unknown Team ({team_id[:8]}...)"
        else:
            team_name = "Personal (Just Me)"
        
        # Status indicator
        if team_id:
            status_icon = "✅"
        else:
            status_icon = "❌"
        
        print(f"{i}. {status_icon} {title}")
        print(f"   Meeting ID: {meeting_id}")
        print(f"   Status: {status}")
        print(f"   Team: {team_name}")
        print(f"   Created: {created_at}")
        
        if team_id:
            print(f"   ✅ TeamId preserved: {team_id}")
        else:
            print(f"   ❌ NO TEAMID - Meeting is personal")
        
        print()

def check_specific_meeting(meeting_id):
    """Check a specific meeting by ID."""
    print(f"\n{'='*80}")
    print(f"CHECKING SPECIFIC MEETING: {meeting_id}")
    print(f"{'='*80}\n")
    
    response = table.get_item(
        Key={
            'userId': USER_ID,
            'meetingId': meeting_id
        }
    )
    
    meeting = response.get('Item')
    
    if not meeting:
        print(f"❌ Meeting {meeting_id} not found")
        return
    
    title = meeting.get('title', 'Untitled')
    status = meeting.get('status', 'UNKNOWN')
    team_id = meeting.get('teamId')
    
    print(f"Title: {title}")
    print(f"Status: {status}")
    
    if team_id:
        if team_id == V1_TEAM_ID:
            team_name = "V1 - Legacy"
        elif team_id == V2_TEAM_ID:
            team_name = "V2 - Active"
        else:
            team_name = f"Unknown Team ({team_id[:8]}...)"
        
        print(f"✅ TeamId: {team_id}")
        print(f"✅ Team: {team_name}")
        print(f"\n✅ SUCCESS: TeamId is preserved!")
    else:
        print(f"❌ NO TEAMID")
        print(f"❌ Team: Personal (Just Me)")
        print(f"\n❌ FAILURE: TeamId was NOT preserved!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Check specific meeting
        meeting_id = sys.argv[1]
        check_specific_meeting(meeting_id)
    else:
        # Check latest meetings
        check_latest_meetings()
        
        print(f"\n{'='*80}")
        print("INSTRUCTIONS:")
        print(f"{'='*80}")
        print("1. Upload a new meeting to V1 or V2 team")
        print("2. Wait for processing to complete (status = DONE)")
        print("3. Run this script again to verify teamId is preserved")
        print("4. Or run: python test-teamid-preservation.py <meeting-id>")
        print(f"{'='*80}\n")
