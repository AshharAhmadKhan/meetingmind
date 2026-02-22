#!/usr/bin/env python3
"""Show detailed demo meeting information"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    return obj

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=True  # Chronological order
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

print("\n" + "="*100)
print("DEMO MEETINGS - COMPLETE DETAILS")
print("="*100)

for i, meeting in enumerate(meetings, 1):
    print(f"\n{'='*100}")
    print(f"MEETING {i}: {meeting.get('title', 'N/A')}")
    print(f"{'='*100}")
    print(f"Date: {meeting.get('createdAt', 'N/A')[:10]}")
    print(f"Grade: {meeting.get('healthScore', 'N/A')}/100")
    print(f"\nSummary:")
    print(f"  {meeting.get('summary', 'N/A')}")
    
    # Action Items
    actions = meeting.get('actionItems', [])
    completed = sum(1 for a in actions if a.get('completed'))
    total = len(actions)
    rate = (completed / total * 100) if total > 0 else 0
    
    print(f"\nAction Items ({completed}/{total} completed = {rate:.0f}%):")
    for j, action in enumerate(actions, 1):
        status = '✅ DONE' if action.get('completed') else '❌ TODO'
        owner = action.get('owner', 'Unassigned')
        deadline = action.get('deadline', 'No deadline')
        task = action.get('task', 'N/A')
        print(f"  {j}. {status} | {owner} | Due: {deadline}")
        print(f"     {task}")
    
    # Decisions
    decisions = meeting.get('decisions', [])
    print(f"\nDecisions ({len(decisions)} total):")
    for j, decision in enumerate(decisions, 1):
        print(f"  {j}. {decision}")
    
    # Follow-ups
    followups = meeting.get('followUps', [])
    if followups:
        print(f"\nFollow-ups ({len(followups)} total):")
        for j, followup in enumerate(followups, 1):
            print(f"  {j}. {followup}")

print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print(f"Total meetings: {len(meetings)}")
print(f"Date range: {meetings[0].get('createdAt', 'N/A')[:10]} to {meetings[-1].get('createdAt', 'N/A')[:10]}")
print(f"Grade progression: {' → '.join(str(m.get('healthScore', 'N/A')) for m in meetings)}")
print(f"\nStory Arc: F → F → F → A → B")
print("="*100 + "\n")
