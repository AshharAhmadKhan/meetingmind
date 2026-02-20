#!/usr/bin/env python3
"""
Check what broke after renaming teams
"""
import boto3

REGION = 'ap-south-1'
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def main():
    print("\n" + "="*70)
    print("  CHECKING WHAT BROKE")
    print("="*70 + "\n")
    
    # Check all teams
    teams_table = dynamodb.Table('meetingmind-teams')
    response = teams_table.scan()
    teams = response['Items']
    
    print(f"Found {len(teams)} teams:\n")
    
    for team in teams:
        print(f"Team: {team.get('name', 'NO NAME FIELD')} / {team.get('teamName', 'NO TEAMNAME FIELD')}")
        print(f"  TeamId: {team['teamId']}")
        print(f"  Fields: {list(team.keys())}")
        print(f"  Members: {len(team.get('members', []))}")
        print()
    
    # Check meetings
    meetings_table = dynamodb.Table('meetingmind-meetings')
    
    print("\nChecking meetings with teamId:\n")
    
    for team in teams:
        team_id = team['teamId']
        try:
            response = meetings_table.query(
                IndexName='teamId-createdAt-index',
                KeyConditionExpression='teamId = :tid',
                ExpressionAttributeValues={':tid': team_id}
            )
            meetings = response['Items']
            print(f"Team {team.get('name', team.get('teamName', 'Unknown'))}: {len(meetings)} meetings")
        except Exception as e:
            print(f"Team {team_id}: ERROR - {e}")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
