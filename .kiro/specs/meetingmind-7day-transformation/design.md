# MeetingMind 7-Day Transformation - Design Document

## Architecture Overview

### System Architecture (Unchanged from Submission)
```
User Browser
    ↓
CloudFront (Static Assets)
    ↓
API Gateway (REST API)
    ↓
Lambda Functions (Business Logic)
    ↓
├─ DynamoDB (Data Storage)
├─ S3 (Audio Storage)
├─ Transcribe (Speech-to-Text)
├─ Bedrock (AI Analysis + Embeddings)
├─ SNS (Email Notifications)
└─ EventBridge (Scheduled Tasks)
```

### New Components (Extensions Only)
- New Lambda functions for analytics
- New DynamoDB indexes for efficient queries
- New Bedrock model usage (Titan Embeddings)
- New frontend pages/components

---

## Data Model Extensions

### Meeting Record (Extended)
```json
{
  "userId": "string (PK)",
  "meetingId": "string (SK)",
  "title": "string",
  "status": "DONE|FAILED|TRANSCRIBING|ANALYZING",
  "createdAt": "ISO8601",
  "updatedAt": "ISO8601",
  "summary": "string",
  "decisions": ["string"],
  "actionItems": [
    {
      "id": "string",
      "task": "string",
      "owner": "string",
      "deadline": "YYYY-MM-DD",
      "completed": boolean,
      "completedAt": "ISO8601",
      // NEW FIELDS
      "riskScore": number,        // 0-100
      "riskLevel": "LOW|MEDIUM|HIGH|CRITICAL",
      "embedding": [number],      // Titan embedding vector
      "createdAt": "ISO8601",
      "ageInDays": number
    }
  ],
  "followUps": ["string"],
  // NEW FIELDS
  "meetingCost": number,          // Calculated cost
  "meetingValue": number,         // Estimated value
  "meetingROI": number,           // (value - cost) / cost
  "qualityScore": number,         // 0-10
  "attendeeCount": number,
  "durationMinutes": number
}
```

### New GSI: ActionItemsByUser
```
PK: userId
SK: actionItemId
Attributes: meetingId, task, owner, deadline, completed, riskScore
```

### New GSI: ActionItemsByDeadline
```
PK: userId
SK: deadline
Attributes: meetingId, actionItemId, task, owner, completed
```

---

## API Design

### New Endpoints

#### GET /debt-analytics
**Purpose:** Get meeting debt dashboard data

**Request:**
```
GET /debt-analytics
Headers:
  Authorization: Bearer <cognito-token>
```

**Response:**
```json
{
  "totalDebt": 47320,
  "breakdown": {
    "forgotten": 18400,
    "overdue": 9800,
    "unassigned": 12200,
    "atRisk": 6920
  },
  "trend": [
    {"date": "2025-02-01", "debt": 35000},
    {"date": "2025-02-08", "debt": 39000},
    {"date": "2025-02-15", "debt": 47320}
  ],
  "completionRate": 0.34,
  "industryBenchmark": 0.67,
  "totalActions": 68,
  "completedActions": 23,
  "incompleteActions": 45
}
```

#### GET /all-actions
**Purpose:** Get all action items across all meetings

**Request:**
```
GET /all-actions?status=incomplete&owner=Ashhar
Headers:
  Authorization: Bearer <cognito-token>
```

**Response:**
```json
{
  "actions": [
    {
      "id": "action-1",
      "task": "Finalize API documentation",
      "owner": "Ashhar",
      "deadline": "2025-03-15",
      "completed": false,
      "riskScore": 87,
      "riskLevel": "CRITICAL",
      "meetingId": "meeting-123",
      "meetingTitle": "Q1 Planning",
      "createdAt": "2025-01-29T10:00:00Z",
      "ageInDays": 47
    }
  ],
  "total": 45,
  "filtered": 12
}
```

#### POST /calculate-risk
**Purpose:** Calculate decay risk for action items

**Request:**
```
POST /calculate-risk
Headers:
  Authorization: Bearer <cognito-token>
Body:
{
  "meetingId": "meeting-123"
}
```

**Response:**
```json
{
  "success": true,
  "updated": 7,
  "highRisk": 3,
  "mediumRisk": 2,
  "lowRisk": 2
}
```

#### POST /check-duplicate
**Purpose:** Check if action item is duplicate

**Request:**
```
POST /check-duplicate
Headers:
  Authorization: Bearer <cognito-token>
Body:
{
  "task": "Finalize API documentation"
}
```

**Response:**
```json
{
  "isDuplicate": true,
  "similarity": 0.94,
  "original": {
    "id": "action-old",
    "task": "Complete API docs",
    "meetingId": "meeting-100",
    "createdAt": "2025-01-10T10:00:00Z",
    "ageInDays": 66
  },
  "history": [
    {"task": "Complete API docs", "date": "2025-01-10"},
    {"task": "Finish API documentation", "date": "2025-01-24"},
    {"task": "Finalize API docs", "date": "2025-02-03"}
  ],
  "isChronicBlocker": true,
  "repeatCount": 4
}
```

---

## Frontend Architecture

