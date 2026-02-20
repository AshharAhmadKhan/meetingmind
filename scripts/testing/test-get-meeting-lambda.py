#!/usr/bin/env python3
"""
Test the get-meeting Lambda function directly
"""
import boto3
import json
from decimal import Decimal

lambda_client = boto3.client('lambda', region_name='ap-south-1')

# Test user (team member)
test_user_id = 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'  # thehidden
test_meeting_id = '27c1d9c8-0aee-46aa-9e10-887d599b71fc'  # V1 Meeting 1

# Simulate API Gateway event
event = {
    'httpMethod': 'GET',
    'pathParameters': {
        'meetingId': test_meeting_id
    },
    'requestContext': {
        'authorizer': {
            'claims': {
                'sub': test_user_id,
                'email': 'thehiddenif@gmail.com'
            }
        }
    }
}

print("=" * 80)
print("TEST: Get Meeting Lambda Function")
print("=" * 80)
print()
print(f"Test User: {test_user_id}")
print(f"Meeting ID: {test_meeting_id}")
print()

try:
    response = lambda_client.invoke(
        FunctionName='meetingmind-get-meeting',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    
    payload = json.loads(response['Payload'].read())
    status_code = payload.get('statusCode')
    
    print(f"Status Code: {status_code}")
    print()
    
    if status_code == 200:
        print("✅ Lambda returned 200 OK")
        print()
        
        body = json.loads(payload['body'])
        
        print("Meeting data returned:")
        print(f"  Title: {body.get('title')}")
        print(f"  Team ID: {body.get('teamId')}")
        print(f"  Status: {body.get('status')}")
        print()
        
        print("Action Items:")
        actions = body.get('actionItems', [])
        print(f"  Count: {len(actions)}")
        if actions:
            action = actions[0]
            print(f"  First action:")
            print(f"    Has 'text' field: {'text' in action}")
            print(f"    Has 'task' field: {'task' in action}")
            print(f"    Status: {action.get('status')}")
            print(f"    Owner: {action.get('owner')}")
        print()
        
        print("Decisions:")
        decisions = body.get('decisions', [])
        print(f"  Count: {len(decisions)}")
        if decisions:
            decision = decisions[0]
            print(f"  First decision type: {type(decision).__name__}")
            if isinstance(decision, dict):
                print(f"    Has 'text' field: {'text' in decision}")
                print(f"    Text: {decision.get('text')}")
            else:
                print(f"    Value: {decision}")
        print()
        
        print("ROI:")
        roi = body.get('roi')
        print(f"  Type: {type(roi).__name__}")
        print(f"  Value: {roi}")
        if isinstance(roi, dict):
            print(f"    Has 'roi' field: {'roi' in roi}")
            print(f"    Has 'value' field: {'value' in roi}")
        print()
        
        print("✅ All checks passed!")
        
    elif status_code == 403:
        print("❌ Lambda returned 403 Forbidden")
        body = json.loads(payload['body'])
        print(f"Error: {body.get('error')}")
        
    elif status_code == 404:
        print("❌ Lambda returned 404 Not Found")
        body = json.loads(payload['body'])
        print(f"Error: {body.get('error')}")
        
    else:
        print(f"❌ Unexpected status code: {status_code}")
        print(f"Response: {payload}")
        
except Exception as e:
    print(f"❌ Error invoking Lambda: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
