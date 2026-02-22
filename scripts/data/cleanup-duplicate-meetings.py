#!/usr/bin/env python3
"""
Cleanup Script: Remove Duplicate and Test Meetings
==================================================

This script removes unnecessary meetings from the database:
1. Original student marketplace meetings (already copied to demo user)
2. Test/junk meetings (fvs ddsv, gfgw4, 123)

SAFETY FEATURES:
- Dry-run mode by default (preview changes without executing)
- Detailed logging of all operations
- Confirmation prompts before deletion
- Preserves demo user meetings (CRITICAL)
- Preserves admin email configuration (CRITICAL)

Usage:
    python scripts/data/cleanup-duplicate-meetings.py          # Dry-run (preview only)
    python scripts/data/cleanup-duplicate-meetings.py --execute # Actually delete
"""

import boto3
import json
import sys
from datetime import datetime
from decimal import Decimal

# AWS Configuration
REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'

# CRITICAL: Demo user must be preserved
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
DEMO_USER_EMAIL = 'demo@meetingmind.com'

# Users with meetings to DELETE
USERS_TO_CLEANUP = [
    {
        'userId': '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c',
        'description': 'Original source of student marketplace meetings (already copied to demo)',
        'reason': 'Duplicates - these meetings were copied to demo user'
    },
    {
        'userId': '71038d7a-e061-70e5-cfe9-401bcf4ec693',
        'description': 'Test/junk meetings',
        'reason': 'Test data - meetings like "fvs ddsv", "gfgw4"'
    },
    {
        'userId': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134',
        'description': 'Test meetings from thehiddenif@gmail.com',
        'reason': 'Test data - meetings like "DFDFD", "D3D3", "cwdceswq"'
    }
]


