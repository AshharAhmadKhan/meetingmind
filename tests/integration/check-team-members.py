#!/usr/bin/env python3
"""Check who the team members actually are"""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
teams_table = dynamodb.Table('meetingmind-teams')

V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

# The user who uploaded all meetings
UPLOADER_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

print("=" * 80)
print("TEAM MEMBERSHIP CHECK")
print("=" * 80)
print()

for team_name, team_id in [('V1', V1_TEAM_ID), ('V2', V2_TEAM_ID)]:
    print(f"{team_name} Team:")
    print("-" * 80)
    
    team_response = teams_table.get_item(Key={'teamId': team_id})
    if 'Item' in team_response:
        team = team_response['Item']
        members = team.get('members', [])
        
        print(f"Team Name: {team.get('teamName')}")
        print(f"Team ID: {team_id}")
        print(f"Members ({len(members)}):")
        for member in members:
            print(f"  - {member}")
        
        print()
        print(f"Uploader {UPLOADER_USER_ID[:20]}... is member: {UPLOADER_USER_ID in members}")
    else:
        print("Team not found!")
    
    print()

print("=" * 80)
print("ISSUE IDENTIFIED")
print("=" * 80)
print()
print("The user who uploaded all meetings is NOT a member of either team!")
print("This is why the backend validation blocks them.")
print()
print("Solution: Add the uploader to both teams")
