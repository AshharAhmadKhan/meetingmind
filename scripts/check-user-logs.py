#!/usr/bin/env python3
"""
Check CloudWatch logs for specific user
"""

import boto3
import json
from datetime import datetime, timedelta

def check_user_logs(email):
    """Check logs for specific user"""
    print("=" * 60)
    print(f"📋 CHECKING LOGS FOR: {email}")
    print("=" * 60)
    
    # First, get user ID from Cognito
    cognito = boto3.client('cognito-idp', region_name='ap-south-1')
    user_pool_id = 'ap-south-1_mkFJawjMp'
    
    print(f"\n1️⃣ Finding user in Cognito...")
    
    try:
        response = cognito.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{email}"'
        )
        
        if not response.get('Users'):
            print(f"   ❌ User not found: {email}")
            return
        
        user = response['Users'][0]
        user_id = user['Username']
        status = user['UserStatus']
        
        print(f"   ✅ Found user:")
        print(f"      User ID: {user_id}")
        print(f"      Status: {status}")
        print(f"      Enabled: {user['Enabled']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Check DynamoDB for user's meetings
    print(f"\n2️⃣ Checking user's meetings...")
    
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('meetingmind-meetings')
    
    try:
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        meetings = response.get('Items', [])
        print(f"   Total meetings: {len(meetings)}")
        
        for meeting in meetings[:5]:
            print(f"\n   Meeting: {meeting.get('title', 'Unknown')}")
            print(f"      ID: {meeting.get('meetingId')}")
            print(f"      Status: {meeting.get('status')}")
            print(f"      Created: {meeting.get('createdAt')}")
            print(f"      Actions: {len(meeting.get('actionItems', []))}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check CloudWatch logs
    print(f"\n3️⃣ Checking CloudWatch logs (last 1 hour)...")
    
    logs = boto3.client('logs', region_name='ap-south-1')
    
    # Check list-meetings Lambda logs
    log_group = '/aws/lambda/meetingmind-ListMeetingsFunction'
    
    try:
        # Get log streams from last hour
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        response = logs.filter_log_events(
            logGroupName=log_group,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
            filterPattern=user_id
        )
        
        events = response.get('events', [])
        print(f"   Found {len(events)} log entries for this user")
        
        for event in events[-10:]:  # Last 10 events
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message']
            print(f"\n   [{timestamp}]")
            print(f"   {message[:200]}")
            
    except Exception as e:
        print(f"   ⚠️  Could not read logs: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_user_logs('thecyberprinciples@gmail.com')
