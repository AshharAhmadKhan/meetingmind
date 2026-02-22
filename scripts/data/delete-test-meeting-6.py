#!/usr/bin/env python3
"""Delete the Test 1 meeting"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

# Find and delete "Test 1"
for meeting in response['Items']:
    if meeting.get('title') == 'Test 1':
        print(f"Deleting: {meeting['title']}")
        print(f"  Meeting ID: {meeting['meetingId']}")
        print(f"  Date: {meeting.get('createdAt', 'N/A')}")
        
        table.delete_item(
            Key={
                'userId': demo_user_id,
                'meetingId': meeting['meetingId']
            }
        )
        print("  ✓ Deleted")

print("\nDemo restored to original 5-meeting state!")
