#!/usr/bin/env python3
"""
Fix Demo User ID Mismatch
==========================

The demo meetings are stored under the wrong user ID.
This script moves them to the correct Cognito sub.

OLD: c1c38d2a-1081-7088-7c71-0abc19a150e9
NEW: 41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c
"""

import boto3
import sys
from datetime import datetime

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
OLD_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
NEW_USER_ID = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'


def main():
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("FIX DEMO USER ID MISMATCH")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    print(f"Old User ID: {OLD_USER_ID}")
    print(f"New User ID: {NEW_USER_ID}")
    
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(MEETINGS_TABLE)
    
    # Fetch all meetings for old user ID
    print("\n" + "="*80)
    print("FETCHING MEETINGS")
    print("="*80)
    
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': OLD_USER_ID}
    )
    
    meetings = response['Items']
    print(f"Found {len(meetings)} meetings to migrate")
    
    if not meetings:
        print("No meetings found - nothing to do")
        return
    
    for meeting in meetings:
        print(f"  - {meeting['title']} ({meeting['meetingId']})")
    
    if not dry_run:
        print("\n" + "="*80)
        print("MIGRATING MEETINGS")
        print("="*80)
        
        response = input("\nType 'MIGRATE' to confirm: ")
        if response != 'MIGRATE':
            print("✗ Cancelled")
            return
        
        for meeting in meetings:
            # Update userId
            meeting['userId'] = NEW_USER_ID
            meeting['updatedAt'] = datetime.now().isoformat()
            
            # Write to new location
            table.put_item(Item=meeting)
            print(f"  ✓ Migrated: {meeting['title']}")
        
        # Delete old items
        print("\n" + "="*80)
        print("CLEANING UP OLD ITEMS")
        print("="*80)
        
        for meeting in meetings:
            table.delete_item(
                Key={
                    'userId': OLD_USER_ID,
                    'meetingId': meeting['meetingId']
                }
            )
            print(f"  ✓ Deleted old: {meeting['title']}")
        
        print("\n" + "="*80)
        print("MIGRATION COMPLETE!")
        print("="*80)
        print(f"Migrated {len(meetings)} meetings")
        print(f"From: {OLD_USER_ID}")
        print(f"To: {NEW_USER_ID}")
    else:
        print("\n" + "="*80)
        print("To execute, run with --execute flag:")
        print("  python scripts/data/fix-demo-user-id.py --execute")
        print("="*80)


if __name__ == '__main__':
    main()
