#!/usr/bin/env python3
"""Check pending meetings and verify if S3 files exist"""
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

table = dynamodb.Table('meetingmind-meetings')
bucket = 'meetingmind-audio-707411439284'

# Get all pending meetings
response = table.scan(
    FilterExpression='#status = :pending',
    ExpressionAttributeNames={'#status': 'status'},
    ExpressionAttributeValues={':pending': 'PENDING'}
)

meetings = response.get('Items', [])
print(f"\n✓ Found {len(meetings)} PENDING meetings:\n")

for m in meetings:
    title = m.get('title')
    created = m.get('createdAt')
    s3_key = m.get('s3Key')
    
    # Check if S3 file exists
    s3_exists = False
    if s3_key:
        try:
            s3.head_object(Bucket=bucket, Key=s3_key)
            s3_exists = True
        except:
            pass
    
    print(f"  - {title}")
    print(f"    Created: {created}")
    print(f"    S3 Key: {s3_key}")
    print(f"    S3 File: {'✓ EXISTS' if s3_exists else '✗ MISSING'}")
    print()
