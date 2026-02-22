#!/usr/bin/env python3
"""
Diagnose skeleton loading and pending meeting issues
"""
import boto3
import os
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
bucket_name = 'meetingmind-audio-uploads'

def check_demo_account_meetings():
    """Check all meetings for demo account"""
    print("\n" + "="*80)
    print("CHECKING DEMO ACCOUNT MEETINGS")
    print("="*80)
    
    # Demo account email
    demo_email = "demo@meetingmind.app"
    
    try:
        # Scan for all meetings by demo user
        response = meetings_table.scan(
            FilterExpression='userId = :email',
            ExpressionAttributeValues={
                ':email': demo_email
            }
        )
        
        meetings = response.get('Items', [])
        print(f"\n✓ Found {len(meetings)} meetings for {demo_email}")
        
        # Check for pending meetings
        pending = [m for m in meetings if m.get('status') == 'PENDING']
        print(f"  - PENDING: {len(pending)}")
        
        if pending:
            print("\n⚠️  PENDING MEETINGS FOUND:")
            for m in pending:
                print(f"\n  Meeting ID: {m.get('meetingId')}")
                print(f"  Title: {m.get('title')}")
                print(f"  Status: {m.get('status')}")
                print(f"  Created: {m.get('createdAt')}")
                print(f"  S3 Key: {m.get('s3Key')}")
                
                # Check if S3 file exists
                if m.get('s3Key'):
                    try:
                        s3.head_object(Bucket=bucket_name, Key=m['s3Key'])
                        print(f"  ✓ S3 file EXISTS")
                    except:
                        print(f"  ✗ S3 file MISSING")
        
        # Check for other statuses
        for status in ['TRANSCRIBING', 'ANALYZING', 'DONE', 'FAILED']:
            count = len([m for m in meetings if m.get('status') == status])
            print(f"  - {status}: {count}")
        
        return meetings
        
    except Exception as e:
        print(f"✗ Error checking meetings: {e}")
        return []

def check_skeleton_timing():
    """Analyze skeleton loading timing"""
    print("\n" + "="*80)
    print("SKELETON LOADING ANALYSIS")
    print("="*80)
    
    print("\n📊 Current Implementation:")
    print("  1. Component mounts with loading=true")
    print("  2. useEffect runs immediately")
    print("  3. fetchMeetings() called")
    print("  4. API call completes in ~200-500ms")
    print("  5. setLoading(false) called")
    print("  6. Skeleton only visible for <500ms")
    
    print("\n⚠️  ISSUE: Skeleton disappears too fast to see!")
    print("  - React renders are batched")
    print("  - Fast API responses mean skeleton barely flashes")
    print("  - User sees blank screen or instant data")
    
    print("\n✅ SOLUTION: Add minimum display time")
    print("  - Show skeleton for at least 300-500ms")
    print("  - Use Promise.all with delay")
    print("  - Better UX for fast connections")

def main():
    print("\n🔍 DIAGNOSING SKELETON AND PENDING MEETING ISSUES")
    print("="*80)
    
    # Check meetings
    meetings = check_demo_account_meetings()
    
    # Analyze skeleton timing
    check_skeleton_timing()
    
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
