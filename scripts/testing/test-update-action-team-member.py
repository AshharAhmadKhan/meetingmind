#!/usr/bin/env python3
"""
Test update-action Lambda with team member access
Verifies that team members can update action items
"""

import boto3
import json
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

# Tables
meetings_table = dynamodb.Table('meetingmind-meetings')
teams_table = dynamodb.Table('meetingmind-teams')

def test_update_action_team_member():
    """Test that team member can update action items"""
    
    print("=" * 80)
    print("TEST: Update Action - Team Member Access")
    print("=" * 80)
    
    # Get a V1 team meeting
    print("\n1. Finding V1 team meeting...")
    response = meetings_table.scan(
        FilterExpression='attribute_exists(teamId)',
        Limit=1
    )
    
    if not response['Items']:
        print("❌ No team meetings found")
        return False
    
    meeting = response['Items'][0]
    meeting_id = meeting['meetingId']
    team_id = meeting['teamId']
    uploader_id = meeting['userId']
    
    print(f"   Meeting ID: {meeting_id}")
    print(f"   Team ID: {team_id}")
    print(f"   Uploader: {uploader_id}")
    
    # Get team members
    print("\n2. Getting team members...")
    team_response = teams_table.get_item(Key={'teamId': team_id})
    if 'Item' not in team_response:
        print("❌ Team not found")
        return False
    
    team = team_response['Item']
    members = team.get('members', [])
    
    # Find a team member who is NOT the uploader
    team_member_id = None
    for member in members:
        member_id = member.get('userId') if isinstance(member, dict) else member
        if member_id != uploader_id:
            team_member_id = member_id
            break
    
    if not team_member_id:
        print("❌ No other team members found")
        return False
    
    print(f"   Team member: {team_member_id}")
    
    # Get an action item from the meeting
    print("\n3. Getting action items...")
    actions = meeting.get('actionItems', [])
    if not actions:
        print("❌ No action items found")
        return False
    
    action = actions[0]
    action_id = action['id']
    current_status = action.get('status', 'todo')
    
    print(f"   Action ID: {action_id}")
    print(f"   Current status: {current_status}")
    print(f"   Task: {action.get('task') or action.get('text')}")
    
    # Simulate Lambda invocation with team member credentials
    print("\n4. Simulating update-action Lambda call...")
    print(f"   Toggling status from {current_status} to {'done' if current_status != 'done' else 'todo'}")
    
    # Create mock event
    new_status = 'done' if current_status != 'done' else 'todo'
    event = {
        'httpMethod': 'PUT',
        'pathParameters': {
            'meetingId': meeting_id,
            'actionId': action_id
        },
        'body': json.dumps({
            'status': new_status,
            'completed': new_status == 'done'
        }),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': team_member_id  # Team member, not uploader
                }
            }
        }
    }
    
    try:
        # Invoke Lambda
        response = lambda_client.invoke(
            FunctionName='meetingmind-update-action',
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"\n   Lambda Response:")
        print(f"   Status Code: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            print(f"   ✅ SUCCESS: Action updated")
            print(f"   New status: {body.get('status')}")
            print(f"   Completed: {body.get('completed')}")
            
            # Verify in DynamoDB
            print("\n5. Verifying update in DynamoDB...")
            verify_response = meetings_table.get_item(
                Key={'userId': uploader_id, 'meetingId': meeting_id}
            )
            
            if 'Item' in verify_response:
                updated_meeting = verify_response['Item']
                updated_actions = updated_meeting.get('actionItems', [])
                updated_action = next((a for a in updated_actions if a['id'] == action_id), None)
                
                if updated_action:
                    print(f"   ✅ Verified: Action status is now {updated_action.get('status')}")
                    return True
                else:
                    print(f"   ❌ Action not found after update")
                    return False
            else:
                print(f"   ❌ Meeting not found after update")
                return False
        else:
            body = json.loads(result.get('body', '{}'))
            print(f"   ❌ FAILED: {body.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_update_action_team_member()
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: Team members can update action items")
    else:
        print("❌ TEST FAILED: Team members cannot update action items")
    print("=" * 80)
