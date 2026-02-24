"""
Shared health score calculation module for MeetingMind.
Used by both process-meeting and update-action Lambda functions.
"""

from datetime import datetime, timezone
from decimal import Decimal


def calculate_health_score(action_items, decisions, created_at):
    """
    Calculate meeting health score (0-100) and letter grade.
    
    Formula:
    - Completion rate: 40%
    - Owner assignment rate: 30%
    - Inverted risk score: 20%
    - Recency bonus: 10%
    
    Args:
        action_items: List of action item dicts
        decisions: List of decision strings
        created_at: datetime object or ISO string
        
    Returns:
        dict with 'score' (Decimal), 'grade' (str), 'label' (str)
    """
    if not action_items:
        # No actions = perfect score (nothing to fail)
        return {'score': Decimal('100.0'), 'grade': 'A', 'label': 'Perfect meeting'}
    
    total = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    owned = sum(1 for a in action_items if a.get('owner') and a['owner'] != 'Unassigned')
    
    # Calculate average risk score
    # Convert to float to avoid Decimal type issues from DynamoDB
    risk_scores = [float(a.get('riskScore', 0)) for a in action_items]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Calculate recency bonus (meetings < 7 days old get bonus)
    recency_bonus = 1.0
    try:
        # Handle both datetime objects and ISO strings
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        days_old = (datetime.now(timezone.utc) - created_at).days
        recency_bonus = 1.0 if days_old < 7 else 0.8
    except:
        pass
    
    # Calculate weighted score
    completion_rate = (completed / total) * 40
    owner_rate = (owned / total) * 30
    risk_inverted = ((100 - avg_risk) / 100) * 20
    recency_component = recency_bonus * 10
    
    score = completion_rate + owner_rate + risk_inverted + recency_component
    score = min(max(score, 0), 100)  # Clamp to 0-100
    
    # Determine grade and label
    if score >= 90:
        grade, label = 'A', 'Excellent meeting'
    elif score >= 80:
        grade, label = 'B', 'Strong meeting'
    elif score >= 70:
        grade, label = 'C', 'Average meeting'
    elif score >= 60:
        grade, label = 'D', 'Poor meeting'
    else:
        grade, label = 'F', 'Failed meeting'
    
    return {
        'score': Decimal(str(round(score, 1))),
        'grade': grade,
        'label': label
    }


def generate_autopsy(action_items, decisions, transcript_text, health_score):
    """
    Generate meeting autopsy for failed meetings using rule-based logic.
    Provides specific, actionable feedback based on meeting patterns.
    
    Args:
        action_items: List of action item dicts
        decisions: List of decision strings
        transcript_text: Meeting transcript (unused but kept for compatibility)
        health_score: Numeric health score (0-100)
        
    Returns:
        str with autopsy message or None if meeting is healthy
    """
    # Only generate for F grade (< 60) or ghost meetings
    is_ghost = len(decisions) == 0 and len(action_items) == 0
    if health_score >= 60 and not is_ghost:
        return None
    
    # Calculate metrics
    total_actions = len(action_items)
    completed = [a for a in action_items if a.get('completed')]
    unassigned = [a for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned']
    decision_count = len(decisions)
    
    completion_rate = len(completed) / total_actions if total_actions > 0 else 0
    unassigned_rate = len(unassigned) / total_actions if total_actions > 0 else 0
    
    # Rule 1: Ghost meeting (no decisions, no actions)
    if is_ghost:
        return "Cause of death: Zero decisions and zero action items extracted from this meeting. Prescription: This meeting could have been an email—try Slack next time."
    
    # Rule 2: High unassigned rate (>50%)
    if unassigned_rate > 0.5:
        return f"Cause of death: {len(unassigned)} of {total_actions} tasks have no owner—classic diffusion of responsibility. Prescription: No one leaves until every task has a name."
    
    # Rule 3: Zero completion (all tasks incomplete)
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
    
    # Rule 10: Generic fallback for other F-grade meetings
    if health_score < 50:
        return f"Cause of death: Meeting health score of {health_score}/100 indicates critical failure. Prescription: Review meeting necessity—this might not need to happen."
    else:
        return f"Cause of death: Meeting scored {health_score}/100 with unclear action clarity. Prescription: Define specific, measurable outcomes before scheduling the next one."
