# Fix #2: Epitaph Pre-Generation - Complete Analysis

**Goal:** Make Graveyard load INSTANTLY (<500ms) instead of 5-10 seconds  
**Impact:** HIGH - Graveyard with AI epitaphs is your UNIQUE differentiator  
**Risk:** LOW - Adds new Lambda, doesn't break existing flow  
**Effort:** 4 hours

---

## Current Architecture (SLOW)

### Flow:
```
User visits /graveyard
    ↓
Frontend calls getAllActions()
    ↓
Backend: get-all-actions Lambda
    ↓
Query DynamoDB for all meetings
    ↓
Filter actions >30 days old
    ↓
FOR EACH graveyard action:
    ├─ Check if epitaph exists
    ├─ Check if epitaph is stale (>7 days)
    └─ If missing/stale:
        ├─ Call generate_epitaph()
        ├─ Try Haiku model (with retries)
        ├─ Try Nova Lite (if Haiku fails)
        ├─ Try Nova Micro (if Nova Lite fails)
        ├─ Fallback to template (if all fail)
        └─ Update DynamoDB with epitaph
    ↓
Return all actions with epitaphs
    ↓
Frontend displays graveyard
```

### Problems:
1. **Synchronous Bedrock calls** - Each epitaph takes 1-3 seconds
2. **Multiple actions** - 10 graveyard items = 10-30 seconds total
3. **Blocks user request** - User waits for ALL epitaphs to generate
4. **Throttling risk** - Multiple concurrent requests = Bedrock throttling
5. **Poor UX** - 5-10 second load time for key differentiator feature

### Current Code Location:
- **File:** `backend/functions/get-all-actions/app.py`
- **Lines:** 250-320 (epitaph generation logic)
- **Function:** `generate_epitaph(action, days_old)`
- **Models:** Haiku → Nova Lite → Nova Micro → Fallback

---

## New Architecture (FAST)

### Flow:
```
EventBridge Schedule (3 AM UTC daily)
    ↓
generate-epitaphs Lambda
    ↓
Scan DynamoDB for all meetings
    ↓
Find graveyard actions (>30 days, incomplete)
    ↓
Filter: missing epitaph OR stale epitaph (>7 days)
    ↓
FOR EACH action needing epitaph:
    ├─ Generate epitaph (reuse existing logic)
    ├─ Add exponential backoff for throttling
    ├─ Update DynamoDB with:
    │   ├─ epitaph: "Here lies..."
    │   └─ epitaphGeneratedAt: "2026-02-22T03:00:00Z"
    └─ Log success/failure
    ↓
CloudWatch logs summary
```

### User Request Flow (INSTANT):
```
User visits /graveyard
    ↓
Frontend calls getAllActions()
    ↓
Backend: get-all-actions Lambda
    ↓
Query DynamoDB for all meetings
    ↓
Filter actions >30 days old
    ↓
Return actions with CACHED epitaphs
    ↓
Frontend displays graveyard (<500ms total)
```

### Benefits:
1. **Instant loading** - No Bedrock calls during user request
2. **No throttling** - Batch generation with backoff
3. **Always fresh** - Regenerated nightly
4. **Scales** - Works with 1000s of users
5. **Better UX** - Graveyard is your killer feature, must be fast

---

## Implementation Plan

### Step 1: Create New Lambda Function (2 hours)

**File:** `backend/functions/generate-epitaphs/app.py`

