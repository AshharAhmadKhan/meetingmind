#!/usr/bin/env python3
"""
Test what list-meetings API returns for team queries
"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Get team IDs
print("=" * 80)
print("TEAMS")
print("=" * 80)
teams_response = teams_table.scan()
teams = teams_response['Items']
for team in teams:
    print(f"Team: {team['teamName']}")
    print(f"  ID: {team['teamId']}")
    print(f"  Members: {len(team.get('members', []))}")
    print()

# Test query for each team
for team in teams:
    team_id = team['teamId']
    team_name = team['teamName']
    
    print("=" * 80)
    print(f"QUERY: teamId = {team_id} ({team_name})")
    print("=" * 80)
    
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team_id},
        ScanIndexForward=False,
    )
    
    meetings = response.get('Items', [])
    print(f"Found {len(meetings)} meetings:")
    for m in meetings:
        print(f"  - {m['title']}")
        print(f"    userId: {m['userId']}")
        print(f"    teamId: {m.get('teamId', 'MISSING')}")
        print(f"    status: {m['status']}")
    print()

# Test personal query (no teamId)
print("=" * 80)
print("QUERY: Personal (userId only, no teamId)")
print("=" * 80)
test_user_id = 'c1c38d2a-1081-7088-'  # Main account
response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': test_user_id},
    ScanIndexForward=False,
)
meetings = response.get('Items', [])
print(f"Found {len(meetings)} meetings for userId {test_user_id}:")
for m in meetings:
    print(f"  - {m['title']}")
    print(f"    teamId: {m.get('teamId', 'NONE')}")
print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print("If team members can't see meetings, the issue is:")
print("1. Frontend not passing teamId correctly")
print("2. Backend team membership validation failing")
print("3. CloudFront cache serving old data")
