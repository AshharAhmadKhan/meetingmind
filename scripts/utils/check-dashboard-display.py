#!/usr/bin/env python3
"""
Check what the dashboard should display
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

print("DASHBOARD DISPLAY CHECK")
print("="*80)
print("\nWhat the frontend should see:")
print()

for meeting in sorted(response['Items'], key=lambda x: x.get('createdAt', '')):
    title = meeting.get('title')
    health_score = meeting.get('healthScore')
    health_grade = meeting.get('healthGrade')
    health_label = meeting.get('healthLabel')
    status = meeting.get('status')
    team_id = meeting.get('teamId')
    
    print(f"{title}")
    print(f"  status: {status}")
    print(f"  healthScore: {health_score}")
    print(f"  healthGrade: {health_grade}")
    print(f"  healthLabel: {health_label}")
    print(f"  teamId: {team_id}")
    
    # Check if meeting is DONE (required for dashboard display)
    if status != 'DONE':
        print(f"  ⚠️  WARNING: status is '{status}', not 'DONE'")
        print(f"     Dashboard only shows meetings with status='DONE'")
    
    print()

print("="*80)
print("\n📍 WHERE TO SEE ACTION ITEM AMNESIA:")
print("  1. Go to Dashboard")
print("  2. Scroll down below the meeting list")
print("  3. Look for '🔍 Pattern Detection' section")
print("  4. You should see 2 cards:")
print("     - Action Item Amnesia (🧠)")
print("     - Chronic Blocker (🚧)")
print()
print("  If you don't see it, check browser console for:")
print("  'Patterns detected: 2'")
print("  'Pattern IDs: ['action-amnesia', 'chronic-blocker']'")
