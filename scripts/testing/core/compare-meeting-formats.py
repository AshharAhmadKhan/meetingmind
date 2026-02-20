#!/usr/bin/env python3
"""
Compare meeting formats to identify differences
"""

import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"

def analyze_meeting(meeting):
    """Analyze meeting structure"""
    title = meeting.get('title', 'Unknown')
    
    print(f"\n{'='*70}")
    print(f"Meeting: {title}")
    print(f"{'='*70}")
    print(f"Meeting ID: {meeting.get('meetingId')}")
    print(f"Status: {meeting.get('status')}")
    print(f"Created: {meeting.get('createdAt', 'N/A')}")
    
    # Check health score format
    health_score = meeting.get('healthScore')
    print(f"\nHealth Score: {health_score} (type: {type(health_score).__name__})")
    
    # Check action items format
    action_items = meeting.get('actionItems', [])
    print(f"\nAction Items: {len(action_items)}")
    
    if action_items:
        first_action = action_items[0]
        print("\nFirst Action Item Structure:")
        print(f"  Keys: {list(first_action.keys())}")
        
        # Check for 'text' vs 'task'
        if 'text' in first_action:
            print(f"  ✓ Uses 'text' field (V1 format)")
            print(f"    text: {first_action['text'][:50]}...")
        elif 'task' in first_action:
            print(f"  ✓ Uses 'task' field (V2 format)")
            print(f"    task: {first_action['task'][:50]}...")
        
        # Check for 'status' vs 'completed'
        if 'status' in first_action:
            print(f"  ✓ Uses 'status' field: {first_action['status']} (V1 format)")
        elif 'completed' in first_action:
            print(f"  ✓ Uses 'completed' field: {first_action['completed']} (V2 format)")
        
        # Check owner field
        print(f"  Owner: {first_action.get('owner', 'N/A')}")
        
        # Check deadline field
        print(f"  Deadline: {first_action.get('deadline', 'N/A')}")
        
        # Check risk fields
        if 'riskScore' in first_action:
            print(f"  Risk Score: {first_action['riskScore']}")
        if 'riskLevel' in first_action:
            print(f"  Risk Level: {first_action['riskLevel']}")
    
    # Check decisions format
    decisions = meeting.get('decisions', [])
    print(f"\nDecisions: {len(decisions)}")
    if decisions:
        first_decision = decisions[0]
        if isinstance(first_decision, dict):
            print(f"  Format: dict with keys {list(first_decision.keys())}")
        else:
            print(f"  Format: {type(first_decision).__name__}")

def main():
    print("\n" + "="*70)
    print("COMPARING MEETING FORMATS")
    print("="*70)
    
    # Query all meetings for the team
    response = meetings_table.query(
        IndexName='teamId-createdAt-index',
        KeyConditionExpression='teamId = :tid',
        ExpressionAttributeValues={':tid': TEAM_ID},
        ScanIndexForward=False
    )
    
    meetings = response.get('Items', [])
    print(f"\nFound {len(meetings)} meetings for team")
    
    for meeting in meetings:
        analyze_meeting(meeting)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    v1_format = []
    v2_format = []
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        if action_items:
            first_action = action_items[0]
            if 'text' in first_action:
                v1_format.append(meeting.get('title'))
            elif 'task' in first_action:
                v2_format.append(meeting.get('title'))
    
    print(f"\nV1 Format (uses 'text', 'status'): {len(v1_format)} meetings")
    for title in v1_format:
        print(f"  - {title}")
    
    print(f"\nV2 Format (uses 'task', 'completed'): {len(v2_format)} meetings")
    for title in v2_format:
        print(f"  - {title}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