```python
import json
import boto3
import os
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from botocore.config import Config
import sys
sys.path.append('/opt/python')
from constants import GRAVEYARD_THRESHOLD_DAYS, EPITAPH_TTL_DAYS

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

bedrock_config = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'ap-south-1'), config=bedrock_config)


def generate_epitaph(action, days_old):
    """
    Generate AI epitaph for graveyard action item.
    REUSE EXACT LOGIC from get-all-actions/app.py
    """
    # Copy entire generate_epitaph() function from get-all-actions
    # Copy get_fallback_epitaph() function too
    pass


def lambda_handler(event, context):
    """
    Nightly job to pre-generate epitaphs for graveyard items.
    Runs at 3 AM UTC (9 AM IST) daily.
    """
    print("Starting epitaph generation job")
    
    table = dynamodb.Table(TABLE_NAME)
    now = datetime.now(timezone.utc)
    
    # Scan all meetings (pagination handled)
    meetings = []
    scan_kwargs = {}
    
    while True:
        response = table.scan(**scan_kwargs)
        meetings.extend(response.get('Items', []))
        
        if 'LastEvaluatedKey' not in response:
            break
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
    
    print(f"Scanned {len(meetings)} meetings")
    
    # Find graveyard actions needing epitaphs
    actions_to_process = []
    
    for meeting in meetings:
        user_id = meeting.get('userId')
        meeting_id = meeting.get('meetingId')
        action_items = meeting.get('actionItems', [])
        
        for action in action_items:
            # Skip completed actions
            if action.get('completed'):
                continue
            
            # Calculate days old
            created_at = action.get('createdAt')
            if not created_at:
                continue
            
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (now - created_dt).days
                
                # Only process graveyard items (>30 days)
                if days_old <= GRAVEYARD_THRESHOLD_DAYS:
                    continue
                
                # Check if epitaph needs generation
                needs_epitaph = False
                
                if not action.get('epitaph'):
                    needs_epitaph = True
                    reason = "missing"
                elif action.get('epitaphGeneratedAt'):
                    try:
                        gen_dt = datetime.fromisoformat(action['epitaphGeneratedAt'].replace('Z', '+00:00'))
                        days_since_gen = (now - gen_dt).days
                        if days_since_gen > EPITAPH_TTL_DAYS:
                            needs_epitaph = True
                            reason = f"stale ({days_since_gen} days old)"
                    except:
                        needs_epitaph = True
                        reason = "invalid timestamp"
                
                if needs_epitaph:
                    actions_to_process.append({
                        'userId': user_id,
                        'meetingId': meeting_id,
                        'action': action,
                        'daysOld': days_old,
                        'reason': reason
                    })
            except Exception as e:
                print(f"Error processing action: {e}")
                continue
    
    print(f"Found {len(actions_to_process)} actions needing epitaphs")
    
    # Generate epitaphs with throttling protection
    success_count = 0
    failure_count = 0
    
    for idx, item in enumerate(actions_to_process):
        try:
            action = item['action']
            days_old = item['daysOld']
            
            print(f"[{idx+1}/{len(actions_to_process)}] Generating epitaph for action {action.get('id')} ({item['reason']})")
            
            # Generate epitaph
            epitaph = generate_epitaph(action, days_old)
            
            if epitaph:
                # Update DynamoDB
                meeting_response = table.get_item(
                    Key={'userId': item['userId'], 'meetingId': item['meetingId']}
                )
                
                if 'Item' in meeting_response:
                    meeting = meeting_response['Item']
                    action_items = meeting.get('actionItems', [])
                    
                    # Update the specific action item
                    for i, a in enumerate(action_items):
                        if a.get('id') == action.get('id'):
                            action_items[i]['epitaph'] = epitaph
                            action_items[i]['epitaphGeneratedAt'] = now.isoformat()
                            break
                    
                    # Save back to DynamoDB
                    table.update_item(
                        Key={'userId': item['userId'], 'meetingId': item['meetingId']},
                        UpdateExpression='SET actionItems = :items',
                        ExpressionAttributeValues={':items': action_items}
                    )
                    
                    success_count += 1
                    print(f"✓ Saved epitaph for action {action.get('id')}")
                else:
                    failure_count += 1
                    print(f"✗ Meeting not found: {item['meetingId']}")
            else:
                failure_count += 1
                print(f"✗ Failed to generate epitaph for action {action.get('id')}")
            
            # Throttling protection: sleep between requests
            if idx < len(actions_to_process) - 1:
                time.sleep(1)  # 1 second between epitaphs
                
        except Exception as e:
            failure_count += 1
            print(f"✗ Error processing action: {e}")
            continue
    
    result = {
        'totalMeetings': len(meetings),
        'actionsProcessed': len(actions_to_process),
        'successCount': success_count,
        'failureCount': failure_count,
        'timestamp': now.isoformat()
    }
    
    print(f"Job complete: {json.dumps(result)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**File:** `backend/functions/generate-epitaphs/requirements.txt`
```
boto3>=1.26.0
```

---

### Step 2: Update CloudFormation Template (30 minutes)

**File:** `backend/template.yaml`

Add new Lambda function:

```yaml
  # ── LAMBDA: GENERATE EPITAPHS (NIGHTLY) ───────────────────
  GenerateEpitaphsFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: meetingmind-generate-epitaphs
      CodeUri: functions/generate-epitaphs/
      Handler: app.lambda_handler
      Timeout: 900  # 15 minutes (may have many epitaphs to generate)
      MemorySize: 512
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref MeetingsTable
        - Statement:
            - Effect: Allow
              Action:
                - bedrock:InvokeModel
              Resource: "*"
      Events:
        NightlySchedule:
          Type: Schedule
          Properties:
            Schedule: cron(0 3 * * ? *)  # 3 AM UTC = 9 AM IST
            Description: Nightly epitaph generation for graveyard items
