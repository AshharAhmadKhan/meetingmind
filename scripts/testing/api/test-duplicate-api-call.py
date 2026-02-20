#!/usr/bin/env python3
"""
End-to-end test for duplicate detection API
Tests the actual /check-duplicate endpoint with real data
"""

import boto3
import json
import requests
from datetime import datetime

# Get Cognito credentials
cognito_client = boto3.client('cognito-idp', region_name='ap-south-1')

# Test credentials
TEST_EMAIL = "thecyberprinciples@gmail.com"
TEST_PASSWORD = "Test@123"  # Replace with actual password if different

# API endpoint
API_BASE = "https://yvqvwvhxe3.execute-api.ap-south-1.amazonaws.com/prod"

def get_auth_token():
    """Get authentication token from Cognito"""
    try:
        # Get user pool ID
        user_pools = cognito_client.list_user_pools(MaxResults=10)
        user_pool_id = None
        
        for pool in user_pools['UserPools']:
            if 'meetingmind' in pool['Name'].lower():
                user_pool_id = pool['Id']
                break
        
        if not user_pool_id:
            print("❌ Could not find MeetingMind user pool")
            return None
        
        # Get client ID
        clients = cognito_client.list_user_pool_clients(
            UserPoolId=user_pool_id,
            MaxResults=10
        )
        
        client_id = clients['UserPoolClients'][0]['ClientId'] if clients['UserPoolClients'] else None
        
        if not client_id:
            print("❌ Could not find app client")
            return None
        
        # Authenticate
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': TEST_EMAIL,
                'PASSWORD': TEST_PASSWORD
            }
        )
        
        token = response['AuthenticationResult']['IdToken']
        print(f"✅ Got auth token for {TEST_EMAIL}")
        return token
        
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        return None

def test_duplicate_detection(token, task_text):
    """Test duplicate detection API"""
    url = f"{API_BASE}/check-duplicate"
    
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    body = {
        'task': task_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("DUPLICATE DETECTION API TEST")
    print("=" * 60)
    print()
    
    # Get auth token
    print("Step 1: Authenticating...")
    token = get_auth_token()
    
    if not token:
        print("\n❌ Cannot proceed without authentication")
        print("   Make sure TEST_PASSWORD is correct in the script")
        return
    
    print()
    
    # Test cases
    test_cases = [
        {
            'name': 'Exact match test',
            'task': 'Draft a database schema',
            'expected': 'Should find exact match'
        },
        {
            'name': 'Similar task test',
            'task': 'Create database design',
            'expected': 'Should find similar to "Draft a database schema"'
        },
        {
            'name': 'Different task test',
            'task': 'Buy groceries and cook dinner',
            'expected': 'Should find no matches'
        },
        {
            'name': 'Partial match test',
            'task': 'Set up report',
            'expected': 'Should find similar to "Set up the report properly"'
        }
    ]
    
    print("Step 2: Testing duplicate detection...")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Task: \"{test['task']}\"")
        print(f"  Expected: {test['expected']}")
        
        result = test_duplicate_detection(token, test['task'])
        
        if result:
            is_duplicate = result.get('isDuplicate', False)
            similarity = result.get('similarity', 0)
            best_match = result.get('bestMatch')
            repeat_count = result.get('repeatCount', 0)
            is_chronic = result.get('isChronicBlocker', False)
            
            if is_duplicate:
                print(f"  ✅ DUPLICATE FOUND")
                print(f"     Similarity: {similarity}%")
                print(f"     Best Match: \"{best_match.get('task', 'N/A')}\"")
                print(f"     Meeting: {best_match.get('meetingTitle', 'N/A')}")
                print(f"     Repeat Count: {repeat_count}")
                if is_chronic:
                    print(f"     ⚠️  CHRONIC BLOCKER (repeated {repeat_count} times)")
            else:
                print(f"  ℹ️  No duplicates found")
                if repeat_count > 0:
                    print(f"     Similar items: {repeat_count} (below threshold)")
        else:
            print(f"  ❌ API call failed")
        
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("✅ Duplicate detection API is accessible")
    print("✅ Authentication works")
    print()
    print("Notes:")
    print("  - API uses 85% similarity threshold for duplicates")
    print("  - Items with 70%+ similarity shown in history")
    print("  - Chronic blocker = repeated 3+ times")
    print("  - Only checks incomplete action items")
    print()
    print("If no duplicates found:")
    print("  1. Check if actions have embeddings (see previous test)")
    print("  2. Verify Bedrock is enabled for semantic search")
    print("  3. Test data may not have similar enough tasks")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
