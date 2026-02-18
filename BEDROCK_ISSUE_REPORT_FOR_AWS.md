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

### ✅ Bedrock Access - RESOLVED!

**Working:**
- ✅ Titan Embeddings v2 (amazon.titan-embed-text-v2:0)
  - Status: Accessible (rate limited but functional)
  - Use case: Semantic duplicate detection with 1536-dim embeddings
  - Test result: Successfully generates embeddings

- ✅ Nova Lite (apac.amazon.nova-lite-v1:0)
  - Status: Accessible (rate limited but functional)
  - Use case: Primary AI analysis fallback
  - Test result: Successfully generates meeting analysis
  - **FIX:** Required APAC inference profile instead of direct model ID

- ✅ Nova Micro (apac.amazon.nova-micro-v1:0)
  - Status: Accessible (rate limited but functional)
  - Use case: Secondary AI analysis fallback
  - Test result: Successfully generates meeting analysis
  - **FIX:** Required APAC inference profile instead of direct model ID

**Still Blocked:**
- ❌ Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)
  - Error: "INVALID_PAYMENT_INSTRUMENT"
  - Message: "Credit card validation pending"
  - Impact: Primary AI analysis path unavailable (but fallbacks working)

---

## Detailed Error Analysis

### ✅ RESOLVED: Nova Models - Inference Profile Required

**Previous Error Code:** ValidationException

**Previous Error Message:**
```
Invocation of model ID amazon.nova-lite-v1:0 with on-demand throughput isn't 
supported. Retry your request with the ID or ARN of an inference profile that 
contains this model.
```

**Solution Found:**
Nova models in ap-south-1 require APAC inference profiles:
- ❌ WRONG: `amazon.nova-lite-v1:0` (direct model ID)
- ✅ CORRECT: `apac.amazon.nova-lite-v1:0` (APAC inference profile)

**Available Inference Profiles:**
- `apac.amazon.nova-lite-v1:0` - APAC Nova Lite (ACTIVE)
- `apac.amazon.nova-micro-v1:0` - APAC Nova Micro (ACTIVE)
- `apac.amazon.nova-pro-v1:0` - APAC Nova Pro (ACTIVE)

**Current Status:** ✅ Both Nova Lite and Nova Micro are now fully operational!

### Issue 1: Claude 3 Haiku - Payment Validation (Still Pending)

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

### Current Status: READY FOR DEMO! 🎉

We successfully resolved the Nova model access issue by using APAC inference profiles. Our multi-tier fallback architecture is now operational:

1. **Tier 1:** Claude 3 Haiku (still blocked by payment validation)
2. **Tier 2:** Nova Lite ✅ (WORKING with apac.amazon.nova-lite-v1:0)
3. **Tier 3:** Nova Micro ✅ (WORKING with apac.amazon.nova-micro-v1:0)
4. **Tier 4:** Intelligent mock (rule-based fallback)

**Current Capability:**
- ✅ Real AI analysis using Nova Lite/Micro
- ✅ Semantic duplicate detection using Titan Embeddings v2
- ✅ Transcription using Amazon Transcribe
- ✅ All infrastructure services operational

**Demo Status:**
- Can now process real meetings with actual AI output
- Nova models generate genuine meeting analysis
- Ready to record demo video with real Bedrock functionality
- No longer relying on mock tier for primary processing

### What We Need

**Current Status:** Nova models are working! We have real AI functionality.

**Optional Enhancement:**
- Claude 3 Haiku access would provide better quality analysis
- But Nova Lite/Micro are sufficient for competition demo

**Competition Ready:** YES ✅

### Timeline

- **Now:** February 19, 2026
- **Nova Models:** ✅ WORKING (resolved with inference profiles)
- **Next Steps:** Process real meetings, record demo video
- **Article Submission Opens:** March 1, 2026
- **Recommended Publish Date:** March 5, 2026 (early for maximum exposure)
- **Article Submission Deadline:** March 13, 2026
- **Voting Period:** March 13-20, 2026

**Status:** Ready to proceed with demo recording using Nova Lite/Micro!

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

1. **Payment Validation (Claude Haiku):**
   - How long does payment instrument validation typically take?
   - Is there a way to verify payment instrument status?
   - Can this be expedited for competition deadlines?

2. **✅ RESOLVED - Nova Inference Profiles:**
   - Solution found: Use `apac.amazon.nova-lite-v1:0` instead of `amazon.nova-lite-v1:0`
   - Both Nova Lite and Nova Micro are now operational
   - Thank you for the inference profile documentation!

3. **Alternative Solutions:**
   - Nova models are now working, so we're competition-ready
   - Claude Haiku would be nice-to-have but not blocking

4. **Timeline:**
   - Nova resolution unblocked us for demo recording
   - Claude Haiku can be resolved at your convenience
   - No longer urgent for competition deadline

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
Date: 2026-02-19 (Updated after Nova fix)
Region: ap-south-1
Account: 707411439284

✅ STS (Credentials): ACCESSIBLE
✅ S3 (Storage): ACCESSIBLE (2 buckets, encrypted, versioned)
✅ DynamoDB (Database): ACCESSIBLE (2 tables, 4 items)
✅ Cognito (Auth): ACCESSIBLE (user pool + client)
✅ Lambda (Functions): ACCESSIBLE (18 functions)
✅ API Gateway: ACCESSIBLE (REST API, prod stage)
✅ Transcribe: ACCESSIBLE (4 jobs completed)
✅ Bedrock (AI): MOSTLY ACCESSIBLE (3/4 models working)
   ✅ Titan Embeddings v2: ACCESSIBLE
   ✅ Nova Lite: ACCESSIBLE (via apac.amazon.nova-lite-v1:0)
   ✅ Nova Micro: ACCESSIBLE (via apac.amazon.nova-micro-v1:0)
   ❌ Claude 3 Haiku: PAYMENT VALIDATION PENDING
✅ SES (Email): ACCESSIBLE (200/day quota)
✅ SNS (Notifications): ACCESSIBLE
✅ SQS (Queues): ACCESSIBLE (2 queues)
✅ CloudFront (CDN): ACCESSIBLE (deployed)
✅ EventBridge (Cron): ACCESSIBLE (2 rules)
✅ CloudWatch (Logs): ACCESSIBLE (5 log groups, 12 alarms)

Overall: 14/14 services accessible, 3/4 Bedrock models working
Status: COMPETITION READY ✅
```

---

**Request:** Nova models are now working! Claude Haiku payment validation can be resolved at your convenience - no longer urgent.

Thank you for your assistance.

**Team ThreadFall**  
AWS AIdeas Competition 2026

---

## UPDATE LOG

**February 19, 2026 - 11:00 PM IST:**
- ✅ RESOLVED: Nova Lite and Nova Micro access
- Solution: Use APAC inference profiles (`apac.amazon.nova-lite-v1:0`)
- Status: Competition ready with 3/4 Bedrock models operational
- Next: Process real meetings and record demo video
