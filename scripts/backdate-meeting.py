#!/usr/bin/env python3
"""
Backdate a meeting and all its action items in DynamoDB.

Usage:
    python scripts/backdate-meeting.py <MEETING_ID> <DAYS_AGO>

Example:
    python scripts/backdate-meeting.py abc123 52
"""

import boto3
import sys
from datetime import datetime, timezone, timedelta

def backdate_meeting(meeting_id, days_ago, user_id='41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'):
    """Backdate a meeting and all its action items."""
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('meetingmind-meetings')
    
    # Calculate the backdated timestamp
    backdated_time = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    
    print(f"🔍 Looking for meeting {meeting_id}...")
    
    # Get the meeting directly using the key
    try:
        response = table.get_item(
            Key={'userId': user_id, 'meetingId': meeting_id}
        )
    except Exception as e:
        print(f"❌ Error fetching meeting: {e}")
        sys.exit(1)
    
    if 'Item' not in response:
        print(f"❌ Meeting {meeting_id} not found")
        sys.exit(1)
    
    meeting = response['Item']
    
    print(f"✅ Found meeting: {meeting.get('title', 'Untitled')}")
    print(f"   User ID: {user_id}")
    print(f"   Current createdAt: {meeting.get('createdAt', 'N/A')}")
    print(f"   Action items: {len(meeting.get('actionItems', []))}")
    print()
    
    # Update createdAt for meeting
    print(f"⏰ Backdating meeting to {days_ago} days ago...")
    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression='SET createdAt = :ca',
        ExpressionAttributeValues={':ca': backdated_time}
    )
    
    # Update createdAt for all action items
    action_items = meeting.get('actionItems', [])
    if action_items:
        print(f"⏰ Backdating {len(action_items)} action items...")
        for action in action_items:
            action['createdAt'] = backdated_time
        
        table.update_item(
            Key={'userId': user_id, 'meetingId': meeting_id},
            UpdateExpression='SET actionItems = :ai',
            ExpressionAttributeValues={':ai': action_items}
        )
    
    print()
    print(f"✅ Meeting {meeting_id} backdated to {days_ago} days ago")
    print(f"   New createdAt: {backdated_time}")
    print(f"   All {len(action_items)} action items updated")
    print()
    print("🪦 These items should now appear in the Graveyard!")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python scripts/backdate-meeting.py <MEETING_ID> <DAYS_AGO>")
        print("Example: python scripts/backdate-meeting.py abc123 52")
        sys.exit(1)
    
    meeting_id = sys.argv[1]
    try:
        days_ago = int(sys.argv[2])
    except ValueError:
        print("Error: DAYS_AGO must be a number")
        sys.exit(1)
    
    if days_ago < 0:
        print("Error: DAYS_AGO must be positive")
        sys.exit(1)
    
    backdate_meeting(meeting_id, days_ago)
