#!/usr/bin/env python3
"""
Simulate a meeting upload by directly creating database entry
This tests if the processing pipeline works
"""
import boto3
import uuid
from datetime import datetime, timezone

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
bucket_name = 'meetingmind-audio-707411439284'

# Demo user ID (from previous checks)
DEMO_USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
DEMO_EMAIL = "demo@meetingmind.app"

def create_test_meeting():
    """Create a test meeting entry in database"""
    print("\n" + "="*80)
    print("CREATING TEST MEETING")
    print("="*80)
    
    meeting_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    meeting = {
        'meetingId': meeting_id,
        'userId': DEMO_USER_ID,
        'title': f'Test Meeting {datetime.now().strftime("%H:%M:%S")}',
        'status': 'PENDING',
        'createdAt': now,
        'updatedAt': now,
        's3Key': f'audio/{DEMO_USER_ID}__{meeting_id}__test.mp3'
    }
    
    try:
        meetings_table.put_item(Item=meeting)
        print(f"\n✓ Meeting created in database")
        print(f"   ID: {meeting_id}")
        print(f"   Title: {meeting['title']}")
        print(f"   Status: PENDING")
        return meeting_id
    except Exception as e:
        print(f"\n✗ Failed to create meeting: {e}")
        return None

def check_meeting_status(meeting_id, user_id, wait_seconds=10):
    """Check meeting status after waiting"""
    import time
    
    print(f"\n⏳ Waiting {wait_seconds} seconds for processing...")
    time.sleep(wait_seconds)
    
    print("\n" + "="*80)
    print("CHECKING MEETING STATUS")
    print("="*80)
    
    try:
        response = meetings_table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        
        if 'Item' in response:
            meeting = response['Item']
            print(f"\n✓ Meeting found")
            print(f"   Status: {meeting.get('status')}")
            print(f"   Updated: {meeting.get('updatedAt')}")
            
            if meeting.get('status') == 'PENDING':
                print(f"\n⚠️  Still PENDING - processing not triggered")
                return 'PENDING'
            elif meeting.get('status') in ['TRANSCRIBING', 'ANALYZING']:
                print(f"\n✓ Processing started!")
                return meeting.get('status')
            elif meeting.get('status') == 'DONE':
                print(f"\n✅ Processing complete!")
                return 'DONE'
            elif meeting.get('status') == 'FAILED':
                print(f"\n❌ Processing failed")
                if meeting.get('error'):
                    print(f"   Error: {meeting.get('error')}")
                return 'FAILED'
        else:
            print(f"\n✗ Meeting not found")
            return None
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

def check_all_pending():
    """Check if there are any pending meetings"""
    print("\n" + "="*80)
    print("CHECKING ALL PENDING MEETINGS")
    print("="*80)
    
    try:
        response = meetings_table.scan(
            FilterExpression='#status = :pending',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':pending': 'PENDING'}
        )
        
        pending = response.get('Items', [])
        print(f"\n✓ Found {len(pending)} PENDING meetings")
        
        for m in pending:
            print(f"\n   - {m.get('title')}")
            print(f"     Created: {m.get('createdAt')}")
            print(f"     Age: {(datetime.now(timezone.utc) - datetime.fromisoformat(m.get('createdAt'))).total_seconds() / 60:.1f} minutes")
        
        return pending
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return []

def main():
    print("\n🧪 SIMULATING MEETING UPLOAD")
    print("="*80)
    
    # 1. Check existing pending meetings first
    existing_pending = check_all_pending()
    
    # 2. Create test meeting
    meeting_id = create_test_meeting()
    
    if not meeting_id:
        print("\n❌ Failed to create test meeting")
        return
    
    # 3. Check status after waiting
    status = check_meeting_status(meeting_id, DEMO_USER_ID, wait_seconds=5)
    
    # 4. Check all pending again
    all_pending = check_all_pending()
    
    # 5. Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if status == 'PENDING':
        print(f"\n❌ ISSUE CONFIRMED: Meetings stay PENDING")
        print(f"\n💡 This means:")
        print(f"   - Meeting IS being created in database")
        print(f"   - But processing is NOT being triggered")
        print(f"   - Likely cause: S3 event notifications not configured")
        print(f"   - Or: Lambda function not being invoked")
    elif status in ['TRANSCRIBING', 'ANALYZING', 'DONE']:
        print(f"\n✅ Processing is working!")
        print(f"   Status changed from PENDING to {status}")
    else:
        print(f"\n⚠️  Unexpected result: {status}")

if __name__ == "__main__":
    main()
