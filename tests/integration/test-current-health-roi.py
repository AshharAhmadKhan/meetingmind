#!/usr/bin/env python3
"""
Test current health scores and ROI calculations
"""
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("=" * 70)
print("CURRENT HEALTH SCORE & ROI TEST")
print("=" * 70)

response = meetings_table.scan()
meetings = response.get('Items', [])

print(f"\nFound {len(meetings)} meetings\n")

for meeting in meetings:
    title = meeting.get('title', 'Untitled')
    action_items = meeting.get('actionItems', [])
    
    # Calculate stats
    total = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    unassigned = sum(1 for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned')
    assigned = total - unassigned
    
    # Get stored values
    health_score = meeting.get('healthScore', {})
    roi_data = meeting.get('roi', {})
    
    # Handle different healthScore formats
    if isinstance(health_score, dict):
        score = float(health_score.get('score', 0))
        grade = health_score.get('grade', 'N/A')
    else:
        try:
            score = float(health_score) if health_score else 0
        except:
            score = 0
        grade = 'N/A'
    
    # Handle both old (number) and new (object) ROI formats
    if isinstance(roi_data, dict):
        roi = roi_data.get('roi', 0)
        value = roi_data.get('value', 0)
        cost = roi_data.get('cost', 0)
    else:
        roi = roi_data
        value = 0
        cost = 0
    
    print(f"Meeting: {title}")
    print(f"  Actions: {total} total, {completed} done, {unassigned} unassigned, {assigned} assigned")
    print(f"  Health Score: {score}/100 (Grade: {grade})")
    print(f"  ROI: {roi}% (Value: ${value}, Cost: ${cost})")
    
    # Flag issues
    if unassigned == total and score > 50:
        print(f"  ⚠️  ISSUE #14: All unassigned but score is {score}/100 (should be ~40-50)")
    
    if unassigned == total and roi > -50:
        print(f"  ⚠️  ISSUE #15: All unassigned but ROI is {roi}% (should be -100%)")
    
    print()

print("=" * 70)
print("EXPECTED FIXES:")
print("=" * 70)
print("Issue #14: Meetings with all unassigned tasks should score 40-50/100")
print("           (Only completion rate + risk + recency, NO owner points)")
print()
print("Issue #15: Meetings with all unassigned tasks should have ROI = -100%")
print("           (Zero value created, only cost)")
print()
