#!/usr/bin/env python3
"""
Complete Demo Transformation Script
====================================

Creates the perfect demo story:
- Meeting 1 (Nov 20): Enthusiastic start, 1/7 done (14%)
- Meeting 2 (Dec 5): Total failure, 0/7 done (0%) + chronic blocker #1
- Meeting 3 (Dec 20): Demoralized, 0/6 done (0%) + chronic blocker #2
- Meeting 4 (Feb 2): Breakthrough pivot, 1/1 done (100%)
- Meeting 5 (Feb 11): Strong execution, 4/5 done (80%) + chronic blocker resolved

Story: Team failed alone (F→F→F), discovered MeetingMind, then succeeded (A→B)

SAFETY: Dry-run by default, creates backup
"""

import boto3
import json
import sys
from datetime import datetime
from decimal import Decimal
from copy import deepcopy

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'


class CompleteDemoTransformer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.dynamodb = boto3.resource('dynamodb', region_name=REGION)
        self.table = self.dynamodb.Table(MEETINGS_TABLE)
        self.fixes_applied = 0
        self.backup_file = f"demo_complete_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def fetch_meeting(self, meeting_id):
        """Fetch a specific meeting"""
        try:
            response = self.table.get_item(
                Key={'userId': DEMO_USER_ID, 'meetingId': meeting_id}
            )
            return response.get('Item')
        except Exception as e:
            print(f"✗ Error fetching meeting: {e}")
            return None
    
    def decimal_to_native(self, obj):
        """Convert Decimal to native Python types"""
        if isinstance(obj, list):
            return [self.decimal_to_native(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.decimal_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        return obj
    
    def create_backup(self, meetings):
        """Create backup of all meetings"""
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'meetings': [self.decimal_to_native(m) for m in meetings]
        }
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"  ✓ Backup created: {self.backup_file}")

    def transform_meeting_1_kickoff(self, meeting):
        """
        Meeting 1: Kickoff Meeting (Nov 20, 2025)
        Story: Enthusiastic start, only company registration done
        Result: 1/7 completed (14%)
        """
        print("\n" + "="*80)
        print("TRANSFORM 1: Kickoff Meeting - Enthusiastic but overcommitted")
        print("="*80)
        
        fixed = deepcopy(meeting)
        
        # Update action items - mark all as incomplete first
        actions = fixed.get('actionItems', [])
        for action in actions:
            action['completed'] = False
            action['status'] = 'todo'
        
        # Find and mark "Register the company" as completed
        for action in actions:
            if 'register' in action.get('task', '').lower() and 'company' in action.get('task', '').lower():
                action['completed'] = True
                action['status'] = 'done'
                print(f"  ✓ Marked as DONE: {action['task']}")
                break
        
        fixed['actionItems'] = actions
        fixed['updatedAt'] = datetime.now().isoformat()
        
        completed = sum(1 for a in actions if a.get('completed'))
        print(f"  Result: {completed}/7 completed (14%)")
        print(f"  Story: Enthusiastic kickoff, but Zeeshan took on too many tasks")
        
        return fixed

    def transform_meeting_2_crisis(self, meeting):
        """
        Meeting 2: Mid-Project Crisis (Dec 5, 2025)
        Story: Total failure, chronic blocker appears
        Result: 0/7 completed (0%)
        """
        print("\n" + "="*80)
        print("TRANSFORM 2: Mid-Project Crisis - Total failure + chronic blocker #1")
        print("="*80)
        
        fixed = deepcopy(meeting)
        
        # Create new action items with chronic blocker
        fixed['actionItems'] = [
            {
                'task': 'Fix auth bug preventing user login',
                'owner': 'Ayush',
                'deadline': '2025-12-10',
                'completed': False,
                'status': 'todo',
                'priority': 'high'
            },
            {
                'task': 'Complete landing page with hero section and screenshots',
                'owner': 'Alishba',
                'deadline': '2025-12-08',
                'completed': False,
                'status': 'todo',
                'priority': 'high'
            },
            {
                'task': 'Finish API endpoints for job applications',
                'owner': 'Ayush',
                'deadline': '2025-12-09',
                'completed': False,
                'status': 'todo',
                'priority': 'high'
            },
            {
                'task': 'Email 20 colleges for outreach',
                'owner': 'Zeeshan',
                'deadline': '2025-12-12',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'task': 'Write pricing page copy',
                'owner': 'Zeeshan',
                'deadline': '2025-12-11',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'task': 'Design pricing page',
                'owner': 'Alishba',
                'deadline': '2025-12-12',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'task': 'Create beta sign-up form',
                'owner': 'Alishba',
                'deadline': '2025-12-10',
                'completed': False,
                'status': 'todo',
                'priority': 'low'
            }
        ]
        
        # Update summary
        fixed['summary'] = ("The team is struggling to make progress. Zero tasks from the kickoff "
                           "were completed. A critical auth bug is blocking user testing. The landing "
                           "page, API endpoints, and outreach efforts are all behind schedule. "
                           "Team morale is low.")
        
        # Update decisions
        fixed['decisions'] = [
            "Focus on fixing the auth bug first",
            "Postpone beta testing until auth is working"
        ]
        
        # Update follow-ups
        fixed['followUps'] = [
            "Check if auth bug is resolved by Friday",
            "Reassess timeline if no progress by next week"
        ]
        
        fixed['updatedAt'] = datetime.now().isoformat()
        
        print(f"  ✓ Added chronic blocker: 'Fix auth bug' (appears 1st time)")
        print(f"  ✓ Updated summary to reflect crisis")
        print(f"  Result: 0/7 completed (0%)")
        print(f"  Story: Complete failure, auth bug blocking everything")
        
        return fixed

    def transform_meeting_3_last_attempt(self, meeting):
        """
        Meeting 3: Last Attempt Before Pivot (Dec 20, 2025)
        Story: Demoralized, chronic blocker still unresolved
        Result: 0/6 completed (0%)
        """
        print("\n" + "="*80)
        print("TRANSFORM 3: Last Attempt - Demoralized + chronic blocker #2")
        print("="*80)
        
        fixed = deepcopy(meeting)
        
        # Create action items with chronic blocker appearing again
        fixed['actionItems'] = [
            {
                'task': 'Fix auth bug preventing user login',
                'owner': 'Ayush',
                'deadline': '2025-12-23',
                'completed': False,
                'status': 'todo',
                'priority': 'critical'
            },
            {
                'task': 'Redesign profile page',
                'owner': 'Alishba',
                'deadline': '2025-12-25',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'task': 'Finish job browse page',
                'owner': 'Alishba',
                'deadline': '2025-12-26',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'task': 'Set up load testing',
                'owner': 'Ayush',
                'deadline': '2025-12-27',
                'completed': False,
                'status': 'todo',
                'priority': 'low'
            },
            {
                'task': 'Recruit 5 beta testers',
                'owner': 'Ayush',
                'deadline': '2025-12-28',
                'completed': False,
                'status': 'todo',
                'priority': 'low'
            },
            {
                'task': 'Write landing page copy',
                'owner': 'Zeeshan',
                'deadline': '2025-12-27',
                'completed': False,
                'status': 'todo',
                'priority': 'medium'
            }
        ]
        
        # Update summary
        fixed['summary'] = ("The team is considering giving up. The auth bug remains unresolved "
                           "after two weeks. No tasks have been completed. The team discussed "
                           "whether to pivot their approach, change target users, or abandon "
                           "the project entirely. They decided to have a strategic discussion "
                           "in the group chat before the next meeting.")
        
        # Update decisions
        fixed['decisions'] = [
            "Discuss pivot options in group chat",
            "Reconvene only if there's a clear path forward"
        ]
        
        # Update follow-ups
        fixed['followUps'] = [
            "Group chat discussion on target user and core features",
            "Decide whether to continue or pivot"
        ]
        
        fixed['updatedAt'] = datetime.now().isoformat()
        
        print(f"  ✓ Added chronic blocker: 'Fix auth bug' (appears 2nd time)")
        print(f"  ✓ Updated summary to reflect demoralization")
        print(f"  Result: 0/6 completed (0%)")
        print(f"  Story: Team almost giving up, auth bug still unresolved")
        
        return fixed

    def transform_meeting_4_pivot(self, meeting):
        """
        Meeting 4: Should We Pivot (Feb 2, 2026)
        Story: BREAKTHROUGH! Team used MeetingMind, had strategic pivot
        Result: 1/1 completed (100%)
        """
        print("\n" + "="*80)
        print("TRANSFORM 4: Should We Pivot - BREAKTHROUGH after MeetingMind")
        print("="*80)
        
        fixed = deepcopy(meeting)
        
        # Single focused action item
        fixed['actionItems'] = [
            {
                'task': 'Discuss target user, core feature, and business model in group chat',
                'owner': 'Zeeshan',
                'deadline': '2026-02-05',
                'completed': True,
                'status': 'done',
                'priority': 'critical'
            }
        ]
        
        # Update summary
        fixed['summary'] = ("The team discovered MeetingMind and uploaded their previous failed meetings. "
                           "Seeing the graveyard of 20 abandoned tasks and the chronic auth bug pattern "
                           "was eye-opening. They had a focused strategic discussion about pivoting: "
                           "should they target designers or developers? Build mobile or responsive web? "
                           "What pricing model? They decided to focus on developers first, build a "
                           "responsive website, and use freemium pricing. This clarity was transformative.")
        
        # Update decisions
        fixed['decisions'] = [
            "Focus on developers first (not designers)",
            "Build responsive website (not mobile app)",
            "Use freemium pricing model",
            "Fix the auth bug before any new features"
        ]
        
        # Update follow-ups
        fixed['followUps'] = [
            "Start fresh sprint with new focus",
            "Prioritize auth bug fix above everything"
        ]
        
        fixed['updatedAt'] = datetime.now().isoformat()
        
        print(f"  ✓ Reduced to 1 strategic action item (completed)")
        print(f"  ✓ Updated summary to show MeetingMind impact")
        print(f"  Result: 1/1 completed (100%)")
        print(f"  Story: Perfect execution after discovering MeetingMind")
        
        return fixed

    def transform_meeting_5_weekly(self, meeting):
        """
        Meeting 5: Weekly Check-In (Feb 11, 2026)
        Story: Strong execution, chronic blocker RESOLVED
        Result: 4/5 completed (80%)
        """
        print("\n" + "="*80)
        print("TRANSFORM 5: Weekly Check-In - Strong execution + chronic blocker RESOLVED")
        print("="*80)
        
        fixed = deepcopy(meeting)
        
        # Action items with auth bug finally resolved
        fixed['actionItems'] = [
            {
                'task': 'Fix auth bug preventing user login',
                'owner': 'Ayush',
                'deadline': '2026-02-09',
                'completed': True,
                'status': 'done',
                'priority': 'critical'
            },
            {
                'task': 'Finish job browse page',
                'owner': 'Alishba',
                'deadline': '2026-02-10',
                'completed': True,
                'status': 'done',
                'priority': 'high'
            },
            {
                'task': 'Check email notifications in production',
                'owner': 'Ayush',
                'deadline': '2026-02-11',
                'completed': True,
                'status': 'done',
                'priority': 'medium'
            },
            {
                'task': 'Set up load testing',
                'owner': 'Ayush',
                'deadline': '2026-02-13',
                'completed': True,
                'status': 'done',
                'priority': 'medium'
            },
            {
                'task': 'Redesign profile page',
                'owner': 'Alishba',
                'deadline': '2026-02-12',
                'completed': False,
                'status': 'todo',
                'priority': 'low'
            }
        ]
        
        # Update summary
        fixed['summary'] = ("Strong progress this week! Ayush FINALLY fixed the auth bug that had been "
                           "blocking us for months. The job browse page is complete, email notifications "
                           "are working, and load testing is set up. Only the profile page redesign "
                           "remains incomplete, but it's low priority. Team morale is high. The focused "
                           "approach from our pivot meeting is paying off.")
        
        # Update decisions
        fixed['decisions'] = [
            "Profile page redesign can wait until after demo",
            "Focus remaining time on demo preparation"
        ]
        
        # Update follow-ups
        fixed['followUps'] = [
            "Prepare demo script and walkthrough",
            "Recruit beta testers for post-demo feedback"
        ]
        
        fixed['updatedAt'] = datetime.now().isoformat()
        
        print(f"  ✓ Added chronic blocker: 'Fix auth bug' (RESOLVED - 3rd appearance)")
        print(f"  ✓ Updated summary to celebrate breakthrough")
        print(f"  Result: 4/5 completed (80%)")
        print(f"  Story: Strong execution, chronic blocker finally resolved")
        
        return fixed

    def apply_transformations(self):
        """Apply all transformations"""
        print("\n" + "="*80)
        print("COMPLETE DEMO TRANSFORMATION")
        print("="*80)
        print(f"Mode: {'DRY RUN (preview)' if self.dry_run else 'LIVE (will modify)'}")
        
        # Meeting IDs (in chronological order)
        meeting_ids = {
            'meeting_1': 'ae4008bf-80fe-4fce-b011-1a19ea6c2b22',  # Kickoff
            'meeting_2': '4f08334d-61fe-40ae-9572-fb577a2fd9ef',  # Mid-Project Crisis
            'meeting_3': '0adac9cd-4449-4c0a-9790-fa55ceb42f85',  # Last Attempt
            'meeting_4': 'cb1a4cdb-e9f2-4bc9-b2fb-02b170f248bd',  # Should We Pivot
            'meeting_5': 'fdd5a72f-e180-451b-ae47-36a6f93a3234'   # Weekly Check-In
        }
        
        # Fetch all meetings
        print("\n" + "="*80)
        print("FETCHING MEETINGS")
        print("="*80)
        
        meetings = {}
        for key, meeting_id in meeting_ids.items():
            meeting = self.fetch_meeting(meeting_id)
            if not meeting:
                print(f"✗ Failed to fetch {key}")
                return False
            meetings[key] = meeting
            print(f"  ✓ Fetched {key}: {meeting.get('title', 'N/A')}")
        
        # Create backup
        print("\n" + "="*80)
        print("CREATING BACKUP")
        print("="*80)
        self.create_backup(list(meetings.values()))
        
        # Apply transformations
        transformed = {
            'meeting_1': self.transform_meeting_1_kickoff(meetings['meeting_1']),
            'meeting_2': self.transform_meeting_2_crisis(meetings['meeting_2']),
            'meeting_3': self.transform_meeting_3_last_attempt(meetings['meeting_3']),
            'meeting_4': self.transform_meeting_4_pivot(meetings['meeting_4']),
            'meeting_5': self.transform_meeting_5_weekly(meetings['meeting_5'])
        }
        
        if not self.dry_run:
            # Save to database
            print("\n" + "="*80)
            print("SAVING TO DATABASE")
            print("="*80)
            
            try:
                for key, meeting in transformed.items():
                    self.table.put_item(Item=meeting)
                    print(f"  ✓ Saved {key}: {meeting.get('title', 'N/A')}")
                    self.fixes_applied += 1
                
            except Exception as e:
                print(f"  ✗ Error saving: {e}")
                return False
        
        # Show final story
        print("\n" + "="*80)
        print("FINAL STORY ARC")
        print("="*80)
        print("Meeting 1 (Nov 20): Kickoff - Grade 55 (F) - 1/7 done (14%)")
        print("  → Enthusiastic start, only company registration done")
        print("")
        print("Meeting 2 (Dec 5): Mid-Project Crisis - Grade 50 (F) - 0/7 done (0%)")
        print("  → Total failure, auth bug appears (chronic blocker #1)")
        print("")
        print("Meeting 3 (Dec 20): Last Attempt - Grade 48 (F) - 0/6 done (0%)")
        print("  → Demoralized, auth bug still unresolved (chronic blocker #2)")
        print("")
        print("[JANUARY: Team discovers MeetingMind, uploads failed meetings]")
        print("")
        print("Meeting 4 (Feb 2): Should We Pivot - Grade 95 (A) - 1/1 done (100%)")
        print("  → BREAKTHROUGH! Strategic pivot after seeing graveyard")
        print("")
        print("Meeting 5 (Feb 11): Weekly Check-In - Grade 85 (B) - 4/5 done (80%)")
        print("  → Strong execution, auth bug RESOLVED (chronic blocker #3)")
        print("")
        print("="*80)
        print("FEATURES SHOWCASED:")
        print("="*80)
        print("✓ Graveyard: 20 abandoned tasks from meetings 1-3")
        print("✓ Chronic Blocker: 'Fix auth bug' appears 3 times, resolved in meeting 5")
        print("✓ Grade Progression: F → F → F → [MeetingMind] → A → B")
        print("✓ Completion Tracking: 14% → 0% → 0% → 100% → 80%")
        print("✓ Pattern Detection: Action Item Amnesia, Chronic Blocker")
        print("✓ Meeting Debt: $4,800 → $720 (83% reduction)")
        print("="*80)
        
        return True


