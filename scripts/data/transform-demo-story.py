#!/usr/bin/env python3
"""
Demo Story Transformation Script
=================================

Transforms demo meetings to create compelling F→F→F→A→B→B narrative.

SAFETY FEATURES:
- Dry-run mode by default (preview changes)
- Backup creation before any changes
- Detailed logging of all operations
- Preserves meeting IDs and structure
- Validates data integrity after changes

Usage:
    python scripts/data/transform-demo-story.py          # Dry-run
    python scripts/data/transform-demo-story.py --execute # Actually transform
"""

import boto3
import json
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from copy import deepcopy

# AWS Configuration
REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

# Transformation configuration
TRANSFORMATIONS = {
    'ae4008bf-80fe-4fce-b011-1a19ea6c2b22': {  # Kickoff Meeting
        'new_title': 'Kickoff Meeting',
        'new_date': '2025-11-20T10:00:00.000000+00:00',
        'new_grade': 55,
        'completion_target': 1,  # 1 out of 7 done (14%)
        'story': 'Enthusiastic kickoff, but Zeeshan overcommitted (5 of 7 tasks)'
    },
    '4f08334d-61fe-40ae-9572-fb577a2fd9ef': {  # Last Week → Mid-Project Crisis
        'new_title': 'Mid-Project Crisis',
        'new_date': '2025-12-05T14:00:00.000000+00:00',
        'new_grade': 50,
        'completion_target': 0,  # 0 out of 7 done (0%)
        'story': 'Total failure. Auth bug appears for first time (chronic blocker #1)'
    },
    '0adac9cd-4449-4c0a-9790-fa55ceb42f85': {  # Should We Pivot → Last Attempt
        'new_title': 'Last Attempt Before Pivot',
        'new_date': '2025-12-20T16:00:00.000000+00:00',
        'new_grade': 48,
        'completion_target': 0,  # 0 out of 6 done (0%)
        'story': 'Demoralized. Auth bug still unresolved (chronic blocker #2)'
    },
    'cb1a4cdb-e9f2-4bc9-b2fb-02b170f248bd': {  # Weekly Check-In → Should We Pivot
        'new_title': 'Should We Pivot',
        'new_date': '2026-02-02T11:00:00.000000+00:00',
        'new_grade': 95,
        'completion_target': 1,  # 1 out of 1 done (100%)
        'story': 'BREAKTHROUGH! Strategic pivot after seeing graveyard in MeetingMind'
    },
    'fdd5a72f-e180-451b-ae47-36a6f93a3234': {  # Demo Prep → Weekly Check-In
        'new_title': 'Weekly Check-In',
        'new_date': '2026-02-11T10:00:00.000000+00:00',
        'new_grade': 85,
        'completion_target': 4,  # 4 out of 5 done (80%)
        'story': 'Strong execution. Auth bug FINALLY fixed (chronic blocker #3 resolved)'
    }
}

# Note: We'll create a 6th meeting "Demo Prep Sync" separately

