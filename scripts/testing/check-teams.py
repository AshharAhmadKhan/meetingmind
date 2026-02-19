#!/usr/bin/env python3
"""Check teams in DynamoDB"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-teams')

response = table.scan()
teams = response['Items']

print(f'Total teams: {len(teams)}\n')
print('Teams:')
print('-' * 100)
print(f"{'Team Name':<40} | {'Team ID':<38} | {'Members':<10}")
print('-' * 100)

for t in teams:
    name = t.get('teamName', 'Untitled')[:39]
    team_id = t.get('teamId', 'N/A')[:37]
    members = len(t.get('members', []))
    print(f"{name:<40} | {team_id:<38} | {members:<10}")
    
print('-' * 100)
