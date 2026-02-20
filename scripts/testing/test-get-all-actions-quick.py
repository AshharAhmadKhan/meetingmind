#!/usr/bin/env python3
import boto3
import json

lambda_client = boto3.client('lambda', region_name='ap-south-1')

# Team member userId
team_member_id = 'f1d33d1a-9041-7006-5af8-d18269b15a92'
team_id = '95febcb2-97e2-4395-bdde-da8475dbae0d'

event = {
    'httpMethod': 'GET',
    'queryStringParameters': {'teamId': team_id},
    'requestContext': {
        'authorizer': {
            'claims': {'sub': team_member_id}
        }
    }
}

print("Testing get-all-actions Lambda...")
response = lambda_client.invoke(
    FunctionName='meetingmind-get-all-actions',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

result = json.loads(response['Payload'].read())
print(f"Status: {result.get('statusCode')}")

if result.get('statusCode') == 200:
    body = json.loads(result.get('body', '{}'))
    actions = body.get('actions', [])
    stats = body.get('stats', {})
    print(f"✅ SUCCESS: Got {len(actions)} actions")
    print(f"Stats: {stats}")
    
    # Check for graveyard items (>30 days old)
    graveyard = [a for a in actions if not a.get('completed')]
    print(f"Incomplete actions: {len(graveyard)}")
else:
    print(f"❌ FAILED: {result.get('body')}")
