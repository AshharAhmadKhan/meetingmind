#!/usr/bin/env python3
"""
Check V2 team details and members
"""

import boto3
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
teams_table = dynamodb.Table('meetingmind-teams')

team_id = 'df29c543-a4d0-4c80-a086-6c11712d66f3'

print("="*70)
print("V2 - ACTIVE TEAM DETAILS")
print("="*70)

response = teams_table.get_item(Key={'teamId': team_id})
team = response.get('Item')

if team:
    print(f"\nTeam Name: {team.get('teamName')}")
    print(f"Team ID: {team.get('teamId')}")
    print(f"Invite Code: {team.get('inviteCode')}")
    print(f"Created: {team.get('createdAt')}")
    
    members = team.get('members', [])
    print(f"\nMembers ({len(members)}):")
    for i, member in enumerate(members, 1):
        role = member.get('role', 'member')
        print(f"  {i}. {member.get('name')} ({member.get('email')}) [{role}]")
    
    print(f"\nFull team data:")
    print(json.dumps(team, indent=2, cls=DecimalEncoder))
else:
    print("❌ Team not found!")

print("\n" + "="*70)
