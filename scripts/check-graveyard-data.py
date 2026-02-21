#!/usr/bin/env python3
"""
Check the actual structure of graveyard items
"""
import boto3
import json
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get cyber user's meetings
user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

meetings = response.get('Items', [])
print(f"Found {len(meetings)} meetings\n")

# Find graveyard items (>30 days old)
graveyard_items = []
for meeting in meetings:
    actions = meeting.get('actionItems', [])
    for action in actions:
        if action.get('completed'):
            continue
        
        created_at = action.get('createdAt')
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now(timezone.utc) - created).days
                
                if days_old > 30:
                    graveyard_items.append({
                        'meeting_id': meeting.get('meetingId'),
                        'meeting_title': meeting.get('title'),
                        'action_id': action.get('id'),
                        'task': action.get('task'),
                        'owner': action.get('owner'),
                        'days_old': days_old
                    })
            except:
                pass

print(f"Found {len(graveyard_items)} graveyard items:\n")

for item in graveyard_items:
    print(f"Meeting: {item['meeting_title']}")
    print(f"  Meeting ID: {item['meeting_id']}")
    print(f"  Action ID: {item['action_id']}")
    print(f"  Task: {item['task'][:50]}...")
    print(f"  Owner: {item['owner']}")
    print(f"  Days old: {item['days_old']}")
    print()
