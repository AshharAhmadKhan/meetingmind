#!/usr/bin/env python3
"""
Detailed check of test meeting - query meeting document directly
"""

import boto3
import json
from boto3.dynamodb.conditions import Key

REGION = 'ap-south-1'
dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table('meetingmind-meetings')

def get_user_id_by_email(email):
    """Get user ID from Cognito by email"""
    cognito = boto3.client('cognito-idp', region_name=REGION)
    user_pool_id = 'ap-south-1_mkFJawjMp'
    
    try:
        response = cognito.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{email}"'
        )
        if response['Users']:
            for attr in response['Users'][0]['Attributes']:
                if attr['Name'] == 'sub':
                    return attr['Value']
    except Exception as e:
        print(f"Error getting user: {e}")
    return None

def main():
    email = 'ashkagakoko@gmail.com'
    meeting_id = 'e3917e6d-a53e-421d-977c-6a822bca927f'
    
    print(f"\n{'='*80}")
    print(f"DETAILED MEETING ANALYSIS")
    print(f"{'='*80}\n")
    
    # Get user ID
    user_id = get_user_id_by_email(email)
    if not user_id:
        print(f"❌ User not found: {email}")
        return
    
    print(f"User: {email}")
    print(f"User ID: {user_id}")
    print(f"Meeting ID: {meeting_id}\n")
    
    # Get meeting document
    try:
        response = meetings_table.get_item(
            Key={
                'userId': user_id,
                'meetingId': meeting_id
            }
        )
        
        if 'Item' not in response:
            print("❌ Meeting not found")
            return
        
        meeting = response['Item']
        
        print(f"{'─'*80}")
        print(f"MEETING DOCUMENT")
        print(f"{'─'*80}\n")
        
        # Basic info
        print(f"Title: {meeting.get('title', 'N/A')}")
        print(f"Status: {meeting.get('status', 'N/A')}")
        print(f"Grade: {meeting.get('healthGrade', 'N/A')}")
        print(f"Created: {meeting.get('createdAt', 'N/A')}")
        
        # Action items stored in meeting document
        actions = meeting.get('actionItems', [])
        print(f"\n{'─'*80}")
        print(f"ACTION ITEMS IN MEETING DOCUMENT: {len(actions)}")
        print(f"{'─'*80}\n")
        
        if actions:
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action.get('text', 'No text')}")
                print(f"   Owner: {action.get('owner', 'Unassigned')}")
                print(f"   Deadline: {action.get('deadline', 'No deadline')}")
                print(f"   Status: {action.get('status', 'TODO')}")
                print(f"   Risk: {action.get('riskScore', 0)}")
                print()
        else:
            print("⚠️ No action items in meeting document")
        
        # Decisions
        decisions = meeting.get('decisions', [])
        print(f"{'─'*80}")
        print(f"DECISIONS: {len(decisions)}")
        print(f"{'─'*80}\n")
        
        if decisions:
            for i, decision in enumerate(decisions, 1):
                if isinstance(decision, dict):
                    print(f"{i}. {decision.get('text', 'No text')}")
                else:
                    print(f"{i}. {decision}")
        
        # Follow-ups
        followups = meeting.get('followUps', [])
        print(f"\n{'─'*80}")
        print(f"FOLLOW-UPS: {len(followups)}")
        print(f"{'─'*80}\n")
        
        if followups:
            for i, followup in enumerate(followups, 1):
                if isinstance(followup, dict):
                    print(f"{i}. {followup.get('text', 'No text')}")
                else:
                    print(f"{i}. {followup}")
        
        # Transcript
        transcript = meeting.get('transcript', '')
        print(f"\n{'─'*80}")
        print(f"TRANSCRIPT LENGTH: {len(transcript)} characters")
        print(f"{'─'*80}\n")
        
        # Show first 500 chars of transcript
        if transcript:
            print("First 500 characters:")
            print(transcript[:500])
            print("...")
        
        # Meeting debt
        debt = meeting.get('meetingDebt', 0)
        print(f"\n{'─'*80}")
        print(f"MEETING DEBT: ${debt}")
        print(f"{'─'*80}\n")
        
        # Analysis
        print(f"{'='*80}")
        print(f"ANALYSIS")
        print(f"{'='*80}\n")
        
        expected_actions = 23
        actual_actions = len(actions)
        
        print(f"Expected action items: {expected_actions}")
        print(f"Actual action items: {actual_actions}")
        print(f"Missing: {expected_actions - actual_actions}")
        print(f"Extraction rate: {(actual_actions / expected_actions * 100):.1f}%\n")
        
        if actual_actions < expected_actions:
            print(f"❌ ISSUE: Only extracted {actual_actions}/{expected_actions} action items ({(actual_actions / expected_actions * 100):.1f}%)")
            print(f"   This is a significant under-extraction.\n")
        
        expected_decisions = 8
        actual_decisions = len(decisions)
        
        print(f"Expected decisions: {expected_decisions}")
        print(f"Actual decisions: {actual_decisions}")
        print(f"Missing: {expected_decisions - actual_decisions}")
        print(f"Extraction rate: {(actual_decisions / expected_decisions * 100):.1f}%\n")
        
        if actual_decisions < expected_decisions:
            print(f"❌ ISSUE: Only extracted {actual_decisions}/{expected_decisions} decisions ({(actual_decisions / expected_decisions * 100):.1f}%)")
        
        grade = meeting.get('healthGrade', 'N/A')
        if grade in ['D', 'E', 'F']:
            print(f"\n❌ ISSUE: Low grade ({grade}) - should be A or B for a productive meeting")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
