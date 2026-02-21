# MeetingMind - Prioritized Issues & Improvements

**Generated:** February 21, 2026  
**Purpose:** Comprehensive architecture review with issues sorted by ease × impact

**Scoring System:**
- **Ease:** 1 (hardest) to 5 (easiest)
- **Impact:** 1 (low) to 5 (critical)
- **Priority Score:** Ease × Impact (max 25)

---

## 🔥 CRITICAL SECURITY ISSUES (Fix Immediately)

### 1. localStorage Token Storage (XSS Vulnerability)
**Priority: 20** (Ease: 4, Impact: 5)  
**Severity:** HIGH  
**File:** `frontend/src/utils/auth.js`

**Issue:**
```javascript
// Current: Vulnerable to XSS attacks
localStorage.setItem('mm_user', displayName)
```

JWT tokens stored in localStorage can be stolen via XSS. One malicious script = full account compromise.

**Fix:**
- Move to httpOnly cookies with SameSite=Strict
- Update Cognito configuration to use cookie-based auth
- Remove all localStorage token references

**Effort:** 4-6 hours  
**Files:** `frontend/src/utils/auth.js`, API Gateway configuration

---

### 2. CORS Wildcard in Template
**Priority: 25** (Ease: 5, Impact: 5)  
**Severity:** HIGH  
**File:** `backend/template.yaml` line 142

**Issue:**
```yaml
Cors:
  AllowOrigin: "'*'"  # ANY website can call your API
```

**Fix:**
```yaml
Cors:
  AllowOrigin: "'https://dcfx593ywvy92.cloudfront.net'"
```

**Effort:** 5 minutes  
**Files:** `backend/template.yaml`

**Note:** Lambda functions already have correct CORS (CloudFront domain only). Template needs update.

---

### 3. No Rate Limiting
**Priority: 15** (Ease: 3, Impact: 5)  
**Severity:** MEDIUM  
**File:** `backend/template.yaml`

**Issue:**
- Single user can spam API and rack up costs
- No throttling on expensive operations (Bedrock calls)
- Vulnerable to DoS attacks

**Fix:**
Add API Gateway usage plans:
```yaml
UsagePlan:
  Type: AWS::ApiGateway::UsagePlan
  Properties:
    Throttle:
      BurstLimit: 100
      RateLimit: 50
    Quota:
      Limit: 10000
      Period: DAY
```

**Effort:** 2-3 hours  
**Files:** `backend/template.yaml`

---

### 4. No Input Validation
**Priority: 12** (Ease: 3, Impact: 4)  
**Severity:** MEDIUM  
**Files:** All Lambda functions

**Issue:**
- No schema validation on request bodies
- Trusts all user input
- File size validation exists but no content-type verification

**Fix:**
- Add JSON schema validation in API Gateway
- Validate file types (not just extensions)
- Sanitize all string inputs

**Effort:** 1 day  
**Files:** All Lambda functions, API Gateway

---

## 🚨 CRITICAL SCALABILITY ISSUES

### 5. No Pagination Anywhere
**Priority: 20** (Ease: 4, Impact: 5)  
**Severity:** CRITICAL  
**Files:** `backend/functions/list-meetings/app.py`, `backend/functions/get-all-actions/app.py`

**Issue:**
```python
# list-meetings returns ALL meetings in one call
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)
meetings = response.get('Items', [])  # No pagination!
```

**Impact:**
- 100 meetings = slow
- 500 meetings = unusable
- 1000 meetings = crashes

**Fix:**
```python
# Implement cursor-based pagination
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id},
    Limit=50,
    ExclusiveStartKey=last_key if last_key else None
)
return {
    'meetings': response['Items'],
    'nextToken': response.get('LastEvaluatedKey')
}
```

**Effort:** 1 day  
**Files:** 
- `backend/functions/list-meetings/app.py`
- `backend/functions/get-all-actions/app.py`
- `frontend/src/utils/api.js`
- `frontend/src/pages/Dashboard.jsx`

---

### 6. No Caching Layer
**Priority: 16** (Ease: 4, Impact: 4)  
**Severity:** HIGH  
**Files:** All Lambda functions

**Issue:**
- Every dashboard load = full DynamoDB scan
- Leaderboard recalculated on every request
- Health scores recalculated every time

**Fix:**
- Add CloudFront caching (TTL: 60s for dashboard)
- Add ElastiCache for leaderboard/patterns
- Cache health scores in DynamoDB

