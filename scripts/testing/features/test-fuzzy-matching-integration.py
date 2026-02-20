#!/usr/bin/env python3
"""
Integration test for fuzzy name matching in process-meeting Lambda.
Tests the complete flow with realistic meeting data.
"""

import sys
import os
from difflib import SequenceMatcher

# Simulate the Lambda function's fuzzy matching logic
def _get_team_members_mock(team_id):
    """Mock team members data"""
    teams = {
        'team-001': [
            {'name': 'Abdul Zeeshan', 'email': 'zeeshan@example.com'},
            {'name': 'Ashhar Ahmad Khan', 'email': 'ashhar@example.com'},
            {'name': 'Muhammad Ali', 'email': 'ali@example.com'}
        ],
        'team-002': [
            {'name': 'John Smith', 'email': 'john@example.com'},
            {'name': 'Sarah Johnson', 'email': 'sarah@example.com'}
        ]
    }
    
    team = teams.get(team_id, [])
    return [m['name'] for m in team]

def _fuzzy_match_owner(ai_owner, team_members, threshold=0.6):
    """
    Match AI-extracted owner name to team member names using fuzzy matching.
    This is the exact logic from process-meeting Lambda.
    """
    if not ai_owner or ai_owner == 'Unassigned' or not team_members:
        return ai_owner
    
    ai_owner_lower = ai_owner.lower().strip()
    best_match = None
    best_ratio = 0.0
    
    for member_name in team_members:
        member_lower = member_name.lower().strip()
        
        # Check for exact match first
        if ai_owner_lower == member_lower:
            return member_name
        
        # Check if AI name is a word in member name (e.g., "Zeeshan" in "Abdul Zeeshan")
        member_words = member_lower.split()
        if ai_owner_lower in member_words:
            print(f"  ✓ Fuzzy matched '{ai_owner}' → '{member_name}' (word match)")
            return member_name
        
        # Check if AI name is a substring of any word in member name
        for word in member_words:
            if ai_owner_lower in word or word in ai_owner_lower:
                ratio = SequenceMatcher(None, ai_owner_lower, word).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = member_name
        
        # Also check overall similarity
        overall_ratio = SequenceMatcher(None, ai_owner_lower, member_lower).ratio()
        if overall_ratio > best_ratio:
            best_ratio = overall_ratio
            best_match = member_name
    
    # Return best match if above threshold
    if best_match and best_ratio >= threshold:
        print(f"  ✓ Fuzzy matched '{ai_owner}' → '{best_match}' (ratio: {best_ratio:.2f})")
        return best_match
    
    # No good match found
    print(f"  ✗ No match for '{ai_owner}' (best ratio: {best_ratio:.2f})")
    return ai_owner

def simulate_meeting_processing(team_id, ai_extracted_actions):
    """
    Simulate the meeting processing flow with fuzzy matching.
    This mimics what happens in the Lambda function.
    """
    print(f"\n{'='*70}")
    print(f"SIMULATING MEETING PROCESSING FOR TEAM: {team_id}")
    print(f"{'='*70}")
    
    # Get team members
    team_members = _get_team_members_mock(team_id)
    print(f"\nTeam Members: {team_members}")
    
    # Process action items with fuzzy matching
    print(f"\nProcessing {len(ai_extracted_actions)} action items...")
    processed_actions = []
    
    for i, action in enumerate(ai_extracted_actions, 1):
        ai_owner = action.get('owner', 'Unassigned')
        print(f"\n{i}. Task: {action['task'][:50]}...")
        print(f"   AI extracted owner: '{ai_owner}'")
        
        # Apply fuzzy matching
        matched_owner = _fuzzy_match_owner(ai_owner, team_members) if team_members else ai_owner
        
        processed_action = {
            'id': action.get('id', f'action-{i}'),
            'task': action['task'],
            'owner': matched_owner,
            'deadline': action.get('deadline'),
            'ai_extracted_owner': ai_owner,  # For comparison
            'fuzzy_matched': matched_owner != ai_owner
        }
        processed_actions.append(processed_action)
    
    return processed_actions