### New Pages

#### /debt-dashboard
**Purpose:** Meeting debt overview
**Components:**
- DebtCounter (animated)
- DebtBreakdown (pie chart)
- TrendGraph (line chart)
- BenchmarkComparison
- QuickActions

#### /actions-overview
**Purpose:** All action items view
**Components:**
- KanbanBoard
- ActionCard
- FilterBar
- BulkActions
- TimelineView (optional)

#### /graveyard
**Purpose:** Abandoned action items
**Components:**
- Tombstone
- GraveyardStats
- ResurrectModal

### Modified Pages

#### /meeting/:id (Enhanced)
**New Components:**
- MeetingROI
- QualityScore
- Recommendations
- ComparisonChart

#### / (Dashboard - Enhanced)
**New Components:**
- TeamLeaderboard
- PatternCards
- DebtWidget

---

## Algorithm Designs

### 1. Decay Risk Calculation

```python
def calculate_decay_risk(action, user_history):
    """
    Calculate risk score (0-100) for action item decay
    
    Risk Factors:
    - No owner: +45 points (89% failure rate)
    - Age >7 days: +25 points
    - Age >14 days: +15 points
    - No deadline: +20 points
    - Owner completion rate <50%: +15 points
    - Vague task (short description): +10 points
    """
    risk = 0
    
    # Factor 1: Owner assignment
    if not action.get('owner') or action['owner'] == 'Unassigned':
        risk += 45
    else:
        # Factor 5: Owner track record
        owner_stats = get_owner_stats(action['owner'], user_history)
        if owner_stats['completionRate'] < 0.5:
            risk += 15
    
    # Factor 2 & 3: Age
    age_days = (datetime.now() - action['createdAt']).days
    if age_days > 7:
        risk += 25
    if age_days > 14:
        risk += 15
    
    # Factor 4: Deadline
    if not action.get('deadline'):
        risk += 20
    
    # Factor 6: Task clarity
    if len(action['task']) < 20:
        risk += 10
    
    return min(risk, 100)

def get_risk_level(score):
    if score >= 75: return 'CRITICAL'
    if score >= 50: return 'HIGH'
    if score >= 25: return 'MEDIUM'
    return 'LOW'
```

### 2. Meeting Debt Calculation

```python
def calculate_meeting_debt(user_id):
    """
    Calculate total meeting debt for user
    
    Debt = Sum of (incomplete action items × estimated blocked time × hourly rate)
    """
    AVG_HOURLY_RATE = 75  # $75/hour
    AVG_BLOCKED_TIME_HOURS = 3.2  # Research-backed
    
    meetings = get_all_meetings(user_id)
    
    debt_breakdown = {
        'forgotten': 0,  # >30 days old
        'overdue': 0,    # Past deadline
        'unassigned': 0, # No owner
        'atRisk': 0      # High risk score
    }
    
    for meeting in meetings:
        for action in meeting['actionItems']:
            if action['completed']:
                continue
            
            cost = AVG_BLOCKED_TIME_HOURS * AVG_HOURLY_RATE
            
            age_days = (datetime.now() - action['createdAt']).days
            
            if age_days > 30:
                debt_breakdown['forgotten'] += cost
            elif action.get('deadline') and action['deadline'] < datetime.now():
                debt_breakdown['overdue'] += cost
            elif not action.get('owner') or action['owner'] == 'Unassigned':
                debt_breakdown['unassigned'] += cost
            elif action.get('riskScore', 0) >= 75:
                debt_breakdown['atRisk'] += cost
    
    total_debt = sum(debt_breakdown.values())
    
    return {
        'totalDebt': total_debt,
        'breakdown': debt_breakdown
    }
```

### 3. Duplicate Detection (Cosine Similarity)

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def find_duplicates(new_action_task, all_actions, threshold=0.85):
    """
    Find duplicate action items using Bedrock Titan Embeddings
    """
    # Generate embedding for new action
    new_embedding = get_bedrock_embedding(new_action_task)
    
    duplicates = []
    
    for existing in all_actions:
        if existing['completed']:
            continue
        
        existing_embedding = existing.get('embedding')
        if not existing_embedding:
            # Generate and store embedding
            existing_embedding = get_bedrock_embedding(existing['task'])
            update_action_embedding(existing['id'], existing_embedding)
        
        similarity = cosine_similarity(new_embedding, existing_embedding)
        
        if similarity >= threshold:
            duplicates.append({
                'action': existing,
                'similarity': similarity
            })
    
    # Sort by similarity (highest first)
    duplicates.sort(key=lambda x: x['similarity'], reverse=True)
    
    return duplicates

