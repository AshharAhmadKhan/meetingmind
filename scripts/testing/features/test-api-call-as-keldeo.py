#!/usr/bin/env python3
"""
Test the actual API call that's failing in the browser
Simulate: GET /meetings?teamId=95febcb2-97e2-4395-bdde-da8475dbae0d
As user: Keldeo (ashkagakoko@gmail.com)
"""
import boto3
import json

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
KELDEO_EMAIL = 'ashkagakoko@gmail.com'
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def simulate_list_meetings_api():
    """Simulate the exact API call that's failing"""
    print_section("SIMULATE: GET /meetings?teamId=V1_TEAM_ID")
    
    # Step 1: Get Keldeo's userId (this is what the API gets from JWT token)
    response = cognito.list_users(
        UserPoolId=USER_POOL_ID,
        Filter=f'email = "{KELDEO_EMAIL}"'
    )
    
    if not response['Users']:
        print(f"❌ User not found: {KELDEO_EMAIL}")
        return
    
    user_id = response['Users'][0]['Username']
    print(f"✓ Keldeo's userId: {user_id}")
    print(f"✓ TeamId requested: {V1_TEAM_ID}\n")
    
    # Step 2: Validate user is member of the team (this is what Lambda does)
    print("Step 1: Lambda checks team membership...")
    teams_table = dynamodb.Table('meetingmind-teams')
    team_response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    
    if 'Item' not in team_response:
        print(f"❌ Team not found: {V1_TEAM_ID}")
        print(f"   Lambda would return: 404 Team not found")
        return
    
    team = team_response['Item']
    members = team.get('members', [])
    
    print(f"✓ Team found: {team.get('teamName', 'Unnamed')}")
    print(f"  Members: {len(members)}\n")
    
    # Step 3: Check if user is a member
    print("Step 2: Lambda checks if Keldeo is in team.members[]...")
    member_ids = []
    for member in members:
        if isinstance(member, dict):
            member_ids.append(member.get('userId'))
        else:
            member_ids.append(member)
    
    if user_id not in member_ids:
        print(f"❌ Keldeo is NOT a member")
        print(f"   Lambda would return: 403 You are not a member of this team")
        return
    
    print(f"✓ Keldeo IS a member\n")
    
    # Step 4: Query meetings by teamId
    print("Step 3: Lambda queries meetings by teamId...")
    meetings_table = dynamodb.Table('meetingmind-meetings')
    
    try:
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': V1_TEAM_ID},
            ScanIndexForward=False  # newest first
        )
        
        meetings = response['Items']
        print(f"✓ Query successful")
        print(f"  Found {len(meetings)} meetings\n")
        
        # Step 5: Return meetings (this is what Lambda returns)
        print("Step 4: Lambda returns meetings...")
        print(f"✓ Lambda would return: 200 OK")
        print(f"  Body: {{ 'meetings': [{len(meetings)} items] }}\n")
        
        # Show sample meetings
        if meetings:
            print("Sample meetings:")
            for i, meeting in enumerate(meetings[:3], 1):
                print(f"  {i}. {meeting.get('title', 'Untitled')}")
                print(f"     Status: {meeting.get('status', 'Unknown')}")
                print(f"     Created: {meeting.get('createdAt', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print(f"   Lambda would return: 500 Internal Server Error")
        return False

def check_gsi_exists():
    """Check if the GSI exists on the meetings table"""
    print_section("CHECK: Does teamId-createdAt-index GSI exist?")
    
    dynamodb_client = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb_client.describe_table(TableName='meetingmind-meetings')
        
        gsis = response['Table'].get('GlobalSecondaryIndexes', [])
        
        print(f"✓ Table has {len(gsis)} GSI(s):\n")
        
        for gsi in gsis:
            print(f"  - {gsi['IndexName']}")
            print(f"    Status: {gsi['IndexStatus']}")
            print(f"    Keys: {[k['AttributeName'] for k in gsi['KeySchema']]}")
            print()
        
        # Check if our GSI exists
        target_gsi = next((g for g in gsis if g['IndexName'] == 'teamId-createdAt-index'), None)
        
        if target_gsi:
            if target_gsi['IndexStatus'] == 'ACTIVE':
                print(f"✓ teamId-createdAt-index exists and is ACTIVE")
                return True
            else:
                print(f"⚠️  teamId-createdAt-index exists but status is: {target_gsi['IndexStatus']}")
                return False
        else:
            print(f"❌ teamId-createdAt-index does NOT exist")
            print(f"   This is why the API call is failing!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  DIAGNOSE: Why is GET /meetings?teamId=... failing?")
    print("="*70)
    
    # Check 1: Does the GSI exist?
    gsi_exists = check_gsi_exists()
    
    if not gsi_exists:
        print_section("ROOT CAUSE")
        print("❌ The teamId-createdAt-index GSI is missing or not active")
        print()
        print("🔧 SOLUTION:")
        print("   1. Check backend/template.yaml for GSI definition")
        print("   2. Deploy backend: sam deploy --stack-name meetingmind-stack ...")
        print("   3. Wait for GSI to become ACTIVE (can take 5-10 minutes)")
        print("   4. Test again")
        print("\n" + "="*70 + "\n")
        return
    
    # Check 2: Simulate the API call
    api_works = simulate_list_meetings_api()
    
    # Summary
    print_section("DIAGNOSIS SUMMARY")
    
    if api_works:
        print("✅ API CALL SHOULD WORK")
        print("   - GSI exists and is active")
        print("   - Keldeo is a team member")
        print("   - Query returns meetings")
        print()
        print("🔍 If browser still shows error:")
        print("   1. Check browser console for actual error message")
        print("   2. Check Network tab for HTTP status code")
        print("   3. Try logging out and logging back in")
        print("   4. Clear browser cache and cookies")
        print("   5. Check CloudWatch logs for Lambda errors")
    else:
        print("❌ API CALL WILL FAIL")
        print("   - Check error messages above")
        print("   - Fix the issue and test again")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
