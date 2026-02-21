# Rate Limiting Analysis - MeetingMind API

**Date:** 2026-02-22  
**Status:** Discovery Phase Complete  
**Next:** Implementation

---

## Current State

**NO RATE LIMITING** - Any user can:
- Upload unlimited files → S3 costs spike
- Spam Bedrock API → $$$$ costs
- DoS attack by flooding endpoints
- Exhaust DynamoDB capacity

---

## API Endpoints Inventory

### 1. POST /upload-url (CRITICAL - Highest Risk)
**Function:** GetUploadUrlFunction  
**Cost Impact:** HIGH (S3 storage + Transcribe + Bedrock)  
**Current Usage:** Unknown  
**Risk:** User uploads 1000 files = $500+ in costs

**Recommended Limits:**
- Burst: 5 requests/second
- Rate: 2 requests/second sustained
- Quota: 50 uploads/day per user

**Reasoning:** 
- Each upload triggers expensive pipeline (Transcribe $0.024/min + Bedrock $0.003/1K tokens)
- Average meeting = 30 min audio = $0.72 transcribe + $0.50 Bedrock = $1.22/meeting
- 50 meetings/day = $61/day max per user (acceptable)
- 1000 meetings/day = $1,220/day (unacceptable)

---

### 2. POST /check-duplicate (CRITICAL - Bedrock Cost)
**Function:** CheckDuplicateFunction  
**Cost Impact:** VERY HIGH (Bedrock API call every request)  
**Current Usage:** Called before every upload  
**Risk:** Spam this endpoint = direct Bedrock costs

**Recommended Limits:**
- Burst: 10 requests/second
- Rate: 5 requests/second sustained
- Quota: 100 checks/day per user

**Reasoning:**
- Each call = 1 Bedrock invocation
- Bedrock Claude Haiku = $0.25/1M input tokens, $1.25/1M output tokens
- Average check = ~500 tokens = $0.001/check
- 100 checks/day = $0.10/day (acceptable)
- 10,000 checks/day = $10/day (unacceptable)

---

### 3. GET /all-actions (HIGH - Expensive Query)
**Function:** GetAllActionsFunction  
**Cost Impact:** MEDIUM (scans all meetings, generates epitaphs)  
**Current Usage:** Dashboard page, frequent polling  
**Risk:** O(n*m) complexity, synchronous Bedrock calls

**Recommended Limits:**
- Burst: 20 requests/second
- Rate: 10 requests/second sustained
- Quota: 1,000 requests/day per user

**Reasoning:**
- Scans all user meetings (could be 100+)
- Generates epitaphs synchronously (Bedrock calls)
- Frontend polls every 8 seconds = 10,800 calls/day (needs caching!)
- With caching, 1,000/day is reasonable

---

### 4. GET /debt-analytics (MEDIUM - Calculation Heavy)
**Function:** GetDebtAnalyticsFunction  
**Cost Impact:** MEDIUM (calculates health scores, ROI)  
**Current Usage:** Dashboard page  
**Risk:** Recalculates on every request

**Recommended Limits:**
- Burst: 20 requests/second
- Rate: 10 requests/second sustained
- Quota: 500 requests/day per user

**Reasoning:**
- Expensive calculations but no external API calls
- Should be cached (future improvement)
- 500/day allows frequent dashboard visits

---

### 5. PUT /meetings/{meetingId}/actions/{actionId} (MEDIUM - Frequent Writes)
**Function:** UpdateActionFunction  
**Cost Impact:** LOW (single DynamoDB write)  
**Current Usage:** Kanban drag-and-drop, status updates  
**Risk:** Rapid status changes could exhaust write capacity

**Recommended Limits:**
- Burst: 50 requests/second
- Rate: 20 requests/second sustained
- Quota: 2,000 updates/day per user

**Reasoning:**
- Users actively manage action items
- Kanban drag-and-drop needs responsive updates
- 2,000/day = ~1 update every 40 seconds during work hours (reasonable)

---

### 6. GET /meetings (LOW - Read Heavy)
**Function:** ListMeetingsFunction  
**Cost Impact:** LOW (DynamoDB query with pagination)  
**Current Usage:** Dashboard page  
**Risk:** No pagination = returns ALL meetings

**Recommended Limits:**
- Burst: 50 requests/second
- Rate: 20 requests/second sustained
- Quota: 5,000 requests/day per user

**Reasoning:**
- Read-only operation
- Should be cached
- High limit for good UX

---

### 7. GET /meetings/{meetingId} (LOW - Read Heavy)
**Function:** GetMeetingFunction  
**Cost Impact:** LOW (single DynamoDB query)  
**Current Usage:** Meeting detail page  
**Risk:** Minimal

