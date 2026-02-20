"*70 + "\n")

if __name__ == '__main__':
    main()
      ':name': 'V2 - Active',
            ':now': datetime.utcnow().isoformat() + 'Z'
        }
    )
    print("✓ V2 team teamName updated to 'V2 - Active'")
    
    # Verify
    print("\nVerifying...")
    response = teams_table.scan()
    for team in response['Items']:
        print(f"\n  Team: {team.get('teamName', 'NO TEAMNAME')}")
        print(f"    TeamId: {team['teamId']}")
        print(f"    Members: {len(team.get('members', []))}")
    
    print("\n" + "="*70)
    print("  FIXED")
    print("=pdateExpression='SET teamName = :name, updatedAt = :now',
        ExpressionAttributeValues={
            ':name': 'V1 - Legacy',
            ':now': datetime.utcnow().isoformat() + 'Z'
        }
    )
    print("✓ V1 team teamName updated to 'V1 - Legacy'")
    
    # Fix V2 team
    print("Fixing V2 team...")
    teams_table.update_item(
        Key={'teamId': 'df29c543-a4d0-4c80-a086-6c11712d66f3'},
        UpdateExpression='SET teamName = :name, updatedAt = :now',
        ExpressionAttributeValues={
      #!/usr/bin/env python3
"""
Fix team names - update teamName field (not name field)
"""
import boto3
from datetime import datetime

REGION = 'ap-south-1'
dynamodb = boto3.resource('dynamodb', region_name=REGION)

def main():
    print("\n" + "="*70)
    print("  FIX TEAM NAMES")
    print("="*70 + "\n")
    
    teams_table = dynamodb.Table('meetingmind-teams')
    
    # Fix V1 team
    print("Fixing V1 team...")
    teams_table.update_item(
        Key={'teamId': '95febcb2-97e2-4395-bdde-da8475dbae0d'},
        U