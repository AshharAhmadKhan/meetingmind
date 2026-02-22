#!/usr/bin/env python3
"""
Test the update-action Lambda directly
"""
import boto3
import json

lambda_client = boto3.client('lambda', region_name='ap-south-1')

# Create a test event that mimics API Gateway
test_event = {
    "httpMethod": "PUT",
    "pathParameters": {
        "meetingId": "27c1d9c8-0aee-46aa-9e10-887d599b71fc",
        "actionId": "6c3c4215-3783-47f5-b2b0-967c1cc4b16a"
    },
    "body": json.dumps({
        "status": "todo",
        "owner": "Test Owner",
        "deadline": "2026-03-01",
        "completed": False
    }),
    "requestContext": {
        "authorizer": {
            "claims": {
                "sub": "c1c38d2a-1081-7088-7c71-0abc19a150e9"  # cyber user ID
            }
        }
    }
}

print("Invoking Lambda with test event...")
print(f"Meeting ID: {test_event['pathParameters']['meetingId']}")
print(f"Action ID: {test_event['pathParameters']['actionId']}")

response = lambda_client.invoke(
    FunctionName='meetingmind-update-action',
    InvocationType='RequestResponse',
    Payload=json.dumps(test_event)
)

# Parse response
payload = json.loads(response['Payload'].read())
print(f"\nLambda Response:")
print(f"Status Code: {payload.get('statusCode')}")
print(f"Body: {payload.get('body')}")

if 'errorMessage' in payload:
    print(f"\nError: {payload['errorMessage']}")
    if 'errorType' in payload:
        print(f"Error Type: {payload['errorType']}")
    if 'stackTrace' in payload:
        print(f"Stack Trace:")
        for line in payload['stackTrace']:
            print(f"  {line}")
