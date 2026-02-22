#!/usr/bin/env python3
"""Check actual team members"""

import boto3

REGION = 'ap-south-1'
TEAMS_TABLE = 'meetingmind-teams'
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
teams_table = dynamodb.Table(TEAMS_TABLE)

response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
if 'Item' in response:
    team = response['Item']
    print(f"Team: {team['teamName']}")
    print(f"Members: {team.get('members', [])}")
    print(f"Count: {len(team.get('members', []))}")