**Recommended Limits:**
- Burst: 50 requests/second
- Rate: 20 requests/second sustained
- Quota: 5,000 requests/day per user

**Reasoning:**
- Read-only, single item query
- Fast response
- High limit for good UX

---

### 8. POST /teams (LOW - Infrequent)
**Function:** CreateTeamFunction  
**Cost Impact:** LOW (single DynamoDB write)  
**Current Usage:** Rare (user creates team once)  
**Risk:** Spam team creation

**Recommended Limits:**
- Burst: 5 requests/second
- Rate: 2 requests/second sustained
- Quota: 10 teams/day per user

**Reasoning:**
- Infrequent operation
- 10 teams/day is generous
- Prevents spam

---

### 9. POST /teams/join (LOW - Infrequent)
**Function:** JoinTeamFunction  
**Cost Impact:** LOW (single DynamoDB write)  
**Current Usage:** Rare (user joins team occasionally)  
**Risk:** Minimal

**Recommended Limits:**
- Burst: 10 requests/second
- Rate: 5 requests/second sustained
- Quota: 20 joins/day per user

**Reasoning:**
- Infrequent operation
- 20 joins/day is generous

---

### 10. GET /teams/{teamId} (LOW - Read Heavy)
**Function:** GetTeamFunction  
**Cost Impact:** LOW (single DynamoDB query)  
**Current Usage:** Team page  
**Risk:** Minimal

**Recommended Limits:**
- Burst: 50 requests/second
- Rate: 20 requests/second sustained
- Quota: 5,000 requests/day per user

**Reasoning:**
- Read-only operation
- Fast response

---

### 11. GET /teams (LOW - Read Heavy)
**Function:** ListUserTeamsFunction  
**Cost Impact:** LOW (DynamoDB query)  
**Current Usage:** Team selector  
**Risk:** Minimal

**Recommended Limits:**
- Burst: 50 requests/second
- Rate: 20 requests/second sustained
- Quota: 5,000 requests/day per user

**Reasoning:**
- Read-only operation
- Fast response

---

## Recommended Rate Limiting Strategy

### Option 1: Global API-Wide Limits (SIMPLEST)
**Pros:**
- Easy to implement (5 minutes)
- Protects against DoS immediately
- No per-endpoint configuration

**Cons:**
- Not granular (treats all endpoints equally)
- May be too restrictive for reads, too lenient for writes

**Configuration:**
```yaml
UsagePlan:
  Type: AWS::ApiGateway::UsagePlan
  Properties:
    UsagePlanName: meetingmind-default-plan
    ApiStages:
      - ApiId: !Ref MeetingMindApi
        Stage: prod
    Throttle:
      BurstLimit: 100    # Max 100 requests in burst
      RateLimit: 50      # 50 requests/second sustained
    Quota:
      Limit: 10000       # 10,000 requests/day per user
      Period: DAY
```

**Estimated Cost Impact:**
- Prevents unlimited uploads (biggest risk)
- Limits Bedrock spam
- Still allows normal usage

---

### Option 2: Per-Endpoint Limits (RECOMMENDED)
**Pros:**
- Granular control
- Optimize for each endpoint's cost/usage pattern
- Better UX (reads not throttled by writes)

**Cons:**
- More complex configuration
- Requires API Gateway method settings

**Configuration:**
```yaml
# Global default (lenient for reads)
UsagePlan:
  Throttle:
    BurstLimit: 100
    RateLimit: 50
  Quota:
    Limit: 10000
    Period: DAY

# Per-method overrides (strict for expensive operations)
MethodSettings:
  - ResourcePath: /upload-url
    HttpMethod: POST
    ThrottlingBurstLimit: 5
    ThrottlingRateLimit: 2
  
  - ResourcePath: /check-duplicate
    HttpMethod: POST
    ThrottlingBurstLimit: 10
    ThrottlingRateLimit: 5
  
  - ResourcePath: /all-actions
    HttpMethod: GET
    ThrottlingBurstLimit: 20
    ThrottlingRateLimit: 10
```

---

### Option 3: Per-User Limits with API Keys (MOST SECURE)
**Pros:**
- Track usage per user
- Enforce quotas per user
- Can offer paid tiers later

**Cons:**
- Requires API key distribution
- More complex setup
- Need to integrate with Cognito

**Configuration:**
```yaml
UsagePlan:
  Type: AWS::ApiGateway::UsagePlan
  Properties:
    ApiKeyRequired: true  # Require API key
    Throttle:
      BurstLimit: 100
      RateLimit: 50
    Quota:
      Limit: 10000
      Period: DAY

# Link to Cognito user
UsagePlanKey:
  Type: AWS::ApiGateway::UsagePlanKey
  Properties:
    KeyId: !Ref ApiKey
    KeyType: API_KEY
    UsagePlanId: !Ref UsagePlan
```

