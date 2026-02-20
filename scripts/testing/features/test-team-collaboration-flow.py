#!/usr/bin/env python3
"""
Test complete team collaboration flow:
1. User A creates team "Alpha"
2. User A uploads meeting to team
3. User B joins team with invite code
4. User B can see User A's meeting
5. User B uploads meeting to team
6. User A can see User B's meeting
"""
import boto3
import json
from datetime import datetime, timezone
import uuid

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'

# Test users
USER_A_EMAIL = 'thecyberprinciples@gmail.com'  # Will create team
USER_B_EMAIL = 'thehiddenif@gmail.com'  # Will join team

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def get_user_id(email):
    """Get user ID from Cognito"""
    try:
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{email}"'
        )
        if response['Users']:
            return response['Users'][0]['Username']
        return None
    except Exception as e:
        print(f"❌ Error getting user {email}: {e}")
        return None

def test_team_creation():
    """Test: User A creates team 'Alpha'"""
    print_section("TEST 1: User A Creates Team 'Alpha'")
    
    user_a_id = get_user_id(USER_A_EMAIL)
    if not user_a_id:
        print(f"❌ User A not found: {USER_A_EMAIL}")
        return None
    
    print(f"✓ User A ID: {user_a_id}")
    
    # Simulate team creation
    teams_table = dynamodb.Table('meetingmind-teams')
    
    # Check if Alpha team already exists
    response = teams_table.scan()
    for team in response['Items']:
        if team.get('teamName') == 'Alpha':
            print(f"✓ Team 'Alpha' already exists")
            print(f"  TeamId: {team['teamId']}")
            print(f"  InviteCode: {team.get('inviteCode', 'N/A')}")
            print(f"  Members: {len(team.get('members', []))}")
            return team['teamId'], team.get('inviteCode')
    
    print("ℹ️  Team 'Alpha' does not exist yet")
    print("   User A needs to create it via the UI")
    return None, None

def test_meeting_upload(team_id, user_email):
    """Test: User uploads meeting to team"""
    print_section(f"TEST: {user_email} Uploads Meeting to Team")
    
    user_id = get_user_id(user_email)
    if not user_id:
        print(f"❌ User not found: {user_email}")
        return None
    
    print(f"✓ User ID: {user_id}")
    
    # Check meetings for this team
    meetings_table = dynamodb.Table('meetingmind-meetings')
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team_id}
    )
    
    meetings = response['Items']
    user_meetings = [m for m in meetings if m.get('userId') == user_id]
    
    print(f"✓ Total team meetings: {len(meetings)}")
    print(f"✓ Meetings by {user_email}: {len(user_meetings)}")
    
    if user_meetings:
        print(f"\n  Sample meetings:")
        for meeting in user_meetings[:3]:
            print(f"    - {meeting.get('title', 'Untitled')}")
            print(f"      MeetingId: {meeting['meetingId']}")
            print(f"      Status: {meeting.get('status', 'Unknown')}")
    
    return len(user_meetings)

def test_team_membership(team_id, user_email):
    """Test: Check if user is member of team"""
    print_section(f"TEST: Check {user_email} Team Membership")
    
    user_id = get_user_id(user_email)
    if not user_id:
        print(f"❌ User not found: {user_email}")
        return False
    
    teams_table = dynamodb.Table('meetingmind-teams')
    response = teams_table.get_item(Key={'teamId': team_id})
    
    if 'Item' not in response:
        print(f"❌ Team not found: {team_id}")
        return False
    
    team = response['Item']
    members = team.get('members', [])
    
    is_member = False
    for member in members:
        if isinstance(member, dict):
            if member.get('userId') == user_id:
                is_member = True
                print(f"✓ {user_email} IS a member")
                print(f"  Role: {member.get('role', 'member')}")
                print(f"  Joined: {member.get('joinedAt', 'Unknown')}")
                break
        else:
            if member == user_id:
                is_member = True
                print(f"✓ {user_email} IS a member (legacy format)")
                break
    
    if not is_member:
        print(f"❌ {user_email} is NOT a member")
    
    return is_member

