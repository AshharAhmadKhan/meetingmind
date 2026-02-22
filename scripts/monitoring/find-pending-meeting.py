import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Scan for pending meetings
response = table.scan(
    FilterExpression='#status = :pending',
    ExpressionAttributeNames={'#status': 'status'},
    ExpressionAttributeValues={':pending': 'PENDING'}
)

pending = response.get('Items', [])

print(f"\n{'='*80}")
print(f"PENDING Meetings: {len(pending)}")
print(f"{'='*80}\n")

if not pending:
    print("No pending meetings found.")
    print("\nSearching for 'zxcfwz' in all meetings...")
    
    all_response = table.scan()
    all_meetings = all_response.get('Items', [])
    
    for meeting in all_meetings:
        if 'zxcfwz' in meeting.get('title', '').lower():
            print(f"\nFound meeting with 'zxcfwz' in title:")
            print(f"  Meeting ID: {meeting.get('meetingId')}")
            print(f"  Title: {meeting.get('title')}")
            print(f"  Status: {meeting.get('status')}")
            print(f"  Created: {meeting.get('createdAt')}")
            print(f"  Updated: {meeting.get('updatedAt')}")
else:
    for meeting in pending:
        print(f"Meeting ID: {meeting.get('meetingId')}")
        print(f"Title: {meeting.get('title')}")
        print(f"Status: {meeting.get('status')}")
        print(f"Owner: {meeting.get('userId')}")
        print(f"Created: {meeting.get('createdAt')}")
        print(f"Updated: {meeting.get('updatedAt')}")
        print(f"S3 Key: {meeting.get('s3Key', 'N/A')}")
        
        # Check Transcribe job
        if 's3Key' in meeting:
            transcribe = boto3.client('transcribe', region_name='ap-south-1')
            s3_key = meeting['s3Key']
            job_name = s3_key.replace('/', '_').replace('.', '_')
            
            try:
                job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                status = job['TranscriptionJob']['TranscriptionJobStatus']
                print(f"\n🔍 Transcribe Job Status: {status}")
                
                if status == 'FAILED':
                    print(f"   Failure Reason: {job['TranscriptionJob'].get('FailureReason', 'Unknown')}")
            except transcribe.exceptions.BadRequestException:
                print(f"\n❌ Transcribe job not found: {job_name}")
                print(f"   This means the process-meeting Lambda never started transcription")
        
        print()
