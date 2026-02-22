#!/usr/bin/env python3
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

team_id = 'c66ebc5b-b5f5-435e-a476-4d57877fe8a2'

response = table.scan(
    FilterExpression='teamId = :tid',
    ExpressionAttributeValues={':tid': team_id}
)

print(f'Meetings in team workspace:\n')
for i, meeting in enumerate(response['Items'], 1):
    title = meeting.get('title', 'N/A')
    grade = meeting.get('healthScore', 'N/A')
    date = meeting.get('createdAt', 'N/A')[:10]
    user_id = meeting.get('userId', 'N/A')
    
    print(f'{i}. {title}')
    print(f'   Grade: {grade}')
    print(f'   Date: {date}')
    print(f'   UserId: {user_id}')
    print()

print(f'Total: {len(response["Items"])} meetings')
