# Day 2: SQS Pipeline Implementation

**Date:** February 18, 2026  
**Status:** ⚠️ BLOCKED - IAM Permissions Required  
**Deployment:** Not deployed (permission error)

---

## Problem
Current architecture: S3 → Lambda (direct invocation)
- If Lambda fails → audio file lost forever
- No retry mechanism
- No visibility into failures

## Proposed Solution
New architecture: S3 → SQS → Lambda
- S3 sends message to SQS queue
- Lambda polls from SQS
- Failed messages retry 3 times
- After 3 failures → Dead Letter Queue
- DLQ triggers notification Lambda → email user

---

## Implementation Complete

### 1. SQS Queues Added ✅
**File:** `backend/template.yaml`

```yaml
ProcessingDeadLetterQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: meetingmind-processing-dlq
    MessageRetentionPeriod: 1209600  # 14 days

ProcessingQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: meetingmind-processing-queue
    VisibilityTimeout: 960  # 16 minutes
    MessageRetentionPeriod: 345600  # 4 days
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt ProcessingDeadLetterQueue.Arn
      maxReceiveCount: 3  # Retry 3 times
```

### 2. ProcessMeetingFunction Updated ✅
**File:** `backend/template.yaml`

- Added SQS event source mapping
- Added SQSPollerPolicy
- Removed direct S3 invocation permission
- BatchSize: 1 (process one meeting at a time)

### 3. Lambda Handler Updated ✅
**File:** `backend/functions/process-meeting/app.py`

- Handles both SQS events (new) and direct S3 events (legacy)
- Backward compatible with existing flow
- Extracts S3 event from SQS message body

```python
# Check if event is from SQS
if 'Records' in event and event['Records'][0].get('eventSource') == 'aws:sqs':
    # SQS event - extract S3 event from message body
    sqs_record = event['Records'][0]
    s3_event = json.loads(sqs_record['body'])
    record = s3_event['Records'][0]['s3']
else:
    # Direct S3 event (legacy path)
    record = event['Records'][0]['s3']
```

### 4. S3 Notification Updated ✅
**File:** `backend/template.yaml`

- Changed from Lambda invocation to SQS message
- Added SQSQueuePolicy for S3 → SQS permissions
- Updated custom resource to configure S3 → SQS

### 5. DLQ Handler Created ✅
**Files:** 
- `backend/functions/dlq-handler/app.py`
- `backend/functions/dlq-handler/requirements.txt`

**Features:**
- Processes failed messages from DLQ
- Updates meeting status to 'FAILED' in DynamoDB
- Sends failure notification email to user
- Provides troubleshooting guidance

---

## Deployment Blocker

### Error
```
User: arn:aws:iam::707411439284:user/meetingmind-dev 
is not authorized to perform: sqs:createqueue
```

### Root Cause
IAM user `meetingmind-dev` lacks SQS permissions

### Required Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:CreateQueue",
        "sqs:DeleteQueue",
        "sqs:GetQueueAttributes",
        "sqs:SetQueueAttributes",
        "sqs:TagQueue"
      ],
      "Resource": "arn:aws:sqs:ap-south-1:707411439284:meetingmind-*"
    }
  ]
}
```

---

## Workaround Options

### Option 1: Add IAM Permissions (Recommended)
1. Go to AWS Console → IAM → Users → meetingmind-dev
2. Add inline policy with SQS permissions above
3. Redeploy stack

### Option 2: Use Root/Admin Account
1. Deploy using AWS account with admin permissions
2. Switch back to meetingmind-dev for regular operations

### Option 3: Manual SQS Creation
1. Create queues manually in AWS Console
2. Remove queue resources from template.yaml
3. Reference existing queues by ARN

### Option 4: Skip SQS for Now
- Current system works with direct S3 → Lambda
- Add SQS later when permissions available
- Focus on other Day 2-7 tasks first

---

## Testing Plan (When Deployed)

### Test 1: Normal Flow
1. Upload meeting audio
2. Verify message appears in SQS queue
3. Verify Lambda processes from queue
4. Verify meeting status updates correctly

### Test 2: Retry Logic
1. Temporarily break Lambda (invalid Bedrock model)
2. Upload meeting
3. Verify message retries 3 times
4. Verify message moves to DLQ after 3 failures

### Test 3: DLQ Handler
1. Trigger DLQ with failed message
2. Verify meeting status set to 'FAILED'
3. Verify failure email sent to user
4. Verify email contains correct details

### Test 4: Backward Compatibility
1. Manually invoke Lambda with S3 event (not SQS)
2. Verify processing still works
3. Ensures no breaking changes

---

## Architecture Diagram

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│   S3    │────▶│   SQS   │────▶│  Lambda  │────▶│ DynamoDB │
│ Bucket  │     │  Queue  │     │ Process  │     │  Table   │
└─────────┘     └─────────┘     └──────────┘     └──────────┘
                     │
                     │ (after 3 retries)
                     ▼
                ┌─────────┐     ┌──────────┐
                │   DLQ   │────▶│  Lambda  │
                │  Queue  │     │ DLQ Hdlr │
                └─────────┘     └──────────┘
                                     │
                                     ▼
                                ┌─────────┐
                                │   SES   │
                                │  Email  │
                                └─────────┘
```

---

## Benefits When Deployed

1. **Resilience**: Automatic retry on failure
2. **Visibility**: CloudWatch metrics for queue depth
3. **No Data Loss**: Messages persist in queue
4. **User Notification**: Email on permanent failure
5. **Debugging**: DLQ messages available for inspection
6. **Scalability**: Queue buffers load spikes

---

## Files Modified

| File | Status | Purpose |
|------|--------|---------|
| `backend/template.yaml` | ✅ Ready | SQS queues, event mappings, policies |
| `backend/functions/process-meeting/app.py` | ✅ Ready | SQS event handling |
| `backend/functions/dlq-handler/app.py` | ✅ Created | DLQ processing |
| `backend/functions/dlq-handler/requirements.txt` | ✅ Created | Dependencies |

---

## Next Steps

1. **Immediate:** Add SQS permissions to IAM user
2. **Deploy:** Run `sam deploy` again
3. **Test:** Upload meeting and verify SQS flow
4. **Move On:** If blocked, proceed to Day 3 (Step Functions)

---

**Day 2 Status:** Implementation complete, deployment blocked by IAM permissions  
**Recommendation:** Add permissions OR skip to Day 3 and return later
