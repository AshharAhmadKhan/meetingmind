#!/usr/bin/env python3
"""
Fix action item completion status to match the intended demo story.
This script ensures the correct items are marked as completed/incomplete.
"""
import boto3
import json
from decimal import Decimal
from datetime import datetime

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

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=True
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

print("Fixing action item completion status...")
print("="*80)

# Meeting 1: Only "Register the company" should be completed
meeting1 = meetings[0]
print(f"\nMeeting 1: {meeting1['title']}")
print(f"Date: {meeting1['createdAt'][:10]}")

for action in meeting1['actionItems']:
    task = action.get('task', '')
    current_status = action.get('completed', False)
    
    # Only "Register the company" should be completed
    if 'Register the company' in task:
        action['completed'] = True
        action['completedAt'] = meeting1['createdAt']
        print(f"  ✅ {task} - SET TO COMPLETED")
    else:
        action['completed'] = False
        action['completedAt'] = None
        print(f"  ❌ {task} - SET TO INCOMPLETE")

# Update Meeting 1
table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meeting1['meetingId']},
    UpdateExpression='SET actionItems = :a, updatedAt = :t',
    ExpressionAttributeValues={
        ':a': meeting1['actionItems'],
        ':t': datetime.utcnow().isoformat()
    }
)
print("  ✓ Meeting 1 updated")

# Meeting 2: All should be incomplete (0/7)
meeting2 = meetings[1]
print(f"\nMeeting 2: {meeting2['title']}")
print(f"Date: {meeting2['createdAt'][:10]}")

for action in meeting2['actionItems']:
    action['completed'] = False
    action['completedAt'] = None
    print(f"  ❌ {action.get('task', '')} - SET TO INCOMPLETE")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meeting2['meetingId']},
    UpdateExpression='SET actionItems = :a, updatedAt = :t',
    ExpressionAttributeValues={
        ':a': meeting2['actionItems'],
        ':t': datetime.utcnow().isoformat()
    }
)
print("  ✓ Meeting 2 updated")

# Meeting 3: All should be incomplete (0/6)
meeting3 = meetings[2]
print(f"\nMeeting 3: {meeting3['title']}")
print(f"Date: {meeting3['createdAt'][:10]}")

for action in meeting3['actionItems']:
    action['completed'] = False
    action['completedAt'] = None
    print(f"  ❌ {action.get('task', '')} - SET TO INCOMPLETE")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meeting3['meetingId']},
    UpdateExpression='SET actionItems = :a, updatedAt = :t',
    ExpressionAttributeValues={
        ':a': meeting3['actionItems'],
        ':t': datetime.utcnow().isoformat()
    }
)
print("  ✓ Meeting 3 updated")

# Meeting 4: Only 1 action, should be completed (1/1)
meeting4 = meetings[3]
print(f"\nMeeting 4: {meeting4['title']}")
print(f"Date: {meeting4['createdAt'][:10]}")

for action in meeting4['actionItems']:
    action['completed'] = True
    action['completedAt'] = meeting4['createdAt']
    print(f"  ✅ {action.get('task', '')} - SET TO COMPLETED")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meeting4['meetingId']},
    UpdateExpression='SET actionItems = :a, updatedAt = :t',
    ExpressionAttributeValues={
        ':a': meeting4['actionItems'],
        ':t': datetime.utcnow().isoformat()
    }
)
print("  ✓ Meeting 4 updated")

# Meeting 5: 4/5 should be completed
meeting5 = meetings[4]
print(f"\nMeeting 5: {meeting5['title']}")
print(f"Date: {meeting5['createdAt'][:10]}")

for action in meeting5['actionItems']:
    task = action.get('task', '')
    
    # Only "Redesign profile page" should be incomplete
    if 'Redesign profile page' in task:
        action['completed'] = False
        action['completedAt'] = None
        print(f"  ❌ {task} - SET TO INCOMPLETE")
    else:
        action['completed'] = True
        action['completedAt'] = meeting5['createdAt']
        print(f"  ✅ {task} - SET TO COMPLETED")

table.update_item(
    Key={'userId': demo_user_id, 'meetingId': meeting5['meetingId']},
    UpdateExpression='SET actionItems = :a, updatedAt = :t',
    ExpressionAttributeValues={
        ':a': meeting5['actionItems'],
        ':t': datetime.utcnow().isoformat()
    }
)
print("  ✓ Meeting 5 updated")

print("\n" + "="*80)
print("✅ All action item completion statuses fixed!")
print("\nExpected completion rates:")
print("  Meeting 1: 1/7 (14%)")
print("  Meeting 2: 0/7 (0%)")
print("  Meeting 3: 0/6 (0%)")
print("  Meeting 4: 1/1 (100%)")
print("  Meeting 5: 4/5 (80%)")
print("="*80)
