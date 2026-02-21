#!/usr/bin/env python3
"""Check detailed meeting data including autopsy and health scores."""

import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("DEMO MEETINGS - DETAILED ANALYSIS")
print("=" * 80)

for meeting in sorted(response['Items'], key=lambda x: x.get('createdAt', '')):
    print(f"\n📋 {meeting['title']}")
    print(f"   Created: {meeting.get('createdAt', 'N/A')}")
    print(f"   Health Score: {meeting.get('healthScore', 'N/A')}")
    print(f"   Grade: {meeting.get('healthGrade', 'N/A')}")
    print(f"   Decisions: {len(meeting.get('decisions', []))}")
    print(f"   Action Items: {len(meeting.get('actionItems', []))}")
    
    # Check for autopsy
    autopsy = meeting.get('autopsy')
    if autopsy:
        print(f"\n   🪦 AUTOPSY:")
        print(f"   {autopsy}")
    
    # Check ROI data
    roi_data = meeting.get('roiData', {})
    if roi_data:
        print(f"\n   💰 ROI:")
        print(f"   Duration: {roi_data.get('meeting_duration_minutes', 'N/A')} mins")
        print(f"   ROI: {roi_data.get('roi_percentage', 'N/A')}%")
    
    print("-" * 80)
