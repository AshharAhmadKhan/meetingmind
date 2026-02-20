#!/usr/bin/env python3
"""
Test V1 meeting access for team members
"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

# Test user (team member)
test_user_id = 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'  # thehidden

print("=" * 80)
print("TEST: V1 Meeting Access for Team Member")
print("=" * 80)
print()

# Get a V1 meeting
response = meetings_table.scan(
    FilterExpression='attribute_exists(teamId)',
    Limit=1
)

if not response['Items']:
    print("❌ No V1 meetings found")
    exit(1)

meeting = response['Items'][0]
meeting_id = meeting['meetingId']
team_id = meeting['teamId']
uploader_id = meeting['userId']

print(f"Meeting: {meeting['title']}")
print(f"Meeting ID: {meeting_id}")
print(f"Team ID: {team_id}")
print(f"Uploader ID: {uploader_id}")
print(f"Test User ID: {test_user_id}")
print()

# Check if test user is in the team
team_response = teams_table.get_item(Key={'teamId': team_id})
if 'Item' not in team_response:
    print("❌ Team not found")
    exit(1)

team = team_response['Item']
members = team.get('members', [])

# Extract member IDs
member_ids = []
for member in members:
    if isinstance(member, dict):
        member_ids.append(member.get('userId'))
    else:
        member_ids.append(member)

print(f"Team: {team['teamName']}")
print(f"Team Members: {len(member_ids)}")
for mid in member_ids:
    print(f"  - {mid}")
print()

# Check if test user is a member
is_member = test_user_id in member_ids
print(f"Test user is member: {is_member}")
print()

if is_member:
    print("✅ Test user should be able to access this meeting")
    print()
    
    # Simulate what the Lambda does
    print("Simulating Lambda logic:")
    print("1. Try to get meeting by userId (uploader)")
    print(f"   Query: userId={test_user_id}, meetingId={meeting_id}")
    print("   Result: Not found (user is not uploader)")
    print()
    
    print("2. Scan for meeting by meetingId")
    scan_response = meetings_table.scan(
        FilterExpression='meetingId = :mid',
        ExpressionAttributeValues={':mid': meeting_id},
        Limit=1
    )
    print(f"   Result: Found {len(scan_response['Items'])} meeting(s)")
    print()
    
    print("3. Check team membership")
    print(f"   Team ID: {team_id}")
    print(f"   User ID: {test_user_id}")
    print(f"   Is member: {is_member}")
    print()
    
    if is_member:
        print("✅ Lambda would return 200 OK with meeting data")
        print()
        print("Meeting data structure:")
        print(f"  - actionItems: {len(meeting.get('actionItems', []))} items")
        print(f"  - decisions: {len(meeting.get('decisions', []))} items")
        print(f"  - followUps: {len(meeting.get('followUps', []))} items")
        print()
        
        # Check action item structure
        if meeting.get('actionItems'):
            action = meeting['actionItems'][0]
            print("First action item structure:")
            for key in action.keys():
                print(f"    {key}: {type(action[key]).__name__}")
            print()
        
        # Check decision structure
        if meeting.get('decisions'):
            decision = meeting['decisions'][0]
            print("First decision structure:")
            print(f"    Type: {type(decision).__name__}")
            if isinstance(decision, dict):
                for key in decision.keys():
                    print(f"    {key}: {type(decision[key]).__name__}")
            print()
        
        # Check ROI structure
        roi = meeting.get('roi')
        print(f"ROI structure: {type(roi).__name__}")
        if isinstance(roi, dict):
            for key in roi.keys():
                print(f"    {key}: {type(roi[key]).__name__}")
        else:
            print(f"    Value: {roi}")
        print()
        
    else:
        print("❌ Lambda would return 403 Forbidden")
else:
    print("❌ Test user is not a team member")

print("=" * 80)
