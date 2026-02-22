#!/usr/bin/env python3
"""
Diagnose why a meeting is stuck in PENDING status
Check the entire processing pipeline
"""
import boto3
import json
from datetime import datetime

REGION = 'ap-south-1'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
sqs = boto3.client('sqs', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)
logs = boto3.client('logs', region_name=REGION)

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def check_pending_meetings():
    """Find all PENDING meetings"""
    print_section("PENDING MEETINGS")
    
    meetings_table = dynamodb.Table('meetingmind-meetings')
    
    # Scan for PENDING meetings
    response = meetings_table.scan(
        FilterExpression='#status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': 'PENDING'}
    )
    
    pending = response['Items']
    
    print(f"Found {len(pending)} PENDING meetings\n")
    
    for meeting in pending:
        meeting_id = meeting.get('meetingId')
        title = meeting.get('title', 'Untitled')
        user_email = meeting.get('email', 'Unknown')
        created_at = meeting.get('createdAt', 'Unknown')
        audio_key = meeting.get('audioKey', 'Unknown')
        
        print(f"Meeting: {title}")
        print(f"  MeetingId: {meeting_id}")
        print(f"  Uploaded by: {user_email}")
        print(f"  Created: {created_at}")
        print(f"  Audio Key: {audio_key}")
        print(f"  Status: PENDING")
        
        # Check how long it's been pending
        if created_at != 'Unknown':
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = datetime.now(created_dt.tzinfo)
                age = now - created_dt
                print(f"  Age: {age.total_seconds():.0f} seconds ({age.total_seconds()/60:.1f} minutes)")
            except:
                pass
        
        print()
    
    return pending

def check_s3_audio(audio_key):
    """Check if audio file exists in S3"""
    print_section(f"S3 CHECK: {audio_key}")
    
    bucket = 'meetingmind-audio-707411439284'
    
    try:
        response = s3.head_object(Bucket=bucket, Key=audio_key)
        print(f"✓ Audio file exists in S3")
        print(f"  Size: {response['ContentLength']} bytes")
        print(f"  Last Modified: {response['LastModified']}")
        print(f"  Content Type: {response.get('ContentType', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Audio file NOT found in S3")
        print(f"  Error: {e}")
        return False

def check_sqs_queue():
    """Check SQS processing queue"""
    print_section("SQS PROCESSING QUEUE")
    
    queue_url = 'https://sqs.ap-south-1.amazonaws.com/707411439284/meetingmind-processing-queue'
    
    try:
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        
        attrs = response['Attributes']
        
        print(f"Queue: meetingmind-processing-queue")
        print(f"  Messages Available: {attrs.get('ApproximateNumberOfMessages', '0')}")
        print(f"  Messages In Flight: {attrs.get('ApproximateNumberOfMessagesNotVisible', '0')}")
        print(f"  Messages Delayed: {attrs.get('ApproximateNumberOfMessagesDelayed', '0')}")
        
        # Try to receive messages (without deleting)
        messages_response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )
        
        messages = messages_response.get('Messages', [])
        
        if messages:
            print(f"\n  Messages in queue: {len(messages)}")
            for i, msg in enumerate(messages, 1):
                body = json.loads(msg['Body'])
                print(f"\n  Message {i}:")
                print(f"    Records: {len(body.get('Records', []))}")
                if body.get('Records'):
                    record = body['Records'][0]
                    s3_info = record.get('s3', {})
                    bucket = s3_info.get('bucket', {}).get('name', 'Unknown')
                    key = s3_info.get('object', {}).get('key', 'Unknown')
                    print(f"    S3 Object: s3://{bucket}/{key}")
        else:
            print(f"\n  No messages in queue")
        
    except Exception as e:
        print(f"❌ Error checking queue: {e}")

def check_dlq():
    """Check Dead Letter Queue"""
    print_section("DEAD LETTER QUEUE")
    
    dlq_url = 'https://sqs.ap-south-1.amazonaws.com/707411439284/meetingmind-processing-dlq'
    
    try:
        response = sqs.get_queue_attributes(
            QueueUrl=dlq_url,
            AttributeNames=['All']
        )
        
        attrs = response['Attributes']
        
        print(f"Queue: meetingmind-processing-dlq")
        print(f"  Messages Available: {attrs.get('ApproximateNumberOfMessages', '0')}")
        
        # Try to receive messages
        messages_response = sqs.receive_message(
            QueueUrl=dlq_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )
        
        messages = messages_response.get('Messages', [])
        
        if messages:
            print(f"\n  ⚠️  {len(messages)} messages in DLQ (processing failed)")
            for i, msg in enumerate(messages, 1):
                body = json.loads(msg['Body'])
                print(f"\n  Message {i}:")
                if body.get('Records'):
                    record = body['Records'][0]
                    s3_info = record.get('s3', {})
                    key = s3_info.get('object', {}).get('key', 'Unknown')
                    print(f"    Failed to process: {key}")
        else:
            print(f"\n  ✓ No messages in DLQ")
        
    except Exception as e:
        print(f"❌ Error checking DLQ: {e}")

def check_lambda_logs(meeting_id):
    """Check CloudWatch logs for processing Lambda"""
    print_section(f"LAMBDA LOGS FOR: {meeting_id}")
    
    log_group = '/aws/lambda/meetingmind-process-meeting'
    
    try:
        # Get recent log streams
        streams_response = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        print(f"Checking recent log streams...\n")
        
        found_logs = False
        
        for stream in streams_response['logStreams']:
            stream_name = stream['logStreamName']
            
            # Get log events
            events_response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                limit=100
            )
            
            events = events_response['events']
            
            # Check if this stream has logs for our meeting
            for event in events:
                message = event['message']
                if meeting_id in message:
                    found_logs = True
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                    print(f"[{timestamp}] {message}")
        
        if not found_logs:
            print(f"No logs found for meeting {meeting_id}")
            print(f"This means the Lambda hasn't processed this meeting yet")
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def main():
    print("\n" + "="*80)
    print("  DIAGNOSE PENDING MEETING")
    print("="*80)
    
    # Step 1: Find pending meetings
    pending = check_pending_meetings()
    
    if not pending:
        print("No pending meetings found!")
        return
    
    # Step 2: Check SQS queue
    check_sqs_queue()
    
    # Step 3: Check DLQ
    check_dlq()
    
    # Step 4: For each pending meeting, check S3 and logs
    for meeting in pending:
        audio_key = meeting.get('audioKey')
        meeting_id = meeting.get('meetingId')
        
        if audio_key:
            check_s3_audio(audio_key)
        
        if meeting_id:
            check_lambda_logs(meeting_id)
    
    # Summary
    print_section("DIAGNOSIS SUMMARY")
    
    print(f"Pending meetings: {len(pending)}")
    print(f"\nPossible causes:")
    print(f"  1. SQS queue has messages but Lambda not processing")
    print(f"  2. Messages in DLQ (processing failed)")
    print(f"  3. S3 notification not triggering SQS")
    print(f"  4. Lambda has errors (check logs above)")
    print(f"  5. Lambda timeout (15 minutes max)")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
