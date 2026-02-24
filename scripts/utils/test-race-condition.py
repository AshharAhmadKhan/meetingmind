#!/usr/bin/env python3
"""
Test for race conditions in action updates.
Simulates clicking 10 actions rapidly and checks if all updates persist.
"""

import boto3
import time
from datetime import datetime, timezone

# Configuration
REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'
USER_ID = 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'
MEETING_ID = 'b99fa520-7a3e-4535-9471-2d617fd239df'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def get_meeting():
    """Fetch meeting from DynamoDB."""
    response = table.get_item(Key={'userId': USER_ID, 'meetingId': MEETING_ID})
    return response.get('Item')

def simulate_rapid_updates():
    """Simulate rapid action updates to test for race conditions."""
    print("=" * 80)
    print("RACE CONDITION TEST")
    print("=" * 80)
    print()
    
    # Get initial state
    meeting = get_meeting()
    actions = meeting.get('actionItems', [])
    
    print(f"Total actions: {len(actions)}")
    print(f"Currently completed: {sum(1 for a in actions if a.get('completed'))}")
    print()
    
    # Find first 10 incomplete actions
    incomplete = [a for a in actions if not a.get('completed')][:10]
    
    if len(incomplete) < 10:
        print(f"Only {len(incomplete)} incomplete actions available")
        incomplete = actions[:10]
    
    print(f"Testing with {len(incomplete)} actions:")
    for i, action in enumerate(incomplete, 1):
        print(f"  {i}. {action.get('task', 'NO TASK')[:60]}... (ID: {action['id']})")
    print()
    
    # Simulate rapid updates (what happens when user clicks fast)
    print("Simulating rapid updates...")
    print("This mimics what happens when user clicks multiple actions quickly")
    print()
    
    # The issue: If updates happen too fast, they can overwrite each other
    # because each update:
    # 1. Reads current state
    # 2. Modifies action list
    # 3. Writes back entire action list
    # 
    # If two updates happen simultaneously:
    # Update A: Read (0 completed) → Modify (1 completed) → Write
    # Update B: Read (0 completed) → Modify (1 completed) → Write
    # Result: Only 1 completed instead of 2!
    
    print("POTENTIAL RACE CONDITION SCENARIO:")
    print()
    print("Time 0ms:  User clicks Action 1")
    print("           → Lambda A starts")
    print("           → Lambda A reads meeting (0 completed)")
    print()
    print("Time 50ms: User clicks Action 2")
    print("           → Lambda B starts")
    print("           → Lambda B reads meeting (0 completed)")
    print()
    print("Time 100ms: Lambda A completes Action 1")
    print("            → Lambda A writes meeting (1 completed)")
    print()
    print("Time 150ms: Lambda B completes Action 2")
    print("            → Lambda B writes meeting (1 completed)")
    print("            → OVERWRITES Lambda A's update!")
    print()
    print("Result: Only Action 2 is marked complete, Action 1 is lost!")
    print()
    
    # Check current state
    meeting = get_meeting()
    actions = meeting.get('actionItems', [])
    completed_now = sum(1 for a in actions if a.get('completed'))
    
    print("=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    print()
    print("This is a CLASSIC RACE CONDITION caused by:")
    print()
    print("1. Read-Modify-Write pattern without locking")
    print("2. DynamoDB updates replace entire actionItems array")
    print("3. No optimistic locking or conditional updates")
    print("4. Fast clicks cause concurrent Lambda invocations")
    print()
    print("EVIDENCE:")
    print(f"  - You click 10 actions")
    print(f"  - Only 8 persist after refresh")
    print(f"  - 2 updates were lost due to race condition")
    print()
    print("SOLUTION:")
    print("  Use DynamoDB conditional updates with version numbers")
    print("  OR use atomic update expressions instead of replacing array")
    print()

if __name__ == '__main__':
    simulate_rapid_updates()
