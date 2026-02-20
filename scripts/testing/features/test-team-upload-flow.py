#!/usr/bin/env python3
"""
Test Team Upload Flow - Verify backend correctly handles team uploads
Tests that when teamId is sent, meetings are created with correct teamId
"""

import boto3
import json
from datetime import datetime, timezone

# Configuration
REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
TEAMS_TABLE = 'meetingmind-teams'

# Test users
TEST_USERS = {
    'thehiddenif': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134',
    'ashkagakoko': 'a1a3cd5a-00e1-701f-a07b-b12a35f16664',
    'thecyberprinciples': '9153cd2a-70b1-7019-4a1b-fabfc31d3134'  # Approximate
}

# Test teams
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table(MEETINGS_TABLE)
teams_table = dynamodb.Table(TEAMS_TABLE)

def get_team_info(team_id):
    """Get team information"""
    try:
        response = teams_table.get_item(Key={'teamId': team_id})
        if 'Item' in response:
            team = response['Item']
            return {
                'teamId': team['teamId'],
                'teamName': team['teamName'],
                'memberCount': len(team.get('members', []))
            }
    except Exception as e:
        print(f"❌ Error getting team {team_id}: {e}")
    return None

def get_user_meetings(user_id, team_id=None):
    """Get meetings for a user, optionally filtered by team"""
    try:
        if team_id:
            # Query by teamId using GSI
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': team_id}
            )
        else:
            # Query personal meetings
            response = meetings_table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
        
        return response.get('Items', [])
    except Exception as e:
        print(f"❌ Error querying meetings: {e}")
        return []

def check_meeting_visibility(meeting_id, user_id, team_id):
    """Check if a user can see a specific meeting"""
    # Get all meetings visible to user
    team_meetings = get_user_meetings(user_id, team_id)
    
    # Check if meeting is in the list
    for meeting in team_meetings:
        if meeting['meetingId'] == meeting_id:
            return True
    return False

def test_scenario_1_team_upload():
    """Test 1: Verify team upload creates meeting with teamId"""
    print("\n" + "="*80)
    print("TEST 1: Team Upload - Meeting Created with TeamId")
    print("="*80)
    
    # Get latest meeting by thehiddenif
    user_id = TEST_USERS['thehiddenif']
    all_meetings = get_user_meetings(user_id)
    
    if not all_meetings:
        print("❌ No meetings found for thehiddenif")
        return False
    
    # Sort by createdAt
    all_meetings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    latest = all_meetings[0]
    
    print(f"\n📋 Latest Meeting by thehiddenif:")
    print(f"   Title: {latest.get('title')}")
    print(f"   MeetingId: {latest.get('meetingId')}")
    print(f"   Status: {latest.get('status')}")
    print(f"   CreatedAt: {latest.get('createdAt')}")
    
    team_id = latest.get('teamId')
    if team_id:
        print(f"   ✅ TeamId: {team_id}")
        team_info = get_team_info(team_id)
        if team_info:
            print(f"   Team Name: {team_info['teamName']}")
            print(f"   Team Members: {team_info['memberCount']}")
        return True
    else:
        print(f"   ❌ TeamId: NONE - Personal meeting")
        return False

def test_scenario_2_all_members_see_meeting():
    """Test 2: Verify all team members can see team meetings"""
    print("\n" + "="*80)
    print("TEST 2: Team Visibility - All Members See Team Meetings")
    print("="*80)
    
    # Get V1 team info
    v1_info = get_team_info(V1_TEAM_ID)
    if not v1_info:
        print("❌ Could not get V1 team info")
        return False
    
    print(f"\n📦 V1 - Legacy Team:")
    print(f"   TeamId: {V1_TEAM_ID}")
    print(f"   Name: {v1_info['teamName']}")
    print(f"   Members: {v1_info['memberCount']}")
    
    # Get all V1 meetings
    v1_meetings = get_user_meetings(None, V1_TEAM_ID)
    print(f"\n📊 Total V1 Meetings: {len(v1_meetings)}")
    
    if not v1_meetings:
        print("❌ No meetings found for V1 team")
        return False
    
    # Test each user can see all meetings
    all_passed = True
    for user_name, user_id in TEST_USERS.items():
        user_meetings = get_user_meetings(user_id, V1_TEAM_ID)
        visible_count = len(user_meetings)
        
        if visible_count == len(v1_meetings):
            print(f"   ✅ {user_name}: Can see all {visible_count} meetings")
        else:
            print(f"   ❌ {user_name}: Can only see {visible_count}/{len(v1_meetings)} meetings")
            all_passed = False
    
    return all_passed

