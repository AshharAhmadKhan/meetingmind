#!/usr/bin/env python3
"""
Create a comprehensive test meeting that exercises ALL MeetingMind features
This meeting is designed to test every aspect of the system with detailed logging
"""

import boto3
import json
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

# User and team info
USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"  # thecyberprinciples@gmail.com
USER_EMAIL = "thecyberprinciples@gmail.com"
TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"  # Project V1 - Legacy

def create_comprehensive_test_meeting():
    """
    Create a meeting that tests ALL features:
    1. Multiple action items (assigned + unassigned)
    2. Various deadlines (past, today, future, none)
    3. Different risk levels
    4. Decisions made
    5. Duplicate tasks (to test duplicate detection)
    6. Mix of completed and incomplete
    7. Proper embeddings (mock)
    8. Team assignment
    """
    
    meeting_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # Create action items that test different scenarios
    action_items = []
    
    # 1. HIGH RISK - Overdue task (tests debt calculation)
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Fix critical security vulnerability in auth system',
        'owner': 'Zeeshan',
        'deadline': (now - timedelta(days=3)).isoformat(),  # 3 days overdue
        'completed': False,
        'riskScore': Decimal('85'),
        'riskLevel': 'HIGH',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]  # Mock embedding
    })
    
    # 2. MEDIUM RISK - Due today (tests at-risk detection)
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Complete API documentation for v2 endpoints',
        'owner': 'Alishba',
        'deadline': now.isoformat(),  # Due today
        'completed': False,
        'riskScore': Decimal('65'),
        'riskLevel': 'MEDIUM',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # 3. LOW RISK - Future deadline with owner (tests healthy task)
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Research AWS Lambda pricing options',
        'owner': 'Aayush',
        'deadline': (now + timedelta(days=7)).isoformat(),  # 7 days from now
        'completed': False,
        'riskScore': Decimal('25'),
        'riskLevel': 'LOW',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # 4. UNASSIGNED - No owner (tests unassigned debt)
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Draft database schema for new features',
        'owner': 'Unassigned',
        'deadline': (now + timedelta(days=5)).isoformat(),
        'completed': False,
        'riskScore': Decimal('70'),
        'riskLevel': 'MEDIUM',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # 5. NO DEADLINE - Tests forgotten category
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Update team documentation wiki',
        'owner': 'Zeeshan',
        'deadline': None,
        'completed': False,
        'riskScore': Decimal('50'),
        'riskLevel': 'MEDIUM',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # 6. COMPLETED TASK - Tests graveyard and completion rate
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Set up CI/CD pipeline',
        'owner': 'Aayush',
        'deadline': (now - timedelta(days=1)).isoformat(),
        'completed': True,
        'completedAt': now.isoformat(),
        'riskScore': Decimal('30'),
        'riskLevel': 'LOW',
        'createdAt': (now - timedelta(days=5)).isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # 7. DUPLICATE TASK - Similar to existing task (tests duplicate detection)
    action_items.append({
        'id': str(uuid.uuid4()),
        'task': 'Create database design document',  # Similar to "Draft database schema"
        'owner': 'Alishba',
        'deadline': (now + timedelta(days=10)).isoformat(),
        'completed': False,
        'riskScore': Decimal('40'),
        'riskLevel': 'LOW',
        'createdAt': now.isoformat(),
        'embedding': [Decimal(str(i/1536.0)) for i in range(1536)]
    })
    
    # Calculate metrics
    total_actions = len(action_items)
    completed_count = sum(1 for a in action_items if a['completed'])
    incomplete_count = total_actions - completed_count
    completion_rate = (completed_count / total_actions * 100) if total_actions > 0 else 0
    
    # Calculate health score (0-100)
    assigned_count = sum(1 for a in action_items if not a['completed'] and a['owner'] != 'Unassigned')
    incomplete_incomplete = sum(1 for a in action_items if not a['completed'])
    
    completion_score = (completed_count / total_actions * 40) if total_actions > 0 else 0
    assignment_score = (assigned_count / incomplete_incomplete * 30) if incomplete_incomplete > 0 else 0
    avg_risk = sum(float(a['riskScore']) for a in action_items if not a['completed']) / incomplete_incomplete if incomplete_incomplete > 0 else 0
    risk_score = ((100 - avg_risk) / 100 * 20)
    recency_bonus = 10  # Recent meeting
    
    health_score = int(completion_score + assignment_score + risk_score + recency_bonus)
    
    # Calculate ROI
    decisions_made = 3  # Simulated
    clear_actions = sum(1 for a in action_items if not a['completed'] and a['owner'] != 'Unassigned' and a['deadline'])
    
    value = (decisions_made * 500) + (clear_actions * 200)
    cost = 4 * 0.5 * 75  # 4 attendees, 0.5 hours, $75/hr
    roi = ((value - cost) / cost * 100) if cost > 0 else 0
    
    # Create meeting object
    meeting = {
        'userId': USER_ID,
        'meetingId': meeting_id,
        'teamId': TEAM_ID,
        'title': 'Comprehensive Feature Test Meeting',
        'createdAt': now.isoformat(),
        'actionItems': action_items,
        'decisions': [
            'Decided to use AWS Lambda for serverless architecture',
            'Approved budget increase for cloud infrastructure',
            'Agreed on weekly sprint cadence'
        ],
        'healthScore': Decimal(str(health_score)),
        'healthGrade': 'B' if health_score >= 70 else 'C' if health_score >= 50 else 'D',
        'roi': Decimal(str(int(roi))),
        'completionRate': Decimal(str(int(completion_rate))),
        'totalActions': total_actions,
        'completedActions': completed_count,
        'incompleteActions': incomplete_count,
        'transcript': 'This is a comprehensive test meeting designed to exercise all MeetingMind features...',
        'duration': 30,
        'attendees': ['Zeeshan', 'Alishba', 'Aayush', 'Sarah']
    }
    
    return meeting

