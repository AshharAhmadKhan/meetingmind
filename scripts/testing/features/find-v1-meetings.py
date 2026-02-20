#!/usr/bin/env python3
"""
Find which team has the V1 historical meetings
"""
import boto3
import json
from datetime import datetime

REGION = 'ap-south-1'

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_team_meetings(team_id, team_name):
    """Check meetings for a specific team"""
    try:
        meetings_table = dynamodb.Table('meetingmind-meetings')
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': team_id}
        )
        
        meetings = response['Items']
        
        if meetings:
            print(f"✓ Team '{team_name}' (ID: {team_id})")
            print(f"  Found {len(meetings)} meetings\n")
            
            # Show first 5 meetings
            for i, meeting in enumerate(meetings[:5]):
                print(f"  {i+1}. {meeting.get('title', 'Untitled')}")
                print(f"     MeetingId: {meeting['meetingId']}")
                print(f"     Status: {meeting.get('status', 'Unknown')}")
                print(f"     Created: {meeting.get('createdAt', 'Unknown')}")
                
                # Check if it has action items
                action_items = meeting.get('actionItems', [])
                if action_items:
                    print(f"     Actions: {len(action_items)}")
                print()
            
            if len(meetings) > 5:
                print(f"  ... and {len(meetings) - 5} more meetings\n")
            
            return len(meetings)
        else:
            print(f"✗ Team '{team_name}' (ID: {team_id})")
            print(f"  No meetings found\n")
            return 0
            
    except Exception as e:
        print(f"❌ Error querying team {team_id}: {e}\n")
        return 0

def main():
    print("\n" + "="*70)
    print("  FIND V1 MEETINGS: Which team has the historical data?")
    print("="*70)
    
    # Get all teams
    print_section("Step 1: Get All Teams")
    teams_table = dynamodb.Table('meetingmind-teams')
    response = teams_table.scan()
    teams = response['Items']
    
    print(f"✓ Found {len(teams)} teams\n")
    
    # Check meetings for each team
    print_section("Step 2: Check Meetings for Each Team")
    
    team_meeting_counts = []
    
    for team in teams:
        team_id = team['teamId']
        team_name = team.get('name', 'Unnamed')
        count = check_team_meetings(team_id, team_name)
        team_meeting_counts.append((team_name, team_id, count))
    
    # Summary
    print_section("SUMMARY")
    
    total_meetings = sum(count for _, _, count in team_meeting_counts)
    print(f"Total meetings across all teams: {total_meetings}\n")
    
    for name, tid, count in sorted(team_meeting_counts, key=lambda x: x[2], reverse=True):
        if count > 0:
            print(f"  {name}: {count} meetings")
            print(f"    TeamId: {tid}\n")
    
    # Find the team with most meetings (likely V1)
    if team_meeting_counts:
        max_team = max(team_meeting_counts, key=lambda x: x[2])
        if max_team[2] > 0:
            print(f"\n🎯 LIKELY V1 TEAM:")
            print(f"   Name: {max_team[0]}")
            print(f"   TeamId: {max_team[1]}")
            print(f"   Meetings: {max_team[2]}")
            
            # Check if Keldeo is a member
            print(f"\n🔍 Checking Keldeo's membership...")
            teams_table = dynamodb.Table('meetingmind-teams')
            team_response = teams_table.get_item(Key={'teamId': max_team[1]})
            
            if 'Item' in team_response:
                team = team_response['Item']
                members = team.get('members', [])
                
                keldeo_email = 'ashkagakoko@gmail.com'
                keldeo_user_id = 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'
                
                is_member = False
                for member in members:
                    if isinstance(member, dict):
                        if member.get('userId') == keldeo_user_id or member.get('email') == keldeo_email:
                            is_member = True
                            break
                    else:
                        if member == keldeo_user_id or member == keldeo_email:
                            is_member = True
                            break
                
                if is_member:
                    print(f"   ✓ Keldeo IS a member of this team")
                    print(f"\n💡 DIAGNOSIS:")
                    print(f"   - Keldeo is already in the team with meetings")
                    print(f"   - Issue is likely frontend/API related")
                    print(f"   - Check browser console for errors")
                    print(f"   - Check Network tab for API failures")
                else:
                    print(f"   ✗ Keldeo is NOT a member of this team")
                    print(f"\n🔧 SOLUTION:")
                    print(f"   1. Add Keldeo to team {max_team[1]}")
                    print(f"   2. OR rename team {max_team[1]} to 'V1' and give Keldeo the join code")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