**Effort:** 2-3 days  
**Files:** CloudFront configuration, Lambda functions

---

### 7. Synchronous Epitaph Generation Blocks Response
**Priority: 15** (Ease: 3, Impact: 5)  
**Severity:** HIGH  
**File:** `backend/functions/get-all-actions/app.py` lines 150-250

**Issue:**
```python
# Generates epitaphs synchronously during API call
for action in all_actions:
    if needs_epitaph:
        epitaph = generate_epitaph(action, days_old)  # BLOCKS!
```

**Impact:**
- API response time: 5-10 seconds (unacceptable)
- Multiple Bedrock calls in request path
- User waits for AI generation

**Fix:**
- Move epitaph generation to async Lambda (EventBridge trigger)
- Generate epitaphs nightly for all graveyard items
- Return cached epitaphs immediately

**Effort:** 1 day  
**Files:** `backend/functions/get-all-actions/app.py`, new Lambda function

---

### 8. Frontend Polling Every 8 Seconds
**Priority: 12** (Ease: 3, Impact: 4)  
**Severity:** MEDIUM  
**File:** `frontend/src/pages/Dashboard.jsx`

**Issue:**
- Wastes API calls
- Increases costs
- Feels sluggish

**Fix:**
- Implement WebSocket for real-time updates (API Gateway WebSocket)
- Use DynamoDB streams to push updates
- Reduce polling to 30 seconds as fallback

**Effort:** 3-4 days  
**Files:** New WebSocket Lambda, frontend

---

## 🐛 FUNCTIONAL BUGS

### 9. Kanban Drag-and-Drop Not Working
**Priority: 20** (Ease: 4, Impact: 5)  
**Severity:** HIGH  
**File:** `frontend/src/components/KanbanBoard.jsx`

**Issue:**
- Drag-and-drop between columns doesn't work
- User reported in context transfer

**Fix:**
- Implement `onDragEnd` handler
- Update action status via API
- Sync with backend

**Effort:** 4-6 hours  
**Files:** `frontend/src/components/KanbanBoard.jsx`, `frontend/src/pages/ActionsOverview.jsx`

---

### 10. Graveyard Resurrection Not Implemented
**Priority: 16** (Ease: 4, Impact: 4)  
**Severity:** MEDIUM  
**File:** `frontend/src/pages/Graveyard.jsx`

**Issue:**
- No way to bring items back from graveyard
- User reported in context transfer

**Fix:**
- Add "Resurrect" button to graveyard items
- Update action status to 'todo'
- Remove from graveyard view

**Effort:** 2-3 hours  
**Files:** `frontend/src/pages/Graveyard.jsx`

---

### 11. Decimal Serialization Crashes
**Priority: 15** (Ease: 3, Impact: 5)  
**Severity:** HIGH  
**File:** Multiple Lambda functions

**Issue:**
```python
# DynamoDB returns Decimal, json.dumps() crashes
return json.dumps(meeting)  # TypeError: Decimal not serializable
```

**Fix:**
```python
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

return json.dumps(meeting, cls=DecimalEncoder)
```

**Effort:** 1 hour  
**Files:** All Lambda functions (already partially fixed)

---

### 12. No Timeout on Transcribe Polling
**Priority: 12** (Ease: 4, Impact: 3)  
**Severity:** MEDIUM  
**File:** `backend/functions/process-meeting/app.py`

**Issue:**
```python
# Infinite loop risk
for _ in range(48):  # Why 48? Magic number
    time.sleep(15)
    # check status
```

**Fix:**
```python
import time
start_time = time.time()
timeout = 720  # 12 minutes
while time.time() - start_time < timeout:
    time.sleep(15)
    if status in ['COMPLETED', 'FAILED']:
        break
else:
    raise TimeoutError("Transcription timeout")
```

**Effort:** 30 minutes  
**Files:** `backend/functions/process-meeting/app.py`

---

## ⚡ PERFORMANCE ISSUES

### 13. No Connection Pooling
**Priority: 12** (Ease: 4, Impact: 3)  
**Severity:** MEDIUM  
**Files:** All Lambda functions

**Issue:**
```python
# Creates new connection every invocation
dynamodb = boto3.resource('dynamodb')
```

**Fix:**
```python
# Reuse connection across invocations
dynamodb = None
def get_dynamodb():
    global dynamodb
    if dynamodb is None:
        dynamodb = boto3.resource('dynamodb')
    return dynamodb
```