```

---

### Step 3: Modify get-all-actions Lambda (1 hour)

**File:** `backend/functions/get-all-actions/app.py`

**Changes:**
1. REMOVE real-time epitaph generation logic (lines 250-320)
2. ONLY return cached epitaphs from DynamoDB
3. Add fallback for missing epitaphs

```python
# BEFORE (lines 250-320):
for action in all_actions:
    if action['completed']:
        continue
    
    # ... calculate days_old ...
    
    if days_old > GRAVEYARD_THRESHOLD_DAYS:
        # Check if epitaph needs generation
        needs_epitaph = False
        
        if not action.get('epitaph'):
            needs_epitaph = True
        # ... more checks ...
        
        # Generate epitaph if needed
        if needs_epitaph:
            epitaph = generate_epitaph(action, days_old)  # REMOVE THIS!
            # ... update DynamoDB ...

# AFTER (simplified):
for action in all_actions:
    if action['completed']:
        continue
    
    # Calculate days old
    created_at = action.get('createdAt')
    if not created_at:
        continue
    
    try:
        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        days_old = (now - created_dt).days
        
        # Only add fallback for graveyard items without epitaph
        if days_old > GRAVEYARD_THRESHOLD_DAYS and not action.get('epitaph'):
            # Fallback message (epitaph will be generated tonight)
            action['epitaph'] = "Awaiting final words... (epitaph generating nightly)"
    except Exception as e:
        print(f"Error processing action: {e}")
        continue
```

**Remove these functions entirely:**
- `generate_epitaph()` (moved to generate-epitaphs Lambda)
- `get_fallback_epitaph()` (moved to generate-epitaphs Lambda)

---

### Step 4: Testing Plan (30 minutes)

#### Test 1: Manual Invocation
```bash
# Invoke Lambda manually
aws lambda invoke \
  --function-name meetingmind-generate-epitaphs \
  --region ap-south-1 \
  --log-type Tail \
  response.json

# Check CloudWatch logs
aws logs tail /aws/lambda/meetingmind-generate-epitaphs --region ap-south-1 --follow
```

#### Test 2: Verify DynamoDB Updates
```python
# Check if epitaphs were saved
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get a meeting with graveyard items
response = table.get_item(Key={'userId': 'USER_ID', 'meetingId': 'MEETING_ID'})
meeting = response['Item']

for action in meeting['actionItems']:
    if action.get('epitaph'):
        print(f"✓ Action {action['id']}: {action['epitaph']}")
        print(f"  Generated: {action.get('epitaphGeneratedAt')}")
```

#### Test 3: Frontend Load Time
```javascript
// In browser console
console.time('graveyard-load')
// Navigate to /graveyard
console.timeEnd('graveyard-load')
// Should be <500ms
```

#### Test 4: EventBridge Schedule
```bash
# Check EventBridge rule
aws events describe-rule \
  --name meetingmind-stack-GenerateEpitaphsFunctionNightlySchedule-XXXXX \
  --region ap-south-1

# Wait 24 hours, check CloudWatch logs
aws logs tail /aws/lambda/meetingmind-generate-epitaphs --region ap-south-1 --since 1h
```

---

## Deployment Steps

### 1. Deploy Backend
```powershell
cd backend
sam build
sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset
cd ..
```

### 2. Manually Invoke Lambda (First Time)
```powershell
# Pre-populate epitaph cache
aws lambda invoke --function-name meetingmind-generate-epitaphs --region ap-south-1 response.json
cat response.json
```

### 3. Verify Graveyard
```
1. Open browser
2. Navigate to https://dcfx593ywvy92.cloudfront.net/graveyard
3. Check load time (should be <500ms)
4. Verify epitaphs display correctly
```

### 4. Commit Changes
```powershell
git add -A
git commit -m "Fix #2: Pre-generate epitaphs nightly - Graveyard now instant"
```

---

## What Users Will See

### Before Fix #2:
```
User clicks "Graveyard" button
    ↓
Loading spinner appears
    ↓
Wait 5-10 seconds (generating epitaphs)
    ↓
Graveyard loads with AI epitaphs
```

### After Fix #2:
```
User clicks "Graveyard" button
    ↓
Loading spinner appears (brief)
    ↓
Graveyard loads INSTANTLY (<500ms)
    ↓
