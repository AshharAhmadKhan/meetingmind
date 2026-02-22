#!/usr/bin/env python3
"""
Test the complete upload flow to see if meetings are being created
"""
import boto3
import requests
import json
import time
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
cognito = boto3.client('cognito-idp', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')

# Demo account credentials
DEMO_EMAIL = "demo@meetingmind.app"
DEMO_PASSWORD = "Demo@123"
USER_POOL_ID = "ap-south-1_YourPoolId"  # Will get from env
CLIENT_ID = "YourClientId"  # Will get from env
API_URL = "https://your-api.execute-api.ap-south-1.amazonaws.com/prod"

def get_demo_credentials():
    """Get demo account auth token"""
    print("\n" + "="*80)
    print("AUTHENTICATING AS DEMO USER")
    print("="*80)
    
    try:
        # Try to get user pool and client from CloudFormation
        cf = boto3.client('cloudformation', region_name='ap-south-1')
        response = cf.describe_stacks(StackName='meetingmind-stack')
        
        outputs = response['Stacks'][0]['Outputs']
        
        user_pool_id = None
        client_id = None
        api_url = None
        
        for output in outputs:
            if output['OutputKey'] == 'UserPoolId':
                user_pool_id = output['OutputValue']
            elif output['OutputKey'] == 'UserPoolClientId':
                client_id = output['OutputValue']
            elif output['OutputKey'] == 'ApiUrl':
                api_url = output['OutputValue']
        
        print(f"\n✓ User Pool: {user_pool_id}")
        print(f"✓ Client ID: {client_id}")
        print(f"✓ API URL: {api_url}")
        
        # Authenticate
        response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': DEMO_EMAIL,
                'PASSWORD': DEMO_PASSWORD
            }
        )
        
        id_token = response['AuthenticationResult']['IdToken']
        print(f"\n✓ Authenticated successfully")
        
        return {
            'id_token': id_token,
            'api_url': api_url,
            'user_pool_id': user_pool_id
        }
        
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return None

def count_meetings_before():
    """Count meetings before upload"""
    print("\n" + "="*80)
    print("COUNTING MEETINGS BEFORE UPLOAD")
    print("="*80)
    
    try:
        response = meetings_table.scan()
        count = len(response.get('Items', []))
        print(f"\n✓ Current meeting count: {count}")
        return count
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 0

def test_upload_api(auth):
    """Test the upload API endpoint"""
    print("\n" + "="*80)
    print("TESTING UPLOAD API")
    print("="*80)
    
    if not auth:
        print("\n✗ No auth credentials")
        return None
    
    try:
        # Request upload URL
        url = f"{auth['api_url']}/upload"
        headers = {
            'Authorization': auth['id_token'],
            'Content-Type': 'application/json'
        }
        
        payload = {
            'title': f'Test Upload {datetime.now().strftime("%H:%M:%S")}',
            'contentType': 'audio/mpeg',
            'fileSize': 1024000  # 1MB
        }
        
        print(f"\n📤 Requesting upload URL...")
        print(f"   URL: {url}")
        print(f"   Title: {payload['title']}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"\n   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Got upload URL")
            print(f"   Meeting ID: {data.get('meetingId')}")
            return data
        else:
            print(f"   ✗ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

def check_meeting_created(meeting_id):
    """Check if meeting was created in database"""
    print("\n" + "="*80)
    print("CHECKING IF MEETING WAS CREATED")
    print("="*80)
    
    try:
        response = meetings_table.get_item(Key={'meetingId': meeting_id})
        
        if 'Item' in response:
            meeting = response['Item']
            print(f"\n✓ Meeting found in database!")
            print(f"   ID: {meeting.get('meetingId')}")
            print(f"   Title: {meeting.get('title')}")
            print(f"   Status: {meeting.get('status')}")
            print(f"   Created: {meeting.get('createdAt')}")
            return True
        else:
            print(f"\n✗ Meeting NOT found in database")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def count_meetings_after():
    """Count meetings after upload"""
    print("\n" + "="*80)
    print("COUNTING MEETINGS AFTER UPLOAD")
    print("="*80)
    
    try:
        response = meetings_table.scan()
        count = len(response.get('Items', []))
        print(f"\n✓ Current meeting count: {count}")
        return count
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 0

def main():
    print("\n🧪 TESTING UPLOAD FLOW")
    print("="*80)
    
    # 1. Count meetings before
    count_before = count_meetings_before()
    
    # 2. Authenticate
    auth = get_demo_credentials()
    
    if not auth:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # 3. Test upload API
    upload_result = test_upload_api(auth)
    
    if not upload_result:
        print("\n❌ Upload API failed")
        return
    
    meeting_id = upload_result.get('meetingId')
    
    # 4. Wait a moment for database write
    print("\n⏳ Waiting 2 seconds for database write...")
    time.sleep(2)
    
    # 5. Check if meeting was created
    created = check_meeting_created(meeting_id)
    
    # 6. Count meetings after
    count_after = count_meetings_after()
    
    # 7. Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    print(f"\n📊 Meetings before: {count_before}")
    print(f"📊 Meetings after:  {count_after}")
    print(f"📊 Difference:      {count_after - count_before}")
    
    if created:
        print(f"\n✅ SUCCESS: Meeting was created in database")
        print(f"   The upload flow is working correctly")
    else:
        print(f"\n❌ FAILURE: Meeting was NOT created in database")
        print(f"   There is a problem with the upload flow")
        print(f"\n💡 Possible issues:")
        print(f"   - Lambda function not triggered")
        print(f"   - Database write permission issue")
        print(f"   - API Gateway integration problem")

if __name__ == "__main__":
    main()
