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

# ── MEETING ROI CALCULATION ────────────────────────────────
AVG_ATTENDEES = 4  # Typical meeting size
AVG_HOURLY_RATE = 75  # USD per hour (average knowledge worker)
DECISION_VALUE = 500  # USD value per decision made
ACTION_VALUE = 200  # USD value per clear action item

# ── DEBT ANALYTICS ─────────────────────────────────────────
AVG_BLOCKED_TIME_HOURS = 3.2  # Hours blocked per incomplete action (research-backed)
INDUSTRY_COMPLETION_RATE = 0.67  # 67% industry benchmark

# ── GRAVEYARD & EPITAPHS ───────────────────────────────────
GRAVEYARD_THRESHOLD_DAYS = 30  # Actions older than this go to graveyard
EPITAPH_TTL_DAYS = 7  # Regenerate epitaphs after this many days
EPITAPH_TASK_TRUNCATION = 80  # Max characters for task in epitaph

# ── DUPLICATE DETECTION ────────────────────────────────────
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # Cosine similarity threshold for duplicates
FUZZY_MATCH_THRESHOLD = 0.6  # Name matching threshold for team members

# ── TRANSCRIPTION ──────────────────────────────────────────
TRANSCRIBE_MAX_RETRIES = 48  # Max polling attempts for transcription job
TRANSCRIBE_RETRY_DELAY_SECONDS = 15  # Seconds between transcription status checks
TRANSCRIPT_TRUNCATION_LENGTH = 5000  # Characters to store in DynamoDB
BEDROCK_PROMPT_TRUNCATION_LENGTH = 6000  # Characters to send to Bedrock for analysis

# ── DEMO MODE ──────────────────────────────────────────────
DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'  # Demo account user ID
DEMO_MEETING_TTL_MINUTES = 30  # Demo meetings auto-delete after 30 minutes
