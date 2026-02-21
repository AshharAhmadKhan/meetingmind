#!/usr/bin/env python3
"""Check all demo meetings and show owner names for each action item."""

import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Demo user ID
user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings for demo user
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

meetings = response.get('Items', [])
if not meetings:
    print("No meetings found!")
    exit(0)

meetings = sorted(meetings, key=lambda x: x.get('createdAt', ''))

print("=" * 80)
print("DEMO MEETINGS - OWNER NAME CHECK")
print("=" * 80)

for meeting in meetings:
    meeting_id = meeting['meetingId']
    title = meeting.get('title', 'Untitled')
    created_at = meeting.get('createdAt', 'N/A')
    action_items = meeting.get('actionItems', [])
    
    print(f"\n📋 {title}")
    print(f"   ID: {meeting_id}")
    print(f"   Created: {created_at}")
    print(f"   Action Items: {len(action_items)}")
    
    if action_items:
        print(f"\n   Owners found:")
        owners = {}
        for item in action_items:
            owner = item.get('owner', 'Unassigned')
            owners[owner] = owners.get(owner, 0) + 1
        
        for owner, count in sorted(owners.items()):
            print(f"      - {owner}: {count} tasks")
    
    print("-" * 80)

print("\n✅ Check complete!")
print("\nCorrect names should be: Ashhar, Alishba, Ayush")
print("If you see variations (Usher, Aliba, etc.), we'll fix them.")
