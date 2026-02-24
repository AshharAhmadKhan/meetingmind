#!/usr/bin/env python3
"""Check Lambda function for errors."""

import boto3
import json
from datetime import datetime, timedelta

logs = boto3.client('logs', region_name='ap-south-1')

# Get log streams from last 30 minutes
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=30)

try:
    response = logs.filter_log_events(
        logGroupName='/aws/lambda/meetingmind-update-action',
        startTime=int(start_time.timestamp() * 1000),
        endTime=int(end_time.timestamp() * 1000),
        limit=50
    )
    
    print('RECENT UPDATE-ACTION LAMBDA LOGS')
    print('=' * 80)
    
    if not response['events']:
        print('No logs found in last 30 minutes')
        print()
        print('This could mean:')
        print('  1. No action updates were made')
        print('  2. Lambda is not being invoked')
        print('  3. API Gateway is not routing correctly')
    else:
        for event in response['events']:
            message = event['message'].strip()
            if any(keyword in message.lower() for keyword in ['error', 'fail', 'exception', 'traceback', 'health']):
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                print(f'[{timestamp}] {message}')
                print()
    
except Exception as e:
    print(f'Error fetching logs: {e}')