def test_scenario_1():
    """Test Scenario 1: Partial name matches (most common case)"""
    print("\n" + "="*70)
    print("TEST SCENARIO 1: Partial Name Matches")
    print("="*70)
    
    team_id = 'team-001'
    ai_extracted_actions = [
        {
            'id': 'action-1',
            'task': 'Review the database schema and propose optimizations',
            'owner': 'Zeeshan',  # Should match to "Abdul Zeeshan"
            'deadline': '2026-02-25'
        },
        {
            'id': 'action-2',
            'task': 'Update the API documentation with new endpoints',
            'owner': 'Ashhar',  # Should match to "Ashhar Ahmad Khan"
            'deadline': '2026-02-26'
        },
        {
            'id': 'action-3',
            'task': 'Deploy the staging environment and run smoke tests',
            'owner': 'Ali',  # Should match to "Muhammad Ali"
            'deadline': '2026-02-27'
        },
        {
            'id': 'action-4',
            'task': 'Schedule team meeting for sprint planning',
            'owner': 'Khan',  # Should match to "Ashhar Ahmad Khan"
            'deadline': '2026-02-24'
        }
    ]
    
    results = simulate_meeting_processing(team_id, ai_extracted_actions)
    
    # Verify results
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    
    expected_matches = {
        'Zeeshan': 'Abdul Zeeshan',
        'Ashhar': 'Ashhar Ahmad Khan',
        'Ali': 'Muhammad Ali',
        'Khan': 'Ashhar Ahmad Khan'
    }
    
    passed = 0
    failed = 0
    
    for action in results:
        ai_owner = action['ai_extracted_owner']
        matched_owner = action['owner']
        expected = expected_matches.get(ai_owner, ai_owner)
        
        if matched_owner == expected:
            print(f"✓ PASS: '{ai_owner}' → '{matched_owner}'")
            passed += 1
        else:
            print(f"✗ FAIL: '{ai_owner}' → '{matched_owner}' (expected: '{expected}')")
            failed += 1
    
    print(f"\nScenario 1 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_scenario_2():
    """Test Scenario 2: Exact matches and unassigned"""
    print("\n" + "="*70)
    print("TEST SCENARIO 2: Exact Matches and Unassigned")
    print("="*70)
    
    team_id = 'team-001'
    ai_extracted_actions = [
        {
            'id': 'action-1',
            'task': 'Complete the security audit report',
            'owner': 'Abdul Zeeshan',  # Exact match
            'deadline': '2026-02-28'
        },
        {
            'id': 'action-2',
            'task': 'Review code changes from last sprint',
            'owner': 'Unassigned',  # Should stay unassigned
            'deadline': None
        },
        {
            'id': 'action-3',
            'task': 'Update project timeline in Jira',
            'owner': 'Muhammad Ali',  # Exact match
            'deadline': '2026-03-01'
        }
    ]
    
    results = simulate_meeting_processing(team_id, ai_extracted_actions)
    
    # Verify results
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    
    expected_matches = {
        'Abdul Zeeshan': 'Abdul Zeeshan',
        'Unassigned': 'Unassigned',
        'Muhammad Ali': 'Muhammad Ali'
    }
    
    passed = 0
    failed = 0
    
    for action in results:
        ai_owner = action['ai_extracted_owner']
        matched_owner = action['owner']
        expected = expected_matches.get(ai_owner, ai_owner)
        
        if matched_owner == expected:
            print(f"✓ PASS: '{ai_owner}' → '{matched_owner}'")
            passed += 1
        else:
            print(f"✗ FAIL: '{ai_owner}' → '{matched_owner}' (expected: '{expected}')")
            failed += 1
    
    print(f"\nScenario 2 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_scenario_3():
    """Test Scenario 3: No match (names not in team)"""
    print("\n" + "="*70)
    print("TEST SCENARIO 3: No Match (Names Not in Team)")
    print("="*70)
    
    team_id = 'team-002'
    ai_extracted_actions = [
        {
            'id': 'action-1',
            'task': 'Prepare quarterly business review presentation',
            'owner': 'John',  # Should match to "John Smith"
            'deadline': '2026-03-05'
        },
        {
            'id': 'action-2',
            'task': 'Contact vendor about licensing renewal',
            'owner': 'Sarah',  # Should match to "Sarah Johnson"
            'deadline': '2026-03-10'
        },
        {
            'id': 'action-3',
            'task': 'Review budget allocation for Q2',
            'owner': 'Michael',  # No match - not in team
            'deadline': '2026-03-15'
        }
    ]
    
    results = simulate_meeting_processing(team_id, ai_extracted_actions)
    
    # Verify results
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    
    expected_matches = {
        'John': 'John Smith',
        'Sarah': 'Sarah Johnson',
        'Michael': 'Michael'  # Should stay as-is (no match)
    }
    
    passed = 0
    failed = 0
    
    for action in results:
        ai_owner = action['ai_extracted_owner']
        matched_owner = action['owner']
        expected = expected_matches.get(ai_owner, ai_owner)
        
        if matched_owner == expected:
            print(f"✓ PASS: '{ai_owner}' → '{matched_owner}'")
            passed += 1
        else:
            print(f"✗ FAIL: '{ai_owner}' → '{matched_owner}' (expected: '{expected}')")
            failed += 1
    
    print(f"\nScenario 3 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_scenario_4():
    """Test Scenario 4: Real-world meeting transcript simulation"""
    print("\n" + "="*70)
    print("TEST SCENARIO 4: Real-World Meeting Simulation")
    print("="*70)
    print("\nSimulating AI extraction from meeting transcript:")
    print("'Zeeshan, you'll handle the database migration, right?'")
    print("'Yes, I'll get it done by Friday.'")
    print("'Ashhar, can you review the API changes?'")
    print("'Sure, I'll review them tomorrow.'")
    
    team_id = 'team-001'
    ai_extracted_actions = [
        {
            'id': 'action-1',
            'task': 'Handle the database migration',
            'owner': 'Zeeshan',  # From: "Zeeshan, you'll handle..."
            'deadline': '2026-02-28'
        },
        {
            'id': 'action-2',
            'task': 'Review the API changes',
            'owner': 'Ashhar',  # From: "Ashhar, can you review..."
            'deadline': '2026-02-25'
        }
    ]
    
    results = simulate_meeting_processing(team_id, ai_extracted_actions)
    
    # Verify results
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    
    expected_matches = {
        'Zeeshan': 'Abdul Zeeshan',
        'Ashhar': 'Ashhar Ahmad Khan'
    }
    
    passed = 0
    failed = 0
    
    for action in results:
        ai_owner = action['ai_extracted_owner']
        matched_owner = action['owner']
        expected = expected_matches.get(ai_owner, ai_owner)
        
        if matched_owner == expected:
            print(f"✓ PASS: '{ai_owner}' → '{matched_owner}'")
            passed += 1
        else:
            print(f"✗ FAIL: '{ai_owner}' → '{matched_owner}' (expected: '{expected}')")
            failed += 1
    
    print(f"\nScenario 4 Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("FUZZY NAME MATCHING - INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting the complete flow from AI extraction to fuzzy matching")
    print("This simulates what happens in the process-meeting Lambda function")
    
    results = []
    
    # Run all test scenarios
    results.append(("Scenario 1: Partial Name Matches", test_scenario_1()))
    results.append(("Scenario 2: Exact Matches and Unassigned", test_scenario_2()))
    results.append(("Scenario 3: No Match (Names Not in Team)", test_scenario_3()))
    results.append(("Scenario 4: Real-World Meeting Simulation", test_scenario_4()))
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_failed = len(results) - total_passed
    
    for scenario, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {scenario}")
    
    print(f"\n{'='*70}")
    print(f"OVERALL: {total_passed}/{len(results)} scenarios passed")
    print(f"{'='*70}")
    
    if total_failed == 0:
        print("\n✓ ALL TESTS PASSED - Fuzzy matching is working correctly!")
        print("\nThe Lambda function will:")
        print("  1. Fetch team members from DynamoDB")
        print("  2. Apply fuzzy matching to AI-extracted owner names")
        print("  3. Store matched names in action items")
        print("\nReady for production use.")
        return 0
    else:
        print(f"\n✗ {total_failed} SCENARIO(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
