#!/usr/bin/env python3
import boto3
from collections import defaultdict

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

print('=' * 80)
print('MEETINGMIND SYSTEM AUDIT')
print('=' * 80)

# Get all meetings
print('\n📊 ALL MEETINGS IN DATABASE:\n')
meetings_response = meetings_table.scan()

meetings_by_user = defaultdict(list)
for meeting in meetings_response['Items']:
    user_id = meeting.get('userId')
    meetings_by_user[user_id].append(meeting)

# Known user IDs
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
STUDENT_MARKETPLACE_USER = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

for user_id, meetings in meetings_by_user.items():
    print(f'\nUser ID: {user_id}')
    
    # Identify user
    if user_id == DEMO_USER_ID:
        print('  Email: demo@meetingmind.com')
        print('  Purpose: PUBLIC DEMO for AWS competition judges')
        print('  Essential: ⭐ YES - CRITICAL')
    elif user_id == STUDENT_MARKETPLACE_USER:
        print('  Email: UNKNOWN (source of student marketplace meetings)')
        print('  Purpose: Original source of demo meetings')
        print('  Essential: ⚠️  REVIEW - may have duplicates')
    else:
        print('  Email: UNKNOWN')
        print('  Purpose: UNKNOWN')
        print('  Essential: ❓ NEEDS REVIEW')
    
    print(f'  Total meetings: {len(meetings)}')
    
    for meeting in meetings:
        title = meeting.get('title', 'N/A')
        grade = meeting.get('healthScore', 'N/A')
        date = meeting.get('createdAt', 'N/A')[:10]
        team_id = meeting.get('teamId', None)
        team_str = f' [Team: {team_id[:20]}...]' if team_id else ''
        print(f'    • {title} (Grade: {grade}, Date: {date}){team_str}')

# Get all teams
print('\n\n👥 ALL TEAMS:\n')
teams_response = teams_table.scan()

for team in teams_response['Items']:
    team_name = team.get('teamName', 'N/A')
    team_id = team.get('teamId', 'N/A')
    owner_id = team.get('ownerId', 'N/A')
    members = team.get('members', [])
    
    print(f'\nTeam: {team_name}')
    print(f'  Team ID: {team_id}')
    print(f'  Owner ID: {owner_id[:20]}...')
    print(f'  Members: {len(members)}')

# Summary
print('\n\n' + '=' * 80)
print('SUMMARY & RECOMMENDATIONS')
print('=' * 80)

print(f'\nTotal Users with meetings: {len(meetings_by_user)}')
print(f'Total Meetings: {len(meetings_response["Items"])}')
print(f'Total Teams: {len(teams_response["Items"])}')

print('\n🎯 CLEANUP RECOMMENDATIONS:\n')

# Demo user
if DEMO_USER_ID in meetings_by_user:
    demo_count = len(meetings_by_user[DEMO_USER_ID])
    print(f'✓ demo@meetingmind.com: {demo_count} meetings')
    print(f'  Action: KEEP ALL - this is for judges')
else:
    print(f'✗ demo@meetingmind.com: NO MEETINGS')
    print(f'  Action: NEEDS SETUP')

print()

# Student marketplace source
if STUDENT_MARKETPLACE_USER in meetings_by_user:
    source_count = len(meetings_by_user[STUDENT_MARKETPLACE_USER])
    print(f'⚠️  Student marketplace source: {source_count} meetings')
    print(f'  Action: DELETE - already copied to demo user')

print()

# Other users
other_users = [uid for uid in meetings_by_user.keys() 
               if uid not in [DEMO_USER_ID, STUDENT_MARKETPLACE_USER]]

if other_users:
    print(f'❓ {len(other_users)} other user(s) with meetings:')
    for uid in other_users:
        count = len(meetings_by_user[uid])
        print(f'  • {uid[:20]}...: {count} meetings')
        print(f'    Action: REVIEW - identify if needed')