---

## Recommendation: Start with Option 1, Upgrade to Option 2

### Phase 1: Global Limits (TODAY - 30 minutes)
1. Add UsagePlan with conservative global limits
2. Deploy and monitor
3. Prevents DoS and cost spikes immediately

### Phase 2: Per-Endpoint Limits (NEXT WEEK - 2 hours)
1. Add MethodSettings for expensive endpoints
2. Tune based on CloudWatch metrics
3. Optimize UX while protecting costs

### Phase 3: Per-User Limits (FUTURE - 1 day)
1. Integrate API keys with Cognito
2. Track usage per user
3. Enable paid tiers

---

## Implementation Plan

### Step 1: Add Global UsagePlan (30 min)
```yaml
# Add after MeetingMindApi resource
MeetingMindUsagePlan:
  Type: AWS::ApiGateway::UsagePlan
  Properties:
    UsagePlanName: meetingmind-default-plan
    Description: Default rate limiting for all API endpoints
    ApiStages:
      - ApiId: !Ref MeetingMindApi
        Stage: prod
    Throttle:
      BurstLimit: 100
      RateLimit: 50
    Quota:
      Limit: 10000
      Period: DAY
```

### Step 2: Deploy and Test (15 min)
```bash
sam build
sam deploy --no-confirm-changeset
```

### Step 3: Monitor CloudWatch (ongoing)
- Check API Gateway metrics
- Look for 429 errors (throttled requests)
- Adjust limits if needed

### Step 4: Add Per-Endpoint Limits (future)
- Add MethodSettings to API Gateway
- Configure per-endpoint throttles

---

## Testing Strategy

### Test 1: Verify Throttling Works
```bash
# Spam API with 200 requests
for i in {1..200}; do
  curl -H "Authorization: Bearer $TOKEN" \
    https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod/meetings &
done
wait

# Expected: Some requests return 429 Too Many Requests
```

### Test 2: Verify Normal Usage Works
```bash
# Normal dashboard load (10 requests)
for i in {1..10}; do
  curl -H "Authorization: Bearer $TOKEN" \
    https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod/meetings
  sleep 1
done

# Expected: All requests succeed (200 OK)
```

### Test 3: Verify Quota Enforcement
```bash
# Make 10,001 requests in one day
# Expected: Request 10,001 returns 429 with quota exceeded message
```

---

## Monitoring and Alerts

### CloudWatch Metrics to Watch
1. **API Gateway → Count** - Total requests
2. **API Gateway → 4XXError** - Client errors (includes 429)
3. **API Gateway → Latency** - Response time
4. **Lambda → Throttles** - Lambda-level throttling

### Recommended Alarms
1. **High 429 Rate** - Alert if >5% of requests throttled
2. **Quota Near Limit** - Alert if user hits 80% of daily quota
3. **Unusual Spike** - Alert if requests >2x normal

---

## Cost Impact Analysis

### Before Rate Limiting
**Worst Case Scenario:**
- Malicious user uploads 1,000 meetings/day
- Cost: $1,220/day = $36,600/month
- Bedrock spam: $100/day = $3,000/month
- **Total Risk: $39,600/month**

### After Rate Limiting (Option 1)
**Worst Case Scenario:**
- User hits 10,000 request quota
- ~50 uploads/day max (based on quota distribution)
- Cost: $61/day = $1,830/month
- Bedrock: $10/day = $300/month
- **Total Risk: $2,130/month**

**Savings: $37,470/month (94% reduction)**

---

## Next Steps

1. ✅ Discovery complete - all endpoints identified
2. ⏳ Review this analysis with user
3. ⏳ Implement Option 1 (global limits)
4. ⏳ Deploy and test
5. ⏳ Monitor for 24 hours
6. ⏳ Tune limits based on real usage
7. ⏳ Plan Option 2 (per-endpoint limits)

---

## Questions for User

1. **Which option do you prefer?**
   - Option 1: Global limits (fast, simple)
   - Option 2: Per-endpoint limits (better UX)
   - Option 3: Per-user limits (most secure)

2. **What are your expected usage patterns?**
   - How many meetings/day per user?
   - How many team members?
   - Peak usage times?

3. **Risk tolerance?**
   - Start conservative and loosen?
   - Start lenient and tighten based on abuse?

4. **Should we proceed with Option 1 today?**
   - 30 minutes to implement
   - Immediate protection
   - Can upgrade later
