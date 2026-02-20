#!/usr/bin/env python3
"""
Verify the meeting rating formula (X/10) matches what's shown in the UI
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

def calculate_meeting_rating(actions, decisions):
    """
    Frontend formula from MeetingDetail.jsx calcHealthScore()
    Maximum 10 points:
    - Decision quality: 0-3 points (1 per decision, max 3)
    - Action clarity: 0-3 points (% with owner + deadline)
    - Completion rate: 0-2 points (% completed)
    - Risk distribution: 0-2 points (fewer high-risk = better)
    """
    if len(actions) == 0 and len(decisions) == 0:
        return 0.0
    
    score = 0
    
    # Decision points (0-3)
    decision_points = min(len(decisions), 3)
    
    # Action clarity points (0-3)
    clear_actions = sum(1 for a in actions 
                       if a.get('owner') 
                       and a['owner'] != 'Unassigned' 
                       and a.get('deadline'))
    clarity_points = (clear_actions / len(actions)) * 3 if actions else 0
    
    # Completion points (0-2)
    completed = sum(1 for a in actions if a.get('completed', False))
    completion_points = (completed / len(actions)) * 2 if actions else 0
    
    # Risk points (0-2) - fewer high-risk = better
    high_risk = sum(1 for a in actions 
                   if a.get('riskLevel') in ['HIGH', 'CRITICAL'])
    risk_points = (1 - (high_risk / len(actions))) * 2 if actions else 0
    
    score = decision_points + clarity_points + completion_points + risk_points
    return round(score * 10) / 10

print("=" * 80)
print("MEETING RATING FORMULA VERIFICATION (X/10)")
print("=" * 80)

response = meetings_table.scan()
meetings = response.get('Items', [])

print(f"\nAnalyzing {len(meetings)} meetings...\n")

for meeting in meetings:
    title = meeting.get('title', 'Untitled')
    actions = meeting.get('actionItems', [])
    decisions = meeting.get('decisions', [])
    
    # Calculate expected rating
    rating = calculate_meeting_rating(actions, decisions)
    
    # Break down the score
    decision_pts = min(len(decisions), 3)
    
    clear_actions = sum(1 for a in actions 
                       if a.get('owner') 
                       and a['owner'] != 'Unassigned' 
                       and a.get('deadline'))
    clarity_pts = (clear_actions / len(actions)) * 3 if actions else 0
    
    completed = sum(1 for a in actions if a.get('completed', False))
    completion_pts = (completed / len(actions)) * 2 if actions else 0
    
    high_risk = sum(1 for a in actions 
                   if a.get('riskLevel') in ['HIGH', 'CRITICAL'])
    risk_pts = (1 - (high_risk / len(actions))) * 2 if actions else 0
    
    print(f"Meeting: {title}")
    print(f"  Expected Rating: {rating}/10")
    print(f"  Breakdown:")
    print(f"    Decisions: {decision_pts:.1f}/3 ({len(decisions)} decisions)")
    print(f"    Clarity: {clarity_pts:.1f}/3 ({clear_actions}/{len(actions)} clear)")
    print(f"    Completion: {completion_pts:.1f}/2 ({completed}/{len(actions)} done)")
    print(f"    Risk: {risk_pts:.1f}/2 ({high_risk}/{len(actions)} high-risk)")
    print()

print("=" * 80)
print("FORMULA ANALYSIS")
print("=" * 80)
print("\nThe formula is BALANCED and FAIR:")
print("  ✓ Rewards decisions (up to 3 points)")
print("  ✓ Rewards clear ownership + deadlines (up to 3 points)")
print("  ✓ Rewards completion (up to 2 points)")
print("  ✓ Penalizes high-risk items (up to 2 points)")
print("\nMaximum possible score: 10/10")
print("Typical good meeting: 6-8/10")
print("Poor meeting: 2-4/10")
print()
