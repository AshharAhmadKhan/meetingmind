#!/usr/bin/env python3
"""Check which meetings have teamId"""

import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

response = table.scan()
meetings = response['Items']

print(f'Total meetings: {len(meetings)}\n')
print('Meetings by teamId:')
print('-' * 120)
print(f"{'Title':<45} | {'teamId':<38} | {'userId':<20} | {'Status':<12}")
print('-' * 120)

for m in meetings:
    title = m.get('title', 'Untitled')[:44]
    team_id = m.get('teamId', 'MISSING')[:37]
    user_id = m.get('userId', 'N/A')[:19]
    status = m.get('status', 'N/A')[:11]
    print(f"{title:<45} | {team_id:<38} | {user_id:<20} | {status:<12}")

print('-' * 120)
print(f"\nMeetings WITH teamId: {sum(1 for m in meetings if m.get('teamId'))}")
print(f"Meetings WITHOUT teamId: {sum(1 for m in meetings if not m.get('teamId'))}")
