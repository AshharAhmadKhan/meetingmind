#!/usr/bin/env python3
"""Fix the 'Team' owner to be 'Ashhar' for the discussion task."""

import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'
meeting_id = '4a7c7a8d-b9ba-4668-b1da-3b5cd8bf1ac8'  # Should We Pivot

response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
meeting = response['Item']

action_items = meeting.get('actionItems', [])

# Fix the Team owner to Ashhar
for action in action_items:
    if action.get('owner', '').lower() == 'team':
        action['owner'] = 'Ashhar'
        print(f"✅ Fixed: '{action['task']}'")
        print(f"   Owner: Team → Ashhar")

table.update_item(
    Key={'userId': user_id, 'meetingId': meeting_id},
    UpdateExpression='SET actionItems = :ai',
    ExpressionAttributeValues={':ai': action_items}
)

print("\n✅ Team owner fixed!")