def get_bedrock_embedding(text):
    """Get embedding from Bedrock Titan"""
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']
```

### 4. Meeting ROI Calculation

```python
def calculate_meeting_roi(meeting):
    """
    Calculate ROI for a meeting
    
    Cost = attendees × duration × hourly_rate
    Value = (decisions × decision_value) + (actionable_items × action_value)
    ROI = (value - cost) / cost
    """
    AVG_HOURLY_RATE = 75
    DECISION_VALUE = 500  # Estimated value per decision
    ACTION_VALUE = 200    # Estimated value per actionable item
    
    # Calculate cost
    attendees = meeting.get('attendeeCount', 5)  # Default 5
    duration_hours = meeting.get('durationMinutes', 60) / 60
    cost = attendees * duration_hours * AVG_HOURLY_RATE
    
    # Calculate value
    decisions = len(meeting.get('decisions', []))
    actionable_items = len([a for a in meeting.get('actionItems', []) 
                           if a.get('owner') and a.get('deadline')])
    
    value = (decisions * DECISION_VALUE) + (actionable_items * ACTION_VALUE)
    
    # Calculate ROI
    if cost == 0:
        roi = 0
    else:
        roi = (value - cost) / cost
    
    # Calculate quality score (0-10)
    quality_score = min(10, max(0, 5 + (roi * 5)))
    
    return {
        'cost': cost,
        'value': value,
        'roi': roi,
        'qualityScore': round(quality_score, 1)
    }
```

---

## Security Considerations

### Authentication
- All API endpoints require Cognito JWT token
- Token validated on every request
- User ID extracted from token claims

### Authorization
- Users can only access their own data
- DynamoDB queries filtered by userId
- No cross-user data leakage

### Data Privacy
- No PII in CloudWatch logs
- Embeddings stored securely in DynamoDB
- Audio files deleted after processing (optional)

---

## Performance Optimizations

### DynamoDB
- Use GSIs for efficient queries
- Batch operations where possible
- Limit scan operations
- Use pagination for large result sets

### Lambda
- Reuse Bedrock client connections
- Cache user statistics (5-minute TTL)
- Async processing for non-critical tasks
- Optimize cold starts (keep functions warm)

### Frontend
- Lazy load components
- Virtualize long lists
- Debounce search inputs
- Cache API responses (React Query)

---

## Testing Strategy

### Unit Tests
- Lambda function logic
- Risk calculation algorithm
- Similarity calculation
- ROI calculation

### Integration Tests
- API endpoint responses
- DynamoDB queries
- Bedrock integration
- Authentication flow

### E2E Tests
- User uploads meeting
- Dashboard displays debt
- Action items update
- Duplicate detection works

### Manual Testing Checklist
- [ ] Debt dashboard loads
- [ ] Numbers are accurate
- [ ] Charts render correctly
- [ ] Filters work
- [ ] Mobile responsive
- [ ] Accessible (keyboard navigation)

---

## Deployment Strategy

### Day-by-Day Deployment

**Day 1:**
- Deploy new Lambda: get-debt-analytics
- Deploy frontend: DebtDashboard page
- Test with existing data

**Day 2:**
- Modify process-meeting Lambda
- Deploy calculate-meeting-roi Lambda
- Update meeting detail page

**Day 3:**
- Deploy get-all-actions Lambda
- Deploy ActionsOverview page
- Create DynamoDB GSIs

**Day 4:**
- Deploy calculate-decay-risk Lambda
- Create EventBridge rule
- Update action item display

**Day 5:**
- Modify process-meeting Lambda (embeddings)
- Deploy check-duplicate Lambda
- Update frontend validation

**Day 6:**
- Deploy Graveyard page
- Deploy Leaderboard component
- Update dashboard

**Day 7:**
- Deploy detect-patterns Lambda
- Deploy Pattern cards
- Update article

### Rollback Plan
- Keep previous Lambda versions
- Feature flags for new UI
- Database migrations are additive only
- Can disable new features via config

---

## Monitoring & Observability

### CloudWatch Metrics
- Lambda invocation count
- Lambda duration
- Lambda errors
- API Gateway 4xx/5xx errors
- DynamoDB read/write capacity

### Custom Metrics
- Meetings processed per day
- Action items created per day
- Completion rate trend
- Debt calculation time
- Duplicate detection accuracy

### Alarms
- Lambda error rate >5%
- API Gateway 5xx >1%
- DynamoDB throttling
- Bedrock quota exceeded

---

## Cost Estimation

### Per Day Costs

**Day 1:**
- Lambda executions: ~$0.50
- DynamoDB reads: ~$0.20
- Total: ~$0.70

**Day 2-7:**
- Lambda executions: ~$1.00/day
- DynamoDB reads/writes: ~$0.50/day
- Bedrock API calls: ~$2.00/day
- Total: ~$3.50/day

**7-Day Total:** ~$22

**Monthly (Production):**
- 100 users × 10 meetings/month = 1000 meetings
- Lambda: ~$15
- DynamoDB: ~$10
- Bedrock: ~$50
- S3/CloudFront: ~$5
- Total: ~$80/month

---

## Success Criteria

### Technical
- [ ] All APIs return <500ms
- [ ] Zero data loss
- [ ] 99.9% uptime
- [ ] No security vulnerabilities

### Business
- [ ] Completion rate improves +50%
- [ ] Meeting debt reduces -60%
- [ ] User engagement: 80% DAU
- [ ] Competition score: 10/10

### User Experience
- [ ] Dashboard loads <2s
- [ ] Mobile responsive
- [ ] Accessible (WCAG AA)
- [ ] Intuitive navigation
