#!/usr/bin/env python3
"""
Test pattern detection logic to see what patterns should be detected
"""
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=True
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

# Filter to last 120 days
from datetime import timezone
cutoff = datetime.now(timezone.utc) - timedelta(days=120)
recent_meetings = [m for m in meetings if datetime.fromisoformat(m['createdAt'].replace('Z', '+00:00')) >= cutoff]

print("Pattern Detection Analysis")
print("="*80)
print(f"Total meetings: {len(meetings)}")
print(f"Recent meetings (last 90 days): {len(recent_meetings)}")
print(f"Cutoff date: {cutoff.date()}")
print()

# Show which meetings are included
for meeting in meetings:
    date = datetime.fromisoformat(meeting['createdAt'].replace('Z', '+00:00'))
    days_ago = (datetime.now(timezone.utc) - date).days
    included = "✅ INCLUDED" if date >= cutoff else "❌ FILTERED OUT"
    print(f"{meeting['title']}: {date.date()} ({days_ago} days ago) {included}")

print("\n" + "="*80)

# Collect all action items from recent meetings
all_actions = []
for meeting in recent_meetings:
    meeting_id = meeting['meetingId']
    for action in meeting.get('actionItems', []):
        all_actions.append({
            'meetingId': meeting_id,
            'task': action.get('task', ''),
            'completed': action.get('completed', False),
            'owner': action.get('owner', 'Unassigned'),
            'createdAt': meeting['createdAt']
        })

print(f"\nTotal action items from recent meetings: {len(all_actions)}")
print(f"MIN_MEETINGS requirement: 5")
print(f"MIN_ACTIONS requirement: 10")

if len(recent_meetings) < 5:
    print(f"\n❌ FAIL: Only {len(recent_meetings)} meetings (need 5)")
    print("   Pattern detection will return empty array")
elif len(all_actions) < 10:
    print(f"\n❌ FAIL: Only {len(all_actions)} actions (need 10)")
    print("   Pattern detection will return empty array")
else:
    print(f"\n✅ PASS: Enough data for pattern detection")

print("\n" + "="*80)
print("PATTERN CHECKS:")
print("="*80)

# Pattern 1: Action Item Amnesia
incomplete_count = sum(1 for a in all_actions if not a['completed'])
incomplete_rate = (incomplete_count / len(all_actions) * 100) if all_actions else 0
INDUSTRY_INCOMPLETE_RATE = 33

print(f"\n1. Action Item Amnesia:")
print(f"   Incomplete rate: {incomplete_rate:.1f}%")
print(f"   Industry average: {INDUSTRY_INCOMPLETE_RATE}%")
print(f"   Threshold: >{INDUSTRY_INCOMPLETE_RATE + 20}%")
if incomplete_rate > INDUSTRY_INCOMPLETE_RATE + 20:
    print(f"   ✅ DETECTED: {incomplete_rate:.1f}% > {INDUSTRY_INCOMPLETE_RATE + 20}%")
else:
    print(f"   ❌ NOT DETECTED: {incomplete_rate:.1f}% <= {INDUSTRY_INCOMPLETE_RATE + 20}%")

# Pattern 2: Chronic Blocker
task_counts = {}
for action in all_actions:
    task = action['task'].lower().strip()
    if len(task) > 10:
        task_counts[task] = task_counts.get(task, 0) + 1

duplicates = [(task, count) for task, count in task_counts.items() if count >= 3]

print(f"\n2. Chronic Blocker:")
print(f"   Looking for tasks repeated 3+ times...")
if duplicates:
    for task, count in sorted(duplicates, key=lambda x: x[1], reverse=True):
        print(f"   ✅ DETECTED: '{task[:60]}...' repeated {count} times")
else:
    print(f"   ❌ NOT DETECTED: No tasks repeated 3+ times")

# Show task frequency
print(f"\n   Task frequency (top 5):")
for task, count in sorted(task_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"     {count}x: {task[:60]}")

print("\n" + "="*80)
