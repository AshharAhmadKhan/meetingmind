#!/usr/bin/env python3
"""
Create test graveyard data by backdating some action items
This lets you see the graveyard feature immediately without waiting 30 days
"""

import boto3
from datetime import datetime, timezone, timedelta
import uuid

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

print("=" * 70)
print("CREATING TEST GRAVEYARD DATA")
print("=" * 70)
print()

# Get first meeting to add old action items to
response = table.scan(Limit=1)
meetings = response.get('Items', [])

if not meetings:
    print("❌ No meetings found! Upload a meeting first.")
    exit(1)

meeting = meetings[0]
user_id = meeting['userId']
meeting_id = meeting['meetingId']
meeting_title = meeting.get('title', 'Test Meeting')

print(f"✓ Found meeting: {meeting_title}")
print(f"  User: {user_id}")
print(f"  Meeting ID: {meeting_id}")
print()

# Create 5 old action items (35-90 days old)
old_actions = [
    {
        'id': str(uuid.uuid4()),
        'task': 'Update project documentation with new API endpoints',
        'owner': 'Sarah',
        'deadline': (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
        'completed': False,
        'status': 'todo',
        'riskScore': 65,
        'riskLevel': 'MEDIUM',
        'createdAt': (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    },
    {
        'id': str(uuid.uuid4()),
        'task': 'Review and merge pending pull requests from Q3',
        'owner': 'Mike',
        'deadline': (datetime.now(timezone.utc) - timedelta(days=50)).isoformat(),
        'completed': False,
        'status': 'blocked',
        'riskScore': 85,
        'riskLevel': 'HIGH',
        'createdAt': (datetime.now(timezone.utc) - timedelta(days=67)).isoformat()
    },
    {
        'id': str(uuid.uuid4()),
        'task': 'Schedule team offsite for Q1 planning',
        'owner': 'Jessica',
        'deadline': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        'completed': False,
        'status': 'todo',
        'riskScore': 45,
        'riskLevel': 'MEDIUM',
        'createdAt': (datetime.now(timezone.utc) - timedelta(days=52)).isoformat()
    },
    {
        'id': str(uuid.uuid4()),
        'task': 'Migrate legacy database to new schema',
        'owner': 'David',
        'deadline': (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
        'completed': False,
        'status': 'blocked',
        'riskScore': 95,
        'riskLevel': 'CRITICAL',
        'createdAt': (datetime.now(timezone.utc) - timedelta(days=89)).isoformat()
    },
    {
        'id': str(uuid.uuid4()),
        'task': 'Set up automated testing pipeline for frontend',
        'owner': 'Alex',
        'deadline': (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
        'completed': False,
        'status': 'in_progress',
        'riskScore': 55,
        'riskLevel': 'MEDIUM',
        'createdAt': (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
    }
]

print("Creating 5 old action items:")
for i, action in enumerate(old_actions, 1):
    days_old = (datetime.now(timezone.utc) - datetime.fromisoformat(action['createdAt'])).days
    print(f"  {i}. {action['task'][:50]}... ({days_old} days old)")

print()

# Get existing action items
existing_actions = meeting.get('actionItems', [])
print(f"✓ Existing action items: {len(existing_actions)}")

# Add old actions
all_actions = existing_actions + old_actions
print(f"✓ Total action items after adding: {len(all_actions)}")
print()

# Update meeting
try:
    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression='SET actionItems = :items',
        ExpressionAttributeValues={':items': all_actions}
    )
    print("✅ Successfully added old action items to meeting!")
except Exception as e:
    print(f"❌ Failed to update meeting: {e}")
    exit(1)

print()
print("=" * 70)
print("NEXT STEP: GENERATE EPITAPHS")
print("=" * 70)
print()
print("Run this command to generate AI epitaphs:")
print("  python scripts/testing/test-fix2-epitaph-generation.py")
print()
print("Or manually invoke Lambda:")
print("  aws lambda invoke --function-name meetingmind-generate-epitaphs --region ap-south-1 response.json")
print()
