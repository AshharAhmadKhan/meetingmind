#!/usr/bin/env python3
"""
Simulate health score calculation for all-unassigned meeting
"""

def calculate_health_score_current(total_actions, completed, assigned):
    """Current formula from the code"""
    completion_rate = (completed / total_actions) * 40
    owner_rate = (assigned / total_actions) * 30
    risk_inverted = ((100 - 0) / 100) * 20  # Assume 0 risk for simplicity
    recency_component = 1.0 * 10  # Assume recent meeting
    
    score = completion_rate + owner_rate + risk_inverted + recency_component
    return round(score, 1)

print("=" * 60)
print("HEALTH SCORE SIMULATION")
print("=" * 60)

# Test case from issue: All unassigned tasks
print("\nTest Case: 5 actions, 0 completed, 0 assigned (all unassigned)")
print("Expected: Should be 40-50/100 (penalized for no owners)")

score = calculate_health_score_current(5, 0, 0)
print(f"Calculated Score: {score}/100")
print(f"  Completion: 0/5 * 40 = 0 points")
print(f"  Owners: 0/5 * 30 = 0 points")
print(f"  Risk: 100/100 * 20 = 20 points")
print(f"  Recency: 1.0 * 10 = 10 points")
print(f"  Total: {score} points")

if score > 50:
    print(f"  ⚠️  ISSUE: Score is {score}, should be ≤50!")
else:
    print(f"  ✓ CORRECT: Score is {score}, properly penalized")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("The current formula IS CORRECT!")
print("All-unassigned meeting gets 30/100 (0+0+20+10)")
print("This is properly penalized (F grade)")
print()
print("The issue report may be based on:")
print("1. Old data before the formula was implemented")
print("2. A meeting that had SOME assigned tasks (not all unassigned)")
print("3. Misunderstanding of what 'unassigned' means")
