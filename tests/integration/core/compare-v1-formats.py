#!/usr/bin/env python3
"""
Compare V1 historical meeting format with comprehensive test meeting format
"""

import boto3
import json
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"  # Project V1 - Legacy

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_all_v1_meetings():
    """Get all meetings for V1 team"""
    response = meetings_table.scan(
        FilterExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': TEAM_ID}
    )
    return response.get('Items', [])

def main():
    print("\n" + "="*70)
    print("COMPARING V1 MEETING FORMATS")
    print("="*70)
    print()
    
    meetings = get_all_v1_meetings()
    print(f"Found {len(meetings)} meetings for V1 team")
    print()
    
    for i, meeting in enumerate(meetings, 1):
        print(f"\n{'='*70}")
        print(f"MEETING {i}: {meeting.get('title', 'Untitled')}")
        print(f"{'='*70}")
        print(f"Meeting ID: {meeting['meetingId']}")
        print(f"Status: {meeting.get('status', 'MISSING')}")
        print(f"Created: {meeting.get('createdAt', 'MISSING')}")
        print()
        
        print("TOP-LEVEL FIELDS:")
        for key in sorted(meeting.keys()):
            if key not in ['actionItems', 'decisions', 'transcript']:
                value = meeting[key]
                if isinstance(value, list):
                    print(f"  {key}: [{len(value)} items]")
                elif isinstance(value, dict):
                    print(f"  {key}: {{dict}}")
                else:
                    print(f"  {key}: {value}")
        print()
        
        if 'actionItems' in meeting and meeting['actionItems']:
            print(f"ACTION ITEMS ({len(meeting['actionItems'])}):")
            action = meeting['actionItems'][0]
            print("  First action item structure:")
            for key in sorted(action.keys()):
                print(f"    {key}: {type(action[key]).__name__}")
            print()
        
        if 'decisions' in meeting and meeting['decisions']:
            print(f"DECISIONS ({len(meeting['decisions'])}):")
            decision = meeting['decisions'][0] if isinstance(meeting['decisions'], list) else meeting['decisions']
            print(f"  Type: {type(decision).__name__}")
            if isinstance(decision, dict):
                print("  Structure:")
                for key in sorted(decision.keys()):
                    print(f"    {key}: {type(decision[key]).__name__}")
            else:
                print(f"  Value: {decision}")
            print()
    
    print("\n" + "="*70)
    print("FULL JSON DUMP OF FIRST MEETING")
    print("="*70)
    if meetings:
        print(json.dumps(meetings[0], indent=2, default=decimal_default))

if __name__ == '__main__':
    main()
