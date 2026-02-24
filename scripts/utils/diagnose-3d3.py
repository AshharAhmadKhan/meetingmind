#!/usr/bin/env python3
"""
Comprehensive diagnosis of meeting 3d3 to understand:
1. Why actions disappear after refresh
2. Why grade doesn't change when score improves
"""

import boto3
import json
from decimal import Decimal

REGION = 'ap-south-1'
TEST_EMAIL = 'ashkagakoko@gmail.com'
MEETING_ID = 'b99fa520-7a3e-4535-9471-2d617fd239df'

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
    
    print(f"User ID: {user_id}")
    print()
    
    try:
        response = meetings_table.get_item(
            Key={'userId': user_id, 'meetingId': MEETING_ID}
        )
        meeting = response.get('Item')
        
        if not meeting:
            print("Meeting not found")
            return
        
        print("=" * 80)
        print("MEETING 3D3 COMPREHENSIVE DIAGNOSIS")
        print("=" * 80)
        
        # Basic info
        print(f"\nBASIC INFO:")
        print(f"   Title: {meeting.get('title')}")
        print(f"   Meeting ID: {MEETING_ID}")
        print(f"   Status: {meeting.get('status')}")
        print(f"   Created: {meeting.get('createdAt')}")
        print(f"   Updated: {meeting.get('updatedAt')}")
        
        # Health metrics
        print(f"\nHEALTH METRICS:")
        print(f"   Health Score: {meeting.get('healthScore')}")
        print(f"   Health Grade: {meeting.get('healthGrade')}")
        print(f"   Health Label: {meeting.get('healthLabel')}")
        
        # Action items analysis
        actions = meeting.get('actionItems', [])
        print(f"\nACTION ITEMS: {len(actions)} total")
        
        completed = [a for a in actions if a.get('completed')]
        print(f"   Completed: {len(completed)}/{len(actions)} ({len(completed)/len(actions)*100:.1f}%)")
        
        # Check for duplicate IDs
        action_ids = [a.get('id') for a in actions]
        duplicate_ids = [id for id in action_ids if action_ids.count(id) > 1]
        if duplicate_ids:
            print(f"   WARNING  DUPLICATE IDs FOUND: {set(duplicate_ids)}")
        else:
            print(f"   OK All action IDs are unique")
        
        # Check for missing IDs
        missing_ids = [i for i, a in enumerate(actions) if not a.get('id')]
        if missing_ids:
            print(f"   WARNING  MISSING IDs at indices: {missing_ids}")
        else:
            print(f"   OK All actions have IDs")
        
        # Show all actions with completion status
        print(f"\n   ACTION DETAILS:")
        for i, action in enumerate(actions, 1):
            status_icon = 'OK' if action.get('completed') else 'X'
            print(f"   {status_icon} {i}. {action.get('task', 'NO TASK')[:70]}...")
            print(f"      ID: {action.get('id')}")
            print(f"      Completed: {action.get('completed')}")
            print(f"      Status: {action.get('status')}")
            print(f"      Owner: {action.get('owner')}")
            print(f"      CompletedAt: {action.get('completedAt')}")
        
        # Decisions
        decisions = meeting.get('decisions', [])
        print(f"\nDECISIONS: {len(decisions)} total")
        
        # Follow-ups
        followups = meeting.get('followUps', [])
        print(f"\nFOLLOW-UPS: {len(followups)} total")
        
        # ROI
        roi = meeting.get('roi', {})
        if roi:
            print(f"\nROI METRICS:")
            print(f"   ROI: {roi.get('roi')}%")
            print(f"   Value: ${roi.get('value')}")
            print(f"   Cost: ${roi.get('cost')}")
            print(f"   Decisions: {roi.get('decision_count')}")
            print(f"   Clear Actions: {roi.get('clear_action_count')}")
        
        # Calculate what health score SHOULD be
        print(f"\nHEALTH SCORE CALCULATION:")
        if len(actions) == 0:
            expected_score = 100.0
            print(f"   No actions = perfect score")
        else:
            total = len(actions)
            completed_count = len(completed)
            owned = sum(1 for a in actions if a.get('owner') and a['owner'] != 'Unassigned')
            
            # Calculate average risk
            risk_scores = [float(a.get('riskScore', 0)) for a in actions]
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            completion_rate = (completed_count / total) * 40
            owner_rate = (owned / total) * 30
            risk_inverted = ((100 - avg_risk) / 100) * 20
            recency_component = 10  # Assume recent
            
            expected_score = completion_rate + owner_rate + risk_inverted + recency_component
            expected_score = min(max(expected_score, 0), 100)
            
            print(f"   Total actions: {total}")
            print(f"   Completed: {completed_count} ({completed_count/total*100:.1f}%)")
            print(f"   Owned: {owned} ({owned/total*100:.1f}%)")
            print(f"   Avg risk: {avg_risk:.1f}")
            print(f"   ")
            print(f"   Completion component: {completion_rate:.1f} (40% weight)")
            print(f"   Owner component: {owner_rate:.1f} (30% weight)")
            print(f"   Risk component: {risk_inverted:.1f} (20% weight)")
            print(f"   Recency component: {recency_component:.1f} (10% weight)")
            print(f"   ")
            print(f"   EXPECTED SCORE: {expected_score:.1f}/100")
            print(f"   STORED SCORE: {meeting.get('healthScore')}/100")
            
            # Determine expected grade
            if expected_score >= 90:
                expected_grade = 'A'
            elif expected_score >= 80:
                expected_grade = 'B'
            elif expected_score >= 70:
                expected_grade = 'C'
            elif expected_score >= 60:
                expected_grade = 'D'
            else:
                expected_grade = 'F'
            
            print(f"   EXPECTED GRADE: {expected_grade}")
            print(f"   STORED GRADE: {meeting.get('healthGrade')}")
        
        # Check for autopsy
        print(f"\nAUTOPSY:")
        if meeting.get('autopsy'):
            print(f"   {meeting.get('autopsy')}")
        else:
            print(f"   No autopsy (score >= 60)")
        
        print("\n" + "=" * 80)
        print("DIAGNOSIS SUMMARY:")
        print("=" * 80)
        
        # Issue 1: Actions disappearing
        if duplicate_ids:
            print(f"\nERROR ISSUE 1: DUPLICATE ACTION IDs")
            print(f"   Found duplicate IDs: {set(duplicate_ids)}")
            print(f"   This causes actions to overwrite each other on update")
            print(f"   Solution: Ensure all action IDs are unique")
        elif missing_ids:
            print(f"\nERROR ISSUE 1: MISSING ACTION IDs")
            print(f"   Some actions don't have IDs")
            print(f"   This causes update failures")
            print(f"   Solution: Ensure all actions have unique IDs")
        else:
            print(f"\nOK ISSUE 1: All action IDs are unique and present")
        
        # Issue 2: Grade not updating
        stored_score = float(meeting.get('healthScore', 0))
        if abs(stored_score - expected_score) > 1:
            print(f"\nERROR ISSUE 2: HEALTH SCORE MISMATCH")
            print(f"   Stored: {stored_score:.1f}")
            print(f"   Expected: {expected_score:.1f}")
            print(f"   Difference: {abs(stored_score - expected_score):.1f}")
            print(f"   Reason: Health score is NOT recalculated on action update")
            print(f"   Solution: update-action Lambda needs to recalculate health score")
        else:
            print(f"\nOK ISSUE 2: Health score matches expected value")
        
        print("\n")
        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()

