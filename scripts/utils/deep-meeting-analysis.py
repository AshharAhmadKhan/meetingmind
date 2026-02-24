#!/usr/bin/env python3
"""
Deep analysis of meeting to understand AI extraction issues
"""

import boto3
import json

REGION = 'ap-south-1'
TEST_EMAIL = 'ashkagakoko@gmail.com'
MEETING_ID = 'ea9c033d-52e1-48bb-800b-04cd004b4c9d'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table('meetingmind-meetings')
cognito = boto3.client('cognito-idp', region_name=REGION)

def get_user_id(email):
    try:
        response = cognito.list_users(
            UserPoolId='ap-south-1_mkFJawjMp',
            Filter=f'email = "{email}"'
        )
        if response['Users']:
            for attr in response['Users'][0]['Attributes']:
                if attr['Name'] == 'sub':
                    return attr['Value']
    except Exception as e:
        print(f"Error: {e}")
    return None

def main():
    user_id = get_user_id(TEST_EMAIL)
    if not user_id:
        print("Could not find user")
        return
    
    try:
        response = meetings_table.get_item(
            Key={'userId': user_id, 'meetingId': MEETING_ID}
        )
        meeting = response.get('Item')
        
        if not meeting:
            print("Meeting not found")
            return
        
        print("=" * 80)
        print("DEEP MEETING ANALYSIS")
        print("=" * 80)
        
        # Transcript analysis
        transcript = meeting.get('transcript', '')
        print(f"\n📝 TRANSCRIPT:")
        print(f"   Length: {len(transcript)} characters")
        print(f"   Word count: {len(transcript.split())}")
        print(f"\n   First 500 chars:")
        print(f"   {transcript[:500]}")
        print(f"\n   Last 500 chars:")
        print(f"   {transcript[-500:]}")
        
        # Action items analysis
        actions = meeting.get('actionItems', [])
        print(f"\n\n✅ ACTION ITEMS EXTRACTED: {len(actions)}")
        for i, action in enumerate(actions, 1):
            print(f"\n   {i}. {action.get('task', 'NO TASK')}")
            print(f"      Owner: {action.get('owner', 'NO OWNER')}")
            print(f"      Deadline: {action.get('deadline', 'NO DEADLINE')}")
            print(f"      Risk: {action.get('riskScore', 'NO RISK')}")
        
        # Decisions
        decisions = meeting.get('decisions', [])
        print(f"\n\n🎯 DECISIONS EXTRACTED: {len(decisions)}")
        for i, decision in enumerate(decisions, 1):
            print(f"   {i}. {decision}")
        
        # Follow-ups
        followups = meeting.get('followUps', [])
        print(f"\n\n🔄 FOLLOW-UPS EXTRACTED: {len(followups)}")
        for i, followup in enumerate(followups, 1):
            print(f"   {i}. {followup}")
        
        # Summary
        summary = meeting.get('summary', '')
        print(f"\n\n📋 SUMMARY:")
        print(f"   {summary}")
        
        print("\n" + "=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        print(f"   Expected: 23 actions, 8 decisions, 4 follow-ups")
        print(f"   Actual: {len(actions)} actions, {len(decisions)} decisions, {len(followups)} follow-ups")
        print(f"   Extraction rate: {len(actions)/23*100:.1f}% actions, {len(decisions)/8*100:.1f}% decisions")
        
        if len(transcript) < 4000:
            print(f"\n   ⚠️  WARNING: Transcript is very short ({len(transcript)} chars)")
            print(f"       Expected ~5000+ chars for 45-minute meeting")
        
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