def main():
    """Main execution"""
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "="*80)
    print("COMPLETE DEMO TRANSFORMATION")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview)' if dry_run else 'LIVE (will modify)'}")
    print("")
    print("This script will:")
    print("  1. Fix Meeting 1: Correct completion (1/7 = 14%)")
    print("  2. Fix Meeting 2: Add chronic blocker #1 (0/7 = 0%)")
    print("  3. Fix Meeting 3: Expand + chronic blocker #2 (0/6 = 0%)")
    print("  4. Fix Meeting 4: Perfect pivot meeting (1/1 = 100%)")
    print("  5. Fix Meeting 5: Resolve chronic blocker (4/5 = 80%)")
    print("")
    
    transformer = CompleteDemoTransformer(dry_run=dry_run)
    
    if dry_run:
        transformer.apply_transformations()
        print("\n" + "="*80)
        print("To execute, run with --execute flag:")
        print("  python scripts/data/complete-demo-transformation.py --execute")
        print("="*80)
    else:
        print("WARNING: This will modify the database!")
        response = input("\nType 'TRANSFORM' to confirm: ")
        if response != 'TRANSFORM':
            print("✗ Cancelled")
            return
        
        success = transformer.apply_transformations()
        if success:
            print("\n" + "="*80)
            print("TRANSFORMATION COMPLETE!")
            print("="*80)
            print(f"Meetings transformed: {transformer.fixes_applied}")
            print(f"Backup saved: {transformer.backup_file}")
            print("")
            print("Next steps:")
            print("  1. Run: python scripts/data/show-demo-details.py")
            print("  2. Verify the story arc")
            print("  3. Test demo account in browser")


if __name__ == '__main__':
    main()
