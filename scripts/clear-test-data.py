#!/usr/bin/env python3
"""Clear all test meetings from DynamoDB"""

import boto3
import sys

def clear_meetings():
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    table_name = 'meetingmind-meetings'
    
    # Scan all items
    response = dynamodb.scan(TableName=table_name)
    items = response.get('Items', [])
    
    print(f"Found {len(items)} meetings to delete...")
    
    # Delete each item
    deleted = 0
    for item in items:
        meeting_id = item['meetingId']['S']
        user_id = item['userId']['S']
        
        try:
            dynamodb.delete_item(
                TableName=table_name,
                Key={
                    'meetingId': {'S': meeting_id},
                    'userId': {'S': user_id}
                }
            )
            deleted += 1
            print(f"Deleted: {meeting_id}")
        except Exception as e:
            print(f"Error deleting {meeting_id}: {e}")
    
    print(f"\n✅ Deleted {deleted}/{len(items)} meetings")
    return deleted

if __name__ == '__main__':
    confirm = input("⚠️  This will delete ALL meetings from DynamoDB. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_meetings()
    else:
        print("Cancelled.")
        sys.exit(0)
