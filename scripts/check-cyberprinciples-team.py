#!/usr/bin/env python3
"""
Check CyberPrinciples team setup and members
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

print("="*70)
print("CYBERPRINCIPLES TEAM CHECK")
print("="*70)

# Scan for teams with "cyber" in the name
response = teams_table.scan()
teams = response.get('Items', [])

cyber_teams = [t for t in teams if 'cyber' in t.get('teamName', '').lower()]

if not cyber_teams:
    print("\n❌ No CyberPrinciples team found!")
    print("\nSearching all teams:")
    for team in teams:
        print(f"  - {team.get('teamName')} (ID: {team.get('teamId')})")
else:
    for team in cyber_teams:
        print(f"\n✓ Found: {team.get('teamName')}")
        print(f"  Team ID: {team.get('teamId')}")
        print(f"  Invite Code: {team.get('inviteCode')}")
        print(f"  Created: {team.get('createdAt')}")
        
        members = team.get('members', [])
        print(f"\n  Members ({len(members)}):")
        for member in members:
            role = member.get('role', 'member')
            print(f"    - {member.get('name')} ({member.get('email')}) [{role}]")
        
        print(f"\n  Full team data:")
        print(json.dumps(team, indent=2, cls=DecimalEncoder))

print("\n" + "="*70)
