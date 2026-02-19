#!/usr/bin/env python3
"""Debug why V2 meetings aren't showing up in GSI query"""

import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

print("=" * 80)
print("DEBUGGING V2 MEETINGS")
print("=" * 80)
print()

# Get all meetings
response = table.scan()
meetings = response['Items']

print(f"Total meetings in table: {len(meetings)}")
print()

# Find V2 meetings
v2_meetings = [m for m in meetings if m.get('teamId') == V2_TEAM_ID]
print(f"Meetings with V2 teamId: {len(v2_meetings)}")
print()

for m in v2_meetings:
    print(f"Meeting: {m.get('title')}")
    print(f"  meetingId: {m.get('meetingId')}")
    print(f"  userId: {m.get('userId')}")
    print(f"  teamId: {m.get('teamId')}")
    print(f"  createdAt: {m.get('createdAt')}")
    print(f"  status: {m.get('status')}")
    print()

# Now try GSI query
print("=" * 80)
print("GSI QUERY TEST")
print("=" * 80)
print()

response = table.query(
    IndexName='teamId-createdAt-index',
    KeyConditionExpression='teamId = :tid',
    ExpressionAttributeValues={':tid': V2_TEAM_ID}
)

print(f"GSI query returned: {len(response['Items'])} meetings")
print()

if len(response['Items']) == 0:
    print("❌ GSI QUERY FAILED!")
    print()
    print("Possible reasons:")
    print("1. GSI not fully updated yet (eventual consistency)")
    print("2. teamId attribute type mismatch")
    print("3. GSI projection doesn't include required attributes")
    print()
    print("Wait 30 seconds and try again...")
else:
    print("✅ GSI query works!")
    for m in response['Items']:
        print(f"  - {m.get('title')}")