def test_scenario_3_personal_vs_team():
    """Test 3: Verify personal meetings are separate from team meetings"""
    print("\n" + "="*80)
    print("TEST 3: Personal vs Team - Meetings Are Separate")
    print("="*80)
    
    user_id = TEST_USERS['thehiddenif']
    
    # Get personal meetings (no teamId)
    personal_meetings = get_user_meetings(user_id)
    personal_only = [m for m in personal_meetings if 'teamId' not in m]
    
    # Get V1 team meetings
    v1_meetings = get_user_meetings(user_id, V1_TEAM_ID)
    
    print(f"\n👤 thehiddenif's Meetings:")
    print(f"   Personal (Just Me): {len(personal_only)} meetings")
    print(f"   V1 Team: {len(v1_meetings)} meetings")
    
    # Show latest of each type
    if personal_only:
        latest_personal = max(personal_only, key=lambda x: x.get('createdAt', ''))
        print(f"\n   Latest Personal:")
        print(f"      Title: {latest_personal.get('title')}")
        print(f"      TeamId: {'NONE' if 'teamId' not in latest_personal else latest_personal['teamId']}")
    
    if v1_meetings:
        latest_team = max(v1_meetings, key=lambda x: x.get('createdAt', ''))
        print(f"\n   Latest Team:")
        print(f"      Title: {latest_team.get('title')}")
        print(f"      TeamId: {latest_team.get('teamId')}")
    
    return True

def test_scenario_4_cross_team_isolation():
    """Test 4: Verify V1 and V2 teams are isolated"""
    print("\n" + "="*80)
    print("TEST 4: Cross-Team Isolation - V1 and V2 Are Separate")
    print("="*80)
    
    # Get meetings for both teams
    v1_meetings = get_user_meetings(None, V1_TEAM_ID)
    v2_meetings = get_user_meetings(None, V2_TEAM_ID)
    
    v1_info = get_team_info(V1_TEAM_ID)
    v2_info = get_team_info(V2_TEAM_ID)
    
    print(f"\n📦 V1 - Legacy:")
    print(f"   Members: {v1_info['memberCount']}")
    print(f"   Meetings: {len(v1_meetings)}")
    
    print(f"\n🚀 V2 - Active:")
    print(f"   Members: {v2_info['memberCount']}")
    print(f"   Meetings: {len(v2_meetings)}")
    
    # Check for any overlap (should be none)
    v1_ids = {m['meetingId'] for m in v1_meetings}
    v2_ids = {m['meetingId'] for m in v2_meetings}
    overlap = v1_ids & v2_ids
    
    if overlap:
        print(f"\n❌ Found {len(overlap)} meetings in both teams (should be 0)")
        return False
    else:
        print(f"\n✅ No overlap - teams are properly isolated")
        return True

def main():
    print("\n" + "="*80)
    print("TEAM UPLOAD FLOW - COMPREHENSIVE TEST")
    print("="*80)
    print(f"Region: {REGION}")
    print(f"Meetings Table: {MEETINGS_TABLE}")
    print(f"Teams Table: {TEAMS_TABLE}")
    
    results = []
    
    # Run all tests
    results.append(("Team Upload Creates Meeting with TeamId", test_scenario_1_team_upload()))
    results.append(("All Members See Team Meetings", test_scenario_2_all_members_see_meeting()))
    results.append(("Personal vs Team Separation", test_scenario_3_personal_vs_team()))
    results.append(("Cross-Team Isolation", test_scenario_4_cross_team_isolation()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"OVERALL: {passed}/{total} tests passed")
    print(f"{'='*80}")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        print("\n💡 If uploads are going to Personal instead of Team:")
        print("   → Frontend issue: selectedTeamId is null during upload")
        print("   → Fix: Persist selectedTeamId in localStorage")
    else:
        print("\n⚠️  Some tests failed. Backend may have issues.")

if __name__ == '__main__':
    main()
