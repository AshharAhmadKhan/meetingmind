#!/usr/bin/env python3
"""List all demo meetings with their IDs."""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Demo user ID
user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("Demo Meetings:")
print("=" * 80)
for item in response['Items']:
    print(f"{item['title']}")
    print(f"  ID: {item['meetingId']}")
    print(f"  Created: {item.get('createdAt', 'N/A')}")
    print()