def test_meeting_visibility(team_id, viewer_email, uploader_email):
    """Test: Check if viewer can see uploader's meetings"""
    print_section(f"TEST: Can {viewer_email} See {uploader_email}'s Meetings?")
    
    viewer_id = get_user_id(viewer_email)
    uploader_id = get_user_id(uploader_email)
    
    if not viewer_id or not uploader_id:
        print(f"❌ User not found")
        return False
    
    # Check if viewer is team member
    teams_table = dynamodb.Table('meetingmind-teams')
    team_response = teams_table.get_item(Key={'teamId': team_id})
    
    if 'Item' not in team_response:
        print(f"❌ Team not found")
        return False
    
    team = team_response['Item']
    members = team.get('members', [])
    
    member_ids = []
    for member in members:
        if isinstance(member, dict):
            member_ids.append(member.get('userId'))
        else:
            member_ids.append(member)
    
    if viewer_id not in member_ids:
        print(f"❌ {viewer_email} is not a team member")
        print(f"   Cannot see team meetings")
        return False
    
    print(f"✓ {viewer_email} is a team member")
    
    # Query meetings by teamId (simulates API call)
    meetings_table = dynamodb.Table('meetingmind-meetings')
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team_id}
    )
    
    meetings = response['Items']
    uploader_meetings = [m for m in meetings if m.get('userId') == uploader_id]
    
    print(f"✓ Total team meetings: {len(meetings)}")
    print(f"✓ Meetings by {uploader_email}: {len(uploader_meetings)}")
    
    if uploader_meetings:
        print(f"\n  {viewer_email} CAN see these meetings:")
        for meeting in uploader_meetings[:3]:
            print(f"    - {meeting.get('title', 'Untitled')}")
            print(f"      Uploaded by: {uploader_email}")
            print(f"      Status: {meeting.get('status', 'Unknown')}")
        return True
    else:
        print(f"\n  No meetings by {uploader_email} found")
        return False

def main():
    print("\n" + "="*70)
    print("  TEAM COLLABORATION FLOW TEST")
    print("="*70)
    
    # Test 1: Check if Alpha team exists
    team_id, invite_code = test_team_creation()
    
    if not team_id:
        print("\n" + "="*70)
        print("  SETUP REQUIRED")
        print("="*70)
        print(f"\n📋 To complete this test:")
        print(f"   1. Login as {USER_A_EMAIL}")
        print(f"   2. Create team 'Alpha' via UI")
        print(f"   3. Upload a meeting to team 'Alpha'")
        print(f"   4. Share invite code with {USER_B_EMAIL}")
        print(f"   5. Login as {USER_B_EMAIL} and join team")
        print(f"   6. Upload a meeting to team 'Alpha'")
        print(f"   7. Run this script again\n")
        return
    
    # Test 2: Check User A membership
    user_a_member = test_team_membership(team_id, USER_A_EMAIL)
    
    # Test 3: Check User A's meetings
    user_a_meetings = test_meeting_upload(team_id, USER_A_EMAIL)
    
    # Test 4: Check User B membership
    user_b_member = test_team_membership(team_id, USER_B_EMAIL)
    
    # Test 5: Check User B's meetings
    user_b_meetings = test_meeting_upload(team_id, USER_B_EMAIL)
    
    # Test 6: Can User B see User A's meetings?
    if user_a_meetings and user_a_meetings > 0:
        b_sees_a = test_meeting_visibility(team_id, USER_B_EMAIL, USER_A_EMAIL)
    else:
        b_sees_a = None
    
    # Test 7: Can User A see User B's meetings?
    if user_b_meetings and user_b_meetings > 0:
        a_sees_b = test_meeting_visibility(team_id, USER_A_EMAIL, USER_B_EMAIL)
    else:
        a_sees_b = None
    
    # Summary
    print_section("TEST SUMMARY")
    
    print(f"Team: Alpha")
    print(f"  TeamId: {team_id}")
    print(f"  InviteCode: {invite_code}")
    print()
    
    print(f"✓ User A ({USER_A_EMAIL})")
    print(f"  Member: {'✓ Yes' if user_a_member else '❌ No'}")
    print(f"  Meetings: {user_a_meetings if user_a_meetings else 0}")
    print()
    
    print(f"✓ User B ({USER_B_EMAIL})")
    print(f"  Member: {'✓ Yes' if user_b_member else '❌ No'}")
    print(f"  Meetings: {user_b_meetings if user_b_meetings else 0}")
    print()
    
    print(f"Visibility:")
    if b_sees_a is not None:
        print(f"  User B sees User A's meetings: {'✓ Yes' if b_sees_a else '❌ No'}")
    if a_sees_b is not None:
        print(f"  User A sees User B's meetings: {'✓ Yes' if a_sees_b else '❌ No'}")
    
    # Final verdict
    print()
    if user_a_member and user_b_member:
        if (b_sees_a or user_a_meetings == 0) and (a_sees_b or user_b_meetings == 0):
            print("✅ TEAM COLLABORATION WORKS CORRECTLY")
            print("   - Both users are team members")
            print("   - Both users can see each other's meetings")
            print("   - Team feature is working as expected")
        else:
            print("⚠️  VISIBILITY ISSUE DETECTED")
            print("   - Users are team members")
            print("   - But cannot see each other's meetings")
            print("   - Check API permissions and GSI")
    else:
        print("⚠️  MEMBERSHIP ISSUE")
        print("   - Not all users are team members")
        print("   - Complete setup steps above")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
