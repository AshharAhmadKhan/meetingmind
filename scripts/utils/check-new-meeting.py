#!/usr/bin/env python3
"""
Quick script to check the latest meeting for a user
Shows action items, decisions, and health metrics
"""

import boto3
import json
from datetime import datetime, timezone
from decimal import Decimal

REGION = 'ap-south-1'
TEST_EMAIL = 'ashkagakoko@gmail.com'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table('meetingmind-meetings')
cognito = boto3.client('cognito-idp', region_name=REGION)

def get_user_id(email):
    """Get user ID from Cognito"""
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
        print(f"Error getting user: {e}")
    return None

def get_latest_meeting(user_id):
    """Get the most recent meeting for user"""
    try:
        response = meetings_table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,  # Sort by newest first
            Limit=5
        )
        
        if response['Items']:
            # Sort by updatedAt to get truly latest
            items = sorted(response['Items'], 
                          key=lambda x: x.get('updatedAt', ''), 
                          reverse=True)
            return items[0]
        return None
    except Exception as e:
        print(f"Error getting meetings: {e}")
        return None

def main():
    print("=" * 80)
    print("LATEST MEETING ANALYSIS")
    print("=" * 80)
    
    user_id = get_user_id(TEST_EMAIL)
    if not user_id:
        print("❌ Could not find user")
        return
    
    meeting = get_latest_meeting(user_id)
    if not meeting:
        print("❌ No meetings found")
        return
    
    # Basic info
    print(f"\n📋 MEETING INFO:")
    print(f"   Title: {meeting.get('title', 'N/A')}")
    print(f"   Meeting ID: {meeting.get('meetingId', 'N/A')}")
    print(f"   Status: {meeting.get('status', 'N/A')}")
    print(f"   Created: {meeting.get('createdAt', 'N/A')}")
    print(f"   Updated: {meeting.get('updatedAt', 'N/A')}")
    
    # Action items
    actions = meeting.get('actionItems', [])
    print(f"\n✅ ACTION ITEMS: {len(actions)} total")
    
    if actions:
        print(f"\n   First 5 actions:")
        for i, action in enumerate(actions[:5], 1):
            task = action.get('task', '')
            owner = action.get('owner', 'Unassigned')
            deadline = action.get('deadline', 'No deadline')
            print(f"   {i}. {task[:60]}...")
            print(f"      Owner: {owner} | Deadline: {deadline}")
    
    # Decisions
    decisions = meeting.get('decisions', [])
    print(f"\n🎯 DECISIONS: {len(decisions)} total")
    
    if decisions:
        print(f"\n   All decisions:")
        for i, decision in enumerate(decisions, 1):
            if isinstance(decision, str):
                print(f"   {i}. {decision[:70]}...")
            else:
                print(f"   {i}. {decision}")
    
    # Follow-ups
    followups = meeting.get('followUps', [])
    print(f"\n🔄 FOLLOW-UPS: {len(followups)} total")
    
    # Health metrics
    print(f"\n💊 HEALTH METRICS:")
    print(f"   Score: {meeting.get('healthScore', 'N/A')}/100")
    print(f"   Grade: {meeting.get('healthGrade', 'N/A')}")
    print(f"   Label: {meeting.get('healthLabel', 'N/A')}")
    
    # ROI
    roi = meeting.get('roi', {})
    if roi:
        print(f"\n💰 ROI METRICS:")
        print(f"   Cost: ${roi.get('cost', 0)}")
        print(f"   Value: ${roi.get('value', 0)}")
        print(f"   ROI: {roi.get('roi', 0)}%")
        print(f"   Decisions: {roi.get('decision_count', 0)}")
        print(f"   Clear Actions: {roi.get('clear_action_count', 0)}")
    
    # Summary
    print(f"\n📝 SUMMARY:")
    summary = meeting.get('summary', '')
    if summary:
        print(f"   {summary}")
    
    print("\n" + "=" * 80)
    print("COMPARISON WITH EXPECTED:")
    print("=" * 80)
    print(f"   Action Items: {len(actions)}/23 expected (target: 20+)")
    print(f"   Decisions: {len(decisions)}/8 expected (target: 7+)")
    print(f"   Follow-ups: {len(followups)}/4 expected (target: 3+)")
    print(f"   Grade: {meeting.get('healthGrade', 'N/A')} (target: A or B)")
    
    # Calculate pass/fail
    action_pass = len(actions) >= 20
    decision_pass = len(decisions) >= 7
    grade_pass = meeting.get('healthGrade') in ['A', 'B']
    
    print(f"\n   Status:")
    print(f"   {'✅' if action_pass else '❌'} Action extraction: {'PASS' if action_pass else 'FAIL'}")
    print(f"   {'✅' if decision_pass else '❌'} Decision extraction: {'PASS' if decision_pass else 'FAIL'}")
    print(f"   {'✅' if grade_pass else '❌'} Grade accuracy: {'PASS' if grade_pass else 'FAIL'}")
    
    overall_pass = action_pass and decision_pass and grade_pass
    print(f"\n   Overall: {'✅ ALL TESTS PASSED' if overall_pass else '❌ SOME TESTS FAILED'}")
    
    print("\n")

if __name__ == '__main__':
    main()
