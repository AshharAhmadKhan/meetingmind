#!/usr/bin/env python3
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

print('Checking ROI data in demo meetings:')
print('=' * 80)
for item in response['Items']:
    print(f"\nMeeting: {item.get('title', 'N/A')}")
    print(f"Grade: {item.get('healthScore', 'N/A')}")
    
    # Check for ROI data
    if 'roi' in item:
        roi_data = item['roi']
        print(f"ROI Data Found:")
        print(f"  Cost: ${roi_data.get('cost', 'N/A')}")
        print(f"  Value: ${roi_data.get('value', 'N/A')}")
        print(f"  ROI: {roi_data.get('roi', 'N/A')}%")
    else:
        print("ROI Data: NOT FOUND")
    
    # Check for meetingCost, meetingValue, meetingROI fields
    if 'meetingCost' in item:
        print(f"Meeting Cost: ${item['meetingCost']}")
    if 'meetingValue' in item:
        print(f"Meeting Value: ${item['meetingValue']}")
    if 'meetingROI' in item:
        print(f"Meeting ROI: {item['meetingROI']}%")

print('\n' + '=' * 80)
