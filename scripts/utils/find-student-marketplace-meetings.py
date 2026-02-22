#!/usr/bin/env python3
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Scan entire table
response = table.scan()

target_titles = [
    'Kickoff Meeting',
    'Last Week Of The Project',
    'Should We Pivot',
    'Weekly Check-In',
    'Demo Prep Sync'
]

print('Searching entire database for student marketplace meetings...\n')

found_meetings = []

for meeting in response['Items']:
    title = meeting.get('title', '')
    if any(target in title for target in target_titles):
        found_meetings.append(meeting)
        print(f'FOUND: {title}')
        print(f'  Grade: {meeting.get("healthScore", "N/A")}')
        print(f'  Date: {meeting.get("createdAt", "N/A")[:10]}')
        print(f'  UserId: {meeting.get("userId", "N/A")}')
        print(f'  TeamId: {meeting.get("teamId", "N/A")}')
        print()

print(f'\nTotal found: {len(found_meetings)}/{len(target_titles)} meetings')

if len(found_meetings) > 0:
    print('\n=== USER IDs ===')
    user_ids = set(m.get('userId') for m in found_meetings)
    for uid in user_ids:
        print(f'  {uid}')
