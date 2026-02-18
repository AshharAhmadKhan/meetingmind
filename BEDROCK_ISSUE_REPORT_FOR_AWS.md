# Bedrock Access Issue Report for AWS Support

**Date:** February 19, 2026  
**AWS Account:** 707411439284  
**Region:** ap-south-1 (Mumbai)  
**IAM User:** meetingmind-dev  
**Project:** MeetingMind (AWS AIdeas Competition 2026)

---

## Executive Summary

We are experiencing partial Bedrock access in our AWS account. Titan Embeddings v2 is fully operational, but Claude 3 Haiku and Nova models are blocked. This is preventing us from completing our competition submission for AWS AIdeas 2026.

**Timeline Critical:** Competition article submission deadline is March 13, 2026. We need Bedrock text models operational to demonstrate real AI output in our demo.

---

## Current Service Status

### ✅ Working Services (14/14 AWS Services Accessible)

All infrastructure services are operational:
- S3 (storage, encrypted, versioned)
- DynamoDB (2 tables, 4 meetings stored)
- Lambda (18 functions deployed)
- API Gateway (REST API with Cognito auth)
- Cognito (user authentication)
- Transcribe (4 jobs completed successfully)
- SES (email notifications working)
- SNS (topic configured)
- SQS (processing queue + DLQ)
- CloudFront (CDN deployed)
- EventBridge (2 cron jobs)
- CloudWatch (5 log groups, 12 alarms)
- X-Ray (tracing enabled)

### ⚠️ Partial Bedrock Access

**Working:**
- ✅ Titan Embeddings v2 (amazon.titan-embed-text-v2:0)
  - Status: Accessible (rate limited but functional)
  - Use case: Semantic duplicate detection with 1536-dim embeddings
  - Test result: Successfully generates embeddings

**Blocked:**
- ❌ Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)
  - Error: "INVALID_PAYMENT_INSTRUMENT"
  - Message: "Credit card validation pending"
  - Impact: Primary AI analysis path unavailable

- ❌ Nova Lite (amazon.nova-lite-v1:0)
  - Error: "ValidationException"
  - Message: "Invocation of model ID amazon.nova-lite-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model."
  - Impact: Fallback tier 1 unavailable

- ❌ Nova Micro (amazon.nova-micro-v1:0)
  - Error: "ValidationException"
  - Message: "Invocation of model ID amazon.nova-micro-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model."
  - Impact: Fallback tier 2 unavailable

---

## Detailed Error Analysis

### Issue 1: Claude 3 Haiku - Payment Validation

**Error Code:** INVALID_PAYMENT_INSTRUMENT

**Full Error Message:**
```
An error occurred (AccessDeniedException) when calling the InvokeModel operation: 
Your account is not authorized to invoke this model. If you are trying to access 
this model for the first time, you need to accept the EULA for this model in the 
Amazon Bedrock console. Additionally, your account must have a valid payment 
instrument on file. Please add a valid payment instrument and try again.
```

**What We've Done:**
1. Added valid credit card to AWS account
2. Accepted EULA for Claude 3 Haiku in Bedrock console (ap-south-1)
3. Enabled model access in Bedrock console
4. Waited 24+ hours for payment validation to propagate

**Current Status:** Still blocked after 24 hours

**Question for AWS Support:**
- Is there a way to expedite payment instrument validation?
- Is there a specific timeline for when this will be resolved?
- Can we verify that our payment instrument is correctly configured?

### Issue 2: Nova Models - Inference Profile Required

**Error Code:** ValidationException

**Full Error Message:**
```
Invocation of model ID amazon.nova-lite-v1:0 with on-demand throughput isn't 
supported. Retry your request with the ID or ARN of an inference profile that 
contains this model.
```

**What We've Tried:**
1. Direct model invocation: `amazon.nova-lite-v1:0` (failed)
2. Direct model invocation: `amazon.nova-micro-v1:0` (failed)
3. Checked Bedrock console for inference profiles (none found)

**Questions for AWS Support:**
- How do we create or access inference profiles for Nova models?
- Are inference profiles required for all Nova model invocations?
- Is there documentation on inference profile setup for ap-south-1?
- Can Nova models be invoked without inference profiles in any region?

---

## Test Code Used

### Bedrock Status Check Script

```python
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

bedrock_config = Config(retries={'max_attempts': 0, 'mode': 'standard'})
bedrock = boto3.client('bedrock-runtime', region_name=REGION, config=bedrock_config)

# Test Claude 3 Haiku
try:
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 10,
        'messages': [{'role': 'user', 'content': 'Hi'}]
    })
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=body
    )
    result = json.loads(response['body'].read())
    print("✅ Claude 3 Haiku: ACCESSIBLE")
except ClientError as e:
    print(f"❌ Claude 3 Haiku: {e.response['Error']['Code']}")
    print(f"   Message: {e.response['Error']['Message']}")

# Test Nova Lite
try:
    body = json.dumps({
        'messages': [{'role': 'user', 'content': [{'text': 'Hi'}]}],
        'inferenceConfig': {'maxTokens': 10, 'temperature': 0.1}
    })
    response = bedrock.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=body
    )
    result = json.loads(response['body'].read())
    print("✅ Nova Lite: ACCESSIBLE")
except ClientError as e:
    print(f"❌ Nova Lite: {e.response['Error']['Code']}")
    print(f"   Message: {e.response['Error']['Message']}")

# Test Titan Embeddings v2
try:
    body = json.dumps({"inputText": "test"})
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        body=body
    )
    result = json.loads(response['body'].read())
    if 'embedding' in result:
        print(f"✅ Titan Embeddings v2: ACCESSIBLE (dimension: {len(result['embedding'])})")
except ClientError as e:
    print(f"❌ Titan Embeddings v2: {e.response['Error']['Code']}")
```