**Effort:** 2 hours  
**Files:** All Lambda functions

---

### 14. O(n*m) Complexity in get-all-actions
**Priority: 10** (Ease: 2, Impact: 5)  
**Severity:** HIGH  
**File:** `backend/functions/get-all-actions/app.py`

**Issue:**
```python
# Nested loops - will timeout with large datasets
for meeting in meetings:
    for action in meeting.get('actionItems', []):
        all_actions.append(action)
```

**Fix:**
- Use DynamoDB streams to maintain materialized view
- Create separate actions table with GSI
- Pre-aggregate action items

**Effort:** 3-4 days  
**Files:** New DynamoDB table, Lambda functions

---

### 15. Health Score Recalculated Every Request
**Priority: 15** (Ease: 5, Impact: 3)  
**Severity:** MEDIUM  
**File:** `backend/functions/list-meetings/app.py`

**Issue:**
```python
# Calculates health score for every meeting on every request
for meeting in meetings:
    health = calculate_health_score(meeting)
```

**Fix:**
- Calculate health score once when meeting completes
- Store in DynamoDB
- Recalculate only when action items change

**Effort:** 2-3 hours  
**Files:** `backend/functions/list-meetings/app.py`, `backend/functions/process-meeting/app.py`

---

## 📊 OBSERVABILITY GAPS

### 16. No Structured Logging
**Priority: 10** (Ease: 5, Impact: 2)  
**Severity:** LOW  
**Files:** All Lambda functions

**Issue:**
```python
print(f"Error: {e}")  # Unstructured
```

**Fix:**
```python
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info(json.dumps({
    'event': 'error',
    'error': str(e),
    'userId': user_id,
    'meetingId': meeting_id
}))
```

**Effort:** 1 day  
**Files:** All Lambda functions

---

### 17. No Correlation IDs
**Priority: 8** (Ease: 4, Impact: 2)  
**Severity:** LOW  
**Files:** All Lambda functions

**Issue:**
- Cannot trace requests across services
- Hard to debug distributed issues

**Fix:**
- Generate correlation ID in API Gateway
- Pass through all Lambda functions
- Log in every function

**Effort:** 1 day  
**Files:** All Lambda functions, API Gateway

---

### 18. No Custom Metrics
**Priority: 6** (Ease: 3, Impact: 2)  
**Severity:** LOW  
**Files:** All Lambda functions

**Issue:**
- No business KPIs tracked
- Only infrastructure metrics

**Fix:**
- Add CloudWatch custom metrics:
  - Meeting processing success rate
  - Average processing time
  - Bedrock model usage
  - Action item assignment rate

**Effort:** 2-3 hours  
**Files:** Lambda functions

---

## 🎨 UX IMPROVEMENTS

### 19. No Search Functionality
**Priority: 12** (Ease: 3, Impact: 4)  
**Severity:** MEDIUM  
**Files:** Frontend

**Issue:**
- Cannot search meetings or action items
- Hard to find specific items

**Fix:**
- Add search bar to dashboard
- Implement client-side filtering
- (Future: Add OpenSearch for full-text search)

**Effort:** 1 day  
**Files:** `frontend/src/pages/Dashboard.jsx`, `frontend/src/pages/ActionsOverview.jsx`

---

### 20. No Undo Functionality
**Priority: 10** (Ease: 5, Impact: 2)  
**Severity:** LOW  
**Files:** Frontend

**Issue:**
- Accidental status changes cannot be undone
- No action history

**Fix:**
- Add undo button (5-second window)
- Store previous state in memory
- Revert API call if undo clicked

**Effort:** 4-6 hours  
**Files:** Frontend components

---

### 21. No Export Functionality
**Priority: 12** (Ease: 4, Impact: 3)  
**Severity:** MEDIUM  
**Files:** Frontend

**Issue:**
- Cannot export meetings to PDF/CSV
- Hard to share with non-users

**Fix:**
- Add export button
- Generate PDF using jsPDF
- Generate CSV using Papa Parse

**Effort:** 1 day  
**Files:** Frontend components

---

## 🏗️ ARCHITECTURAL IMPROVEMENTS

### 22. Monolithic Lambda Functions
**Priority: 6** (Ease: 1, Impact: 6)  
**Severity:** HIGH (but hard to fix)  
**File:** `backend/functions/process-meeting/app.py`

