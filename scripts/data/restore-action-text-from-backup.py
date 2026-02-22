#!/usr/bin/env python3
"""
Restore action item text fields from backup.
The text field was accidentally removed during previous updates.
"""
import boto3
import json
from decimal import Decimal

# Load backup
with open('demo_complete_backup_20260222_161939.json', 'r') as f:
    backup_file = json.load(f)
    backup_data = backup_file['meetings']

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

print("Restoring action item text from backup...")
print("=" * 80)

for backup_meeting in backup_data:
    meeting_id = backup_meeting['meetingId']
    title = backup_meeting['title']
    
    print(f"\nProcessing: {title}")
    
    # Get current meeting from DynamoDB
    response = table.get_item(
        Key={
            'userId': demo_user_id,
            'meetingId': meeting_id
        }
    )
    
    if 'Item' not in response:
        print(f"  ⚠️  Meeting not found in DynamoDB")
        continue
    
    current_meeting = response['Item']
    current_actions = current_meeting.get('actionItems', [])
    backup_actions = backup_meeting.get('actionItems', [])
    
    # Create mapping of action IDs to backup actions
    backup_map = {action['id']: action for action in backup_actions}
    
    # Restore text for each action
    updated_actions = []
    for action in current_actions:
        action_id = action.get('id')
        if action_id in backup_map:
            backup_action = backup_map[action_id]
            # Restore text field
            action['text'] = backup_action.get('text', 'MISSING')
            print(f"  ✅ Restored: {action['text'][:60]}...")
        else:
            print(f"  ⚠️  No backup found for action ID: {action_id}")
        
        updated_actions.append(action)
    
    # Update meeting in DynamoDB
    table.update_item(
        Key={
            'userId': demo_user_id,
            'meetingId': meeting_id
        },
        UpdateExpression='SET actionItems = :actions',
        ExpressionAttributeValues={
            ':actions': updated_actions
        }
    )
    
    print(f"  ✅ Updated {len(updated_actions)} actions")

print("\n" + "=" * 80)
print("✅ Restoration complete!")
print("\nRun verify-demo-checklist.py to confirm all tests pass.")
