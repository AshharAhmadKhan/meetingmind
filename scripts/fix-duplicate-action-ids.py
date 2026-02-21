#!/usr/bin/env python3
"""
Fix duplicate action IDs in the database by replacing them with unique UUIDs.
This script scans all meetings and replaces non-UUID action IDs (like "action-1")
with proper UUIDs.
"""

import boto3
import uuid
from decimal import Decimal

REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def is_uuid(value):
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False

def fix_meeting_actions(meeting):
    """Fix action IDs in a single meeting."""
    user_id = meeting['userId']
    meeting_id = meeting['meetingId']
    action_items = meeting.get('actionItems', [])
    
    if not action_items:
        return 0
    
    # Check if any actions need fixing
    needs_fix = any(not is_uuid(action.get('id', '')) for action in action_items)
    
    if not needs_fix:
        return 0
    
    # Replace non-UUID IDs with UUIDs
    fixed_count = 0
    for action in action_items:
        old_id = action.get('id', '')
        if not is_uuid(old_id):
            new_id = str(uuid.uuid4())
            action['id'] = new_id
            fixed_count += 1
            print(f"  Fixed: {old_id} → {new_id} | {action.get('task', '')[:50]}")
    
    # Update the meeting in DynamoDB
    try:
        table.update_item(
            Key={'userId': user_id, 'meetingId': meeting_id},
            UpdateExpression='SET actionItems = :actions',
            ExpressionAttributeValues={':actions': action_items}
        )
        print(f"✓ Updated meeting {meeting_id} ({fixed_count} actions fixed)")
        return fixed_count
    except Exception as e:
        print(f"✗ Failed to update meeting {meeting_id}: {e}")
        return 0

def main():
    print("🔍 Scanning for meetings with duplicate action IDs...")
    
    # Scan all meetings
    response = table.scan()
    meetings = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        meetings.extend(response.get('Items', []))
    
    print(f"Found {len(meetings)} meetings")
    
    total_fixed = 0
    meetings_fixed = 0
    
    for meeting in meetings:
        meeting_id = meeting.get('meetingId', 'unknown')
        title = meeting.get('title', 'Untitled')
        print(f"\n📋 {title} ({meeting_id})")
        
        fixed = fix_meeting_actions(meeting)
        if fixed > 0:
            total_fixed += fixed
            meetings_fixed += 1
    
    print(f"\n✅ Done! Fixed {total_fixed} actions across {meetings_fixed} meetings")

if __name__ == '__main__':
    main()
