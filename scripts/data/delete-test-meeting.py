#!/usr/bin/env python3
"""Delete test meeting that's not part of demo story"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

meetings = response['Items']

for meeting in meetings:
    if meeting.get('title') == 'New Recording 2':
        table.delete_item(
            Key={
                'userId': demo_user_id,
                'meetingId': meeting['meetingId']
            }
        )
        print(f"✓ Deleted: {meeting['title']} ({meeting['meetingId']})")
