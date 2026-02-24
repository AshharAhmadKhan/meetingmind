#!/usr/bin/env python3
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
cognito = boto3.client('cognito-idp', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

response = cognito.list_users(
    UserPoolId='ap-south-1_mkFJawjMp',
    Filter='email = "ashkagakoko@gmail.com"'
)
user_id = None
for attr in response['Users'][0]['Attributes']:
    if attr['Name'] == 'sub':
        user_id = attr['Value']
        break

print(f'User ID: {user_id}')
print()

response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id},
    ScanIndexForward=False,
    Limit=10
)

print('Recent meetings:')
for item in response['Items']:
    actions = item.get('actionItems', [])
    completed = sum(1 for a in actions if a.get('completed'))
    print(f'  ID: {item.get("meetingId")}')
    print(f'     Title: {item.get("title")}')
    print(f'     Status: {item.get("status")}')
    print(f'     Actions: {completed}/{len(actions)} completed')
    print(f'     Health: {item.get("healthScore")} ({item.get("healthGrade")})')
    print()
