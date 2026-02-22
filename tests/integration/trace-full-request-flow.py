#!/usr/bin/env python3
"""
Trace the complete request flow from frontend to backend
Check every step where userId and teamId are used
"""

import boto3
import json

print("=" * 100)
print("COMPLETE REQUEST FLOW ANALYSIS")
print("=" * 100)
print()

# Step 1: Check what user is logged in
print("STEP 1: USER AUTHENTICATION")
print("-" * 100)
print("The logged-in user is: thecyberprinciples@gmail.com")
print("User ID: c1c38d2a-1081-7088-7c71-0abc19a150e9")
print()

# Step 2: Check teams this user is member of
print("STEP 2: USER'S TEAMS")
print("-" * 100)
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
teams_table = dynamodb.Table('meetingmind-teams')

response = teams_table.scan()
teams = response['Items']

user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
user_teams = []

for team in teams:
    members = team.get('members', [])
    for member in members:
        if isinstance(member, dict):
            if member.get('userId') == user_id:
                user_teams.append({
                    'teamId': team['teamId'],
                    'teamName': team['teamName'],
                    'role': member.get('role')
                })
        elif member == user_id:
            user_teams.append({
                'teamId': team['teamId'],
                'teamName': team['teamName'],
                'role': 'member'
            })

print(f"User is member of {len(user_teams)} teams:")
for team in user_teams:
    print(f"  - {team['teamName']} ({team['teamId'][:20]}...) as {team['role']}")
print()

# Step 3: Check meetings in database
print("STEP 3: MEETINGS IN DATABASE")
print("-" * 100)
meetings_table = dynamodb.Table('meetingmind-meetings')

# Query by userId
response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)
user_meetings = response['Items']

print(f"Meetings uploaded by this user: {len(user_meetings)}")
for m in user_meetings:
    print(f"  - {m.get('title', 'Untitled')[:40]:40} | teamId: {m.get('teamId', 'NONE')[:30]:30} | createdAt: {str(m.get('createdAt', 'NONE'))[:20]}")
print()

# Step 4: Test GSI queries for each team
print("STEP 4: GSI QUERIES FOR EACH TEAM")
print("-" * 100)
for team in user_teams:
    team_id = team['teamId']
    team_name = team['teamName']
    
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team_id}
    )
    
    team_meetings = response['Items']
    print(f"{team_name}: {len(team_meetings)} meetings")
    for m in team_meetings:
        print(f"  - {m.get('title', 'Untitled')[:40]}")
    print()

# Step 5: Check what frontend is sending
print("STEP 5: FRONTEND REQUEST ANALYSIS")
print("-" * 100)
print("When user selects a team, frontend should:")
print("  1. Get teamId from TeamSelector component")
print("  2. Pass teamId to listMeetings(teamId)")
print("  3. API adds teamId as query parameter: /meetings?teamId=xxx")
print()
print("Check browser Network tab for:")
print("  - Request URL: Should have ?teamId=xxx")
print("  - Response: Should return filtered meetings")
print()

# Step 6: Check backend Lambda code
print("STEP 6: BACKEND LAMBDA VALIDATION")
print("-" * 100)
print("Backend should:")
print("  1. Extract teamId from query parameters")
print("  2. Get team from teams table")
print("  3. Extract member userIds from members list")
print("  4. Check if requesting user is in member list")
print("  5. Query meetings by teamId using GSI")
print()

# Step 7: Common issues
print("STEP 7: COMMON ISSUES TO CHECK")
print("-" * 100)
print("❌ Frontend not passing teamId parameter")
print("❌ Backend not reading teamId from query params")
print("❌ Team membership check failing (dict vs string)")
print("❌ GSI query failing (missing createdAt)")
print("❌ CloudFront caching old responses")
print("❌ Lambda not deployed correctly")
print()

print("=" * 100)
print("NEXT STEPS")
print("=" * 100)
print("1. Open browser DevTools (F12)")
print("2. Go to Network tab")
print("3. Refresh the page")
print("4. Look for /meetings request")
print("5. Check if it has ?teamId=xxx parameter")
print("6. Check the response - does it return filtered meetings?")
print()
print("If no teamId parameter: Frontend issue")
print("If teamId parameter but wrong response: Backend issue")
print("If correct response but UI shows wrong data: Frontend rendering issue")
