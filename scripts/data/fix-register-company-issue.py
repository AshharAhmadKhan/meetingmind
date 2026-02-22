#!/usr/bin/env python3
"""
Fix: "Register the company" is marked DONE but showing in graveyard
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get Kickoff Meeting
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id}
)

kickoff = next((m for m in response['Items'] if m.get('title') == 'Kickoff Meeting'), None)

if kickoff:
    print("Checking 'Register the company' task...")
    actions = kickoff.get('actionItems', [])
    
    for action in actions:
        if 'register' in action.get('text', '').lower():
            print(f"\nFound: {action.get('text')}")
            print(f"  Status: {action.get('status')}")
            print(f"  Epitaph: {action.get('epitaph', 'NONE')}")
            
            if action.get('status') == 'DONE':
                print("\n  ✅ Status is DONE - this is correct")
                print("  ℹ️  Graveyard should filter this out (only shows incomplete)")
                print("  ℹ️  The 'Awaiting final words' message is normal for completed tasks")
            else:
                print("\n  ❌ Status should be DONE but it's:", action.get('status'))
