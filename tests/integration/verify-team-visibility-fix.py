#!/usr/bin/env python3
"""
Verify that the team visibility fix is working at the database level
"""
import boto3
import json
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

print("=" * 80)
print("TEAM VISIBILITY FIX VERIFICATION")
print("=" * 80)
print()

# Get teams
print("Step 1: Checking teams...")
teams_response = teams_table.scan()
teams = teams_response['Items']
print(f"✓ Found {len(teams)} teams")
print()

for team in teams:
    team_id = team['teamId']
    team_name = team['teamName']
    members = team.get('members', [])
    
    # Determine emoji
    if 'V1' in team_name or 'Legacy' in team_name:
        emoji = '📦'
    elif 'V2' in team_name or 'Active' in team_name:
        emoji = '🚀'
    else:
        emoji = '👥'
    
    print(f"{emoji} {team_name}")
    print(f"   Team ID: {team_id}")
    print(f"   Members: {len(members)}")
    
    # Extract member info
    for member in members:
        if isinstance(member, dict):
            email = member.get('email', 'unknown')
            user_id = member.get('userId', 'unknown')
            print(f"     - {email}")
        else:
            print(f"     - {member}")
    
    print()

# Test GSI query for each team
print("=" * 80)
print("Step 2: Testing GSI queries (simulating API calls)...")
print("=" * 80)
print()

for team in teams:
    team_id = team['teamId']
    team_name = team['teamName']
    
    # Determine emoji
    if 'V1' in team_name or 'Legacy' in team_name:
        emoji = '📦'
    elif 'V2' in team_name or 'Active' in team_name:
        emoji = '🚀'
    else:
        emoji = '👥'
    
    print(f"{emoji} Querying: {team_name}")
    print(f"   GSI: teamId-createdAt-index")
    print(f"   Key: teamId = {team_id}")
    
    try:
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': team_id},
            ScanIndexForward=False,
        )
        
        meetings = response.get('Items', [])
        print(f"   ✓ Found {len(meetings)} meetings:")
        
        for m in meetings:
            print(f"     - {m['title']}")
            print(f"       Status: {m['status']}")
            print(f"       Uploaded by: {m['userId'][:20]}...")
        
        if len(meetings) == 0:
            print("   ⚠ WARNING: No meetings found for this team!")
            print("   This means team members will see empty state.")
        
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")
    
    print()

# Summary
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print()

v1_team = next((t for t in teams if 'V1' in t['teamName'] or 'Legacy' in t['teamName']), None)
v2_team = next((t for t in teams if 'V2' in t['teamName'] or 'Active' in t['teamName']), None)

if v1_team:
    v1_response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': v1_team['teamId']},
    )
    v1_count = len(v1_response.get('Items', []))
    print(f"📦 V1 Team: {v1_count} meetings")
    if v1_count == 3:
        print("   ✓ PASS: Expected 3 meetings")
    else:
        print(f"   ✗ FAIL: Expected 3, got {v1_count}")

if v2_team:
    v2_response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': v2_team['teamId']},
    )
    v2_count = len(v2_response.get('Items', []))
    print(f"🚀 V2 Team: {v2_count} meetings")
    if v2_count == 3:
        print("   ✓ PASS: Expected 3 meetings")
    else:
        print(f"   ✗ FAIL: Expected 3, got {v2_count}")

print()
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. If all queries return meetings: Backend is working correctly")
print("   → Test in browser with team member accounts")
print("   → Check browser console for errors")
print("   → Verify CloudFront cache is cleared")
print()
print("2. If queries return 0 meetings: Data issue")
print("   → Run: python scripts/data/add-teamid-to-meetings.py")
print("   → Verify meetings have teamId field")
print()
print("3. If queries fail with error: GSI issue")
print("   → Check DynamoDB console for GSI status")
print("   → Verify teamId-createdAt-index exists")
