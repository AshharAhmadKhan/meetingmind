# Quick Reference - MeetingMind Improvements

## What Was Changed

### 📊 CloudWatch Dashboard
- **Location**: AWS Console → CloudWatch → Dashboards → "MeetingMind-Production"
- **Widgets**: 6 monitoring widgets covering Lambda, API Gateway, DynamoDB
- **Cost**: $3/month

### 🔍 X-Ray Tracing
- **Enabled On**: All Lambda functions + API Gateway
- **View Traces**: AWS Console → X-Ray → Traces
- **Subsegments**: parse_s3_event, transcribe_audio, bedrock_analysis, send_email_notification

### 📧 Email Notifications
- **Sender**: thecyberprinciples@gmail.com
- **Recipient**: User's email from DynamoDB
- **Triggers**: Meeting DONE or FAILED status
- **Content**: HTML + Plain text with meeting summary and link

## Files Modified

```
backend/
├── template.yaml                              # Added X-Ray, Dashboard, SES permissions
└── functions/
    └── process-meeting/
        ├── app.py                             # Added email function, X-Ray subsegments
        └── requirements.txt                   # Added aws-xray-sdk
```

## Key Code Changes

### template.yaml
```yaml
Globals:
  Function:
    Tracing: Active  # ← NEW: X-Ray tracing

MeetingMindApi:
  Properties:
    TracingEnabled: true  # ← NEW: X-Ray for API Gateway

ProcessMeetingFunction:
  Policies:
    - Statement:
        - Effect: Allow
          Action:
            - ses:SendEmail  # ← NEW: SES permissions
            - ses:SendRawEmail

MeetingMindDashboard:  # ← NEW: CloudWatch Dashboard
  Type: AWS::CloudWatch::Dashboard
```

### app.py
```python
# NEW: X-Ray instrumentation
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

# NEW: SES client
ses = boto3.client('ses', region_name=REGION)

# NEW: Email notification function
def _send_email_notification(email, meeting_id, title, status, ...):
    # Sends HTML + text email via SES

# NEW: X-Ray subsegments
with xray_recorder.capture('transcribe_audio'):
    # ... transcription code

with xray_recorder.capture('send_email_notification'):
    _send_email_notification(...)
```

## Environment Variables

```bash
FRONTEND_URL=https://dcfx593ywvy92.cloudfront.net
SES_FROM_EMAIL=thecyberprinciples@gmail.com
```

## Deployment Commands

```bash
# 1. Verify SES email (REQUIRED FIRST TIME)
aws ses verify-email-identity \
  --email-address thecyberprinciples@gmail.com \
  --region ap-south-1

# 2. Build
cd backend
sam build

# 3. Deploy
sam deploy  # or sam deploy --guided for first time
```

## Testing Commands

```bash
# Check SES verification
aws ses get-identity-verification-attributes \
  --identities thecyberprinciples@gmail.com \
  --region ap-south-1

# View Lambda logs
aws logs tail /aws/lambda/meetingmind-process-meeting --follow

# Check X-Ray traces
aws xray get-service-graph \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --region ap-south-1

# View dashboard
aws cloudwatch get-dashboard \
  --dashboard-name MeetingMind-Production \
  --region ap-south-1
```

## Verification Checklist

After deployment, verify:

- [ ] SES email verified (check email for verification link)
- [ ] Stack deployed successfully (`sam deploy` completed)
- [ ] CloudWatch Dashboard visible in console
- [ ] X-Ray tracing enabled on Lambda functions
- [ ] Upload test audio file
- [ ] Email notification received
- [ ] Dashboard shows metrics
- [ ] X-Ray traces visible

## Email Templates

### Success Email
```
Subject: ✅ Meeting Analysis Complete: [Title]

Your meeting "[Title]" has been processed!

View your analysis: https://dcfx593ywvy92.cloudfront.net/meeting/{meetingId}

Summary: [AI-generated summary]
Action Items: [count]
```

### Failure Email
```
Subject: ❌ Meeting Processing Failed: [Title]

Unfortunately, we couldn't process your meeting "[Title]".

Error: [error message]

Please try uploading again.
```

## Dashboard Widgets

1. **Lambda Performance** - Invocations, Errors, Duration, Throttles
2. **Lambda Duration by Function** - Per-function performance
3. **API Gateway Metrics** - Requests, 4xx/5xx errors, latency
4. **DynamoDB Metrics** - Read/Write capacity, errors
5. **Recent Errors** - Last 20 errors from process-meeting
6. **Lambda Concurrency** - Concurrent executions

## X-Ray Subsegments

1. **parse_s3_event** - S3 event parsing and DynamoDB lookup
2. **transcribe_audio** - AWS Transcribe job execution (longest)
3. **bedrock_analysis** - Bedrock AI analysis
4. **send_email_notification** - SES email sending

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Email not received | Check SES verification status |
| X-Ray traces missing | Verify `Tracing: Active` in template |
| Dashboard empty | Wait 5-15 minutes for metrics |
| Deployment failed | Check CloudFormation events |
| SES sandbox limit | Request production access |

## Important Notes

⚠️ **SES Sandbox Mode**: By default, SES is in sandbox mode and can only send to verified addresses. Request production access to send to any email.

⚠️ **X-Ray Sampling**: X-Ray samples 1 req/sec + 5% of additional requests by default. Adjust sampling rules if needed.

⚠️ **Email Failures**: Email failures don't break the pipeline - they're logged but processing continues.

## Cost Impact

| Service | Cost |
|---------|------|
| CloudWatch Dashboard | $3/month |
| X-Ray Traces | Free (first 100k/month) |
| SES Emails | Free (first 62k/month) |
| CloudWatch Logs | Free (first 5GB/month) |
| **Total** | **~$3-5/month** |

## Links

- **CloudWatch Dashboard**: AWS Console → CloudWatch → Dashboards → MeetingMind-Production
- **X-Ray Traces**: AWS Console → X-Ray → Traces
- **SES Console**: AWS Console → Simple Email Service
- **Lambda Logs**: AWS Console → CloudWatch → Log groups → /aws/lambda/meetingmind-process-meeting
