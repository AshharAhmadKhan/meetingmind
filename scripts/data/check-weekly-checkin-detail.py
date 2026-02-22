#!/usr/bin/env python3
"""
Check Weekly Check-In details
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

checkin = next((m for m in response['Items'] if m.get('title') == 'Weekly Check-In'), None)

if checkin:
    print("Weekly Check-In action items:")
    print("=" * 80)
    actions = checkin.get('actionItems', [])
    for i, action in enumerate(actions):
        print(f"\n{i+1}. {action.get('text')}")
        print(f"   Status: {action.get('status')}")
        print(f"   Completed: {action.get('completed')}")
        print(f"   Owner: {action.get('owner')}")
    
    done_count = sum(1 for a in actions if a.get('status') == 'DONE')
    print(f"\n\nTotal: {done_count}/{len(actions)} completed")
