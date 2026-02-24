#!/usr/bin/env python3
"""Check if update-action Lambda has ANY recent activity."""

import boto3
from datetime import datetime, timedelta

logs = boto3.client('logs', region_name='ap-south-1')

# Check last 2 hours
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=2)

try:
    response = logs.filter_log_events(
        logGroupName='/aws/lambda/meetingmind-update-action',
        startTime=int(start_time.timestamp() * 1000),
        endTime=int(end_time.timestamp() * 1000),
        limit=100
    )
    
    print('UPDATE-ACTION LAMBDA ACTIVITY (Last 2 hours)')
    print('=' * 80)
    
    if not response['events']:
        print('❌ NO ACTIVITY in last 2 hours')
        print()
        print('This means:')
        print('  - Lambda is NOT being invoked')
        print('  - API Gateway might not be routing correctly')
        print('  - Or frontend is not actually calling the API')
    else:
        print(f'✅ Found {len(response["events"])} log events')
        print()
        print('Recent invocations:')
        
        invocations = []
        for event in response['events']:
            message = event['message'].strip()
            if 'START RequestId' in message:
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                invocations.append(timestamp)
        
        print(f'  Total invocations: {len(invocations)}')
        if invocations:
            print(f'  Most recent: {max(invocations)}')
            print(f'  Oldest: {min(invocations)}')
        
        print()
        print('Sample log messages:')
        for event in response['events'][:10]:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f'[{timestamp}] {message[:100]}')
    
except Exception as e:
    print(f'Error: {e}')
