#!/usr/bin/env python3
"""
Remove TTL from Existing Demo Meetings
=======================================

The 5 demo story meetings should be permanent (no TTL).
Only NEW uploads by demo user should have TTL.

This script removes the TTL field from existing demo meetings.
"""

import boto3
import sys
from datetime import datetime

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'


def main():
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("REMOVE TTL FROM DEMO MEETINGS")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    print(f"Demo User ID: {DEMO_USER_ID}")
    
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(MEETINGS_TABLE)
    
    # Fetch all meetings for demo user
    print("\n" + "="*80)
    print("FETCHING DEMO MEETINGS")
    print("="*80)
    
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': DEMO_USER_ID}
    )
    
    meetings = response['Items']
    print(f"Found {len(meetings)} demo meetings")
    
    meetings_with_ttl = []
    for meeting in meetings:
        has_ttl = 'ttl' in meeting
        ttl_value = meeting.get('ttl', 'N/A')
        print(f"  - {meeting['title']}")
        print(f"    TTL: {ttl_value if has_ttl else 'None'}")
        if has_ttl:
            meetings_with_ttl.append(meeting)
    
    if not meetings_with_ttl:
        print("\n✓ No meetings have TTL - nothing to do")
        return
    
    print(f"\n{len(meetings_with_ttl)} meetings have TTL and will be updated")
    
    if not dry_run:
        print("\n" + "="*80)
        print("REMOVING TTL")
        print("="*80)
        
        response = input("\nType 'REMOVE' to confirm: ")
        if response != 'REMOVE':
            print("✗ Cancelled")
            return
        
        for meeting in meetings_with_ttl:
            # Remove TTL field
            table.update_item(
                Key={
                    'userId': DEMO_USER_ID,
                    'meetingId': meeting['meetingId']
                },
                UpdateExpression='REMOVE #ttl SET updatedAt = :updated',
                ExpressionAttributeNames={
                    '#ttl': 'ttl'
                },
                ExpressionAttributeValues={
                    ':updated': datetime.now().isoformat()
                }
            )
            print(f"  ✓ Removed TTL from: {meeting['title']}")
        
        print("\n" + "="*80)
        print("TTL REMOVAL COMPLETE!")
        print("="*80)
        print(f"Updated {len(meetings_with_ttl)} meetings")
        print("These meetings are now permanent (no auto-delete)")
        print("New uploads by demo user will still have TTL")
    else:
        print("\n" + "="*80)
        print("To execute, run with --execute flag:")
        print("  python scripts/data/remove-ttl-from-demo-meetings.py --execute")
        print("="*80)


if __name__ == '__main__':
    main()
