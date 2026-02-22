#!/usr/bin/env python3
import boto3
import uuid

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

source_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'
demo_user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

# Get all meetings from source user
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': source_user_id}
)

print(f'Copying {len(response["Items"])} meetings to demo user...\n')

for meeting in response['Items']:
    title = meeting.get('title', '')
    
    # Create new meeting with demo user ID
    new_meeting = meeting.copy()
    new_meeting['userId'] = demo_user_id
    new_meeting['meetingId'] = str(uuid.uuid4())  # New ID
    
    # Remove teamId if exists
    if 'teamId' in new_meeting:
        del new_meeting['teamId']
    
    table.put_item(Item=new_meeting)
    print(f'✓ Copied: {title}')

print(f'\nDone! {len(response["Items"])} meetings copied to demo user.')
