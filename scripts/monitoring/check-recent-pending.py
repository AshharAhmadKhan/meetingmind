import boto3
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get meetings from last 10 minutes
now = datetime.now(timezone.utc)
ten_min_ago = now - timedelta(minutes=10)

response = table.scan()
meetings = response.get('Items', [])

recent_meetings = []
for meeting in meetings:
    created = meeting.get('createdAt', '')
    if created:
        try:
            # Parse ISO format
            if '+' in created:
                created_dt = datetime.fromisoformat(created)
            else:
                created_dt = datetime.fromisoformat(created).replace(tzinfo=timezone.utc)
            
            if created_dt > ten_min_ago:
                recent_meetings.append(meeting)
        except:
            pass

print(f"\n{'='*80}")
print(f"Meetings from last 10 minutes: {len(recent_meetings)}")
print(f"{'='*80}\n")

if not recent_meetings:
    print("No meetings uploaded in the last 10 minutes.")
else:
    for meeting in recent_meetings:
        print(f"Meeting ID: {meeting.get('meetingId', 'N/A')}")
        print(f"Title: {meeting.get('title', 'N/A')}")
        print(f"Status: {meeting.get('status', 'N/A')}")
        print(f"Owner: {meeting.get('userId', 'N/A')}")
        print(f"Created: {meeting.get('createdAt', 'N/A')}")
        print(f"Updated: {meeting.get('updatedAt', 'N/A')}")
        
        if meeting.get('status') == 'PENDING':
            print(f"\n🔍 PENDING MEETING FOUND!")
            print(f"   S3 Key: {meeting.get('s3Key', 'N/A')}")
            print(f"   Audio URL: {meeting.get('audioUrl', 'N/A')}")
            
            # Check if transcription job exists
            if 's3Key' in meeting:
                print(f"\n   Checking Transcribe job...")
                transcribe = boto3.client('transcribe', region_name='ap-south-1')
                job_name = meeting['s3Key'].replace('/', '_').replace('.', '_')
                try:
                    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                    print(f"   Transcribe Status: {job['TranscriptionJob']['TranscriptionJobStatus']}")
                except Exception as e:
                    print(f"   Transcribe job not found: {e}")
        
        print()
