#!/usr/bin/env python3
"""
Detailed report of all meetings with health scores and ROI
"""
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("=" * 80)
print("DETAILED MEETING HEALTH SCORE & ROI REPORT")
print("=" * 80)

response = meetings_table.scan()
meetings = response.get('Items', [])

print(f"\nTotal Meetings: {len(meetings)}\n")
print("=" * 80)

for i, meeting in enumerate(meetings, 1):
    title = meeting.get('title', 'Untitled')
    meeting_id = meeting.get('meetingId', 'unknown')
    team_id = meeting.get('teamId', 'personal')
    action_items = meeting.get('actionItems', [])
    decisions = meeting.get('decisions', [])
    
    # Calculate action stats
    total_actions = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    unassigned = sum(1 for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned')
    assigned = total_actions - unassigned
    with_deadline = sum(1 for a in action_items if a.get('deadline'))
    
    # Get health score
    health_score = meeting.get('healthScore', {})
    if isinstance(health_score, dict):
        score = health_score.get('score', 'N/A')
        grade = health_score.get('grade', 'N/A')
        label = health_score.get('label', 'N/A')
    else:
        score = health_score if health_score else 'N/A'
        grade = 'N/A'
        label = 'N/A'
    
    # Get ROI
    roi_data = meeting.get('roi', {})
    if isinstance(roi_data, dict):
        roi = roi_data.get('roi', 'N/A')
        value = roi_data.get('value', 'N/A')
        cost = roi_data.get('cost', 'N/A')
        clear_actions = roi_data.get('clear_action_count', 'N/A')
        decision_count = roi_data.get('decision_count', 'N/A')
    else:
        roi = roi_data if roi_data else 'N/A'
        value = 'N/A'
        cost = 'N/A'
        clear_actions = 'N/A'
        decision_count = 'N/A'
    
    print(f"\n{i}. {title}")
    print("-" * 80)
    print(f"   Meeting ID: {meeting_id[:20]}...")
    print(f"   Team: {'Personal' if team_id == 'personal' else 'Team'}")
    
    print(f"\n   📊 ACTION ITEMS:")
    print(f"      Total: {total_actions}")
    print(f"      Completed: {completed}/{total_actions} ({int(completed/total_actions*100) if total_actions > 0 else 0}%)")
    print(f"      Assigned: {assigned}/{total_actions} ({int(assigned/total_actions*100) if total_actions > 0 else 0}%)")
    print(f"      Unassigned: {unassigned}/{total_actions}")
    print(f"      With Deadline: {with_deadline}/{total_actions}")
    
    print(f"\n   🎯 DECISIONS: {len(decisions)}")
    
    print(f"\n   ❤️  HEALTH SCORE:")
    print(f"      Score: {score}/100")
    print(f"      Grade: {grade}")
    print(f"      Label: {label}")
    
    print(f"\n   💰 ROI:")
    print(f"      ROI: {roi}%")
    print(f"      Value: ${value}")
    print(f"      Cost: ${cost}")
    print(f"      Clear Actions: {clear_actions}")
    print(f"      Decisions: {decision_count}")
    
    # Analysis
    print(f"\n   📝 ANALYSIS:")
    if score == 'N/A' or score == 0:
        print(f"      ⚠️  No health score (old V1 format or not processed)")
    elif isinstance(score, (int, float, Decimal)):
        score_num = float(score)
        if score_num >= 80:
            print(f"      ✅ Excellent health score!")
        elif score_num >= 60:
            print(f"      ✓ Good health score")
        elif score_num >= 40:
            print(f"      ⚠️  Average health score")
        else:
            print(f"      ❌ Poor health score")
    
    if roi == 'N/A' or roi == -100:
        if roi == -100:
            print(f"      💸 Negative ROI - meeting cost more than value created")
    elif isinstance(roi, (int, float, Decimal)):
        roi_num = float(roi)
        if roi_num > 500:
            print(f"      🚀 Excellent ROI!")
        elif roi_num > 0:
            print(f"      ✓ Positive ROI")
        else:
            print(f"      💸 Negative ROI")
    
    if unassigned == total_actions and total_actions > 0:
        print(f"      ⚠️  ALL TASKS UNASSIGNED - This is the test case for Issues #14 & #15!")
    
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)

# Count meetings by health score
v1_meetings = sum(1 for m in meetings if not isinstance(m.get('healthScore', {}), dict) or m.get('healthScore', {}).get('score') in [0, 'N/A', None])
v2_meetings = len(meetings) - v1_meetings

print(f"\nV1 Meetings (old format): {v1_meetings}")
print(f"V2 Meetings (new format): {v2_meetings}")

# Find meetings with all unassigned
all_unassigned = []
for m in meetings:
    actions = m.get('actionItems', [])
    if actions:
        unassigned = sum(1 for a in actions if not a.get('owner') or a['owner'] == 'Unassigned')
        if unassigned == len(actions):
            all_unassigned.append(m.get('title', 'Untitled'))

if all_unassigned:
    print(f"\n⚠️  Meetings with ALL unassigned tasks: {len(all_unassigned)}")
    for title in all_unassigned:
        print(f"   - {title}")
else:
    print(f"\n✓ No meetings with ALL unassigned tasks found")
    print(f"  (Cannot reproduce Issues #14 & #15 with current data)")

print()
