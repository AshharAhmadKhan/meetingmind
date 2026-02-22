#!/usr/bin/env python3
"""
Diagnose why Keldeo user cannot load V1 project meetings
"""
import boto3
import json

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
KELDEO_EMAIL = 'ashkagakoko@gmail.com'

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def get_keldeo_user_id():
    """Get Keldeo's Cognito userId"""
    print_section("Step 1: Get Keldeo's User ID")
    
    try:
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{KELDEO_EMAIL}"'
        )
        
        if not response['Users']:
            print(f"❌ User not found: {KELDEO_EMAIL}")
            return None
        
        user = response['Users'][0]
        user_id = user['Username']
        
        print(f"✓ Keldeo's userId: {user_id}")
        return user_id
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_all_teams():
    """List all teams in the system"""
    print_section("Step 2: List All Teams")
    
    try:
        teams_table = dynamodb.Table('meetingmind-teams')
        response = teams_table.scan()
        teams = response['Items']
        
        print(f"✓ Found {len(teams)} teams:\n")
        
        for team in teams:
            print(f"  Team: {team.get('name', 'Unnamed')}")
            print(f"    TeamId: {team['teamId']}")
            print(f"    Created: {team.get('createdAt', 'Unknown')}")
            print(f"    Members: {len(team.get('members', []))}")
            
            # Show member details
            members = team.get('members', [])
            if members:
                print(f"    Member List:")
                for member in members:
                    if isinstance(member, dict):
                        print(f"      - {member.get('email', 'Unknown')} (userId: {member.get('userId', 'Unknown')})")
                    else:
                        print(f"      - {member}")
            print()
        
        return teams
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def check_keldeo_memberships(user_id, teams):
    """Check which teams Keldeo is a member of"""
    print_section("Step 3: Check Keldeo's Team Memberships")
    
    keldeo_teams = []
    
    for team in teams:
        members = team.get('members', [])
        is_member = False
        
        for member in members:
            if isinstance(member, dict):
                if member.get('userId') == user_id or member.get('email') == KELDEO_EMAIL:
                    is_member = True
                    break
            else:
                if member == user_id or member == KELDEO_EMAIL:
                    is_member = True
                    break
        
        if is_member:
            keldeo_teams.append(team)
            print(f"✓ Member of: {team.get('name', 'Unnamed')} (teamId: {team['teamId']})")
    
    if not keldeo_teams:
        print(f"❌ Keldeo is not a member of any teams")
    
    return keldeo_teams

def check_v1_team_meetings(teams):
    """Check if V1 team exists and has meetings"""
    print_section("Step 4: Check V1 Team Meetings")
    
    v1_team = None
    for team in teams:
        if 'V1' in team.get('name', '') or 'Legacy' in team.get('name', ''):
            v1_team = team
            break
    
    if not v1_team:
        print("❌ V1/Legacy team not found")
        return
    
    print(f"✓ Found V1 team: {v1_team.get('name')}")
    print(f"  TeamId: {v1_team['teamId']}")
    
    # Check meetings for this team
    try:
        meetings_table = dynamodb.Table('meetingmind-meetings')
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': v1_team['teamId']}
        )
        
        meetings = response['Items']
        print(f"  Meetings: {len(meetings)}")
        
        if meetings:
            print(f"\n  Sample meetings:")
            for meeting in meetings[:3]:
                print(f"    - {meeting.get('title', 'Untitled')}")
                print(f"      MeetingId: {meeting['meetingId']}")
                print(f"      Status: {meeting.get('status', 'Unknown')}")
                print(f"      Created: {meeting.get('createdAt', 'Unknown')}")
        
        return v1_team, meetings
    except Exception as e:
        print(f"❌ Error querying meetings: {e}")
        return v1_team, []

def check_join_code(teams):
    """Check if V1 team has a valid join code"""
    print_section("Step 5: Check V1 Team Join Code")
    
    v1_team = None
    for team in teams:
        if 'V1' in team.get('name', '') or 'Legacy' in team.get('name', ''):
            v1_team = team
            break
    
    if not v1_team:
        print("❌ V1 team not found")
        return
    
    join_code = v1_team.get('joinCode')
    if join_code:
        print(f"✓ Join code exists: {join_code}")
        print(f"  Use this code to join V1 team")
    else:
        print(f"❌ No join code set for V1 team")
        print(f"  Team can only be joined by invitation")

def main():
    print("\n" + "="*70)
    print("  DIAGNOSE: Failed to Load Meeting (V1 Project)")
    print("="*70)
    
    # Step 1: Get Keldeo's userId
    user_id = get_keldeo_user_id()
    if not user_id:
        return
    
    # Step 2: List all teams
    teams = list_all_teams()
    if not teams:
        return
    
    # Step 3: Check Keldeo's memberships
    keldeo_teams = check_keldeo_memberships(user_id, teams)
    
    # Step 4: Check V1 team meetings
    v1_result = check_v1_team_meetings(teams)
    
    # Step 5: Check join code
    check_join_code(teams)
    
    # Summary
    print_section("DIAGNOSIS SUMMARY")
    
    if not keldeo_teams:
        print("❌ ROOT CAUSE: Keldeo is not a member of any teams")
        print("\n🔧 SOLUTION:")
        print("  1. Find V1 team join code (see above)")
        print("  2. Login as Keldeo")
        print("  3. Use join code to join V1 team")
        print("  4. Try loading meetings again")
    else:
        v1_in_keldeo_teams = any('V1' in t.get('name', '') or 'Legacy' in t.get('name', '') for t in keldeo_teams)
        
        if v1_in_keldeo_teams:
            print("✓ Keldeo IS a member of V1 team")
            print("\n🔍 POSSIBLE CAUSES:")
            print("  1. Frontend not sending teamId in API request")
            print("  2. API Gateway authorization issue")
            print("  3. Lambda function error")
            print("  4. CloudFront caching old response")
            print("\n🔧 NEXT STEPS:")
            print("  1. Check browser console for errors")
            print("  2. Check Network tab for API request")
            print("  3. Check CloudWatch logs for Lambda errors")
            print("  4. Try clearing browser cache and cookies")
        else:
            print("❌ Keldeo is NOT a member of V1 team")
            print(f"   Member of: {', '.join([t.get('name', 'Unnamed') for t in keldeo_teams])}")
            print("\n🔧 SOLUTION:")
            print("  1. Use V1 team join code to join")
            print("  2. OR manually add Keldeo to V1 team in DynamoDB")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
