#!/usr/bin/env python3
"""Delete the stuck PENDING meeting"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Delete the hELLO meeting
meeting_id = 'f5597e57-2528-422e-a27d-8db66a58c8ee'

print(f"Deleting stuck PENDING meeting: hELLO")
print(f"  Meeting ID: {meeting_id}")

table.delete_item(
    Key={
        'userId': demo_user_id,
        'meetingId': meeting_id
    }
)

print("  ✓ Deleted")
print("\nNew uploads will now work correctly!")