---

## Impact on Competition Submission

### Current Workaround

We implemented a multi-tier fallback architecture:
1. **Tier 1:** Claude 3 Haiku (blocked)
2. **Tier 2:** Nova Lite (blocked)
3. **Tier 3:** Nova Micro (blocked)
4. **Tier 4:** Intelligent mock (rule-based, currently active)

**Problem:** Our demo is running on the mock tier, which means:
- AI analysis is deterministic, not generative
- Judges will see structured output but not real AI reasoning
- We cannot demonstrate the actual AI capabilities we built

### What We Need

**Minimum Requirement:**
- Claude 3 Haiku access (primary model)
- OR Nova Lite/Micro access (fallback models)

**Ideal Solution:**
- All three text models operational
- Demonstrates robust multi-model fallback architecture

### Timeline

- **Now:** February 19, 2026
- **Article Submission Opens:** March 1, 2026
- **Recommended Publish Date:** March 5, 2026 (early for maximum exposure)
- **Article Submission Deadline:** March 13, 2026
- **Voting Period:** March 13-20, 2026

**Critical Path:** We need Bedrock text models working by March 1 to:
1. Process 10+ real meetings with actual AI output
2. Record demo video showing real Bedrock analysis
3. Publish article with credible proof of AI functionality

---

## Account Information

**AWS Account ID:** 707411439284  
**Region:** ap-south-1 (Mumbai)  
**IAM User:** meetingmind-dev  
**User ARN:** arn:aws:iam::707411439284:user/meetingmind-dev

**Bedrock Console Access:**
- Logged in as root user
- Accepted EULAs for all models
- Enabled model access in console
- Payment instrument added and verified

**Billing Status:**
- Valid credit card on file
- No outstanding charges
- Free tier eligible
- $340 in AWS credits available (AWS AIdeas Competition)

---

## Questions for AWS Support

1. **Payment Validation:**
   - How long does payment instrument validation typically take?
   - Is there a way to verify payment instrument status?
   - Can this be expedited for competition deadlines?

2. **Nova Inference Profiles:**
   - How do we create inference profiles for Nova models?
   - Are they required for all Nova invocations?
   - Is there region-specific documentation for ap-south-1?

3. **Alternative Solutions:**
   - Can we use Bedrock in us-east-1 instead of ap-south-1?
   - Would cross-region inference work for our use case?
   - Are there any temporary access grants for competition participants?

4. **Timeline:**
   - What is the realistic timeline for resolution?
   - Should we plan for alternative approaches?
   - Is there a support escalation path for competition deadlines?

---

## Supporting Documentation

**Test Results:** See `scripts/comprehensive-access-check.py` output above

**Architecture:** Multi-tier AI fallback with Transcribe + Bedrock

**Use Case:** 
- Transcribe meeting audio (working)
- Extract decisions, action items, follow-ups (needs Bedrock text models)
- Generate embeddings for duplicate detection (working with Titan)
- Calculate risk scores (working)

**Competition Context:** AWS AIdeas 2026, Team ThreadFall, MeetingMind project

---

## Contact Information

**Email:** thecyberprinciples@gmail.com  
**Project:** MeetingMind  
**Live Demo:** https://dcfx593ywvy92.cloudfront.net  
**GitHub:** (available upon request)

**Availability:** Available for immediate follow-up, screen sharing, or additional testing as needed.

---

## Appendix: Full Service Test Results

```
MEETINGMIND - COMPREHENSIVE AWS ACCESS CHECK
Date: 2026-02-19 04:16:54
Region: ap-south-1
Account: 707411439284

✅ STS (Credentials): ACCESSIBLE
✅ S3 (Storage): ACCESSIBLE (2 buckets, encrypted, versioned)
✅ DynamoDB (Database): ACCESSIBLE (2 tables, 4 items)
✅ Cognito (Auth): ACCESSIBLE (user pool + client)
✅ Lambda (Functions): ACCESSIBLE (18 functions)
✅ API Gateway: ACCESSIBLE (REST API, prod stage)
✅ Transcribe: ACCESSIBLE (4 jobs completed)
⚠️  Bedrock (AI): PARTIAL (1/4 models accessible)
   ✅ Titan Embeddings v2: ACCESSIBLE
   ❌ Claude 3 Haiku: PAYMENT VALIDATION PENDING
   ❌ Nova Lite: NEEDS INFERENCE PROFILE
   ❌ Nova Micro: NEEDS INFERENCE PROFILE
✅ SES (Email): ACCESSIBLE (200/day quota)
✅ SNS (Notifications): ACCESSIBLE
✅ SQS (Queues): ACCESSIBLE (2 queues)
✅ CloudFront (CDN): ACCESSIBLE (deployed)
✅ EventBridge (Cron): ACCESSIBLE (2 rules)
✅ CloudWatch (Logs): ACCESSIBLE (5 log groups, 12 alarms)

Overall: 14/14 services accessible, Bedrock text models blocked
```

---

**Request:** Please advise on next steps to resolve Bedrock text model access before March 1, 2026.

Thank you for your assistance.

**Team ThreadFall**  
AWS AIdeas Competition 2026
