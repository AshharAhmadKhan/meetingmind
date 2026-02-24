#!/usr/bin/env python3
"""
Test health score recalculation after deploying the fix.
Toggles an action and verifies health score updates.
"""

import boto3
import requests
import json
import time

# Configuration
MEETING_ID = "6f1f9423-a000-436e-a862-c96edb9f356d"
USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
TABLE_NAME = "meetingmind-meetings"
API_URL = "https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
USER_POOL_ID = "ap-south-1_mkFJawjMp"
CLIENT_ID = "150n899gkc651g6e0p7hacguac"
USERNAME = "yatra@meetingmind.ai"
PASSWORD = "Test@1234"

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
cognito = boto3.client('cognito-idp', region_name='ap-south-1')
table = dynamodb.Table(TABLE_NAME)

def get_auth_token():
    """Get Cognito auth token"""
    response = cognito.admin_initiate_auth(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': USERNAME,
            'PASSWORD': PASSWORD
        }
    )
    return response['AuthenticationResult']['IdToken']

def get_meeting():
    """Get meeting from DynamoDB"""
    response = table.get_item(Key={'userId': USER_ID, 'meetingId': MEETING_ID})
    return response.get('Item')

def toggle_action(action_id, completed, token):
    """Toggle action via API"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    body = {
        'completed': completed,
        'status': 'done' if completed else 'todo'
    }
    response = requests.put(
        f'{API_URL}/meetings/{MEETING_ID}/actions/{action_id}',
        headers=headers,
        json=body
    )
    return response.json()

def main():
    print("=" * 70)
    print("TESTING HEALTH SCORE RECALCULATION")
    print("=" * 70)
    
    # Get auth token
    print("\n1. Getting auth token...")
    token = get_auth_token()
    print("   ✓ Token obtained")
    
    # Get current meeting state
    print("\n2. Getting current meeting state...")
    meeting = get_meeting()
    actions = meeting['actionItems']
    current_health = float(meeting.get('healthScore', 0))
    current_grade = meeting.get('healthGrade', 'N/A')
    
    print(f"   Current health: {current_health}/100 (Grade: {current_grade})")
    print(f"   Total actions: {len(actions)}")
    print(f"   Completed: {sum(1 for a in actions if a.get('completed'))}")
    
    # Find a completed action to toggle
    completed_action = next((a for a in actions if a.get('completed')), None)
    if not completed_action:
        print("   ✗ No completed actions found to toggle")
        return
    
    action_id = completed_action['id']
    print(f"\n3. Toggling action {action_id} to incomplete...")
    
    # Toggle to incomplete
    response = toggle_action(action_id, False, token)
    print(f"   API Response: {response}")
    
    # Wait for DynamoDB to update
    print("\n4. Waiting 3 seconds for DynamoDB update...")
    time.sleep(3)
    
    # Check new health score
    print("\n5. Checking new health score...")
    updated_meeting = get_meeting()
    new_health = float(updated_meeting.get('healthScore', 0))
    new_grade = updated_meeting.get('healthGrade', 'N/A')
    new_completed = sum(1 for a in updated_meeting['actionItems'] if a.get('completed'))
    
    print(f"   New health: {new_health}/100 (Grade: {new_grade})")
    print(f"   New completed: {new_completed}/{len(actions)}")
    
    # Verify health score changed
    print("\n" + "=" * 70)
    if new_health != current_health:
        print("✓ SUCCESS: Health score recalculated!")
        print(f"  Old: {current_health}/100 ({current_grade})")
        print(f"  New: {new_health}/100 ({new_grade})")
        print(f"  Change: {new_health - current_health:+.1f} points")
    else:
        print("✗ FAILED: Health score did not change")
        print("  This means the fix is not working yet")
    print("=" * 70)
    
    # Toggle back to completed
    print("\n6. Toggling action back to completed...")
    toggle_action(action_id, True, token)
    time.sleep(2)
    
    final_meeting = get_meeting()
    final_health = float(final_meeting.get('healthScore', 0))
    final_grade = final_meeting.get('healthGrade', 'N/A')
    print(f"   Final health: {final_health}/100 (Grade: {final_grade})")
    
    if final_health == current_health:
        print("   ✓ Health score restored to original value")
    else:
        print(f"   ⚠ Health score is now {final_health} (was {current_health})")

if __name__ == '__main__':
    main()
