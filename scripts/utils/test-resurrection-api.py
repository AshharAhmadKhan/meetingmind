#!/usr/bin/env python3
"""
Test the resurrection API endpoint directly
"""
import boto3
import json
from datetime import datetime

# Get Cognito credentials for cyber user
cognito = boto3.client('cognito-idp', region_name='ap-south-1')

# Authenticate
response = cognito.initiate_auth(
    ClientId='25g9j8rqup9t2clapi-south-1.amazonaws.com',
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': 'thecyberprinciples@gmail.com',
        'PASSWORD': input('Enter password for cyber user: ')
    }
)

id_token = response['AuthenticationResult']['IdToken']
print(f"✓ Got ID token: {id_token[:50]}...")

# Now test the update-action API
import requests

# Get a graveyard item first
api_base = 'https://zsc4j.execute-api.ap-south-1.amazonaws.com/prod'
headers = {
    'Authorization': id_token,
    'Content-Type': 'application/json'
}

# Get all actions
print("\n1. Fetching all actions...")
response = requests.get(f'{api_base}/all-actions', headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    actions = data.get('actions', [])
    
    # Find a graveyard item (>30 days old)
    graveyard_items = []
    for action in actions:
        created_at = action.get('createdAt')
        if created_at:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.now(created.tzinfo) - created).days
            if days_old > 30 and not action.get('completed'):
                graveyard_items.append(action)
    
    if graveyard_items:
        item = graveyard_items[0]
        print(f"\n2. Found graveyard item: {item['task'][:50]}...")
        print(f"   Meeting ID: {item['meetingId']}")
        print(f"   Action ID: {item['id']}")
        
        # Try to resurrect it
        print("\n3. Attempting resurrection...")
        update_url = f"{api_base}/meetings/{item['meetingId']}/actions/{item['id']}"
        update_data = {
            'status': 'todo',
            'owner': 'Test Owner',
            'deadline': '2026-03-01',
            'completed': False
        }
        
        print(f"   URL: {update_url}")
        print(f"   Data: {json.dumps(update_data, indent=2)}")
        print(f"   Headers: Authorization={id_token[:30]}..., Content-Type=application/json")
        
        response = requests.put(update_url, headers=headers, json=update_data)
        print(f"\n   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✓ Resurrection successful!")
        else:
            print(f"\n✗ Resurrection failed: {response.status_code}")
    else:
        print("\n✗ No graveyard items found")
else:
    print(f"✗ Failed to get actions: {response.text}")
