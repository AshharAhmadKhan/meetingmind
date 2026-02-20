# Comprehensive Fix Plan - All 40+ Issues

**Goal:** Fix every single issue identified in the audit before AWS Support responds  
**Timeline:** Execute immediately  
**Approach:** Systematic, prioritized by severity

---

## Phase 1: CRITICAL - Backend CORS & Serialization (Issues 1-5)

### 1.1 Fix All Lambda CORS Headers
**Files:** All 18 Lambda functions
**Action:** 
- Add CORS_HEADERS constant with CloudFront domain
- Add OPTIONS handler at start of lambda_handler
- Ensure CORS headers in ALL return statements (success + error)

### 1.2 Fix Decimal Serialization
**Files:** All Lambda functions that use DynamoDB
**Action:**
- Add decimal_to_float() function
- Use `default=decimal_to_float` in ALL json.dumps() calls
- Test with sample data

### 1.3 Fix API Gateway CORS Configuration
**File:** backend/template.yaml
**Action:**
- Remove duplicate CORS configuration
- Let Lambda functions handle CORS headers
- Remove `Cors:` section from HttpApi

---

## Phase 2: HIGH PRIORITY - Error Handling & Configuration (Issues 6-15)

### 2.1 Frontend API Error Handling
**File:** frontend/src/utils/api.js
**Action:**
- Add axios interceptor for auth headers
- Add timeout configuration (30s)
- Add retry logic for 502/503 errors
- Add user-friendly error messages

### 2.2 Frontend Environment Variable Validation
**File:** frontend/src/utils/auth.js
**Action:**
- Validate required env vars on startup
- Show error message if missing
- Add fallback values for development

### 2.3 S3 Upload Content-Type Fix
**File:** frontend/src/utils/api.js
**Action:**
- Include Content-Type header in S3 upload
- Match presigned URL signature

### 2.4 DynamoDB Pagination
**Files:** list-meetings/app.py, get-all-actions/app.py
**Action:**
- Implement pagination with LastEvaluatedKey
- Add limit parameter
- Handle large result sets

### 2.5 Bedrock Retry Configuration
**File:** check-duplicate/app.py
**Action:**
- Enable retries (currently disabled)
- Use exponential backoff
- Match process-meeting configuration

---

## Phase 3: MEDIUM PRIORITY - Data Validation & Security (Issues 16-25)

### 3.1 Input Validation
**Files:** create-team/app.py, update-action/app.py
**Action:**
- Validate team name length/characters
- Validate action status values
- Add input sanitization

### 3.2 Hardcoded Values to Environment Variables
**Files:** process-meeting/app.py, send-welcome-email/app.py
**Action:**
- Move FRONTEND_URL to env var (already done)
- Move SES_FROM_EMAIL to env var (already done)
- Verify all env vars are set in template.yaml

### 3.3 Health Score Calculation Consistency
**Files:** list-meetings/app.py, get-meeting/app.py
**Action:**
- Use same calculation logic in both
- Add health score to get-meeting response
- Cache calculated scores

### 3.4 Epitaph Caching
**File:** get-all-actions/app.py
**Action:**
- Check for existing epitaph before generating
- Only regenerate if >7 days old
- Reduce Bedrock costs

### 3.5 Timezone Handling
**File:** frontend/src/components/KanbanBoard.jsx
**Action:**
- Use user's timezone for deadline calculations
- Display timezone-aware dates
- Handle DST transitions

---

## Phase 4: CONFIGURATION - Infrastructure (Issues 26-34)

### 4.1 API Gateway Throttling
**File:** backend/template.yaml
**Action:**
- Add throttling configuration
- Set rate limit: 1000 req/sec
- Set burst limit: 2000 req

### 4.2 S3 Bucket Security
**File:** backend/template.yaml
**Action:**
- Enable versioning
- Enable encryption (AES256)
- Add lifecycle policy

### 4.3 DynamoDB Point-in-Time Recovery
**File:** backend/template.yaml
**Action:**
- Enable PITR on both tables
- Add backup retention policy

### 4.4 CloudWatch Alarms
**File:** backend/template.yaml
**Action:**
- Add alarm for Lambda errors (>10 in 5 min)
- Add alarm for API Gateway 5xx (>5 in 5 min)
- Add alarm for DynamoDB throttling

### 4.5 SQS Configuration
**File:** backend/template.yaml
**Action:**
- Increase visibility timeout to 1200s
- Increase DLQ handler timeout to 300s
- Add message retention policy

### 4.6 X-Ray Sampling Rules
**File:** backend/template.yaml
**Action:**
- Add sampling rules (10% of requests)
- Reduce tracing costs
- Keep critical paths at 100%

---

## Phase 5: FRONTEND - UX & Error Handling (Issues 35-40)

### 5.1 Loading States
**Files:** Dashboard.jsx, MeetingDetail.jsx, ActionsOverview.jsx
**Action:**
- Add loading spinners
- Add skeleton screens
- Improve perceived performance

### 5.2 Error Boundaries
**File:** frontend/src/App.jsx
**Action:**
- Add React error boundary
- Show user-friendly error page
- Log errors to console

### 5.3 Vite Dev Proxy
**File:** frontend/vite.config.js
**Action:**
- Add proxy for API calls during development
- Avoid CORS issues in dev mode

### 5.4 Axios Configuration
**File:** frontend/src/utils/api.js
**Action:**
- Add axios instance with defaults
- Add request/response interceptors
- Add automatic token refresh

---

## Execution Order

1. **Phase 1** (30 min) - Fix all CORS and Decimal issues
2. **Phase 2** (20 min) - Add error handling and pagination
3. **Phase 3** (15 min) - Add validation and security
4. **Phase 4** (20 min) - Update infrastructure configuration
5. **Phase 5** (15 min) - Improve frontend UX

**Total Time:** ~100 minutes  
**Deployment:** After each phase, build and deploy

---

## Success Criteria

- [ ] All Lambda functions return proper CORS headers
- [ ] All Decimal values properly serialized
- [ ] All error responses include CORS headers
- [ ] All OPTIONS requests handled
- [ ] Frontend loads without 502 errors
- [ ] All API calls succeed
- [ ] No CORS errors in console
- [ ] All security best practices implemented
- [ ] All infrastructure properly configured
- [ ] All user-facing errors are friendly

---

**Status:** READY TO EXECUTE  
**Start Time:** Now  
**Expected Completion:** 100 minutes

