#!/usr/bin/env python3
"""
Test that the API returns correct grades after the fix
"""
import boto3
import json

# Simulate what the Lambda does
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

meetings = response['Items']

print("=" * 80)
print("API RESPONSE SIMULATION - WHAT FRONTEND WILL SEE")
print("=" * 80)
print()

for meeting in sorted(meetings, key=lambda x: x.get('createdAt', '')):
    if meeting.get('status') == 'DONE':
        title = meeting.get('title')
        
        # Check if healthGrade exists in database
        has_stored_grade = 'healthGrade' in meeting and 'healthScore' in meeting
        
        if has_stored_grade:
            # Lambda will use stored values
            grade = meeting.get('healthGrade')
            score = meeting.get('healthScore')
            label = meeting.get('healthLabel')
            print(f"✅ {title}")
            print(f"   Grade: {grade} (Score: {score})")
            print(f"   Label: {label}")
            print(f"   Source: DATABASE (stored values)")
        else:
            # Lambda will calculate dynamically
            print(f"⚠️  {title}")
            print(f"   Grade: WILL BE CALCULATED")
            print(f"   Source: DYNAMIC (no stored values)")
        
        print()

print("=" * 80)
print("EXPECTED BEHAVIOR:")
print("  - All meetings should show '✅' with DATABASE source")
print("  - Grades should be: F, F, F, A, B")
print("  - If any show '⚠️', the database is missing healthGrade field")
print("=" * 80)