def insert_meeting(meeting):
    """Insert meeting into DynamoDB"""
    try:
        meetings_table.put_item(Item=meeting)
        return True
    except Exception as e:
        print(f"❌ Error inserting meeting: {e}")
        return False

def log_test_scenarios(meeting):
    """Log all test scenarios this meeting covers"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST MEETING CREATED")
    print("="*70)
    print()
    print(f"Meeting ID: {meeting['meetingId']}")
    print(f"Title: {meeting['title']}")
    print(f"Team: Project V1 - Legacy")
    print(f"Created: {meeting['createdAt']}")
    print()
    
    print("="*70)
    print("TEST SCENARIOS COVERED")
    print("="*70)
    print()
    
    action_items = meeting['actionItems']
    
    print("1. ✅ RISK LEVELS")
    high_risk = [a for a in action_items if a['riskLevel'] == 'HIGH']
    medium_risk = [a for a in action_items if a['riskLevel'] == 'MEDIUM']
    low_risk = [a for a in action_items if a['riskLevel'] == 'LOW']
    print(f"   HIGH: {len(high_risk)} | MEDIUM: {len(medium_risk)} | LOW: {len(low_risk)}")
    print()
    
    print("2. ✅ DEADLINE SCENARIOS")
    overdue = [a for a in action_items if not a['completed'] and a['deadline'] and datetime.fromisoformat(a['deadline'].replace('Z', '+00:00')) < datetime.now(timezone.utc)]
    due_today = [a for a in action_items if not a['completed'] and a['deadline'] and datetime.fromisoformat(a['deadline'].replace('Z', '+00:00')).date() == datetime.now(timezone.utc).date()]
    future = [a for a in action_items if not a['completed'] and a['deadline'] and datetime.fromisoformat(a['deadline'].replace('Z', '+00:00')) > datetime.now(timezone.utc) and datetime.fromisoformat(a['deadline'].replace('Z', '+00:00')).date() != datetime.now(timezone.utc).date()]
    no_deadline = [a for a in action_items if not a['completed'] and not a['deadline']]
    print(f"   Overdue: {len(overdue)} | Due Today: {len(due_today)} | Future: {len(future)} | No Deadline: {len(no_deadline)}")
    print()
    
    print("3. ✅ OWNERSHIP")
    assigned = [a for a in action_items if not a['completed'] and a['owner'] != 'Unassigned']
    unassigned = [a for a in action_items if not a['completed'] and a['owner'] == 'Unassigned']
    print(f"   Assigned: {len(assigned)} | Unassigned: {len(unassigned)}")
    print()
    
    print("4. ✅ COMPLETION STATUS")
    completed = [a for a in action_items if a['completed']]
    incomplete = [a for a in action_items if not a['completed']]
    print(f"   Completed: {len(completed)} | Incomplete: {len(incomplete)}")
    print(f"   Completion Rate: {meeting['completionRate']}%")
    print()
    
    print("5. ✅ EMBEDDINGS")
    with_embeddings = [a for a in action_items if a.get('embedding')]
    print(f"   All {len(with_embeddings)}/{len(action_items)} actions have embeddings")
    print()
    
    print("6. ✅ DECISIONS")
    print(f"   {len(meeting['decisions'])} decisions made")
    print()
    
    print("7. ✅ METRICS")
    print(f"   Health Score: {meeting['healthScore']}/100 (Grade: {meeting['healthGrade']})")
    print(f"   ROI: {meeting['roi']}%")
    print(f"   Total Actions: {meeting['totalActions']}")
    print()
    
    print("="*70)
    print("ACTION ITEMS BREAKDOWN")
    print("="*70)
    print()
    
    for i, action in enumerate(action_items, 1):
        status = "✅ DONE" if action['completed'] else "⏳ PENDING"
        deadline_str = action['deadline'][:10] if action['deadline'] else "No deadline"
        print(f"{i}. [{status}] {action['task']}")
        print(f"   Owner: {action['owner']} | Deadline: {deadline_str}")
        print(f"   Risk: {action['riskLevel']} ({action['riskScore']}/100)")
        print()
    
    print("="*70)
    print("FEATURES TO TEST IN UI")
    print("="*70)
    print()
    print("Dashboard:")
    print("  ✅ Meeting card shows correct health score and ROI")
    print("  ✅ Leaderboard shows Zeeshan, Alishba, Aayush")
    print("  ✅ Team selector shows V1 team")
    print()
    print("Meeting Detail:")
    print("  ✅ All 7 action items visible")
    print("  ✅ Risk badges (HIGH/MEDIUM/LOW)")
    print("  ✅ Overdue items highlighted")
    print("  ✅ Completion checkbox works")
    print("  ✅ Edit owner/deadline works")
    print()
    print("Actions Overview:")
    print("  ✅ Shows 6 incomplete items")
    print("  ✅ Filters by status work")
    print("  ✅ Filters by owner work")
    print()
    print("Kanban Board:")
    print("  ✅ Drag and drop between columns")
    print("  ✅ Items in correct columns (overdue/at-risk/on-track)")
    print()
    print("Graveyard:")
    print("  ✅ Shows 1 completed item")
    print("  ✅ Resurrect function works")
    print()
    print("Debt Dashboard:")
    print("  ✅ Shows debt from overdue/unassigned/at-risk")
    print("  ✅ Completion rate chart")
    print("  ✅ 8-week trend")
    print()
    print("Duplicate Detection (if Bedrock enabled):")
    print("  ✅ 'Create database design document' similar to existing 'Draft database schema'")
    print()
    print("="*70)

def main():
    print("\n" + "="*70)
    print("CREATING COMPREHENSIVE TEST MEETING")
    print("="*70)
    print()
    
    # Create meeting
    print("Step 1: Generating meeting data...")
    meeting = create_comprehensive_test_meeting()
    print("✅ Meeting data generated")
    print()
    
    # Insert into database
    print("Step 2: Inserting into DynamoDB...")
    success = insert_meeting(meeting)
    
    if success:
        print("✅ Meeting inserted successfully")
        print()
        
        # Log test scenarios
        log_test_scenarios(meeting)
        
        print("="*70)
        print("NEXT STEPS")
        print("="*70)
        print()
        print("1. Open MeetingMind in browser")
        print("2. Select 'Project V1 - Legacy' team")
        print("3. Find 'Comprehensive Feature Test Meeting'")
        print("4. Test all features listed above")
        print("5. Check console logs for any errors")
        print()
        print("Meeting ID for reference:")
        print(f"  {meeting['meetingId']}")
        print()
        print("="*70)
    else:
        print("❌ Failed to insert meeting")

if __name__ == '__main__':
    main()
