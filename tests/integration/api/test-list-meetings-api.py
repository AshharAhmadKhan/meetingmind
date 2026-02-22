#!/usr/bin/env python3
"""Test the list meetings API to see if test meeting appears"""

import boto3
import json

lambda_client = boto3.client('lambda', region_name='ap-south-1')

USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"

# Simulate API Gateway event
event = {
    'httpMethod': 'GET',
    'queryStringParameters': {
        'teamId': TEAM_ID
    },
    'requestContext': {
        'authorizer': {
            'claims': {
                'sub': USER_ID
            }
        }
    }
}

print("Testing GET /meetings API...")
print(f"User ID: {USER_ID}")
print(f"Team ID: {TEAM_ID}")
print()

try:
    response = lambda_client.invoke(
        FunctionName='meetingmind-list-meetings',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    
    payload = json.loads(response['Payload'].read())
    
    if payload.get('statusCode') == 200:
        body = json.loads(payload['body'])
        meetings = body.get('meetings', [])
        
        print(f"✅ API returned {len(meetings)} meetings")
        print()
        
        # Find test meeting
        test_meeting = None
        for meeting in meetings:
            if meeting.get('title') == 'Comprehensive Feature Test Meeting':
                test_meeting = meeting
                break
        
        if test_meeting:
            print("✅ TEST MEETING FOUND IN API RESPONSE!")
            print(f"   Title: {test_meeting['title']}")
            print(f"   Meeting ID: {test_meeting['meetingId']}")
            print(f"   Health Score: {test_meeting.get('healthScore')}")
            print(f"   ROI: {test_meeting.get('roi')}%")
            print(f"   Action Items: {test_meeting.get('totalActions')}")
        else:
            print("❌ Test meeting NOT in API response")
            print()
            print("Meetings returned:")
            for m in meetings:
                print(f"  - {m.get('title')}")
    else:
        print(f"❌ API error: {payload.get('statusCode')}")
        print(f"   Body: {payload.get('body')}")
        
except Exception as e:
    print(f"❌ Lambda invocation failed: {e}")
