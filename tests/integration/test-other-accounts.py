#!/usr/bin/env python3
"""
Test team filtering for the OTHER two accounts
Simulate what they would see when querying teams
"""

import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

# The two accounts that see 0 meetings
ACCOUNTS = {
    'whispersbehindthecode@gmail.com': 'f1d33d1a-9041-7006-5af8-d18269b15a92',
    'thehiddenif@gmail.com': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'
}

# Team IDs
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

print("=" * 100)
print("TESTING OTHER ACCOUNTS - SIMULATING LAMBDA BEHAVIOR")
print("=" * 100)
print()

for email, user_id in ACCOUNTS.items():
    print(f"Testing: {email}")
    print(f"User ID: {user_id}")
    print("-" * 100)
    
    # Test 1: Query by userId (personal meetings)
    print("\n1. Personal meetings (no teamId):")
    response = meetings_table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id}
    )
    personal_meetings = response['Items']
    print(f"   Found {len(personal_meetings)} personal meetings")
    if personal_meetings:
        for m in personal_meetings:
            print(f"   - {m.get('title', 'Untitled')}")
    
    # Test 2: Check team membership for V1
    print("\n2. V1 Team membership check:")
    team_response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    if 'Item' in team_response:
        team = team_response['Item']
        members = team.get('members', [])
        
        # Extract member IDs (handle both dict and string formats)
        member_ids = []
        for member in members:
            if isinstance(member, dict):
                member_ids.append(member.get('userId'))
            else:
                member_ids.append(member)
        
        is_member = user_id in member_ids
        print(f"   Team: {team.get('teamName')}")
        print(f"   Is member: {is_member}")
        print(f"   Member IDs: {member_ids}")
        
        if is_member:
            # Query by teamId using GSI
            print("\n   Querying V1 team meetings via GSI:")
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': V1_TEAM_ID}
            )
            team_meetings = response['Items']
            print(f"   Found {len(team_meetings)} meetings")
            for m in team_meetings:
                print(f"   - {m.get('title', 'Untitled')}")
        else:
            print("   ❌ NOT A MEMBER - Would get 403 error")
    
    # Test 3: Check team membership for V2
    print("\n3. V2 Team membership check:")
    team_response = teams_table.get_item(Key={'teamId': V2_TEAM_ID})
    if 'Item' in team_response:
        team = team_response['Item']
        members = team.get('members', [])
        
        # Extract member IDs (handle both dict and string formats)
        member_ids = []
        for member in members:
            if isinstance(member, dict):
                member_ids.append(member.get('userId'))
            else:
                member_ids.append(member)
        
        is_member = user_id in member_ids
        print(f"   Team: {team.get('teamName')}")
        print(f"   Is member: {is_member}")
        print(f"   Member IDs: {member_ids}")
        
        if is_member:
            # Query by teamId using GSI
            print("\n   Querying V2 team meetings via GSI:")
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': V2_TEAM_ID}
            )
            team_meetings = response['Items']
            print(f"   Found {len(team_meetings)} meetings")
            for m in team_meetings:
                print(f"   - {m.get('title', 'Untitled')}")
        else:
            print("   ❌ NOT A MEMBER - Would get 403 error")
    
    print()
    print("=" * 100)
    print()

print("\nCONCLUSION:")
print("-" * 100)
print("If the script shows they ARE members and CAN query meetings:")
print("  → Backend logic is correct")
print("  → Issue is likely:")
print("    1. Frontend not passing teamId parameter")
print("    2. CloudFront cache not cleared")
print("    3. User needs hard refresh (Ctrl+Shift+R)")
print()
print("If the script shows they are NOT members:")
print("  → Database team membership data is wrong")
print("  → Need to fix team membership")
