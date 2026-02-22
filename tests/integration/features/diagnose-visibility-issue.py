#!/usr/bin/env python3
"""
Diagnose why team members can't see meetings
Test all 3 users in V1 team
"""
import boto3

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'

# Test users
USERS = [
    'thecyberprinciples@gmail.com',  # Uploader
    'thehiddenif@gmail.com',         # Team member
    'ashkagakoko@gmail.com',         # Team member (Keldeo)
]

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def get_user_id(email):
    response = cognito.list_users(
        UserPoolId=USER_POOL_ID,
        Filter=f'email = "{email}"'
    )
    if response['Users']:
        return response['Users'][0]['Username']
    return None

def test_user_access(email):
    print(f"\n{'='*70}")
    print(f"  Testing: {email}")
    print(f"{'='*70}\n")
    
    user_id = get_user_id(email)
    if not user_id:
        print(f"❌ User not found")
        return
    
    print(f"✓ UserId: {user_id}")
    
    # Check team membership
    teams_table = dynamodb.Table('meetingmind-teams')
    team_response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    
    if 'Item' not in team_response:
        print(f"❌ Team not found")
        return
    
    team = team_response['Item']
    members = team.get('members', [])
    
    # Check if user is member
    member_ids = []
    for member in members:
        if isinstance(member, dict):
            member_ids.append(member.get('userId'))
        else:
            member_ids.append(member)
    
    if user_id not in member_ids:
        print(f"❌ NOT a team member")
        return
    
    print(f"✓ IS a team member")
    
    # Query meetings
    meetings_table = dynamodb.Table('meetingmind-meetings')
    try:
        response = meetings_table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': V1_TEAM_ID}
        )
        meetings = response['Items']
        print(f"✓ Can query meetings: {len(meetings)} found")
        
        # Show which meetings
        for meeting in meetings:
            uploader_id = meeting.get('userId')
            uploader_email = "Unknown"
            for member in members:
                if isinstance(member, dict):
                    if member.get('userId') == uploader_id:
                        uploader_email = member.get('email', 'Unknown')
                        break
            
            print(f"  - {meeting.get('title', 'Untitled')}")
            print(f"    Uploaded by: {uploader_email}")
            print(f"    Status: {meeting.get('status', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  DIAGNOSE: Why can't team members see meetings?")
    print("="*70)
    
    results = {}
    for email in USERS:
        results[email] = test_user_access(email)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}\n")
    
    for email, can_see in results.items():
        status = "✓ CAN see meetings" if can_see else "❌ CANNOT see meetings"
        print(f"{email}: {status}")
    
    if all(results.values()):
        print(f"\n✅ ALL USERS CAN SEE MEETINGS")
        print(f"   The backend is working correctly")
        print(f"   Issue is likely frontend/browser related")
    else:
        print(f"\n❌ SOME USERS CANNOT SEE MEETINGS")
        print(f"   Backend issue detected")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
