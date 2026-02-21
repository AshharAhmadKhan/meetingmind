"""
Shared constants for MeetingMind backend Lambda functions
"""

# Action item statuses
ACTION_STATUSES = {
    'TODO': 'todo',
    'IN_PROGRESS': 'in_progress',
    'BLOCKED': 'blocked',
    'DONE': 'done'
}

VALID_ACTION_STATUSES = list(ACTION_STATUSES.values())

# Meeting processing statuses
MEETING_STATUSES = {
    'PENDING': 'PENDING',
    'TRANSCRIBING': 'TRANSCRIBING',
    'ANALYZING': 'ANALYZING',
    'DONE': 'DONE',
    'FAILED': 'FAILED'
}

VALID_MEETING_STATUSES = list(MEETING_STATUSES.values())

# Risk levels
RISK_LEVELS = {
    'LOW': 'LOW',
    'MEDIUM': 'MEDIUM',
    'HIGH': 'HIGH',
    'CRITICAL': 'CRITICAL'
}

VALID_RISK_LEVELS = list(RISK_LEVELS.values())

# Team member roles
TEAM_ROLES = {
    'ADMIN': 'admin',
    'MEMBER': 'member'
}

VALID_TEAM_ROLES = list(TEAM_ROLES.values())
