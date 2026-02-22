#!/usr/bin/env python3
import boto3
from collections import defaultdict

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
cognito = boto3.client('cognito-idp', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

USER_POOL_ID = 'ap-south-1_YiKn1yGVe'

print('=' * 80)
print('MEETINGMIND SYSTEM AUDIT')
print('=' * 80)

# Get all users from Cognito
print('\n📧 USERS IN COGNITO:\n')
users_response = cognito.list_users(UserPoolId=USER_POOL_ID)

user_map = {}
for user in users_response['Users']:
    email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), 'N/A')
    user_id = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'sub'), 'N/A')
    status = user['UserStatus']
    enabled = user['Enabled']
    
    user_map[user_id] = email
    
    print(f'Email: {email}')
    print(f'  User ID: {user_id}')
    print(f'  Status: {status}')
    print(f'  Enabled: {enabled}')
    print()

# Get all meetings
print('\n📊 MEETINGS BY USER:\n')
meetings_response = meetings_table.scan()

meetings_by_user = defaultdict(list)
for meeting in meetings_response['Items']:
    user_id = meeting.get('userId')
    meetings_by_user[user_id].append(meeting)

for user_id, meetings in meetings_by_user.items():
    email = user_map.get(user_id, 'UNKNOWN EMAIL')
    print(f'{email} ({user_id[:20]}...)')
    print(f'  Total meetings: {len(meetings)}')
    
    for meeting in meetings:
        title = meeting.get('title', 'N/A')
        grade = meeting.get('healthScore', 'N/A')
        date = meeting.get('createdAt', 'N/A')[:10]
        print(f'    - {title} (Grade: {grade}, Date: {date})')
    print()

# Get all teams
print('\n👥 TEAMS:\n')
teams_response = teams_table.scan()

for team in teams_response['Items']:
    team_name = team.get('teamName', 'N/A')
    team_id = team.get('teamId', 'N/A')
    owner_id = team.get('ownerId', 'N/A')
    members = team.get('members', [])
    
    owner_email = user_map.get(owner_id, 'UNKNOWN')
    
    print(f'Team: {team_name}')
    print(f'  Team ID: {team_id}')
    print(f'  Owner: {owner_email}')
    print(f'  Members: {len(members)}')
    print()

# Summary
print('\n' + '=' * 80)
print('SUMMARY')
print('=' * 80)
print(f'Total Users: {len(users_response["Users"])}')
print(f'Total Meetings: {len(meetings_response["Items"])}')
print(f'Total Teams: {len(teams_response["Items"])}')
print()

# Recommendations
print('🎯 RECOMMENDATIONS:\n')

# Check for demo user
demo_user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
if demo_user_id in meetings_by_user:
    demo_meetings = len(meetings_by_user[demo_user_id])
    print(f'✓ Demo user (demo@meetingmind.com): {demo_meetings} meetings')
    print(f'  Purpose: PUBLIC DEMO for judges')
    print(f'  Essential: YES - keep all meetings')
else:
    print(f'✗ Demo user has no meetings!')

print()

# Check other users
for user_id, meetings in meetings_by_user.items():
    if user_id != demo_user_id:
        email = user_map.get(user_id, 'UNKNOWN')
        print(f'• {email}: {len(meetings)} meetings')
        if 'thecyberprinciples' in email or 'itzashhar' in email:
            print(f'  Purpose: YOUR PERSONAL ACCOUNT')
            print(f'  Essential: YES - your real data')
        elif 'henryhoof' in email:
            print(f'  Purpose: TEST USER for registration flow')
            print(f'  Essential: NO - can delete if testing complete')
        else:
            print(f'  Purpose: UNKNOWN')
            print(f'  Essential: REVIEW NEEDED')
        print()
