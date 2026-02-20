#!/usr/bin/env python3
"""
Fix the comprehensive test meeting by adding missing status field
"""

import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
MEETING_ID = "c12dbaa2-8125-4861-8d98-77b5719328ec"

def fix_meeting():
    """Add missing status and other fields to the test meeting"""
    print("\n" + "="*70)
    print("FIXING TEST MEETING")
    print("="*70)
    print()
    
    try:
        # Update the meeting with missing fields
        response = meetings_table.update_item(
            Key={
                'userId': USER_ID,
                'meetingId': MEETING_ID
            },
            UpdateExpression='SET #status = :status, updatedAt = :updated, audioUrl = :audio',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': 'DONE',
                ':updated': datetime.now(timezone.utc).isoformat(),
                ':audio': f's3://meetingmind-audio-707411439284/{MEETING_ID}.mp3'
            },
            ReturnValues='ALL_NEW'
        )
        
        meeting = response['Attributes']
        print("✅ Meeting updated successfully")
        print(f"   Status: {meeting.get('status')}")
        print(f"   Updated: {meeting.get('updatedAt')}")
        print(f"   Audio URL: {meeting.get('audioUrl')}")
        print()
        print("The meeting should now be visible and clickable in the UI!")
        
    except Exception as e:
        print(f"❌ Error updating meeting: {e}")
    
    print("="*70)

if __name__ == '__main__':
    fix_meeting()
