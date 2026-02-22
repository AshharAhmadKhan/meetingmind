#!/usr/bin/env python3
"""
Diagnose the REAL issue - test as if we're the actual users
Test all 3 accounts with REAL API calls
"""
import boto3
import requests
import json

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
CLIENT_ID = '6qnj0ku56g7or26vhqjnfe0oa5'
API_URL = 'https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod'

# Test users
USERS = {
    'uploader': {
        'email': 'thecyberprinciples@gmail.com',
        'password': 'Test@123456'  # User needs to provide
    },
    'member1': {
        'email': 'thehiddenif@gmail.com',
        'password': 'Test@123456'  # User needs to provide
    },
    'member2': {
        'email': 'ashkagakoko@gmail.com',
        'password': 'Test@123456'  # User needs to provide
    }
}

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def get_id_token(email, password):
    """Get ID token for user"""
    try:
        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']['IdToken']
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_list_meetings_api(email, password, team_id=None):
    """Test the actual API call that frontend makes"""
    print(f"\n{'─'*80}")
    print(f"Testing: {email}")
    print(f"{'─'*80}")
    
    # Get token
    token = get_id_token(email, password)
    if not token:
        print("❌ Cannot get token - check password")
        return False
    
    print(f"✓ Got authentication token")
    
    # Make API call
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test with team
    if team_id:
        url = f"{API_URL}/meetings?teamId={team_id}"
        print(f"\nAPI Call: GET {url}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                meetings = data.get('meetings', [])
                print(f"✓ SUCCESS: Got {len(meetings)} meetings")
                
                for i, meeting in enumerate(meetings, 1):
                    print(f"  {i}. {meeting.get('title', 'Untitled')}")
                    print(f"     Status: {meeting.get('status', 'Unknown')}")
                    print(f"     MeetingId: {meeting.get('meetingId', 'Unknown')}")
                
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    else:
        # Test personal meetings
        url = f"{API_URL}/meetings"
        print(f"\nAPI Call: GET {url}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                meetings = data.get('meetings', [])
                print(f"✓ SUCCESS: Got {len(meetings)} meetings")
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False

def check_database_state():
    """Check what's actually in the database"""
    print_section("DATABASE STATE CHECK")
    
    # Check teams
    teams_table = dynamodb.Table('meetingmind-teams')
    teams_response = teams_table.scan()
    teams = teams_response['Items']
    
    print(f"Total teams: {len(teams)}\n")
    
    for team in teams:
        team_id = team.get('teamId')
        team_name = team.get('teamName', team.get('name', 'Unnamed'))
        members = team.get('members', [])
        
        print(f"Team: {team_name}")
        print(f"  TeamId: {team_id}")
        print(f"  Members: {len(members)}")
        
        for member in members:
            if isinstance(member, dict):
                print(f"    - {member.get('email', 'Unknown')} ({member.get('role', 'member')})")
            else:
                print(f"    - {member}")
        
        # Count meetings for this team
        meetings_table = dynamodb.Table('meetingmind-meetings')
        try:
            meetings_response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': team_id}
            )
            meeting_count = len(meetings_response['Items'])
            print(f"  Meetings: {meeting_count}")
            
            for meeting in meetings_response['Items']:
                print(f"    - {meeting.get('title', 'Untitled')} (uploaded by {meeting.get('email', 'Unknown')})")
        except Exception as e:
            print(f"  ❌ Cannot query meetings: {e}")
        
        print()

def check_gsi_status():
    """Check if GSI is active"""
    print_section("GSI STATUS CHECK")
    
    dynamodb_client = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb_client.describe_table(TableName='meetingmind-meetings')
        table = response['Table']
        
        gsi_list = table.get('GlobalSecondaryIndexes', [])
        
        print(f"Total GSIs: {len(gsi_list)}\n")
        
        for gsi in gsi_list:
            print(f"GSI: {gsi['IndexName']}")
            print(f"  Status: {gsi['IndexStatus']}")
            print(f"  Keys: {gsi['KeySchema']}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "="*80)
    print("  COMPREHENSIVE REAL ISSUE DIAGNOSIS")
    print("  Testing as actual users with real API calls")
    print("="*80)
    
    # Step 1: Check database state
    check_database_state()
    
    # Step 2: Check GSI status
    check_gsi_status()
    
    # Step 3: Test API calls
    print_section("API CALL TESTS")
    
    print("\n⚠️  NOTE: You need to provide passwords for test users")
    print("Edit this script and add passwords to USERS dict\n")
    
    # Get team IDs
    teams_table = dynamodb.Table('meetingmind-teams')
    teams_response = teams_table.scan()
    teams = teams_response['Items']
    
    v1_team = None
    v2_team = None
    
    for team in teams:
        name = team.get('teamName', team.get('name', ''))
        if 'V1' in name or 'Legacy' in name:
            v1_team = team['teamId']
        elif 'V2' in name or 'Active' in name:
            v2_team = team['teamId']
    
    if not v1_team:
        print("❌ V1 team not found")
        return
    
    print(f"Testing with V1 team: {v1_team}\n")
    
    # Test each user
    results = {}
    
    for role, user_info in USERS.items():
        email = user_info['email']
        password = user_info['password']
        
        if password == 'Test@123456':
            print(f"\n⚠️  Skipping {email} - password not set")
            results[email] = None
            continue
        
        results[email] = test_list_meetings_api(email, password, v1_team)
    
    # Summary
    print_section("SUMMARY")
    
    for email, result in results.items():
        if result is None:
            print(f"{email}: ⚠️  SKIPPED (no password)")
        elif result:
            print(f"{email}: ✅ CAN see meetings")
        else:
            print(f"{email}: ❌ CANNOT see meetings")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