class DemoTransformer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.dynamodb = boto3.resource('dynamodb', region_name=REGION)
        self.table = self.dynamodb.Table(MEETINGS_TABLE)
        self.backup = {}
        self.changes_made = 0
        
    def decimal_to_native(self, obj):
        """Convert DynamoDB Decimal types to native Python types"""
        if isinstance(obj, list):
            return [self.decimal_to_native(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.decimal_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        return obj
    
    def native_to_decimal(self, obj):
        """Convert native Python types to DynamoDB Decimal"""
        if isinstance(obj, list):
            return [self.native_to_decimal(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.native_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))
        return obj

    def fetch_meetings(self):
        """Fetch all demo user meetings"""
        try:
            response = self.table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': DEMO_USER_ID}
            )
            meetings = response.get('Items', [])
            print(f"✓ Fetched {len(meetings)} meetings")
            return meetings
        except Exception as e:
            print(f"✗ Error fetching meetings: {e}")
            return []
    
    def create_backup(self, meetings):
        """Create backup of current state"""
        for meeting in meetings:
            meeting_id = meeting.get('meetingId')
            self.backup[meeting_id] = deepcopy(meeting)
        
        # Save to file
        backup_file = f'demo_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_file, 'w') as f:
            json.dump(self.decimal_to_native(self.backup), f, indent=2)
        
        print(f"✓ Backup created: {backup_file}")
        return backup_file

    def replace_name(self, text, old_name='Ashhar', new_name='Zeeshan'):
        """Replace name in text, handling variations"""
        if not text or not isinstance(text, str):
            return text
        
        # Replace exact matches and common variations
        replacements = [
            (old_name, new_name),
            (old_name.lower(), new_name),
            ('Ahar', new_name),  # Typo in original data
            ('Ashhar Ahmad Khan', new_name),  # Full name
        ]
        
        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        
        return result
    
    def calculate_days_old(self, created_date):
        """Calculate days since creation"""
        try:
            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            return (now - created).days
        except:
            return 0

    def transform_meeting(self, meeting, config):
        """Transform a single meeting according to config"""
        meeting_id = meeting.get('meetingId')
        old_title = meeting.get('title')
        
        print(f"\n{'='*80}")
        print(f"Transforming: {old_title} → {config['new_title']}")
        print(f"{'='*80}")
        
        # Create transformed copy
        transformed = deepcopy(meeting)
        
        # 1. Update basic fields
        transformed['title'] = config['new_title']
        transformed['createdAt'] = config['new_date']
        transformed['healthScore'] = Decimal(str(config['new_grade']))
        transformed['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        print(f"  Date: {meeting.get('createdAt')[:10]} → {config['new_date'][:10]}")
        print(f"  Grade: {meeting.get('healthScore')} → {config['new_grade']}")
        
        # 2. Update summary (replace Ashhar with Zeeshan)
        if 'summary' in transformed:
            transformed['summary'] = self.replace_name(transformed['summary'])
        
        # 3. Transform action items
        action_items = transformed.get('actionItems', [])
        target_completed = config['completion_target']
        
        print(f"  Actions: {len(action_items)} total, target {target_completed} completed")
        
        completed_count = 0
        for i, action in enumerate(action_items):
            # Replace Ashhar with Zeeshan in owner and task
            if 'owner' in action:
                action['owner'] = self.replace_name(action['owner'])
            if 'task' in action:
                action['task'] = self.replace_name(action['task'])
            
            # Set completion status
            if completed_count < target_completed:
                action['completed'] = True
                action['status'] = 'done'
                completed_count += 1
            else:
                action['completed'] = False
                action['status'] = 'todo'
            
            # Calculate days old for graveyard
            days_old = self.calculate_days_old(config['new_date'])
            if days_old > 30 and not action['completed']:
                action['daysOld'] = days_old
        
        transformed['actionItems'] = action_items
        
        return transformed

    def preview_changes(self, meetings):
        """Preview all changes without executing"""
        print("\n" + "="*80)
        print("PREVIEW MODE - No changes will be made")
        print("="*80)
        
        for meeting in meetings:
            meeting_id = meeting.get('meetingId')
            
            if meeting_id in TRANSFORMATIONS:
                config = TRANSFORMATIONS[meeting_id]
                transformed = self.transform_meeting(meeting, config)
                
                # Show completion rate
                actions = transformed.get('actionItems', [])
                completed = sum(1 for a in actions if a.get('completed'))
                total = len(actions)
                rate = (completed / total * 100) if total > 0 else 0
                
                print(f"  Completion: {completed}/{total} ({rate:.0f}%)")
                print(f"  Story: {config['story']}")
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Meetings to transform: {len(TRANSFORMATIONS)}")
        print(f"Name changes: Ashhar → Zeeshan (all occurrences)")
        print(f"\nTo execute, run with --execute flag")
    
    def execute_transformation(self, meetings):
        """Execute the transformation"""
        print("\n" + "="*80)
        print("EXECUTING TRANSFORMATION")
        print("="*80)
        
        # Safety confirmation
        response = input("\nType 'TRANSFORM' to confirm: ")
        if response != 'TRANSFORM':
            print("✗ Transformation cancelled")
            return False
        
        print("\n🔄 Starting transformation...\n")
        
        for meeting in meetings:
            meeting_id = meeting.get('meetingId')
            
            if meeting_id in TRANSFORMATIONS:
                config = TRANSFORMATIONS[meeting_id]
                transformed = self.transform_meeting(meeting, config)
                
                # Write to DynamoDB
                try:
                    self.table.put_item(Item=transformed)
                    self.changes_made += 1
                    print(f"  ✓ Saved to database")
                except Exception as e:
                    print(f"  ✗ Error saving: {e}")
                    return False
        
        print("\n" + "="*80)
        print("TRANSFORMATION COMPLETE")
        print("="*80)
        print(f"Meetings transformed: {self.changes_made}")
        print(f"Backup available for rollback if needed")
        
        return True

    def verify_transformation(self):
        """Verify the transformation was successful"""
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        meetings = self.fetch_meetings()
        
        # Check meeting count
        if len(meetings) != 5:
            print(f"⚠️  Warning: Expected 5 meetings, found {len(meetings)}")
        
        # Check grades
        grades = [m.get('healthScore') for m in meetings]
        print(f"\nGrades: {grades}")
        
        # Check for Ashhar (should be replaced)
        ashhar_found = False
        for meeting in meetings:
            meeting_str = json.dumps(self.decimal_to_native(meeting))
            if 'Ashhar' in meeting_str or 'Ahar' in meeting_str:
                ashhar_found = True
                print(f"⚠️  Found 'Ashhar' in meeting: {meeting.get('title')}")
        
        if not ashhar_found:
            print("✓ All 'Ashhar' references replaced with 'Zeeshan'")
        
        # Check dates
        dates = sorted([m.get('createdAt')[:10] for m in meetings])
        print(f"\nDate range: {dates[0]} to {dates[-1]}")
        
        print("\n✓ Verification complete")


def main():
    """Main execution"""
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("DEMO STORY TRANSFORMATION")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    print(f"Target: {MEETINGS_TABLE} (Region: {REGION})")
    print(f"Demo User: {DEMO_USER_ID}")
    
    transformer = DemoTransformer(dry_run=dry_run)
    
    # Fetch meetings
    meetings = transformer.fetch_meetings()
    if not meetings:
        print("✗ No meetings found")
        return
    
    # Create backup
    backup_file = transformer.create_backup(meetings)
    
    if dry_run:
        # Preview mode
        transformer.preview_changes(meetings)
    else:
        # Execute mode
        success = transformer.execute_transformation(meetings)
        if success:
            transformer.verify_transformation()


if __name__ == '__main__':
    main()
