#!/usr/bin/env python3
"""
Check the newly uploaded meeting status
"""
import boto3
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
bucket_name = 'meetingmind-audio-uploads'

def check_recent_meetings():
    """Check most recent meetings"""
    print("\n" + "="*80)
    print("CHECKING RECENT MEETINGS")
    print("="*80)
    
    try:
        # Scan for all meetings, sorted by creation time
        response = meetings_table.scan()
        meetings = response.get('Items', [])
        
        # Sort by createdAt (most recent first)
        meetings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        print(f"\n✓ Found {len(meetings)} total meetings")
        print("\n📋 MOST RECENT 5 MEETINGS:")
        
        for i, m in enumerate(meetings[:5], 1):
            print(f"\n{i}. Meeting ID: {m.get('meetingId')}")
            print(f"   Title: {m.get('title')}")
            print(f"   Status: {m.get('status')}")
            print(f"   User: {m.get('userId')}")
            print(f"   Created: {m.get('createdAt')}")
            print(f"   Updated: {m.get('updatedAt')}")
            
            # Check S3 file
            if m.get('s3Key'):
                try:
                    s3.head_object(Bucket=bucket_name, Key=m['s3Key'])
                    print(f"   S3 File: ✓ EXISTS")
                except:
                    print(f"   S3 File: ✗ MISSING")
            
            # Show processing details if available
            if m.get('status') == 'PENDING':
                print(f"   ⏳ Waiting for processing to start...")
            elif m.get('status') == 'TRANSCRIBING':
                print(f"   🎤 Transcription in progress...")
            elif m.get('status') == 'ANALYZING':
                print(f"   🤖 AI analysis in progress...")
            elif m.get('status') == 'DONE':
                print(f"   ✅ Processing complete!")
                if m.get('summary'):
                    print(f"   Summary: {m['summary'][:80]}...")
            elif m.get('status') == 'FAILED':
                print(f"   ❌ Processing failed")
                if m.get('error'):
                    print(f"   Error: {m['error']}")
        
        return meetings
        
    except Exception as e:
        print(f"✗ Error checking meetings: {e}")
        return []

def main():
    print("\n🔍 CHECKING NEW MEETING STATUS")
    print("="*80)
    
    meetings = check_recent_meetings()
    
    # Check for any pending/processing meetings
    pending = [m for m in meetings if m.get('status') in ['PENDING', 'TRANSCRIBING', 'ANALYZING']]
    
    if pending:
        print("\n" + "="*80)
        print(f"⏳ {len(pending)} MEETING(S) CURRENTLY PROCESSING")
        print("="*80)
        print("\nProcessing typically takes 2-5 minutes depending on audio length.")
        print("You can refresh the dashboard to see updates.")
    
    print("\n" + "="*80)
    print("CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
