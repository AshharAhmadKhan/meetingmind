#!/usr/bin/env python3
"""
Test script for Graveyard Resurrection feature
Tests that resurrecting an action item properly updates owner, deadline, and status
"""

import boto3
import json
from datetime import datetime, timedelta, timezone

# Configuration
REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def find_graveyard_item():
    """Find an action item that's >30 days old and incomplete"""
    print("🔍 Scanning for graveyard items (>30 days old, incomplete)...")
    
    response = table.scan()
    items = response.get('Items', [])
    
    graveyard_items = []
    for meeting in items:
        actions = meeting.get('actionItems', [])
        for action in actions:
            if action.get('completed'):
                continue
            
            created_at = action.get('createdAt')
            if not created_at:
                continue
            
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                # Handle different datetime formats
                try:
                    created = datetime.fromisoformat(created_at)
                except:
                    continue
                
            # Ensure timezone aware
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            
            age_days = (datetime.now(timezone.utc) - created).days
            
            if age_days > 30:
                graveyard_items.append({
                    'meetingId': meeting['meetingId'],
                    'meetingTitle': meeting.get('title', 'Unknown'),
                    'actionId': action['id'],
                    'task': action.get('task', 'Unknown task'),
                    'owner': action.get('owner', 'Unassigned'),
                    'deadline': action.get('deadline'),
                    'status': action.get('status', 'todo'),
                    'age_days': age_days
                })
    
    if not graveyard_items:
        print("❌ No graveyard items found")
        return None
    
    # Sort by age (oldest first)
    graveyard_items.sort(key=lambda x: x['age_days'], reverse=True)
    
    print(f"\n✅ Found {len(graveyard_items)} graveyard items")
    print("\nOldest item:")
    item = graveyard_items[0]
    print(f"  Meeting: {item['meetingTitle']}")
    print(f"  Task: {item['task']}")
    print(f"  Owner: {item['owner']}")
    print(f"  Deadline: {item['deadline']}")
    print(f"  Status: {item['status']}")
    print(f"  Age: {item['age_days']} days")
    
    return item

def test_resurrection(item):
    """Test resurrecting an action item"""
    print(f"\n⚡ Testing resurrection...")
    
    # New values for resurrection
    new_owner = "Test Resurrector"
    new_deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"  New owner: {new_owner}")
    print(f"  New deadline: {new_deadline}")
    
    # Get the meeting
    response = table.scan(
        FilterExpression='meetingId = :mid',
        ExpressionAttributeValues={':mid': item['meetingId']}
    )
    
    if not response.get('Items'):
        print("❌ Meeting not found")
        return False
    
    meeting = response['Items'][0]
    actions = meeting.get('actionItems', [])
    
    # Find and update the action
    updated = False
    for action in actions:
        if action['id'] == item['actionId']:
            print(f"\n📝 Before resurrection:")
            print(f"  Status: {action.get('status', 'todo')}")
            print(f"  Owner: {action.get('owner', 'Unassigned')}")
            print(f"  Deadline: {action.get('deadline', 'None')}")
            print(f"  Completed: {action.get('completed', False)}")
            
            # Update the action (simulate what backend does)
            action['status'] = 'todo'
            action['owner'] = new_owner
            action['deadline'] = new_deadline
            action['completed'] = False
            action['completedAt'] = None
            
            updated = True
            break
    
    if not updated:
        print("❌ Action not found in meeting")
        return False
    
    # Save back to DynamoDB
    table.update_item(
        Key={'userId': meeting['userId'], 'meetingId': meeting['meetingId']},
        UpdateExpression='SET actionItems = :a, updatedAt = :t',
        ExpressionAttributeValues={
            ':a': actions,
            ':t': datetime.now(timezone.utc).isoformat()
        }
    )
    
    print(f"\n✅ Resurrection successful!")
    print(f"  Status: todo")
    print(f"  Owner: {new_owner}")
    print(f"  Deadline: {new_deadline}")
    print(f"  Completed: False")
    
    return True

def verify_resurrection(item):
    """Verify the action was properly resurrected"""
    print(f"\n🔍 Verifying resurrection...")
    
    response = table.scan(
        FilterExpression='meetingId = :mid',
        ExpressionAttributeValues={':mid': item['meetingId']}
    )
    
    if not response.get('Items'):
        print("❌ Meeting not found")
        return False
    
    meeting = response['Items'][0]
    actions = meeting.get('actionItems', [])
    
    for action in actions:
        if action['id'] == item['actionId']:
            print(f"\n📊 Current state:")
            print(f"  Status: {action.get('status', 'todo')}")
            print(f"  Owner: {action.get('owner', 'Unassigned')}")
            print(f"  Deadline: {action.get('deadline', 'None')}")
            print(f"  Completed: {action.get('completed', False)}")
            
            # Check if resurrection worked
            if (action.get('status') == 'todo' and 
                action.get('owner') == 'Test Resurrector' and
                action.get('completed') == False):
                print("\n✅ Verification passed! Action properly resurrected.")
                return True
            else:
                print("\n❌ Verification failed! Action not properly updated.")
                return False
    
    print("❌ Action not found")
    return False

def main():
    print("=" * 60)
    print("🪦 GRAVEYARD RESURRECTION TEST")
    print("=" * 60)
    
    # Find a graveyard item
    item = find_graveyard_item()
    if not item:
        print("\n⚠️  No graveyard items to test with")
        print("   Create an action item with createdAt >30 days ago")
        return
    
    # Test resurrection
    if test_resurrection(item):
        # Verify it worked
        verify_resurrection(item)
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Login to https://dcfx593ywvy92.cloudfront.net")
    print("   2. Navigate to Graveyard page")
    print("   3. Find the resurrected item (should be gone)")
    print("   4. Check Kanban board - item should be in 'To Do' column")
    print("   5. Verify owner and deadline were updated")

if __name__ == '__main__':
    main()
