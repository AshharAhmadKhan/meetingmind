#!/usr/bin/env python3
"""Check all user accounts and their team memberships"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
teams_table = dynamodb.Table('meetingmind-teams')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("=" * 100)
print("ALL ACCOUNTS AND TEAM MEMBERSHIPS")
print("=" * 100)
print()

# Get all teams
response = teams_table.scan()
teams = response['Items']

print(f"Total teams: {len(teams)}")
print()

# Known accounts
accounts = {
    'thecyberprinciples@gmail.com': 'c1c38d2a-1081-7088-7c71-0abc19a150e9',
    'whispersbehindthecode@gmail.com': 'f1d33d1a-9041-7006-5af8-d18269b15a92',
    'thehiddenif@gmail.com': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'
}

for team in teams:
    print(f"Team: {team['teamName']}")
    print(f"Team ID: {team['teamId']}")
    print(f"Members ({len(team.get('members', []))}):")
    print()
    
    members = team.get('members', [])
    for member in members:
        if isinstance(member, dict):
            user_id = member.get('userId')
            email = member.get('email', 'Unknown')
            role = member.get('role', 'member')
            
            # Find account name
            account_name = email
            
            print(f"  {role.upper():8} | {email:40} | {user_id}")
        else:
            print(f"  MEMBER  | {member}")
    
    print()
    
    # Check meetings for this team
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team['teamId']}
    )
    
    team_meetings = response['Items']
    print(f"  Meetings: {len(team_meetings)}")
    for m in team_meetings:
        print(f"    - {m.get('title', 'Untitled')}")
    
    print()
    print("-" * 100)
    print()

print("=" * 100)
print("ACCOUNT VERIFICATION")
print("=" * 100)
print()

for email, user_id in accounts.items():
    print(f"Account: {email}")
    print(f"User ID: {user_id}")
    
    # Check which teams this user is in
    user_teams = []
    for team in teams:
        members = team.get('members', [])
        for member in members:
            if isinstance(member, dict):
                if member.get('userId') == user_id:
                    user_teams.append(team['teamName'])
            elif member == user_id:
                user_teams.append(team['teamName'])
    
    print(f"Teams: {', '.join(user_teams) if user_teams else 'NONE'}")
    
    # Check meetings uploaded by this user
    response = meetings_table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id}
    )
    
    user_meetings = response['Items']
    print(f"Meetings uploaded: {len(user_meetings)}")
    
    print()

print("=" * 100)
print("ISSUE DIAGNOSIS")
print("=" * 100)
print()

print("If other accounts see 0 meetings:")
print("1. Check if they're members of the teams (should be)")
print("2. Check if meetings have teamId (should have)")
print("3. Check if GSI query works (should work)")
print("4. Check browser console for 403 errors")
print("5. Check Network tab for API requests")
