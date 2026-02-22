#!/usr/bin/env python3
"""Check user's recent meetings"""
import boto3
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'  # Demo user

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

meetings = sorted(response.get('Items', []), key=lambda x: x.get('createdAt', ''), reverse=True)[:15]

print(f"\n✓ Recent 15 meetings for demo user:\n")

for i, m in enumerate(meetings, 1):
    title = m.get('title')
    status = m.get('status')
    created = m.get('createdAt', '')[:19]
    
    print(f"{i}. {title} - {status} - Created: {created}")
