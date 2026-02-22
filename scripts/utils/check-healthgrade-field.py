#!/usr/bin/env python3
"""
Check if healthGrade field exists
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

print("Checking for healthGrade field:")
print("="*80)

for meeting in sorted(response['Items'], key=lambda x: x.get('createdAt', '')):
    title = meeting.get('title')
    health_score = meeting.get('healthScore')
    health_grade = meeting.get('healthGrade')
    health_label = meeting.get('healthLabel')
    
    print(f"\n{title}")
    print(f"  healthScore: {health_score}")
    print(f"  healthGrade: {health_grade} {'❌ MISSING!' if not health_grade else '✅'}")
    print(f"  healthLabel: {health_label}")

print("\n" + "="*80)
print("\n🔍 DIAGNOSIS:")
if not any(m.get('healthGrade') for m in response['Items']):
    print("❌ healthGrade field is MISSING from all meetings!")
    print("   This is why all meetings show F grade in the UI.")
    print("\n💡 SOLUTION:")
    print("   Need to add healthGrade field based on healthScore:")
    print("   - 90-100: A")
    print("   - 80-89: B")
    print("   - 70-79: C")
    print("   - 60-69: D")
    print("   - 0-59: F")