class MeetingCleanup:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.dynamodb = boto3.resource('dynamodb', region_name=REGION)
        self.meetings_table = self.dynamodb.Table(MEETINGS_TABLE)
        self.deleted_count = 0
        self.preserved_count = 0
        
    def decimal_to_native(self, obj):
        """Convert DynamoDB Decimal types to native Python types"""
        if isinstance(obj, list):
            return [self.decimal_to_native(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.decimal_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return obj
    
    def get_user_meetings(self, user_id):
        """Fetch all meetings for a specific user"""
        try:
            response = self.meetings_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"❌ Error fetching meetings for user {user_id}: {e}")
            return []
    
    def delete_meeting(self, user_id, meeting_id):
        """Delete a single meeting"""
        try:
            if not self.dry_run:
                self.meetings_table.delete_item(
                    Key={
                        'userId': user_id,
                        'meetingId': meeting_id
                    }
                )
            self.deleted_count += 1
            return True
        except Exception as e:
            print(f"❌ Error deleting meeting {meeting_id}: {e}")
            return False
    
    def preview_cleanup(self):
        """Preview what will be deleted"""
        print("\n" + "=" * 80)
        print("🔍 CLEANUP PREVIEW - DRY RUN MODE")
        print("=" * 80)
        print(f"\n⚠️  This is a DRY RUN - no changes will be made to the database")
        print(f"   Run with --execute flag to actually delete meetings\n")
        
        total_to_delete = 0
        
        for user_info in USERS_TO_CLEANUP:
            user_id = user_info['userId']
            description = user_info['description']
            reason = user_info['reason']
            
            meetings = self.get_user_meetings(user_id)
            
            if not meetings:
                print(f"\n📭 User: {user_id[:20]}...")
                print(f"   Description: {description}")
                print(f"   Status: No meetings found (already clean)")
                continue
            
            print(f"\n🗑️  User: {user_id[:20]}...")
            print(f"   Description: {description}")
            print(f"   Reason: {reason}")
            print(f"   Meetings to delete: {len(meetings)}")
            print(f"\n   Meeting Details:")
            
            for i, meeting in enumerate(meetings, 1):
                title = meeting.get('title', 'N/A')
                grade = meeting.get('healthScore', 'N/A')
                date = meeting.get('createdAt', 'N/A')
                actions = len(meeting.get('actionItems', []))
                
                print(f"   {i}. {title}")
                print(f"      Grade: {grade}, Date: {date}, Actions: {actions}")
            
            total_to_delete += len(meetings)
        
        # Show demo user preservation
        print(f"\n" + "=" * 80)
        print("✅ PRESERVED DATA (WILL NOT BE TOUCHED)")
        print("=" * 80)
        
        demo_meetings = self.get_user_meetings(DEMO_USER_ID)
        print(f"\n🎯 Demo User: {DEMO_USER_EMAIL}")
        print(f"   User ID: {DEMO_USER_ID}")
        print(f"   Status: PROTECTED - will be preserved")
        print(f"   Meetings: {len(demo_meetings)}")
        
        if demo_meetings:
            print(f"\n   Demo Meetings:")
            for i, meeting in enumerate(demo_meetings, 1):
                title = meeting.get('title', 'N/A')
                grade = meeting.get('healthScore', 'N/A')
                print(f"   {i}. {title} (Grade: {grade})")
        
        self.preserved_count = len(demo_meetings)
        
        # Summary
        print(f"\n" + "=" * 80)
        print("📊 CLEANUP SUMMARY")
        print("=" * 80)
        print(f"\n   Meetings to DELETE: {total_to_delete}")
        print(f"   Meetings to PRESERVE: {self.preserved_count}")
        print(f"   Users affected: {len(USERS_TO_CLEANUP)}")
        
        return total_to_delete
    
    def execute_cleanup(self):
        """Actually delete the meetings"""
        print("\n" + "=" * 80)
        print("🚀 EXECUTING CLEANUP - LIVE MODE")
        print("=" * 80)
        print(f"\n⚠️  WARNING: This will permanently delete meetings from the database!")
        print(f"   Demo user ({DEMO_USER_EMAIL}) will be preserved.\n")
        
        # Safety check
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            print("\n❌ Cleanup cancelled - confirmation not received")
            return False
        
        print("\n🔄 Starting cleanup...\n")
        
        for user_info in USERS_TO_CLEANUP:
            user_id = user_info['userId']
            description = user_info['description']
            
            meetings = self.get_user_meetings(user_id)
            
            if not meetings:
                print(f"✓ User {user_id[:20]}... - No meetings to delete")
                continue
            
            print(f"\n🗑️  Processing user: {user_id[:20]}...")
            print(f"   Description: {description}")
            print(f"   Deleting {len(meetings)} meetings...")
            
            for meeting in meetings:
                meeting_id = meeting.get('meetingId')
                title = meeting.get('title', 'N/A')
                
                if self.delete_meeting(user_id, meeting_id):
                    print(f"   ✓ Deleted: {title}")
                else:
                    print(f"   ✗ Failed: {title}")
        
        # Verify demo user is intact
        print(f"\n" + "=" * 80)
        print("✅ VERIFICATION")
        print("=" * 80)
        
        demo_meetings = self.get_user_meetings(DEMO_USER_ID)
        print(f"\n🎯 Demo User: {DEMO_USER_EMAIL}")
        print(f"   Meetings preserved: {len(demo_meetings)}")
        
        if len(demo_meetings) == self.preserved_count:
            print(f"   Status: ✅ All demo meetings intact!")
        else:
            print(f"   Status: ⚠️  WARNING - meeting count changed!")
            print(f"   Expected: {self.preserved_count}, Found: {len(demo_meetings)}")
        
        # Final summary
        print(f"\n" + "=" * 80)
        print("📊 CLEANUP COMPLETE")
        print("=" * 80)
        print(f"\n   Meetings deleted: {self.deleted_count}")
        print(f"   Demo meetings preserved: {len(demo_meetings)}")
        print(f"   Status: ✅ Cleanup successful!\n")
        
        return True


def main():
    """Main execution"""
    # Check for execute flag
    dry_run = '--execute' not in sys.argv
    
    print("\n" + "=" * 80)
    print("🧹 MEETINGMIND DATABASE CLEANUP")
    print("=" * 80)
    print(f"\nTarget: {MEETINGS_TABLE} (Region: {REGION})")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will delete)'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize cleanup
    cleanup = MeetingCleanup(dry_run=dry_run)
    
    if dry_run:
        # Preview mode
        total = cleanup.preview_cleanup()
        
        print(f"\n" + "=" * 80)
        print("💡 NEXT STEPS")
        print("=" * 80)
        print(f"\nTo execute this cleanup, run:")
        print(f"   python scripts/data/cleanup-duplicate-meetings.py --execute")
        print(f"\nThis will delete {total} meetings while preserving demo user data.\n")
    else:
        # Execute mode
        cleanup.preview_cleanup()
        cleanup.execute_cleanup()


if __name__ == '__main__':
    main()