**Issue:**
- 900s timeout (15 minutes!)
- Does transcription + analysis + storage + email
- Hard to debug and maintain

**Fix:**
- Break into Step Functions workflow:
  1. Transcribe audio
  2. Analyze transcript
  3. Extract structure
  4. Generate embeddings
  5. Calculate risk
  6. Store in DynamoDB
  7. Send email

**Effort:** 1-2 weeks  
**Files:** New Step Functions definition, multiple Lambda functions

---

### 23. No Dead Letter Queue Monitoring
**Priority: 10** (Ease: 5, Impact: 2)  
**Severity:** LOW  
**File:** `backend/template.yaml`

**Issue:**
- DLQ exists but no alerting
- Failed messages go unnoticed

**Fix:**
- Add CloudWatch alarm on DLQ depth
- Send SNS notification to admin
- Create dashboard widget

**Effort:** 1 hour  
**Files:** `backend/template.yaml`

---

### 24. No Circuit Breakers
**Priority: 8** (Ease: 2, Impact: 4)  
**Severity:** MEDIUM  
**Files:** Lambda functions

**Issue:**
- No protection against cascading failures
- Bedrock throttling can cause retries storm

**Fix:**
- Implement circuit breaker pattern
- Stop calling Bedrock after N failures
- Use fallback tier immediately

**Effort:** 2-3 days  
**Files:** Lambda functions

---

## 📝 CODE QUALITY ISSUES

### 25. Magic Numbers Everywhere
**Priority: 15** (Ease: 5, Impact: 3)  
**Severity:** LOW  
**Files:** Multiple

**Issue:**
```python
for _ in range(48):  # Why 48?
    time.sleep(15)   # Why 15?

if days_old > 30:  # Why 30?
    # graveyard logic

cost = hours * 75  # Why $75?
```

**Fix:**
- Extract to constants:
```python
TRANSCRIBE_POLL_INTERVAL_SECONDS = 15
TRANSCRIBE_MAX_POLLS = 48
GRAVEYARD_THRESHOLD_DAYS = 30
HOURLY_RATE_USD = 75
```

**Effort:** 2 hours  
**Files:** All Lambda functions

---

### 26. Inconsistent Error Responses
**Priority: 12** (Ease: 4, Impact: 3)  
**Severity:** MEDIUM  
**Files:** All Lambda functions

**Issue:**
- Some return 500, some 400
- No standard error format
- Hard to handle in frontend

**Fix:**
```python
# Standard error format
{
    'error': {
        'code': 'VALIDATION_ERROR',
        'message': 'Invalid meeting ID',
        'details': {...}
    }
}
```

**Effort:** 1 day  
**Files:** All Lambda functions

---

### 27. No Code Coverage Metrics
**Priority: 6** (Ease: 3, Impact: 2)  
**Severity:** LOW  
**Files:** Testing infrastructure

**Issue:**
- Claims 95% coverage but no proof
- No coverage reports

**Fix:**
- Add pytest-cov
- Generate coverage reports
- Add to CI/CD pipeline

**Effort:** 2-3 hours  
**Files:** `backend/tests/`, CI/CD configuration

---

## 🧪 TESTING GAPS

### 28. No Load Testing
**Priority: 10** (Ease: 2, Impact: 5)  
**Severity:** HIGH  
**Files:** None (missing)

**Issue:**
- No idea how many concurrent uploads it can handle
- No performance benchmarks

**Fix:**
- Use Locust or Artillery
- Test scenarios:
  - 100 concurrent uploads
  - 1000 dashboard loads
  - 500 action item updates

**Effort:** 2-3 days  
**Files:** New load testing scripts

---

### 29. No Chaos Engineering
**Priority: 6** (Ease: 2, Impact: 3)  
**Severity:** MEDIUM  
**Files:** None (missing)

**Issue:**
- What happens when Bedrock is down?
- What happens when DynamoDB throttles?

**Fix:**
- Implement chaos tests
- Simulate service failures
- Verify fallback behavior

**Effort:** 3-4 days  
**Files:** New chaos testing scripts

---

### 30. 1 Failing Test
**Priority: 25** (Ease: 5, Impact: 5)  
**Severity:** CRITICAL  
**Files:** `backend/tests/`

**Issue:**
- "Acceptable for MVP" is not acceptable
- Indicates broken functionality

**Fix:**
- Identify failing test
- Fix root cause
- Ensure all tests pass

