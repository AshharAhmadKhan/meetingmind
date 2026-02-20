#!/usr/bin/env python3
"""
Check current database state - teams, members, meetings
"""
import boto3
import json

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'

cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def get_user_email(user_id):
    """Get email for a user ID"""
    try:
        response = cognito.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id
        )
        for attr in response['UserAttributes']:
            if attr['Name'] == 'email':
                return attr['Value']
    except:
        pass
    return 'Unknown'

def main():
    print("\n" + "="*80)
    print("  CURRENT DATABASE STATE")
    print("="*80)
    
    # Get all teams
    teams_table = dynamodb.Table('meetingmind-teams')
    teams_response = teams_table.scan()
    teams = teams_response['Items']
    
    print_section(f"TEAMS ({len(teams)} total)")
    
    for team in teams:
        team_id = team.get('teamId')
        team_name = team.get('teamName', team.get('name', 'Unnamed'))
        invite_code = team.get('inviteCode', 'N/A')
        members = team.get('members', [])
        
        print(f"Team: {team_name}")
        print(f"  TeamId: {team_id}")
        print(f"  InviteCode: {invite_code}")
        print(f"  Members: {len(members)}")
        
        for i, member in enumerate(members, 1):
            if isinstance(member, dict):
                email = member.get('email', 'Unknown')
                role = member.get('role', 'member')
                user_id = member.get('userId', 'Unknown')
                print(f"    {i}. {email} ({role})")
                print(f"       UserId: {user_id}")
            else:
                # Old format - just userId string
                email = get_user_email(member)
                print(f"    {i}. {email}")
                print(f"       UserId: {member}")
        
        # Get meetings for this team
        meetings_table = dynamodb.Table('meetingmind-meetings')
        try:
            meetings_response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': team_id}
            )
            meetings = meetings_response['Items']
            
            print(f"  Meetings: {len(meetings)}")
            
            for j, meeting in enumerate(meetings, 1):
                title = meeting.get('title', 'Untitled')
                status = meeting.get('status', 'Unknown')
                uploader_id = meeting.get('userId')
                uploader_email = meeting.get('email', get_user_email(uploader_id))
                meeting_id = meeting.get('meetingId')
                
                print(f"    {j}. {title}")
                print(f"       Status: {status}")
                print(f"       Uploaded by: {uploader_email}")
                print(f"       MeetingId: {meeting_id}")
                print(f"       TeamId in meeting: {meeting.get('teamId', 'MISSING')}")
        except Exception as e:
            print(f"  ❌ Error querying meetings: {e}")
        
        print()
    
    # Check GSI status
    print_section("GSI STATUS")
    
    dynamodb_client = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb_client.describe_table(TableName='meetingmind-meetings')
        table = response['Table']
        
        gsi_list = table.get('GlobalSecondaryIndexes', [])
        
        for gsi in gsi_list:
            print(f"GSI: {gsi['IndexName']}")
            print(f"  Status: {gsi['IndexStatus']}")
            print(f"  Projection: {gsi['Projection']['ProjectionType']}")
            
            keys = gsi['KeySchema']
            for key in keys:
                print(f"  {key['KeyType']}: {key['AttributeName']}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Get all users from Cognito
    print_section("COGNITO USERS")
    
    try:
        response = cognito.list_users(UserPoolId=USER_POOL_ID)
        users = response['Users']
        
        print(f"Total users: {len(users)}\n")
        
        for user in users:
            username = user['Username']
            email = 'Unknown'
            name = 'Unknown'
            
            for attr in user['Attributes']:
                if attr['Name'] == 'email':
                    email = attr['Value']
                elif attr['Name'] == 'name':
                    name = attr['Value']
            
            print(f"User: {email}")
            print(f"  Name: {name}")
            print(f"  UserId: {username}")
            print(f"  Status: {user['UserStatus']}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
