#!/usr/bin/env python3
"""
Verify the "New Test" meeting data and check for bugs
"""

import boto3
import json
from decimal import Decimal
from datetime import datetime

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("="*70)
print("VERIFYING 'NEW TEST' MEETING")
print("="*70)

# Scan for meetings with "New Test" title
response = meetings_table.scan(
    FilterExpression='contains(title, :title)',
    ExpressionAttributeValues={':title': 'New Test'}
)

meetings = response.get('Items', [])

if not meetings:
    print("\n❌ No 'New Test' meeting found!")
else:
    meeting = meetings[0]  # Get the first one
    
    print(f"\n✓ Found meeting: {meeting.get('title')}")
    print(f"  Meeting ID: {meeting.get('meetingId')}")
    print(f"  Status: {meeting.get('status')}")
    print(f"  Health Score: {meeting.get('healthScore')}/100")
    print(f"  Health Grade: {meeting.get('healthGrade')}")
    print(f"  ROI: {meeting.get('roi', {}).get('roi')}%")
    
    action_items = meeting.get('actionItems', [])
    print(f"\n  Action Items ({len(action_items)}):")
    
    unassigned_count = 0
    owner_counts = {}
    
    for i, action in enumerate(action_items, 1):
        owner = action.get('owner', 'Unassigned')
        task = action.get('task', '')
        deadline = action.get('deadline', 'No deadline')
        
        if owner == 'Unassigned' or not owner:
            unassigned_count += 1
            print(f"    {i}. ❌ UNASSIGNED: {task[:50]}... (Deadline: {deadline})")
        else:
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
            print(f"    {i}. ✓ {owner}: {task[:50]}... (Deadline: {deadline})")
    
    print(f"\n  Owner Distribution:")
    for owner, count in owner_counts.items():
        print(f"    - {owner}: {count} tasks")
    
    if unassigned_count > 0:
        print(f"\n  ⚠️  WARNING: {unassigned_count} unassigned tasks!")
    else:
        print(f"\n  ✓ SUCCESS: All {len(action_items)} tasks have owners!")
    
    # Check autopsy
    autopsy = meeting.get('autopsy')
    if autopsy:
        print(f"\n  Autopsy Generated:")
        print(f"    {autopsy}")
        
        # Check if autopsy is wrong
        if unassigned_count == 0 and 'no action items were assigned' in autopsy.lower():
            print(f"\n  ❌ BUG DETECTED: Autopsy says 'no action items assigned' but all {len(action_items)} tasks have owners!")
            print(f"     This is a Bedrock AI hallucination issue.")
        elif unassigned_count == 0 and 'leaving all' in autopsy.lower() and 'tasks unclaimed' in autopsy.lower():
            print(f"\n  ❌ BUG DETECTED: Autopsy says tasks are 'unclaimed' but all have owners!")
            print(f"     This is a Bedrock AI hallucination issue.")
    
    # Check decisions
    decisions = meeting.get('decisions', [])
    print(f"\n  Decisions ({len(decisions)}):")
    for i, decision in enumerate(decisions, 1):
        print(f"    {i}. {decision}")
    
    # Check follow-ups
    follow_ups = meeting.get('followUps', [])
    print(f"\n  Follow-ups ({len(follow_ups)}):")
    for i, followup in enumerate(follow_ups, 1):
        print(f"    {i}. {followup}")
    
    # Calculate expected health score
    print(f"\n  Health Score Analysis:")
    total = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    owned = sum(1 for a in action_items if a.get('owner') and a['owner'] != 'Unassigned')
    
    completion_rate = (completed / total) * 40 if total > 0 else 0
    owner_rate = (owned / total) * 30 if total > 0 else 0
    
    print(f"    - Completion rate: {completed}/{total} = {completion_rate:.1f}/40 points")
    print(f"    - Owner assignment: {owned}/{total} = {owner_rate:.1f}/30 points")
    print(f"    - Expected score: ~{completion_rate + owner_rate + 20 + 10:.1f}/100")
    print(f"    - Actual score: {meeting.get('healthScore')}/100")
    
    if owned == total and meeting.get('healthScore', 0) < 65:
        print(f"\n  ⚠️  NOTE: All tasks have owners but health score is low because:")
        print(f"      - 0 tasks completed yet (0/40 points)")
        print(f"      - Meeting just created (tasks not done)")
        print(f"      - This triggers autopsy generation (score < 65)")

print("\n" + "="*70)
