#!/usr/bin/env python3
"""
Add Missing Action Item IDs
============================

The transformation script created action items without IDs.
This script adds unique IDs to all action items that are missing them.
"""

import boto3
import sys
import uuid
from datetime import datetime

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'


def main():
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("ADD MISSING ACTION ITEM IDs")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(MEETINGS_TABLE)
    
    # Fetch all meetings
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': DEMO_USER_ID}
    )
    
    meetings = response['Items']
    meetings_to_fix = []
    
    print("\n" + "="*80)
    print("ANALYZING MEETINGS")
    print("="*80)
    
    for meeting in meetings:
        actions = meeting.get('actionItems', [])
        missing_ids = sum(1 for a in actions if 'id' not in a)
        
        print(f"\n{meeting['title']}:")
        print(f"  Total actions: {len(actions)}")
        print(f"  Missing IDs: {missing_ids}")
        
        if missing_ids > 0:
            meetings_to_fix.append(meeting)
            print(f"  ✓ Will add {missing_ids} IDs")
    
    if not meetings_to_fix:
        print("\n✓ All action items have IDs - nothing to do")
        return
    
    print(f"\n{len(meetings_to_fix)} meetings need fixing")
    
    if not dry_run:
        print("\n" + "="*80)
        print("ADDING MISSING IDs")
        print("="*80)
        
        response = input("\nType 'FIX' to confirm: ")
        if response != 'FIX':
            print("✗ Cancelled")
            return
        
        for meeting in meetings_to_fix:
            actions = meeting.get('actionItems', [])
            fixed_count = 0
            
            for action in actions:
                if 'id' not in action:
                    action['id'] = str(uuid.uuid4())
                    fixed_count += 1
            
            # Update meeting
            table.update_item(
                Key={
                    'userId': DEMO_USER_ID,
                    'meetingId': meeting['meetingId']
                },
                UpdateExpression='SET actionItems = :a, updatedAt = :t',
                ExpressionAttributeValues={
                    ':a': actions,
                    ':t': datetime.now().isoformat()
                }
            )
            
            print(f"  ✓ {meeting['title']}: Added {fixed_count} IDs")
        
        print("\n" + "="*80)
        print("FIX COMPLETE!")
        print("="*80)
        print(f"Fixed {len(meetings_to_fix)} meetings")
        print("All action items now have unique IDs")
    else:
        print("\n" + "="*80)
        print("To execute, run with --execute flag:")
        print("  python scripts/data/add-missing-action-ids.py --execute")
        print("="*80)


if __name__ == '__main__':
    main()
