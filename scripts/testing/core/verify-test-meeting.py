#!/usr/bin/env python3
"""
Verify the comprehensive test meeting is accessible
"""

import boto3
import json

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"
MEETING_ID = "c12dbaa2-8125-4861-8d98-77b5719328ec"

def check_database():
    """Check if meeting exists in DynamoDB"""
    print("\n" + "="*70)
    print("CHECKING DATABASE")
    print("="*70)
    
    try:
        response = meetings_table.get_item(
            Key={
                'userId': USER_ID,
                'meetingId': MEETING_ID
            }
        )
        
        if 'Item' in response:
            meeting = response['Item']
            print("✅ Meeting found in database")
            print(f"   Title: {meeting.get('title')}")
            print(f"   Team ID: {meeting.get('teamId')}")
            print(f"   Health Score: {meeting.get('healthScore')}")
            print(f"   ROI: {meeting.get('roi')}%")
            print(f"   Action Items: {len(meeting.get('actionItems', []))}")
            return True
        else:
            print("❌ Meeting NOT found in database")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def check_team_query():
    """Check if meeting appears in team query"""
    print("\n" + "="*70)
    print("CHECKING TEAM QUERY")
    print("="*70)
    
    try:
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={
                ':tid': TEAM_ID
            },
            ScanIndexForward=False
        )
        
        meetings = response.get('Items', [])
        print(f"✅ Found {len(meetings)} meetings for team")
        
        test_meeting = next((m for m in meetings if m['meetingId'] == MEETING_ID), None)
        if test_meeting:
            print("✅ Test meeting found in team query")
            print(f"   Title: {test_meeting.get('title')}")
            return True
        else:
            print("❌ Test meeting NOT found in team query")
            print("\nMeetings found:")
            for m in meetings:
                print(f"  - {m.get('title')} ({m.get('meetingId')})")
            return False
    except Exception as e:
        print(f"❌ Error checking team query: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST MEETING VERIFICATION")
    print("="*70)
    print()
    print(f"Meeting ID: {MEETING_ID}")
    print(f"User ID: {USER_ID}")
    print(f"Team ID: {TEAM_ID}")
    
    db_ok = check_database()
    team_ok = check_team_query()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if db_ok and team_ok:
        print("✅ Meeting is accessible and ready for testing")
        print()
        print("NEXT STEPS:")
        print("1. Open MeetingMind in browser")
        print("2. Hard refresh (Ctrl+Shift+R) or open in incognito mode")
        print("3. Select 'Project V1 - Legacy' team")
        print("4. You should see 'Comprehensive Feature Test Meeting' as first card")
        print()
        print("If still not visible:")
        print("- Check browser console for errors (F12)")
        print("- Verify you're logged in as thecyberprinciples@gmail.com")
        print("- Try clearing browser cache completely")
    else:
        print("❌ Meeting has issues - see details above")
    
    print("="*70)

if __name__ == '__main__':
    main()
