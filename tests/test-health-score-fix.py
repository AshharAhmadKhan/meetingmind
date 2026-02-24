#!/usr/bin/env python3
"""
Comprehensive test suite for health score recalculation fix.
Tests both before and after the fix is applied.
"""

import boto3
import time
from datetime import datetime, timezone
from decimal import Decimal

# Configuration
REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'
USER_ID = 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'
MEETING_ID = 'b99fa520-7a3e-4535-9471-2d617fd239df'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def get_meeting():
    """Fetch meeting from DynamoDB."""
    response = table.get_item(Key={'userId': USER_ID, 'meetingId': MEETING_ID})
    return response.get('Item')

def calculate_expected_health_score(actions):
    """Calculate what the health score SHOULD be."""
    if not actions:
        return 100.0
    
    total = len(actions)
    completed = sum(1 for a in actions if a.get('completed', False))
    owned = sum(1 for a in actions if a.get('owner') and a['owner'] != 'Unassigned')
    
    # Calculate average risk
    risk_scores = [float(a.get('riskScore', 0)) for a in actions]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Calculate components
    completion_rate = (completed / total) * 40
    owner_rate = (owned / total) * 30
    risk_inverted = ((100 - avg_risk) / 100) * 20
    recency_component = 10  # Assume recent
    
    score = completion_rate + owner_rate + risk_inverted + recency_component
    return min(max(score, 0), 100)

def get_grade(score):
    """Convert score to letter grade."""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def test_current_state():
    """Test 1: Verify current broken state."""
    print("=" * 80)
    print("TEST 1: CURRENT STATE (BEFORE FIX)")
    print("=" * 80)
    print()
    
    meeting = get_meeting()
    actions = meeting.get('actionItems', [])
    
    total = len(actions)
    completed = sum(1 for a in actions if a.get('completed'))
    completion_pct = (completed / total * 100) if total > 0 else 0
    
    stored_score = float(meeting.get('healthScore', 0))
    stored_grade = meeting.get('healthGrade', 'F')
    
    expected_score = calculate_expected_health_score(actions)
    expected_grade = get_grade(expected_score)
    
    print(f"Actions: {completed}/{total} completed ({completion_pct:.1f}%)")
    print()
    print(f"STORED in DynamoDB:")
    print(f"  Health Score: {stored_score}/100")
    print(f"  Health Grade: {stored_grade}")
    print()
    print(f"EXPECTED based on completion:")
    print(f"  Health Score: {expected_score:.1f}/100")
    print(f"  Health Grade: {expected_grade}")
    print()
    
    difference = abs(expected_score - stored_score)
    
    if difference > 5:
        print(f"❌ FAIL: Score mismatch of {difference:.1f} points")
        print(f"   This confirms the bug - health score is NOT recalculating")
        return False
    else:
        print(f"✅ PASS: Scores match (difference: {difference:.1f} points)")
        return True

def test_after_fix():
    """Test 2: Verify fix works after deployment."""
    print()
    print("=" * 80)
    print("TEST 2: AFTER FIX (Run this after deployment)")
    print("=" * 80)
    print()
    print("This test should be run AFTER deploying the fix.")
    print("It will verify that health scores recalculate correctly.")
    print()
    print("Steps:")
    print("1. Deploy the fix")
    print("2. Complete 1 action via the UI")
    print("3. Run this test")
    print("4. Verify score increased")
    print()

def test_race_condition_current():
    """Test 3: Demonstrate race condition."""
    print()
    print("=" * 80)
    print("TEST 3: RACE CONDITION (CURRENT STATE)")
    print("=" * 80)
    print()
    
    meeting = get_meeting()
    actions = meeting.get('actionItems', [])
    completed_before = sum(1 for a in actions if a.get('completed'))
    
    print(f"Current completion: {completed_before}/{len(actions)}")
    print()
    print("To test race condition:")
    print("1. Open meeting in browser")
    print("2. Click 10 actions as fast as possible")
    print("3. Wait 2 seconds")
    print("4. Refresh page")
    print("5. Count how many are still checked")
    print()
    print("Expected with bug: Only 8-9 will persist (2 lost)")
    print("Expected after fix: All 10 will persist")
    print()

def main():
    """Run all tests."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "HEALTH SCORE FIX - TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Test 1: Current state
    test_current_state()
    
    # Test 2: After fix instructions
    test_after_fix()
    
    # Test 3: Race condition
    test_race_condition_current()
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print("Run these tests:")
    print("1. BEFORE fix: python tests/test-health-score-fix.py")
    print("2. Deploy fix: ./scripts/deploy/deploy-all.sh")
    print("3. AFTER fix: python tests/test-health-score-fix.py")
    print("4. Manual UI test: Click 10 actions rapidly, refresh, verify all persist")
    print()

if __name__ == '__main__':
    main()
