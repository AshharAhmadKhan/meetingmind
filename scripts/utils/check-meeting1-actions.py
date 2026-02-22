#!/usr/bin/env python3
import boto3
import json
from decimal import Decimal

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    return obj

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=True
)

meetings = sorted(response['Items'], key=lambda x: x.get('createdAt', ''))

# Check Meeting 1 action items
meeting1 = meetings[0]
print('Meeting 1: Kickoff Meeting')
print('='*80)
print('Action Items:')
for i, action in enumerate(meeting1.get('actionItems', []), 1):
    print(f'{i}. ID: {action.get("id")}')
    print(f'   Task: {action.get("task")}')
    print(f'   Completed: {action.get("completed")}')
    print(f'   Owner: {action.get("owner")}')
    print()
