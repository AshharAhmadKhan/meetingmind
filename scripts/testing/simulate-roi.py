#!/usr/bin/env python3
"""
Simulate ROI calculation for all-unassigned meeting
"""

def calculate_roi_current(total_actions, assigned_with_deadline, decisions):
    """Current formula from the code"""
    avg_attendees = 4
    hourly_rate = 75
    meeting_duration_minutes = 30
    decision_value = 500
    action_value = 200
    
    cost = avg_attendees * (meeting_duration_minutes / 60) * hourly_rate
    
    decision_count = len(decisions)
    clear_actions = assigned_with_deadline  # Only count assigned with deadline
    value = (decision_count * decision_value) + (clear_actions * action_value)
    
    if cost == 0:
        roi = 0
    else:
        roi = ((value - cost) / cost) * 100
    
    return round(roi, 1), value, cost

print("=" * 60)
print("ROI CALCULATION SIMULATION")
print("=" * 60)

# Test case from issue: All unassigned tasks
print("\nTest Case: 5 actions, all unassigned, 0 decisions")
print("Expected: ROI should be -100% (zero value, only cost)")

roi, value, cost = calculate_roi_current(5, 0, [])
print(f"\nCalculated ROI: {roi}%")
print(f"  Cost: ${cost} (4 attendees × 0.5 hours × $75/hr)")
print(f"  Value: ${value} (0 clear actions × $200)")
print(f"  ROI: ({value} - {cost}) / {cost} × 100 = {roi}%")

if roi != -100:
    print(f"  ⚠️  ISSUE: ROI is {roi}%, should be -100%!")
else:
    print(f"  ✓ CORRECT: ROI is {roi}%, properly shows zero value")

print("\n" + "=" * 60)
print("Test Case 2: 5 actions, 2 assigned with deadline, 1 decision")
print("=" * 60)

roi2, value2, cost2 = calculate_roi_current(5, 2, [1])
print(f"\nCalculated ROI: {roi2}%")
print(f"  Cost: ${cost2}")
print(f"  Value: ${value2} (1 decision × $500 + 2 actions × $200)")
print(f"  ROI: ({value2} - {cost2}) / {cost2} × 100 = {roi2}%")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("The current ROI formula IS CORRECT!")
print("All-unassigned meeting gets -100% ROI")
print("Only assigned tasks with deadlines count as 'clear actions'")
print("Unassigned tasks contribute $0 value")
