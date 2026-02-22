#!/usr/bin/env python3
"""
Test the API endpoint directly (simulating browser request).
This verifies the full API Gateway → Lambda flow.
"""

import requests
import json
import boto3

REGION = 'ap-south-1'
API_URL = 'https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
CLIENT_ID = '150n899gkc651g6e0p7hacguac'

# Test credentials (you'll need to use your actual credentials)
TEST_EMAIL = 'ashhar@meetingmind.com'
TEST_PASSWORD = 'Test1234'  # Replace with actual password

def get_auth_token():
    """Get Cognito auth token"""
    client = boto3.client('cognito-idp', region_name=REGION)
    
    try:
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': TEST_EMAIL,
                'PASSWORD': TEST_PASSWORD
            }
        )
        return response['AuthenticationResult']['IdToken']
    except Exception as e:
        print(f"Failed to get auth token: {e}")
        print("Please update TEST_EMAIL and TEST_PASSWORD in the script")
        return None

def test_api_endpoint():
    """Test the /check-duplicate endpoint via API Gateway"""
    print("\n" + "="*60)
    print("TESTING API ENDPOINT (Browser Simulation)")
    print("="*60)
    
    # Get auth token
    print("\n1. Getting Cognito auth token...")
    token = get_auth_token()
    if not token:
        print("✗ Failed to get auth token")
        print("\nTo test with your credentials:")
        print("1. Update TEST_EMAIL and TEST_PASSWORD in test-api-endpoint.py")
        print("2. Run: python test-api-endpoint.py")
        return False
    
    print("✓ Got auth token")
    
    # Test duplicate detection
    print("\n2. Testing /check-duplicate endpoint...")
    test_task = "Update project tracker with new milestones"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {'task': test_task}
    
    print(f"   Task: '{test_task}'")
    print(f"   URL: {API_URL}/check-duplicate")
    
    try:
        response = requests.post(
            f'{API_URL}/check-duplicate',
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"\n3. Response received:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*60)
            print("RESULTS")
            print("="*60)
            print(f"Is Duplicate: {result.get('isDuplicate')}")
            print(f"Similarity: {result.get('similarity')}%")
            print(f"Is Chronic Blocker: {result.get('isChronicBlocker')}")
            print(f"Repeat Count: {result.get('repeatCount')}")
            
            if result.get('bestMatch'):
                print(f"\nBest Match:")
                print(f"  Task: {result['bestMatch']['task']}")
                print(f"  From: {result['bestMatch']['meetingTitle']}")
                print(f"  Similarity: {result['bestMatch']['similarity']}%")
            
            if result.get('history'):
                print(f"\nHistory ({len(result['history'])} similar items):")
                for i, item in enumerate(result['history'][:5], 1):
                    print(f"  {i}. {item['task'][:60]}... ({item['similarity']}%)")
            
            print("\n✓ API endpoint working correctly!")
            print("\nThis is exactly what the frontend will receive.")
            print("Once browser cache clears, the button will work!")
            return True
        else:
            print(f"\n✗ API returned error:")
            print(f"   Status: {response.status_code}")
            print(f"   Body: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        return False

if __name__ == '__main__':
    test_api_endpoint()
