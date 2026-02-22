#!/usr/bin/env python3
"""
Verify that the Kanban drag-and-drop fix is working by checking:
1. All action IDs are now unique UUIDs
2. No duplicate IDs exist in the database
"""

import boto3
import uuid
from collections import Counter

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

def main():
    print("🔍 Verifying Kanban fix...")
    
    # Scan all meetings
    response = table.scan()
    meetings = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        meetings.extend(response.get('Items', []))
    
    print(f"Found {len(meetings)} meetings\n")
    
    all_action_ids = []
    non_uuid_count = 0
    meetings_with_actions = 0
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        if not action_items:
            continue
        
        meetings_with_actions += 1
        
        for action in action_items:
            action_id = action.get('id', '')
            all_action_ids.append(action_id)
            
            if not is_uuid(action_id):
                non_uuid_count += 1
                print(f"❌ Non-UUID ID found: {action_id} in meeting {meeting.get('meetingId')}")
                print(f"   Task: {action.get('task', '')[:50]}")
    
    # Check for duplicates
    id_counts = Counter(all_action_ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}
    
    print(f"\n📊 Results:")
    print(f"  Total meetings: {len(meetings)}")
    print(f"  Meetings with actions: {meetings_with_actions}")
    print(f"  Total actions: {len(all_action_ids)}")
    print(f"  Non-UUID IDs: {non_uuid_count}")
    print(f"  Duplicate IDs: {len(duplicates)}")
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate IDs:")
        for dup_id, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {dup_id}: appears {count} times")
    
    if non_uuid_count == 0 and len(duplicates) == 0:
        print(f"\n✅ SUCCESS! All action IDs are unique UUIDs")
        print(f"   Kanban drag-and-drop should now work correctly")
        return True
    else:
        print(f"\n❌ FAILED! Issues found:")
        if non_uuid_count > 0:
            print(f"   - {non_uuid_count} actions still have non-UUID IDs")
        if len(duplicates) > 0:
            print(f"   - {len(duplicates)} duplicate IDs still exist")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
