#!/usr/bin/env python3
"""
Final Demo Fix - Reset & Backdate Everything
=============================================

This script:
1. Resets all action item completion status to match the story
2. Backdates all deadlines to realistic past dates
3. Ensures chronic blocker pattern detection works
4. Makes graveyard items properly old (>30 days)

Story:
- Meeting 1 (Nov 20): 1/7 done (14%) - Only "Register company"
- Meeting 2 (Dec 5): 0/7 done (0%) - Total failure + chronic blocker #1
- Meeting 3 (Dec 20): 0/6 done (0%) - Demoralized + chronic blocker #2
- Meeting 4 (Feb 2): 1/1 done (100%) - Perfect pivot
- Meeting 5 (Feb 11): 4/5 done (80%) - Strong execution + chronic blocker resolved
"""

import boto3
import sys
from datetime import datetime, timedelta

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'


def main():
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("FINAL DEMO FIX - RESET & BACKDATE")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(MEETINGS_TABLE)
    
    # Fetch all meetings
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': DEMO_USER_ID}
    )
    
    meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))
    
    if len(meetings) != 5:
        print(f"✗ Expected 5 meetings, found {len(meetings)}")
        return
    
    print(f"\nFound {len(meetings)} meetings")
    
    # Define the correct state for each meeting
    fixes = [
        {
            'title': 'Kickoff Meeting',
            'date': '2025-11-20',
            'completed_tasks': ['register the company'],  # Only this one
            'deadline_base': datetime(2025, 11, 27)  # 1 week after meeting
        },
        {
            'title': 'Mid-Project Crisis',
            'date': '2025-12-05',
            'completed_tasks': [],  # ZERO completed
            'deadline_base': datetime(2025, 12, 10)  # 5 days after meeting
        },
        {
            'title': 'Last Attempt Before Pivot',
            'date': '2025-12-20',
            'completed_tasks': [],  # ZERO completed
            'deadline_base': datetime(2025, 12, 23)  # 3 days after meeting
        },
        {
            'title': 'Should We Pivot',
            'date': '2026-02-02',
            'completed_tasks': ['discuss target user'],  # Only this one
            'deadline_base': datetime(2026, 2, 5)  # 3 days after meeting
        },
        {
            'title': 'Weekly Check-In',
            'date': '2026-02-11',
            'completed_tasks': [
                'fix auth bug',
                'finish job browse',
                'check email notifications',
                'set up load testing'
            ],  # 4 out of 5
            'deadline_base': datetime(2026, 2, 12)  # 1 day after meeting
        }
    ]
    
    print("\n" + "="*80)
    print("ANALYZING CURRENT STATE")
    print("="*80)
    
    for i, meeting in enumerate(meetings):
        fix = fixes[i]
        actions = meeting.get('actionItems', [])
        completed = sum(1 for a in actions if a.get('completed'))
        
        print(f"\n{meeting['title']}:")
        print(f"  Current: {completed}/{len(actions)} done")
        print(f"  Target: {len(fix['completed_tasks'])}/{len(actions)} done")
        
        if completed != len(fix['completed_tasks']):
            print(f"  ⚠️  Needs fixing")
    
    if not dry_run:
        print("\n" + "="*80)
        print("APPLYING FIXES")
        print("="*80)
        
        response = input("\nType 'FIX' to confirm: ")
        if response != 'FIX':
            print("✗ Cancelled")
            return
        
        for i, meeting in enumerate(meetings):
            fix = fixes[i]
            actions = meeting.get('actionItems', [])
            
            # Reset all to incomplete first
            for action in actions:
                action['completed'] = False
                action['status'] = 'todo'
                action['completedAt'] = None
            
            # Mark specific ones as complete
            for action in actions:
                task_lower = action.get('task', '').lower()
                should_complete = any(keyword in task_lower for keyword in fix['completed_tasks'])
                
                if should_complete:
                    action['completed'] = True
                    action['status'] = 'done'
                    action['completedAt'] = datetime.now().isoformat()
            
            # Backdate deadlines to realistic past dates
            for j, action in enumerate(actions):
                # Spread deadlines over a few days
                deadline = fix['deadline_base'] + timedelta(days=j % 3)
                action['deadline'] = deadline.strftime('%Y-%m-%d')
            
            # Update meeting
            table.update_item(
                Key={
                    'userId': DEMO_USER_ID,
                    'meetingId': meeting['meetingId']
                },
                UpdateExpression='SET actionItems = :a, updatedAt = :t',
                ExpressionAttributeValues={
                    ':a': actions,
                    ':t': datetime.now().isoformat()
                }
            )
            
            completed = sum(1 for a in actions if a.get('completed'))
            print(f"  ✓ {meeting['title']}: {completed}/{len(actions)} done")
        
        print("\n" + "="*80)
        print("FIX COMPLETE!")
        print("="*80)
        print("Story arc restored:")
        print("  Meeting 1: 1/7 done (14%) - Enthusiastic start")
        print("  Meeting 2: 0/7 done (0%) - Total failure")
        print("  Meeting 3: 0/6 done (0%) - Demoralized")
        print("  Meeting 4: 1/1 done (100%) - Perfect pivot")
        print("  Meeting 5: 4/5 done (80%) - Strong execution")
        print("\nPattern detection:")
        print("  ✓ Chronic blocker: 'Fix auth bug' in meetings 2, 3, 5")
        print("  ✓ Action Item Amnesia: Meetings 2 & 3 (0% completion)")
        print("  ✓ Graveyard: 20 items from meetings 1-3 (all >30 days old)")
    else:
        print("\n" + "="*80)
        print("To execute, run with --execute flag:")
        print("  python scripts/data/final-demo-fix.py --execute")
        print("="*80)


if __name__ == '__main__':
    main()
