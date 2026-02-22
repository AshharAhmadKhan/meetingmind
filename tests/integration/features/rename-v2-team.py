#!/usr/bin/env python3
"""
Rename the team with V2 meetings to "V2 - Active" for clarity
"""
import boto3
from datetime import datetime

REGION = 'ap-south-1'
V2_TEAM_ID = 'df29c543-a4d0-4c80-a086-6c11712d66f3'
NEW_TEAM_NAME = 'V2 - Active'

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def main():
    print("\n" + "="*70)
    print("  RENAME V2 TEAM")
    print("="*70 + "\n")
    
    teams_table = dynamodb.Table('meetingmind-teams')
    
    # Get current team
    print(f"📋 Fetching team {V2_TEAM_ID}...")
    response = teams_table.get_item(Key={'teamId': V2_TEAM_ID})
    
    if 'Item' not in response:
        print(f"❌ Team not found: {V2_TEAM_ID}")
        return
    
    team = response['Item']
    old_name = team.get('name', 'Unnamed')
    
    print(f"✓ Current name: '{old_name}'")
    print(f"✓ Members: {len(team.get('members', []))}")
    
    # Update team name
    print(f"\n🔄 Renaming to '{NEW_TEAM_NAME}'...")
    
    teams_table.update_item(
        Key={'teamId': V2_TEAM_ID},
        UpdateExpression='SET #n = :name, updatedAt = :now',
        ExpressionAttributeNames={'#n': 'name'},
        ExpressionAttributeValues={
            ':name': NEW_TEAM_NAME,
            ':now': datetime.utcnow().isoformat() + 'Z'
        }
    )
    
    print(f"✓ Team renamed successfully!")
    
    # Verify
    print(f"\n🔍 Verifying...")
    response = teams_table.get_item(Key={'teamId': V2_TEAM_ID})
    updated_team = response['Item']
    
    print(f"✓ New name: '{updated_team.get('name')}'")
    print(f"✓ Updated at: {updated_team.get('updatedAt')}")
    
    print("\n" + "="*70)
    print("  SUCCESS")
    print("="*70)
    print(f"\n💡 Team renamed to '{NEW_TEAM_NAME}'\n")

if __name__ == '__main__':
    main()
