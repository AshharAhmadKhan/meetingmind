#!/usr/bin/env python3
"""
Test script to check what data is returned for a V1 meeting
"""
import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get a V1 meeting (one with teamId)
response = table.scan(
    FilterExpression='attribute_exists(teamId)',
    Limit=1
)

if response['Items']:
    meeting = response['Items'][0]
    
    print("=== V1 Meeting Data Structure ===\n")
    print(f"Meeting ID: {meeting.get('meetingId')}")
    print(f"Title: {meeting.get('title')}")
    print(f"Team ID: {meeting.get('teamId')}")
    print(f"Created At: {meeting.get('createdAt')}")
    print(f"Updated At: {meeting.get('updatedAt')}")
    
    print("\n=== Action Items ===")
    actions = meeting.get('actionItems', [])
    print(f"Total actions: {len(actions)}")
    
    if actions:
        print("\nFirst action structure:")
        first_action = actions[0]
        for key, value in first_action.items():
            print(f"  {key}: {value} (type: {type(value).__name__})")
    
    print("\n=== Decisions ===")
    decisions = meeting.get('decisions', [])
    print(f"Total decisions: {len(decisions)}")
    
    print("\n=== Follow-ups ===")
    followups = meeting.get('followUps', [])
    print(f"Total follow-ups: {len(followups)}")
    
    print("\n=== Other Fields ===")
    for key in meeting.keys():
        if key not in ['meetingId', 'title', 'teamId', 'createdAt', 'updatedAt', 
                       'actionItems', 'decisions', 'followUps', 'transcript']:
            value = meeting[key]
            print(f"{key}: {value} (type: {type(value).__name__})")
else:
    print("No V1 meetings found")
