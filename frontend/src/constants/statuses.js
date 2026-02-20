// Action item statuses
export const ACTION_STATUSES = {
  TODO: 'todo',
  IN_PROGRESS: 'in_progress',
  BLOCKED: 'blocked',
  DONE: 'done'
}

export const VALID_ACTION_STATUSES = Object.values(ACTION_STATUSES)

// Meeting processing statuses
export const MEETING_STATUSES = {
  PENDING: 'PENDING',
  TRANSCRIBING: 'TRANSCRIBING',
  ANALYZING: 'ANALYZING',
  DONE: 'DONE',
  FAILED: 'FAILED'
}

export const VALID_MEETING_STATUSES = Object.values(MEETING_STATUSES)

// Risk levels
export const RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
}

export const VALID_RISK_LEVELS = Object.values(RISK_LEVELS)