**Effort:** 1-2 hours  
**Files:** Test files

---

## 📱 MISSING FEATURES

### 31. No Mobile App
**Priority: 4** (Ease: 1, Impact: 4)  
**Severity:** LOW (but high value)  
**Files:** None (missing)

**Issue:**
- Web-only
- No native mobile experience

**Fix:**
- Build React Native app
- Reuse API layer
- Add push notifications

**Effort:** 4-6 weeks  
**Files:** New mobile app

---

### 32. No Calendar Integration
**Priority: 8** (Ease: 2, Impact: 4)  
**Severity:** MEDIUM  
**Files:** None (missing)

**Issue:**
- Cannot sync with Google Calendar/Outlook
- Manual meeting creation

**Fix:**
- Add OAuth for Google/Microsoft
- Sync meetings automatically
- Add calendar invites for deadlines

**Effort:** 1-2 weeks  
**Files:** New Lambda functions, frontend

---

### 33. No Jira/Asana Export
**Priority: 10** (Ease: 2, Impact: 5)  
**Severity:** HIGH (for enterprise)  
**Files:** None (missing)

**Issue:**
- Action items stuck in MeetingMind
- No integration with project management tools

**Fix:**
- Add Jira API integration
- Add Asana API integration
- One-click export of action items

**Effort:** 1-2 weeks  
**Files:** New Lambda functions, frontend

---

## 💰 COST OPTIMIZATION

### 34. Always Tries Claude First (Most Expensive)
**Priority: 15** (Ease: 5, Impact: 3)  
**Severity:** MEDIUM  
**File:** `backend/functions/process-meeting/app.py`

**Issue:**
```python
models = [
    ('anthropic.claude-3-haiku-20240307-v1:0', 'anthropic'),  # $$$
    ('apac.amazon.nova-lite-v1:0', 'nova'),                   # $$
    ('apac.amazon.nova-micro-v1:0', 'nova'),                  # $
]
```

**Fix:**
- Start with Nova Micro (cheapest)
- Escalate to Claude only if quality is poor
- Track model success rates

**Effort:** 2 hours  
**Files:** `backend/functions/process-meeting/app.py`

---

### 35. No S3 Lifecycle Policies
**Priority: 20** (Ease: 5, Impact: 4)  
**Severity:** MEDIUM  
**File:** `backend/template.yaml`

**Issue:**
```yaml
LifecycleConfiguration:
  Rules:
    - Id: DeleteOldAudio
      Status: Enabled
      ExpirationInDays: 30  # Good, but could be better
```

**Fix:**
- Move to Glacier after 7 days
- Delete after 90 days
- Save 80% on storage costs

**Effort:** 10 minutes  
**Files:** `backend/template.yaml`

---

## 📊 SUMMARY

### By Priority Score (Top 10)
1. **CORS Wildcard** (25) - 5 minutes
2. **1 Failing Test** (25) - 1-2 hours
3. **localStorage Tokens** (20) - 4-6 hours
4. **No Pagination** (20) - 1 day
5. **Kanban Drag-and-Drop** (20) - 4-6 hours
6. **S3 Lifecycle** (20) - 10 minutes
7. **Graveyard Resurrection** (16) - 2-3 hours
8. **No Caching** (16) - 2-3 days
9. **Epitaph Generation Blocks** (15) - 1 day
10. **Rate Limiting** (15) - 2-3 hours

### Quick Wins (High Impact, Low Effort)
1. Fix CORS wildcard (5 min)
2. Fix failing test (1-2 hours)
3. Add S3 lifecycle policies (10 min)
4. Extract magic numbers to constants (2 hours)
5. Add DLQ monitoring (1 hour)
6. Cache health scores (2-3 hours)

### Must-Fix Before Competition
1. CORS wildcard
2. Failing test
3. localStorage tokens
4. No pagination
5. Rate limiting
6. Kanban drag-and-drop
7. Graveyard resurrection

### Long-Term Improvements
1. Break monolithic Lambda into Step Functions
2. Add WebSocket for real-time updates
3. Implement full-text search (OpenSearch)
4. Build mobile app
5. Add calendar integrations
6. Add Jira/Asana export

---

**Total Issues:** 35  
**Critical:** 10  
**High:** 12  
**Medium:** 10  
**Low:** 3

**Estimated Effort to Fix All Critical:** 2-3 weeks  
**Estimated Effort for Competition-Ready:** 3-5 days
