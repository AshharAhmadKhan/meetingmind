#!/usr/bin/env python3
"""
Check test meeting for ashkagakoko@gmail.com account
Analyze action items, decisions, grade, and identify any issues
"""

import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key

REGION = 'ap-south-1'
dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table('meetingmind-meetings')
actions_table = dynamodb.Table('meetingmind-actions')

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

def get_user_meetings(user_id):
    """Get all meetings for a user"""
    try:
        response = meetings_table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error getting meetings: {e}")
        return []

def get_meeting_actions(meeting_id):
    """Get all action items for a meeting"""
    try:
        response = actions_table.scan(
            FilterExpression=Key('meetingId').eq(meeting_id)
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error getting actions: {e}")
        return []

def analyze_meeting(meeting, actions):
    """Analyze meeting for issues"""
    issues = []
    
    # Check action items count
    action_count = len(actions)
    if action_count < 5:
        issues.append(f"⚠️ LOW ACTION ITEMS: Only {action_count} action items extracted (expected 20+)")
    
    # Check grade
    grade = meeting.get('healthGrade', 'N/A')
    if grade in ['D', 'E', 'F']:
        issues.append(f"⚠️ LOW GRADE: Meeting grade is {grade}")
    
    # Check decisions
    decisions = meeting.get('decisions', [])
    decision_count = len(decisions) if isinstance(decisions, list) else 0
    if decision_count < 3:
        issues.append(f"⚠️ LOW DECISIONS: Only {decision_count} decisions extracted (expected 8+)")
    
    # Check transcript
    transcript = meeting.get('transcript', '')
    if not transcript or len(transcript) < 1000:
        issues.append(f"⚠️ SHORT TRANSCRIPT: Transcript is too short ({len(transcript)} chars)")
    
    # Check action item details
    incomplete_actions = []
    for action in actions:
        if not action.get('owner'):
            incomplete_actions.append(f"Action '{action.get('text', 'Unknown')[:50]}' has no owner")
        if not action.get('deadline'):
            incomplete_actions.append(f"Action '{action.get('text', 'Unknown')[:50]}' has no deadline")
    
    if incomplete_actions:
        issues.append(f"⚠️ INCOMPLETE ACTIONS: {len(incomplete_actions)} actions missing owner/deadline")
    
    return issues

def main():
    email = 'ashkagakoko@gmail.com'
    print(f"\n{'='*80}")
    print(f"CHECKING TEST MEETING FOR: {email}")
    print(f"{'='*80}\n")
    
    # Get user ID
    user_id = get_user_id_by_email(email)
    if not user_id:
        print(f"❌ User not found: {email}")
        return
    
    print(f"✅ User ID: {user_id}\n")
    
    # Get meetings
    meetings = get_user_meetings(user_id)
    if not meetings:
        print(f"❌ No meetings found for user")
        return
    
    print(f"📊 Found {len(meetings)} meeting(s)\n")
    
    # Analyze each meeting
    for idx, meeting in enumerate(meetings, 1):
        meeting_id = meeting.get('meetingId')
        title = meeting.get('title', 'Untitled')
        status = meeting.get('status', 'Unknown')
        grade = meeting.get('healthGrade', 'N/A')
        created = meeting.get('createdAt', 'Unknown')
        
        print(f"\n{'─'*80}")
        print(f"MEETING #{idx}: {title}")
        print(f"{'─'*80}")
        print(f"Meeting ID: {meeting_id}")
        print(f"Status: {status}")
        print(f"Grade: {grade}")
        print(f"Created: {created}")
        
        # Get actions
        actions = get_meeting_actions(meeting_id)
        print(f"\n📋 ACTION ITEMS: {len(actions)}")
        
        for i, action in enumerate(actions, 1):
            text = action.get('text', 'No text')[:80]
            owner = action.get('owner', 'Unassigned')
            deadline = action.get('deadline', 'No deadline')
            status = action.get('status', 'Unknown')
            risk = action.get('riskScore', 0)
            print(f"  {i}. [{status}] {text}")
            print(f"     Owner: {owner} | Deadline: {deadline} | Risk: {risk}")
        
        # Get decisions
        decisions = meeting.get('decisions', [])
        print(f"\n🎯 DECISIONS: {len(decisions) if isinstance(decisions, list) else 0}")
        if isinstance(decisions, list):
            for i, decision in enumerate(decisions, 1):
                if isinstance(decision, dict):
                    print(f"  {i}. {decision.get('text', 'No text')[:100]}")
                else:
                    print(f"  {i}. {str(decision)[:100]}")
        
        # Get transcript length
        transcript = meeting.get('transcript', '')
        print(f"\n📝 TRANSCRIPT: {len(transcript)} characters")
        
        # Analyze for issues
        issues = analyze_meeting(meeting, actions)
        
        if issues:
            print(f"\n❌ ISSUES FOUND ({len(issues)}):")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"\n✅ NO ISSUES FOUND - Meeting looks good!")
        
        # Show meeting debt if available
        if 'meetingDebt' in meeting:
            debt = meeting['meetingDebt']
            print(f"\n💰 MEETING DEBT: ${debt}")
    
    print(f"\n{'='*80}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
