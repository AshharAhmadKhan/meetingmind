#!/usr/bin/env python3
"""
Seed V1 Historical Data for Demo
Creates 3 failed meetings with 11 graveyard items for "Project V1 - Legacy" team
"""

import boto3
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

# AWS Configuration
REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def get_team_id(team_name):
    """Get team ID by name"""
    teams_table = dynamodb.Table('meetingmind-teams')
    response = teams_table.scan(
        FilterExpression='teamName = :name',
        ExpressionAttributeValues={':name': team_name}
    )
    if response['Items']:
        return response['Items'][0]['teamId']
    return None

def create_v1_meeting_1(user_id, team_id):
    """Meeting 1: The Kickoff - Grade D"""
    meeting_id = str(uuid.uuid4())
    created_at = (datetime.now() - timedelta(days=91)).isoformat()
    
    meeting = {
        'userId': user_id,
        'meetingId': meeting_id,
        'teamId': team_id,
        'title': 'V1 Meeting 1: The Kickoff',
        'status': 'DONE',
        'createdAt': created_at,
        'updatedAt': created_at,
        'audioUrl': f's3://meetingmind-audio-707411439284/{meeting_id}.mp3',
        'transcript': 'Historical V1 meeting - imported for analysis',
        'summary': 'Team held initial kickoff meeting with high energy and ambitious goals. One vague decision was made about building something useful. Six action items were created, most without clear owners or deadlines. Meeting lacked structure and accountability mechanisms.',
        'healthScore': 'D',
        'attendees': ['Zeeshan', 'Alishba', 'Aayush'],
        'decisions': [
            {
                'id': str(uuid.uuid4()),
                'text': 'We will build something people actually use',
                'timestamp': created_at
            }
        ],
        'actionItems': [
            {
                'id': str(uuid.uuid4()),
                'text': 'Handle the backend architecture',
                'owner': 'Unassigned',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('95'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Figure out the tech stack',
                'owner': 'Unassigned',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('90'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Design the UI mockups',
                'owner': 'Alishba',
                'deadline': 'Next week',
                'status': 'PENDING',
                'riskScore': Decimal('75'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Set up the GitHub repo',
                'owner': 'Zeeshan',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('70'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Write up our idea properly',
                'owner': 'Unassigned',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('85'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Research existing tools',
                'owner': 'Aayush',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('65'),
                'createdAt': created_at,
                'daysOld': Decimal('91')
            }
        ],
        'patterns': ['Planning Paralysis', 'Action Item Amnesia'],
        'meetingCost': Decimal('225'),
        'meetingValue': Decimal('0'),
        'roi': Decimal('-100')
    }
    
    table.put_item(Item=meeting)
    print(f"✓ Created Meeting 1: The Kickoff (Grade D)")
    return meeting_id

def create_v1_meeting_2(user_id, team_id):
    """Meeting 2: The Cracks - Grade F"""
    meeting_id = str(uuid.uuid4())
    created_at = (datetime.now() - timedelta(days=80)).isoformat()
    
    meeting = {
        'userId': user_id,
        'meetingId': meeting_id,
        'teamId': team_id,
        'title': 'V1 Meeting 2: The Cracks',
        'status': 'DONE',
        'createdAt': created_at,
        'updatedAt': created_at,
        'audioUrl': f's3://meetingmind-audio-707411439284/{meeting_id}.mp3',
        'transcript': 'Historical V1 meeting - imported for analysis',
        'summary': 'Team reconvened after 11 days with minimal progress. Confusion about task ownership led to defensive exchanges. Same blockers from Meeting 1 remained unresolved. Five new action items created, all vague or unassigned. Meeting revealed systemic accountability breakdown.',
        'healthScore': 'F',
        'attendees': ['Zeeshan', 'Alishba', 'Aayush'],
        'decisions': [],
        'actionItems': [
            {
                'id': str(uuid.uuid4()),
                'text': 'Fix the backend setup',
                'owner': 'Unassigned',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('95'),
                'createdAt': created_at,
                'daysOld': Decimal('80'),
                'chronicBlocker': True
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Finish the UI mockups',
                'owner': 'Alishba',
                'deadline': 'Overdue',
                'status': 'PENDING',
                'riskScore': Decimal('80'),
                'createdAt': created_at,
                'daysOld': Decimal('80')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Document the API plan',
                'owner': 'Zeeshan',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('75'),
                'createdAt': created_at,
                'daysOld': Decimal('80')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Set up the database',
                'owner': 'Aayush',
                'deadline': 'This week maybe',
                'status': 'PENDING',
                'riskScore': Decimal('85'),
                'createdAt': created_at,
                'daysOld': Decimal('80')
            },
            {
                'id': str(uuid.uuid4()),
                'text': 'Talk to potential users',
                'owner': 'Unassigned',
                'deadline': None,
                'status': 'PENDING',
                'riskScore': Decimal('70'),
                'createdAt': created_at,
                'daysOld': Decimal('80')
            }
        ],
        'patterns': ['Chronic Blocker', 'Meeting Debt Spiral', 'Action Item Amnesia'],
        'meetingCost': Decimal('225'),
        'meetingValue': Decimal('0'),
        'roi': Decimal('-100')
    }
    
    table.put_item(Item=meeting)
    print(f"✓ Created Meeting 2: The Cracks (Grade F)")
    return meeting_id

def create_v1_meeting_3(user_id, team_id):
    """Meeting 3: The Quiet Funeral - Grade GHOST"""
    meeting_id = str(uuid.uuid4())
    created_at = (datetime.now() - timedelta(days=66)).isoformat()
    
    meeting = {
        'userId': user_id,
        'meetingId': meeting_id,
        'teamId': team_id,
        'title': 'V1 Meeting 3: The Quiet Funeral',
        'status': 'DONE',
        'createdAt': created_at,
        'updatedAt': created_at,
        'audioUrl': f's3://meetingmind-audio-707411439284/{meeting_id}.mp3',
        'transcript': 'Historical V1 meeting - imported for analysis',
        'summary': 'Team discussed project status. Acknowledged delays and communication gaps. No concrete decisions were made. No action items were assigned. Meeting ended with vague plans to reconnect. This was the last V1 meeting. The project was quietly abandoned.',
        'healthScore': 'GHOST',
        'attendees': ['Zeeshan', 'Alishba', 'Aayush'],
        'decisions': [],
        'actionItems': [],
        'patterns': ['Ghost Meeting'],
        'meetingCost': Decimal('375'),
        'meetingValue': Decimal('0'),
        'roi': Decimal('-100')
    }
    
    table.put_item(Item=meeting)
    print(f"✓ Created Meeting 3: The Quiet Funeral (Grade GHOST)")
    return meeting_id

def main():
    print("🌱 Seeding V1 Historical Data...")
    print()
    
    # Get team ID
    team_id = get_team_id('Project V1 - Legacy')
    if not team_id:
        print("❌ Error: Team 'Project V1 - Legacy' not found!")
        print("   Please create the team first.")
        return
    
    print(f"✓ Found team: Project V1 - Legacy ({team_id})")
    print()
    
    # Use Zeeshan's account (thecyberprinciples@gmail.com)
    # You'll need to get the actual userId from Cognito
    user_id = input("Enter Zeeshan's userId (from Cognito): ")
    
    print()
    print("Creating V1 meetings...")
    
    # Create all 3 meetings
    create_v1_meeting_1(user_id, team_id)
    create_v1_meeting_2(user_id, team_id)
    create_v1_meeting_3(user_id, team_id)
    
    print()
    print("✅ V1 Historical Data Seeded Successfully!")
    print()
    print("Summary:")
    print("  • 3 meetings created (D, F, GHOST)")
    print("  • 11 action items (all abandoned)")
    print("  • 5 patterns triggered")
    print("  • $825 meeting debt")
    print("  • 0% completion rate")
    print()
    print("Next: Open the app and verify:")
    print("  1. Switch to 'Project V1 - Legacy' team")
    print("  2. Check Dashboard for 3 meetings")
    print("  3. Check Graveyard for 11 tombstones")
    print("  4. Check Patterns for 5 toxic patterns")
    print("  5. Check Debt Dashboard for $825")

if __name__ == '__main__':
    main()
