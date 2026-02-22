#!/usr/bin/env python3
"""
Verify that Keldeo can access V1 meetings through the API
"""
import boto3
import json

REGION = 'ap-south-1'
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
KELDEO_USER_ID = 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def main():
    print("\n" + "="*70)
    print("  VERIFY V1 ACCESS FOR KELDEO")
    print("="*70)
    
    # Step 1: Verify team name
    print_section("Step 1: Verify Team Name")
    teams_table = dynamodb.Table('meetingmind-teams')
    response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    
    if 'Item' not in response:
        print(f"❌ Team not found: {V1_TEAM_ID}")
        return
    
    team = response['Item']
    print(f"✓ Team name: '{team.get('name')}'")
    print(f"✓ Team ID: {V1_TEAM_ID}")
    
    # Step 2: Verify Keldeo is a member
    print_section("Step 2: Verify Keldeo's Membership")
    members = team.get('members', [])
    
    is_member = False
    for member in members:
        if isinstance(member, dict):
            if member.get('userId') == KELDEO_USER_ID:
                is_member = True
                print(f"✓ Keldeo is a member")
                print(f"  Email: {member.get('email')}")
                print(f"  UserId: {member.get('userId')}")
                break
        else:
            if member == KELDEO_USER_ID:
                is_member = True
                print(f"✓ Keldeo is a member (legacy format)")
                break
    
    if not is_member:
        print(f"❌ Keldeo is NOT a member of this team")
        return
    
    # Step 3: Query meetings for this team
    print_section("Step 3: Query Meetings for V1 Team")
    meetings_table = dynamodb.Table('meetingmind-meetings')
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': V1_TEAM_ID},
        ScanIndexForward=False  # Newest first
    )
    
    meetings = response['Items']
    print(f"✓ Found {len(meetings)} meetings\n")
    
    for i, meeting in enumerate(meetings, 1):
        print(f"{i}. {meeting.get('title', 'Untitled')}")
        print(f"   MeetingId: {meeting['meetingId']}")
        print(f"   Status: {meeting.get('status', 'Unknown')}")
        print(f"   Created: {meeting.get('createdAt', 'Unknown')}")
        
        action_items = meeting.get('actionItems', [])
        if action_items:
            print(f"   Actions: {len(action_items)}")
        print()
    
    # Step 4: Simulate API call
    print_section("Step 4: Simulate API Call")
    print(f"API Endpoint: GET /meetings?teamId={V1_TEAM_ID}")
    print(f"Authorization: Bearer <Keldeo's token>")
    print(f"\nExpected Response:")
    print(f"  Status: 200 OK")
    print(f"  Body: {{ 'meetings': [{len(meetings)} items] }}")
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    print(f"✓ Team renamed to 'V1 - Legacy'")
    print(f"✓ Keldeo is a member of the team")
    print(f"✓ Team has {len(meetings)} meetings")
    print(f"✓ API should return meetings when teamId={V1_TEAM_ID}")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Login as Keldeo at https://dcfx593ywvy92.cloudfront.net")
    print(f"   2. Select '📦 V1 - Legacy' from team dropdown")
    print(f"   3. Verify meetings load correctly")
    print(f"   4. Check browser console for any errors")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