All epitaphs already generated and cached
```

### User Experience:
- **Instant gratification** - No waiting for AI generation
- **Smooth experience** - Feels like a polished product
- **Reliable** - No throttling errors
- **Scalable** - Works with 100s of graveyard items

---

## Edge Cases & Fallbacks

### Case 1: New Graveyard Item (Just Turned 31 Days Old)
- **Problem:** Epitaph not generated yet (job runs nightly)
- **Solution:** Show fallback message: "Awaiting final words... (epitaph generating nightly)"
- **Impact:** Minimal - epitaph appears next day

### Case 2: Bedrock Throttling During Nightly Job
- **Problem:** Too many epitaphs to generate, Bedrock throttles
- **Solution:** Exponential backoff + retry logic (already in generate_epitaph)
- **Impact:** Some epitaphs may fail, will retry next night

### Case 3: Lambda Timeout (900s)
- **Problem:** Too many epitaphs to generate in 15 minutes
- **Solution:** Process in batches, resume next night
- **Impact:** Some epitaphs delayed by 1 day

### Case 4: EventBridge Rule Disabled
- **Problem:** Epitaphs never regenerate
- **Solution:** CloudWatch alarm if job hasn't run in 25 hours
- **Impact:** Stale epitaphs (>7 days old)

---

## Cost Analysis

### Current (Real-Time Generation):
- **Bedrock calls:** 10 epitaphs × 100 users/day = 1,000 calls/day
- **Cost:** $0.00025/call × 1,000 = $0.25/day = $7.50/month

### New (Nightly Pre-Generation):
- **Bedrock calls:** 10 epitaphs × 1 job/day = 10 calls/day
- **Cost:** $0.00025/call × 10 = $0.0025/day = $0.075/month
- **Lambda:** 1 invocation/day × 900s × $0.0000166667/GB-second = $0.015/day = $0.45/month

### Savings:
- **Before:** $7.50/month
- **After:** $0.525/month
- **Savings:** $6.98/month (93% reduction!)

---

## Risks & Mitigation

### Risk 1: DynamoDB Scan is Expensive
- **Mitigation:** Use GSI (status-createdAt-index) instead of scan
- **Alternative:** Maintain separate graveyard table

### Risk 2: Lambda Timeout with Large Dataset
- **Mitigation:** Process in batches, use Step Functions for orchestration
- **Alternative:** Increase timeout to 15 minutes (max)

### Risk 3: Stale Epitaphs if Job Fails
- **Mitigation:** CloudWatch alarm + SNS notification
- **Alternative:** Fallback to real-time generation if epitaph >14 days old

### Risk 4: Breaking Existing Functionality
- **Mitigation:** Thorough testing before deployment
- **Alternative:** Feature flag to toggle between real-time and cached

---

## Success Metrics

### Performance:
- ✅ Graveyard load time: <500ms (was 5-10 seconds)
- ✅ No Bedrock throttling errors
- ✅ 100% epitaph coverage (all graveyard items have epitaphs)

### Cost:
- ✅ 93% reduction in Bedrock costs
- ✅ Minimal Lambda cost increase

### User Experience:
- ✅ Instant loading (killer feature must be fast)
- ✅ No waiting for AI generation
- ✅ Smooth, polished experience

---

## Rollback Plan

If Fix #2 causes issues:

1. **Revert get-all-actions Lambda:**
   ```bash
   git revert HEAD
   cd backend
   sam deploy
   ```

2. **Disable EventBridge Rule:**
   ```bash
   aws events disable-rule --name meetingmind-stack-GenerateEpitaphsFunctionNightlySchedule-XXXXX --region ap-south-1
   ```

3. **Delete Lambda Function:**
   ```bash
   aws lambda delete-function --function-name meetingmind-generate-epitaphs --region ap-south-1
   ```

---

## Post-Deployment Checklist

- [ ] Deploy backend with new Lambda
- [ ] Manually invoke generate-epitaphs Lambda
- [ ] Check CloudWatch logs for success
- [ ] Verify DynamoDB has epitaphs
- [ ] Test Graveyard page load time (<500ms)
- [ ] Verify epitaphs display correctly
- [ ] Check EventBridge rule is enabled
- [ ] Set CloudWatch alarm for job failures
- [ ] Commit changes to git
- [ ] Update CHANGELOG.md

---

## Next Steps (After Fix #2)

1. **Fix #3:** Add frontend loading states (2 hours)
2. **Test in browser:** Upload meeting, check graveyard
3. **Commit all changes:** Final commit before demo
4. **Prepare demo:** Practice showing graveyard feature
