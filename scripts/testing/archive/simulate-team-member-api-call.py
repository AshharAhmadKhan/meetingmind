#!/usr/bin/env python3
"""
Simulate what happens when team members call the list-meetings API
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

# Get team data
teams_response = teams_table.scan()
teams = teams_response['Items']

v1_team = next((t for t in teams if 'V1' in t['teamName'] or 'Legacy' in t['teamName']), None)
v2_team = next((t for t in teams if 'V2' in t['teamName'] or 'Active' in t['teamName']), None)

print("=" * 80)
print("SIMULATING API CALLS FOR TEAM MEMBERS")
print("=" * 80)
print()

# Test accounts
test_users = [
    {
        'name': 'thehidden',
        'email': 'thehiddenif@gmail.com',
        'userId': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'
    },
    {
        'name': 'whisperbehind',
        'email': 'whispersbehindthecode@gmail.com',
        'userId': 'f1d33d1a-9041-7006-5af8-d18269b15a92'
    }
]

for user in test_users:
    print(f"User: {user['name']} ({user['email']})")
    print(f"UserId: {user['userId']}")
    print()
    
    # Test V1 team access
    if v1_team:
        print(f"  Testing V1 Team: {v1_team['teamName']}")
        members = v1_team.get('members', [])
        member_ids = []
        for member in members:
            if isinstance(member, dict):
                member_ids.append(member.get('userId'))
            else:
                member_ids.append(member)
        
        is_member = user['userId'] in member_ids
        print(f"    Is member: {is_member}")
        
        if is_member:
            # Simulate GSI query
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': v1_team['teamId']},
                ScanIndexForward=False,
            )
            meetings = response.get('Items', [])
            print(f"    ✓ Would return {len(meetings)} meetings:")
            for m in meetings:
                print(f"      - {m['title']}")
        else:
            print(f"    ✗ Would return 403 Forbidden")
        print()
    
    # Test V2 team access
    if v2_team:
        print(f"  Testing V2 Team: {v2_team['teamName']}")
        members = v2_team.get('members', [])
        member_ids = []
        for member in members:
            if isinstance(member, dict):
                member_ids.append(member.get('userId'))
            else:
                member_ids.append(member)
        
        is_member = user['userId'] in member_ids
        print(f"    Is member: {is_member}")
        
        if is_member:
            # Simulate GSI query
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': v2_team['teamId']},
                ScanIndexForward=False,
            )
            meetings = response.get('Items', [])
            print(f"    ✓ Would return {len(meetings)} meetings:")
            for m in meetings:
                print(f"      - {m['title']}")
        else:
            print(f"    ✗ Would return 403 Forbidden")
        print()
    
    print("-" * 80)
    print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
print("If both users show 'Is member: True' and meetings are returned,")
print("then the backend logic is correct.")
print()
print("If users see empty state in browser:")
print("1. Check browser console for 403 errors")
print("2. Check Network tab for actual API responses")
print("3. Verify JWT token has correct userId (sub claim)")
print("4. Try hard refresh (Ctrl+Shift+R) to clear cache")
