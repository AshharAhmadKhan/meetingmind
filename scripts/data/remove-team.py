#!/usr/bin/env python3
"""
Remove a specific team from MeetingMind
Usage: python scripts/data/remove-team.py [team_id or team_name]
"""

import boto3
import sys

REGION = 'ap-south-1'
TEAMS_TABLE = 'meetingmind-teams'
MEETINGS_TABLE = 'meetingmind-meetings'

def list_all_teams():
    """List all teams in the system"""
    print("\n👥 All Teams in System")
    print("=" * 80)
    
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb.scan(TableName=TEAMS_TABLE)
        items = response.get('Items', [])
        
        if not items:
            print("No teams found")
            return []
        
        teams = []
        for idx, item in enumerate(items, 1):
            team_id = item['teamId']['S']
            team_name = item.get('teamName', {}).get('S', 'Unknown')
            invite_code = item.get('inviteCode', {}).get('S', 'N/A')
            created_by = item.get('createdBy', {}).get('S', 'Unknown')
            members = item.get('members', {}).get('L', [])
            member_count = len(members)
            
            teams.append({
                'teamId': team_id,
                'teamName': team_name,
                'inviteCode': invite_code,
                'createdBy': created_by,
                'memberCount': member_count
            })
            
            print(f"{idx}. {team_name}")
            print(f"   Team ID: {team_id}")
            print(f"   Invite Code: {invite_code}")
            print(f"   Created By: {created_by}")
            print(f"   Members: {member_count}")
            print()
        
        return teams
        
    except Exception as e:
        print(f"❌ Error listing teams: {e}")
        return []

def find_team(search_term):
    """Find a team by ID, name, or invite code"""
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb.scan(TableName=TEAMS_TABLE)
        items = response.get('Items', [])
        
        for item in items:
            team_id = item['teamId']['S']
            team_name = item.get('teamName', {}).get('S', '').lower()
            invite_code = item.get('inviteCode', {}).get('S', '').lower()
            
            search_lower = search_term.lower()
            
            if (team_id == search_term or 
                search_lower in team_name or 
                invite_code == search_lower):
                return item
        
        return None
        
    except Exception as e:
        print(f"❌ Error finding team: {e}")
        return None

def get_team_meetings(team_id):
    """Get all meetings associated with a team"""
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        # Scan meetings table for meetings with this teamId
        response = dynamodb.scan(
            TableName=MEETINGS_TABLE,
            FilterExpression='teamId = :tid',
            ExpressionAttributeValues={
                ':tid': {'S': team_id}
            }
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"⚠️  Error getting team meetings: {e}")
        return []

def remove_team_from_meetings(team_id):
    """Remove teamId from all meetings associated with this team"""
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    meetings = get_team_meetings(team_id)
    
    if not meetings:
        print("  No meetings associated with this team")
        return 0
    
    print(f"  Found {len(meetings)} meetings to update...")
    
    updated = 0
    for meeting in meetings:
        user_id = meeting['userId']['S']
        meeting_id = meeting['meetingId']['S']
        title = meeting.get('title', {}).get('S', 'Unknown')
        
        try:
            # Remove teamId attribute from meeting
            dynamodb.update_item(
                TableName=MEETINGS_TABLE,
                Key={
                    'userId': {'S': user_id},
                    'meetingId': {'S': meeting_id}
                },
                UpdateExpression='REMOVE teamId'
            )
            updated += 1
            print(f"    ✓ Updated: {title}")
        except Exception as e:
            print(f"    ✗ Error updating {meeting_id}: {e}")
    
    print(f"  ✅ Updated {updated}/{len(meetings)} meetings")
    return updated

def delete_team(team_id):
    """Delete a team from DynamoDB"""
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        dynamodb.delete_item(
            TableName=TEAMS_TABLE,
            Key={'teamId': {'S': team_id}}
        )
        return True
    except Exception as e:
        print(f"❌ Error deleting team: {e}")
        return False

def remove_team_interactive(search_term=None):
    """Interactive team removal"""
    print("=" * 80)
    print("MeetingMind Team Removal Tool")
    print("=" * 80)
    
    # List all teams
    teams = list_all_teams()
    
    if not teams:
        print("\n❌ No teams found in the system")
        return
    
    # Get search term if not provided
    if not search_term:
        print("\nEnter team ID, name, or invite code to remove:")
        search_term = input("> ").strip()
    
    if not search_term:
        print("❌ No search term provided")
        return
    
    # Find the team
    print(f"\n🔍 Searching for team: {search_term}")
    team = find_team(search_term)
    
    if not team:
        print(f"❌ Team not found: {search_term}")
        print("\nAvailable teams:")
        for t in teams:
            print(f"  - {t['teamName']} (ID: {t['teamId']}, Code: {t['inviteCode']})")
        return
    
    # Display team details
    team_id = team['teamId']['S']
    team_name = team.get('teamName', {}).get('S', 'Unknown')
    invite_code = team.get('inviteCode', {}).get('S', 'N/A')
    created_by = team.get('createdBy', {}).get('S', 'Unknown')
    members = team.get('members', {}).get('L', [])
    
    print("\n✅ Found team:")
    print("=" * 80)
    print(f"Team Name: {team_name}")
    print(f"Team ID: {team_id}")
    print(f"Invite Code: {invite_code}")
    print(f"Created By: {created_by}")
    print(f"Members: {len(members)}")
    
    # Show members
    if members:
        print("\nMembers:")
        for member in members:
            member_data = member.get('M', {})
            user_id = member_data.get('userId', {}).get('S', 'Unknown')
            role = member_data.get('role', {}).get('S', 'member')
            print(f"  - {user_id} ({role})")
    
    # Check for associated meetings
    meetings = get_team_meetings(team_id)
    if meetings:
        print(f"\n⚠️  This team has {len(meetings)} associated meetings")
        print("   These meetings will be unlinked from the team (but not deleted)")
    
    # Confirm deletion
    print("\n⚠️  WARNING: This will permanently delete this team!")
    print("   - Team will be removed from DynamoDB")
    print("   - Meetings will be unlinked (but not deleted)")
    print("   - Members will lose access to team features")
    
    confirm = input(f"\nType '{team_name}' to confirm deletion: ")
    
    if confirm != team_name:
        print("\n❌ Cancelled. Team was not deleted.")
        return
    
    # Perform deletion
    print(f"\n🗑️  Removing team: {team_name}")
    print("=" * 80)
    
    # Step 1: Remove team from meetings
    print("\n1️⃣  Unlinking meetings from team...")
    meetings_updated = remove_team_from_meetings(team_id)
    
    # Step 2: Delete team
    print("\n2️⃣  Deleting team from database...")
    if delete_team(team_id):
        print(f"  ✅ Team deleted successfully")
    else:
        print(f"  ❌ Failed to delete team")
        return
    
    # Summary
    print("\n" + "=" * 80)
    print("TEAM REMOVAL COMPLETE")
    print("=" * 80)
    print(f"Team: {team_name}")
    print(f"Meetings unlinked: {meetings_updated}")
    print("\n✨ Team has been successfully removed!")
    print("=" * 80)

if __name__ == '__main__':
    # Check for command line argument
    if len(sys.argv) > 1:
        search_term = ' '.join(sys.argv[1:])
        remove_team_interactive(search_term)
    else:
        remove_team_interactive()
