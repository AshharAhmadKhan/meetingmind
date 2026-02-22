#!/usr/bin/env python3
"""
Test script to verify Debt Dashboard shows real data (not mock data)
"""
import boto3
import json
from datetime import datetime, timezone

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

def test_debt_analytics():
    """Test that debt analytics are calculated from real meeting data"""
    
    print("=" * 60)
    print("DEBT DASHBOARD DATA TEST")
    print("=" * 60)
    
    # Get all meetings
    response = meetings_table.scan()
    meetings = response.get('Items', [])
    
    print(f"\n✓ Found {len(meetings)} meetings in database")
    
    # Calculate expected analytics
    total_actions = 0
    completed_actions = 0
    incomplete_actions = 0
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        for action in action_items:
            total_actions += 1
            if action.get('completed'):
                completed_actions += 1
            else:
                incomplete_actions += 1
    
    print(f"\n📊 Action Items Summary:")
    print(f"   Total Actions: {total_actions}")
    print(f"   Completed: {completed_actions}")
    print(f"   Incomplete: {incomplete_actions}")
    
    # Calculate expected debt
    AVG_COST = 240  # $75/hr * 3.2 hours
    expected_debt = incomplete_actions * AVG_COST
    
    print(f"\n💰 Expected Debt Calculation:")
    print(f"   {incomplete_actions} incomplete × $240 = ${expected_debt:,}")
    
    # Check breakdown categories
    now = datetime.now(timezone.utc)
    breakdown = {
        'forgotten': 0,
        'overdue': 0,
        'unassigned': 0,
        'atRisk': 0
    }
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        for action in action_items:
            if action.get('completed'):
                continue
            
            # Calculate age
            created_at_str = action.get('createdAt') or meeting.get('createdAt')
            age_days = 0
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    age_days = (now - created_at).days
                except:
                    pass
            
            # Categorize
            if age_days > 30:
                breakdown['forgotten'] += AVG_COST
            elif action.get('deadline'):
                try:
                    deadline = datetime.fromisoformat(action['deadline'] + 'T00:00:00+00:00')
                    if deadline < now:
                        breakdown['overdue'] += AVG_COST
                    else:
                        breakdown['atRisk'] += AVG_COST
                except:
                    breakdown['atRisk'] += AVG_COST
            elif not action.get('owner') or action['owner'] == 'Unassigned':
                breakdown['unassigned'] += AVG_COST
            else:
                breakdown['atRisk'] += AVG_COST
    
    print(f"\n📈 Debt Breakdown:")
    for category, amount in breakdown.items():
        if amount > 0:
            print(f"   {category.capitalize()}: ${amount:,}")
    
    # Calculate completion rate
    completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
    
    print(f"\n✅ Completion Rate: {completion_rate:.1f}%")
    print(f"   Industry Benchmark: 67%")
    
    if completion_rate > 67:
        print(f"   🎉 Above industry average!")
    else:
        print(f"   ⚠️  Below industry average")
    
    print("\n" + "=" * 60)
    print("TEST RESULT: Debt Dashboard should show REAL DATA")
    print("=" * 60)
    print("\nExpected values on dashboard:")
    print(f"  • Total Debt: ${expected_debt:,}")
    print(f"  • Total Actions: {total_actions}")
    print(f"  • Completed: {completed_actions}")
    print(f"  • Incomplete: {incomplete_actions}")
    print(f"  • Completion Rate: {completion_rate:.0f}%")
    print("\nIf dashboard shows different values, it's using MOCK DATA ❌")
    print("If dashboard shows these values, it's using REAL DATA ✅")
    print()

if __name__ == '__main__':
    test_debt_analytics()
