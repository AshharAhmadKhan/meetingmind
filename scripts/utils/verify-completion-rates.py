#!/usr/bin/env python3
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=True
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

print("Demo Meeting Completion Rates")
print("="*80)

for i, meeting in enumerate(meetings, 1):
    actions = meeting.get('actionItems', [])
    completed = sum(1 for a in actions if a.get('completed'))
    total = len(actions)
    rate = (completed / total * 100) if total > 0 else 0
    
    print(f"\nMeeting {i}: {meeting.get('title')}")
    print(f"  Date: {meeting.get('createdAt')[:10]}")
    print(f"  Grade: {meeting.get('healthScore')}/100")
    print(f"  Completion: {completed}/{total} ({rate:.0f}%)")
    
    # Show which items are completed
    for j, action in enumerate(actions, 1):
        status = 'DONE' if action.get('completed') else 'TODO'
        task = action.get('task', 'N/A')
        if len(task) > 50:
            task = task[:50] + '...'
        print(f"    {j}. [{status}] {task}")

print("\n" + "="*80)
print("Expected: 14% -> 0% -> 0% -> 100% -> 80%")
print("="*80)
