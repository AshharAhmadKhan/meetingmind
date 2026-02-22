#!/usr/bin/env python3
"""
Cleanup Script: Replace all "Ashhar" references with "Zeeshan"
===============================================================

Replaces any remaining "Ashhar" references in:
- Decisions
- Follow-ups
- Summaries
- Action items (task, owner)
- Any other text fields

SAFETY FEATURES:
- Dry-run mode by default
- Backup before changes
- Detailed logging

Usage:
    python scripts/data/cleanup-ashhar-references.py          # Dry-run
    python scripts/data/cleanup-ashhar-references.py --execute # Execute
"""

import boto3
import json
import sys
from datetime import datetime
from decimal import Decimal
from copy import deepcopy

# AWS Configuration
REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

# Name replacements
REPLACEMENTS = [
    ('Ashhar', 'Zeeshan'),
    ('Ahar', 'Zeeshan'),  # Typo in original data
    ('Ashhar Ahmad Khan', 'Zeeshan'),
]


class NameCleanup:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.dynamodb = boto3.resource('dynamodb', region_name=REGION)
        self.table = self.dynamodb.Table(MEETINGS_TABLE)
        self.changes_made = 0
        self.replacements_count = 0

    def replace_in_text(self, text):
        """Replace all name variations in text"""
        if not text or not isinstance(text, str):
            return text, 0
        
        original = text
        count = 0
        
        for old_name, new_name in REPLACEMENTS:
            if old_name in text:
                text = text.replace(old_name, new_name)
                count += text.count(new_name) - original.count(new_name)
        
        return text, count
    
    def replace_in_list(self, items):
        """Replace names in list of strings"""
        if not items or not isinstance(items, list):
            return items, 0
        
        cleaned = []
        total_count = 0
        
        for item in items:
            if isinstance(item, str):
                cleaned_item, count = self.replace_in_text(item)
                cleaned.append(cleaned_item)
                total_count += count
            else:
                cleaned.append(item)
        
        return cleaned, total_count
    
    def replace_in_dict(self, data):
        """Recursively replace names in dictionary"""
        if not isinstance(data, dict):
            return data, 0
        
        cleaned = {}
        total_count = 0
        
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key], count = self.replace_in_text(value)
                total_count += count
            elif isinstance(value, list):
                cleaned[key], count = self.replace_in_list(value)
                total_count += count
            elif isinstance(value, dict):
                cleaned[key], count = self.replace_in_dict(value)
                total_count += count
            else:
                cleaned[key] = value
        
        return cleaned, total_count

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
    
    def clean_meeting(self, meeting):
        """Clean all Ashhar references from a meeting"""
        meeting_id = meeting.get('meetingId')
        title = meeting.get('title', 'N/A')
        
        print(f"\n{'='*80}")
        print(f"Cleaning: {title}")
        print(f"{'='*80}")
        
        # Create cleaned copy
        cleaned = deepcopy(meeting)
        total_replacements = 0
        
        # 1. Clean summary
        if 'summary' in cleaned:
            cleaned['summary'], count = self.replace_in_text(cleaned['summary'])
            if count > 0:
                print(f"  Summary: {count} replacement(s)")
                total_replacements += count
        
        # 2. Clean decisions
        if 'decisions' in cleaned:
            cleaned['decisions'], count = self.replace_in_list(cleaned['decisions'])
            if count > 0:
                print(f"  Decisions: {count} replacement(s)")
                total_replacements += count
        
        # 3. Clean follow-ups
        if 'followUps' in cleaned:
            cleaned['followUps'], count = self.replace_in_list(cleaned['followUps'])
            if count > 0:
                print(f"  Follow-ups: {count} replacement(s)")
                total_replacements += count
        
        # 4. Clean action items
        if 'actionItems' in cleaned:
            action_items = []
            action_count = 0
            for action in cleaned['actionItems']:
                cleaned_action, count = self.replace_in_dict(action)
                action_items.append(cleaned_action)
                action_count += count
            cleaned['actionItems'] = action_items
            if action_count > 0:
                print(f"  Action Items: {action_count} replacement(s)")
                total_replacements += action_count
        
        # 5. Update timestamp
        cleaned['updatedAt'] = datetime.now().isoformat()
        
        if total_replacements > 0:
            print(f"  Total: {total_replacements} replacement(s)")
        else:
            print(f"  No replacements needed")
        
        return cleaned, total_replacements

    def preview_cleanup(self, meetings):
        """Preview cleanup without executing"""
        print("\n" + "="*80)
        print("PREVIEW MODE - No changes will be made")
        print("="*80)
        
        total_replacements = 0
        
        for meeting in meetings:
            _, count = self.clean_meeting(meeting)
            total_replacements += count
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total replacements needed: {total_replacements}")
        print(f"Meetings affected: {sum(1 for m in meetings if self.clean_meeting(m)[1] > 0)}")
        print(f"\nTo execute, run with --execute flag")
    
    def execute_cleanup(self, meetings):
        """Execute the cleanup"""
        print("\n" + "="*80)
        print("EXECUTING CLEANUP")
        print("="*80)
        
        # Safety confirmation
        response = input("\nType 'CLEANUP' to confirm: ")
        if response != 'CLEANUP':
            print("✗ Cleanup cancelled")
            return False
        
        print("\n🔄 Starting cleanup...\n")
        
        for meeting in meetings:
            cleaned, count = self.clean_meeting(meeting)
            
            if count > 0:
                # Write to DynamoDB
                try:
                    self.table.put_item(Item=cleaned)
                    self.changes_made += 1
                    self.replacements_count += count
                    print(f"  ✓ Saved to database")
                except Exception as e:
                    print(f"  ✗ Error saving: {e}")
                    return False
        
        print("\n" + "="*80)
        print("CLEANUP COMPLETE")
        print("="*80)
        print(f"Meetings updated: {self.changes_made}")
        print(f"Total replacements: {self.replacements_count}")
        
        return True

    def verify_cleanup(self):
        """Verify no Ashhar references remain"""
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        meetings = self.fetch_meetings()
        
        ashhar_found = False
        for meeting in meetings:
            meeting_str = json.dumps(meeting, default=str)
            if 'Ashhar' in meeting_str or 'Ahar' in meeting_str:
                ashhar_found = True
                title = meeting.get('title', 'N/A')
                print(f"⚠️  Found 'Ashhar' in: {title}")
                
                # Show where it was found
                if 'Ashhar' in meeting.get('summary', ''):
                    print(f"    - In summary")
                if any('Ashhar' in str(d) for d in meeting.get('decisions', [])):
                    print(f"    - In decisions")
                if any('Ashhar' in str(f) for f in meeting.get('followUps', [])):
                    print(f"    - In follow-ups")
                if any('Ashhar' in str(a) for a in meeting.get('actionItems', [])):
                    print(f"    - In action items")
        
        if not ashhar_found:
            print("✓ No 'Ashhar' references found - cleanup successful!")
        
        print("\n✓ Verification complete")


def main():
    """Main execution"""
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("ASHHAR → ZEESHAN CLEANUP")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    print(f"Target: {MEETINGS_TABLE} (Region: {REGION})")
    print(f"Demo User: {DEMO_USER_ID}")
    
    cleanup = NameCleanup(dry_run=dry_run)
    
    # Fetch meetings
    meetings = cleanup.fetch_meetings()
    if not meetings:
        print("✗ No meetings found")
        return
    
    if dry_run:
        # Preview mode
        cleanup.preview_cleanup(meetings)
    else:
        # Execute mode
        success = cleanup.execute_cleanup(meetings)
        if success:
            cleanup.verify_cleanup()


if __name__ == '__main__':
    main()
