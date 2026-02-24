#!/usr/bin/env python3
"""Check action item timestamps to see if they were actually updated."""

import boto3
from datetime import datetime

REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'
MEETING_ID = '6f1f9423-a000-436e-a862-c96edb9f356d'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# Scan for the meeting
response = table.scan(
    FilterExpression='meetingId = :mid',
    ExpressionAttributeValues={':mid': MEETING_ID}
)

if not response['Items']:
    print('Meeting not found')
    exit(1)

meeting = response['Items'][0]
actions = meeting.get('actionItems', [])

print('ACTION ITEM TIMESTAMPS')
print('=' * 80)
print(f'Meeting updated at: {meeting.get("updatedAt", "N/A")}')
print()
print('Completed actions:')
print()

completed_count = 0
for i, action in enumerate(actions, 1):
    if action.get('completed'):
        completed_count += 1
        completed_at = action.get('completedAt', 'N/A')
        print(f'{i}. {action.get("task", "N/A")[:60]}...')
        print(f'   Completed at: {completed_at}')
        print()

print(f'Total completed: {completed_count}/{len(actions)}')
print()
print('DIAGNOSIS:')
if completed_count > 0:
    # Check if completedAt timestamps are recent
    recent_updates = []
    for action in actions:
        if action.get('completed') and action.get('completedAt'):
            try:
                completed_time = datetime.fromisoformat(action['completedAt'].replace('Z', '+00:00'))
                age_minutes = (datetime.now(datetime.timezone.utc) - completed_time).total_seconds() / 60
                if age_minutes < 60:  # Last hour
                    recent_updates.append(age_minutes)
            except:
                pass
    
    if recent_updates:
        print(f'  ✅ {len(recent_updates)} actions updated in last hour')
        print(f'  ⚠️  But health score NOT recalculated')
        print()
        print('POSSIBLE CAUSES:')
        print('  1. Health calculation code has an error')
        print('  2. Import from health_calculator module failing')
        print('  3. DynamoDB update for health metrics failing silently')
    else:
        print('  ℹ️  No recent updates (all completions are old)')
else:
    print('  ℹ️  No completed actions found')
