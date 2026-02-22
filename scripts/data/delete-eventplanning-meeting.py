#!/usr/bin/env python3
"""Delete the eventplanning test meeting"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

print("Current meetings:")
for meeting in response['Items']:
    title = meeting.get('title', '')
    meeting_id = meeting['meetingId']
    created_at = meeting.get('createdAt', '')[:10]
    print(f"  - {title} ({created_at}) [{meeting_id}]")

print("\nDeleting test meetings...")
deleted_count = 0
for meeting in response['Items']:
    title = meeting.get('title', '').lower()
    # Delete any meeting that's not part of the 5-meeting story
    if title not in ['kickoff meeting', 'mid-project crisis', 'last attempt before pivot', 
                     'should we pivot', 'weekly check-in']:
        print(f'Deleting: {meeting.get("title")} ({meeting["meetingId"]})')
        table.delete_item(Key={'userId': demo_user_id, 'meetingId': meeting['meetingId']})
        print('  ✓ Deleted')
        deleted_count += 1

print(f'\nDeleted {deleted_count} test meeting(s)')
print('Demo restored to original 5-meeting state!')
