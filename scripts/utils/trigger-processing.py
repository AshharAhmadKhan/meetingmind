#!/usr/bin/env python3
"""
Manually trigger processing for a stuck meeting
"""
import boto3
import json

REGION = 'ap-south-1'
BUCKET = 'meetingmind-audio-707411439284'
S3_KEY = 'audio/a1a3cd5a-00e1-701f-a07b-b12a35f16664__0a292ff3-973f-42aa-84b9-b56928f2a4d3__WhatsApp-Audio-2026-02-17-at-19.24.27.mp4'
QUEUE_URL = 'https://sqs.ap-south-1.amazonaws.com/707411439284/meetingmind-processing-queue'

sqs = boto3.client('sqs', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)

# Create S3 event message
message = {
    'Records': [
        {
            'eventVersion': '2.1',
            'eventSource': 'aws:s3',
            'awsRegion': REGION,
            'eventTime': '2026-02-20T17:19:27.000Z',
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {
                    'name': BUCKET,
                    'arn': f'arn:aws:s3:::{BUCKET}'
                },
                'object': {
                    'key': S3_KEY,
                    'size': 1024000
                }
            }
        }
    ]
}

print(f"Sending message to SQS queue...")
print(f"  Bucket: {BUCKET}")
print(f"  Key: {S3_KEY}")

response = sqs.send_message(
    QueueUrl=QUEUE_URL,
    MessageBody=json.dumps(message)
)

print(f"\n✓ Message sent successfully")
print(f"  MessageId: {response['MessageId']}")
print(f"\nThe Lambda should process this meeting within 1-2 minutes.")
print(f"Check status with: python scripts/check-meeting-status.py")
