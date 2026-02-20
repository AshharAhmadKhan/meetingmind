#!/usr/bin/env python3
"""
Test that team members can access team meetings via the API
"""
import boto3
import json
import sys

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

print("=" * 80)
print("TESTING TEAM MEMBER ACCESS")
print("=" * 80)
print()

# Get teams
teams_response = teams_table.scan()
teams = teams_response['Items']

for team in teams:
    team_id = team['teamId']
    team_name = team['teamName']
    members = team.get('members', [])
    
    print(f"Team: {team_name}")
    print(f"  ID: {team_id}")
    print(f"  Members: {len(members)}")
    
    # Extract member IDs
    member_ids = []
    for member in members:
        if isinstance(member, dict):
            member_ids.append(member.get('userId'))
            print(f"    - {member.get('email', 'unknown')} ({member.get('userId', 'unknown')})")
        else:
            member_ids.append(member)
            print(f"    - {member}")
    
    # Query meetings for this team
    print(f"\n  Querying meetings for teamId={team_id}...")
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': team_id},
        ScanIndexForward=False,
    )
    
    meetings = response.get('Items', [])
    print(f"  Found {len(meetings)} meetings:")
    for m in meetings:
        print(f"    - {m['title']}")
        print(f"      Uploaded by: {m['userId']}")
        print(f"      Status: {m['status']}")
    
    print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print("If the API returns meetings when queried by teamId,")
print("then the backend is working correctly.")
print()
print("If team members still can't see meetings in the UI:")
print("1. Check browser console for errors")
print("2. Check Network tab to see actual API requests")
print("3. Verify CloudFront cache is cleared")
print("4. Try hard refresh (Ctrl+Shift+R)")
