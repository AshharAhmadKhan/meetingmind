#!/usr/bin/env python3
"""
URGENT: Check why all meetings showing F grade
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

print("URGENT GRADE CHECK")
print("="*80)

for meeting in sorted(response['Items'], key=lambda x: x.get('createdAt', '')):
    title = meeting.get('title')
    health_score = meeting.get('healthScore')
    quality_score = meeting.get('qualityScore')
    
    # Check what grade fields exist
    print(f"\n{title}")
    print(f"  healthScore: {health_score}")
    print(f"  qualityScore: {quality_score}")
    
    # Check if there's a grade field
    if 'grade' in meeting:
        print(f"  grade: {meeting['grade']}")
    
    # Show letter grade calculation
    if health_score:
        if health_score >= 90:
            letter = 'A'
        elif health_score >= 80:
            letter = 'B'
        elif health_score >= 70:
            letter = 'C'
        elif health_score >= 60:
            letter = 'D'
        else:
            letter = 'F'
        print(f"  Calculated letter: {letter}")
    
    # Show action items
    actions = meeting.get('actionItems', [])
    completed = sum(1 for a in actions if a.get('status') == 'DONE')
    print(f"  Actions: {completed}/{len(actions)} completed")

print("\n" + "="*80)
print("\nExpected grades:")
print("  Kickoff Meeting: 55 (F)")
print("  Mid-Project Crisis: 50 (F)")
print("  Last Attempt Before Pivot: 48 (F)")
print("  Should We Pivot: 95 (A)")
print("  Weekly Check-In: 85 (B)")
