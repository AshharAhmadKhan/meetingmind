#!/usr/bin/env python3
"""
Regenerate autopsies using the new rule-based logic (no AI needed).
"""

import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

def generate_autopsy_rulebased(action_items, decisions, health_score):
    """Rule-based autopsy generation matching the Lambda logic."""
    is_ghost = len(decisions) == 0 and len(action_items) == 0
    if health_score >= 60 and not is_ghost:
        return None
    
    total_actions = len(action_items)
    completed = [a for a in action_items if a.get('completed')]
    unassigned = [a for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned']
    decision_count = len(decisions)
    
    completion_rate = len(completed) / total_actions if total_actions > 0 else 0
    unassigned_rate = len(unassigned) / total_actions if total_actions > 0 else 0
    
    # Rule 1: Ghost meeting
    if is_ghost:
        return "Cause of death: Zero decisions and zero action items extracted from this meeting. Prescription: This meeting could have been an email—try Slack next time."
    
    # Rule 2: High unassigned rate (>50%)
    if unassigned_rate > 0.5:
        return f"Cause of death: {len(unassigned)} of {total_actions} tasks have no owner—classic diffusion of responsibility. Prescription: No one leaves until every task has a name."
    
    # Rule 3: Zero completion
    if total_actions > 0 and completion_rate == 0:
        return f"Cause of death: Zero of {total_actions} action items completed despite clear assignments. Prescription: Set up accountability check-ins before the next meeting."
    
    # Rule 4: Very low completion (1-25%)
    if 0 < completion_rate <= 0.25:
        return f"Cause of death: Only {len(completed)} of {total_actions} commitments delivered—poor follow-through. Prescription: Assign fewer, higher-priority tasks or reduce meeting frequency."
    
    # Rule 5: Low completion (26-50%)
    if 0.25 < completion_rate <= 0.5:
        return f"Cause of death: Half the commitments were abandoned ({len(completed)}/{total_actions} completed). Prescription: Focus on the critical few instead of the trivial many."
    
    # Rule 6: No decisions but many actions
    if decision_count == 0 and total_actions > 3:
        return f"Cause of death: {total_actions} tasks assigned but zero decisions made—this was a status update, not a meeting. Prescription: Cancel recurring meetings that don't drive decisions."
    
    # Rule 7: Many decisions, few actions
    if decision_count > 3 and total_actions < 2:
        return f"Cause of death: {decision_count} decisions with no clear next steps—lots of talk, little execution. Prescription: Convert decisions into concrete action items with owners."
    
    # Rule 8: No decisions at all
    if decision_count == 0 and total_actions > 0:
        return f"Cause of death: {total_actions} tasks but zero decisions—no strategic direction. Prescription: Decide what NOT to do before assigning more work."
    
    # Rule 9: Some unassigned tasks (20-50%)
    if 0.2 < unassigned_rate <= 0.5:
        return f"Cause of death: {len(unassigned)} of {total_actions} tasks lack clear ownership. Prescription: Use the 'who does what by when' format for every commitment."
    
    # Rule 10: Generic fallback
    if health_score < 50:
        return f"Cause of death: Meeting health score of {health_score}/100 indicates critical failure. Prescription: Review meeting necessity—this might not need to happen."
    else:
        return f"Cause of death: Meeting scored {health_score}/100 with unclear action clarity. Prescription: Define specific, measurable outcomes before scheduling the next one."

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("Regenerating autopsies with rule-based logic...")
print("=" * 80)

for meeting in response['Items']:
    meeting_id = meeting['meetingId']
    title = meeting['title']
    health_score = meeting.get('healthScore', 100)
    
    # Only generate for F grade meetings
    if health_score < 60:
        print(f"\n📋 {title} (Score: {health_score})")
        
        action_items = meeting.get('actionItems', [])
        decisions = meeting.get('decisions', [])
        
        autopsy = generate_autopsy_rulebased(action_items, decisions, health_score)
        
        if autopsy:
            print(f"   🪦 NEW AUTOPSY:")
            print(f"   {autopsy}")
            
            # Save to DynamoDB
            table.update_item(
                Key={'userId': user_id, 'meetingId': meeting_id},
                UpdateExpression='SET autopsy = :a, autopsyGeneratedAt = :t',
                ExpressionAttributeValues={
                    ':a': autopsy,
                    ':t': datetime.now(timezone.utc).isoformat()
                }
            )
            print(f"   ✅ Saved")

print("\n" + "=" * 80)
print("✅ Autopsies regenerated with smart rule-based logic!")
print("\nNow you'll see varied, specific feedback based on:")
print("  - Completion rates")
print("  - Unassigned tasks")
print("  - Decision counts")
print("  - Meeting patterns")
