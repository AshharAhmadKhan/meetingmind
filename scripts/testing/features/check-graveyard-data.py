#!/usr/bin/env python3
"""
Check if there are any completed (buried) action items in the database
"""
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("=" * 60)
print("GRAVEYARD DATA CHECK")
print("=" * 60)

# Get all meetings
response = meetings_table.scan()
meetings = response.get('Items', [])

print(f"\n✓ Found {len(meetings)} meetings total")

# Count action items by status
total_actions = 0
completed_actions = 0
incomplete_actions = 0
graveyard_items = []

for meeting in meetings:
    meeting_title = meeting.get('title', 'Untitled')
    meeting_id = meeting.get('meetingId', 'unknown')
    team_id = meeting.get('teamId', 'personal')
    action_items = meeting.get('actionItems', [])
    
    for action in action_items:
        total_actions += 1
        
        # Check if completed (V1 and V2 formats)
        is_completed = action.get('completed', False)
        status = action.get('status', '')
        
        # V1 uses status: "DONE", V2 uses completed: true
        if is_completed or status == 'DONE':
            completed_actions += 1
            
            # Calculate days old
            created_at_str = action.get('createdAt') or meeting.get('createdAt')
            days_old = 0
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    days_old = (datetime.now(timezone.utc) - created_at).days
                except:
                    pass
            
            graveyard_items.append({
                'meeting': meeting_title,
                'meetingId': meeting_id,
                'teamId': team_id,
                'task': action.get('task') or action.get('text', 'Unknown'),
                'owner': action.get('owner', 'Unassigned'),
                'daysOld': days_old,
                'completed': is_completed,
                'status': status
            })
        else:
            incomplete_actions += 1

print(f"\n📊 Action Items Summary:")
print(f"   Total: {total_actions}")
print(f"   Incomplete: {incomplete_actions}")
print(f"   Completed (Graveyard): {completed_actions}")

if completed_actions > 0:
    print(f"\n⚰️  GRAVEYARD ITEMS ({len(graveyard_items)}):")
    print("-" * 60)
    for item in graveyard_items:
        print(f"\n   Meeting: {item['meeting']}")
        print(f"   Team: {item['teamId']}")
        print(f"   Task: {item['task'][:60]}...")
        print(f"   Owner: {item['owner']}")
        print(f"   Days Old: {item['daysOld']}")
        print(f"   Completed: {item['completed']}, Status: {item['status']}")
else:
    print(f"\n❌ NO GRAVEYARD ITEMS FOUND")
    print("   All action items are incomplete - nothing has been marked as done")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)

if completed_actions == 0:
    print("✗ Graveyard is empty because NO actions are marked complete")
    print("  This is expected if all tasks are still in progress")
else:
    print(f"✓ Graveyard should show {completed_actions} items")
    print("  If graveyard page is empty, there's a bug in the frontend/backend")

print()
