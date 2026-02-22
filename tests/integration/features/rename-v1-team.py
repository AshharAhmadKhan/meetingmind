#!/usr/bin/env python3
"""
Rename the team with V1 meetings to "V1 - Legacy" for clarity
"""
import boto3
from datetime import datetime

REGION = 'ap-south-1'
V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'
NEW_TEAM_NAME = 'V1 - Legacy'

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def main():
    print("\n" + "="*70)
    print("  RENAME V1 TEAM")
    print("="*70 + "\n")
    
    teams_table = dynamodb.Table('meetingmind-teams')
    
    # Get current team
    print(f"📋 Fetching team {V1_TEAM_ID}...")
    response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    
    if 'Item' not in response:
        print(f"❌ Team not found: {V1_TEAM_ID}")
        return
    
    team = response['Item']
    old_name = team.get('name', 'Unnamed')
    
    print(f"✓ Current name: '{old_name}'")
    print(f"✓ Members: {len(team.get('members', []))}")
    
    # Update team name
    print(f"\n🔄 Renaming to '{NEW_TEAM_NAME}'...")
    
    teams_table.update_item(
        Key={'teamId': V1_TEAM_ID},
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
    response = teams_table.get_item(Key={'teamId': V1_TEAM_ID})
    updated_team = response['Item']
    
    print(f"✓ New name: '{updated_team.get('name')}'")
    print(f"✓ Updated at: {updated_team.get('updatedAt')}")
    
    print("\n" + "="*70)
    print("  SUCCESS")
    print("="*70)
    print(f"\n💡 Now Keldeo can select 'V1 - Legacy' from the team dropdown")
    print(f"   and see all the historical V1 meetings!\n")

if __name__ == '__main__':
    main()
