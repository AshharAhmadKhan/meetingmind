#!/usr/bin/env python3
"""
Diagnose why meetings are stuck in PENDING status
"""
import boto3
import json
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')
logs = boto3.client('logs', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
bucket_name = 'meetingmind-audio-uploads'

def check_pending_meetings():
    """Find all pending meetings"""
    print("\n" + "="*80)
    print("CHECKING PENDING MEETINGS")
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
            print(f"\n📋 Meeting: {m.get('title')}")
            print(f"   ID: {m.get('meetingId')}")
            print(f"   User: {m.get('userId')}")
            print(f"   Created: {m.get('createdAt')}")
            print(f"   S3 Key: {m.get('s3Key')}")
            
            # Check S3 file
            if m.get('s3Key'):
                try:
                    obj = s3.head_object(Bucket=bucket_name, Key=m['s3Key'])
                    print(f"   S3 File: ✓ EXISTS ({obj['ContentLength']} bytes)")
                except Exception as e:
                    print(f"   S3 File: ✗ MISSING - {e}")
        
        return pending
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def check_process_meeting_lambda():
    """Check if process-meeting Lambda is working"""
    print("\n" + "="*80)
    print("CHECKING PROCESS-MEETING LAMBDA")
    print("="*80)
    
    try:
        # Get Lambda function
        response = lambda_client.get_function(
            FunctionName='meetingmind-stack-ProcessMeetingFunction-xxxxxxxx'
        )
        print(f"\n✓ Lambda exists")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"\n✗ Lambda not found - checking all Lambdas...")
        
        # List all Lambdas
        response = lambda_client.list_functions()
        process_lambdas = [f for f in response['Functions'] if 'ProcessMeeting' in f['FunctionName']]
        
        if process_lambdas:
            print(f"\n✓ Found {len(process_lambdas)} ProcessMeeting Lambda(s):")
            for f in process_lambdas:
                print(f"   - {f['FunctionName']}")
                print(f"     Last Modified: {f['LastModified']}")
                print(f"     Runtime: {f['Runtime']}")
        else:
            print(f"\n✗ NO ProcessMeeting Lambda found!")
    
    except Exception as e:
        print(f"\n✗ Error checking Lambda: {e}")

def check_s3_event_notifications():
    """Check if S3 bucket has event notifications configured"""
    print("\n" + "="*80)
    print("CHECKING S3 EVENT NOTIFICATIONS")
    print("="*80)
    
    try:
        response = s3.get_bucket_notification_configuration(Bucket=bucket_name)
        
        lambda_configs = response.get('LambdaFunctionConfigurations', [])
        
        if lambda_configs:
            print(f"\n✓ Found {len(lambda_configs)} Lambda notification(s):")
            for config in lambda_configs:
                print(f"\n   Lambda: {config.get('LambdaFunctionArn')}")
                print(f"   Events: {config.get('Events')}")
                if config.get('Filter'):
                    print(f"   Filter: {config.get('Filter')}")
        else:
            print(f"\n✗ NO Lambda notifications configured!")
            print(f"   This is why meetings stay PENDING - no Lambda is triggered on upload")
        
    except Exception as e:
        print(f"\n✗ Error checking S3 notifications: {e}")

def check_recent_lambda_logs():
    """Check recent Lambda execution logs"""
    print("\n" + "="*80)
    print("CHECKING RECENT LAMBDA LOGS")
    print("="*80)
    
    try:
        # List log groups
        response = logs.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/meetingmind-stack-ProcessMeeting'
        )
        
        log_groups = response.get('logGroups', [])
        
        if log_groups:
            print(f"\n✓ Found {len(log_groups)} log group(s)")
            
            for log_group in log_groups[:1]:  # Check first one
                log_group_name = log_group['logGroupName']
                print(f"\n   Checking: {log_group_name}")
                
                # Get recent log streams
                streams_response = logs.describe_log_streams(
                    logGroupName=log_group_name,
                    orderBy='LastEventTime',
                    descending=True,
                    limit=3
                )
                
                streams = streams_response.get('logStreams', [])
                
                if streams:
                    print(f"   Last execution: {datetime.fromtimestamp(streams[0]['lastEventTimestamp']/1000)}")
                else:
                    print(f"   No recent executions")
        else:
            print(f"\n✗ No log groups found")
            print(f"   Lambda may not have been invoked yet")
        
    except Exception as e:
        print(f"\n✗ Error checking logs: {e}")

def main():
    print("\n🔍 DIAGNOSING PENDING MEETINGS")
    print("="*80)
    
    # 1. Find pending meetings
    pending = check_pending_meetings()
    
    if not pending:
        print("\n✅ No pending meetings found!")
        return
    
    # 2. Check Lambda function
    check_process_meeting_lambda()
    
    # 3. Check S3 event notifications
    check_s3_event_notifications()
    
    # 4. Check Lambda logs
    check_recent_lambda_logs()
    
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)
    
    print("\n💡 LIKELY ISSUE:")
    print("   S3 bucket event notifications may not be configured")
    print("   This means Lambda doesn't get triggered when files are uploaded")
    print("\n🔧 SOLUTION:")
    print("   Need to manually trigger processing for these meetings")

if __name__ == "__main__":
    main()
