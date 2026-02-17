# MeetingMind Deployment Guide

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. AWS SAM CLI installed
3. Python 3.11 installed
4. Access to AWS account with permissions for:
   - Lambda
   - API Gateway
   - DynamoDB
   - S3
   - SES
   - CloudWatch
   - X-Ray
   - IAM

## Step 1: Verify SES Email Address

**IMPORTANT**: Before deploying, you must verify the sender email address in Amazon SES.

```bash
# Verify the sender email address
aws ses verify-email-identity \
  --email-address thecyberprinciples@gmail.com \
  --region ap-south-1

# Check verification status (wait for verification email and click the link)
aws ses get-identity-verification-attributes \
  --identities thecyberprinciples@gmail.com \
  --region ap-south-1
```

**Expected Output** (after clicking verification link):
```json
{
    "VerificationAttributes": {
        "thecyberprinciples@gmail.com": {
            "VerificationStatus": "Success"
        }
    }
}
```

## Step 2: Build the SAM Application

```bash
cd backend
sam build
```

**Expected Output**:
```
Building codeuri: functions/process-meeting/ runtime: python3.11 ...
Running PythonPipBuilder:ResolveDependencies
Running PythonPipBuilder:CopySource
...
Build Succeeded
```

## Step 3: Deploy the Stack

### First-Time Deployment (Guided)

```bash
sam deploy --guided
```

**Answer the prompts**:
- Stack Name: `meetingmind-stack` (or your preferred name)
- AWS Region: `ap-south-1` (or your preferred region)
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N`
- Save arguments to configuration file: `Y`
- SAM configuration file: `samconfig.toml`
- SAM configuration environment: `default`

### Subsequent Deployments

```bash
sam deploy
```

## Step 4: Verify Deployment

### Check CloudFormation Stack

```bash
aws cloudformation describe-stacks \
  --stack-name meetingmind-stack \
  --region ap-south-1 \
  --query 'Stacks[0].StackStatus'
```

**Expected Output**: `"CREATE_COMPLETE"` or `"UPDATE_COMPLETE"`

### Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name meetingmind-stack \
  --region ap-south-1 \
  --query 'Stacks[0].Outputs'
```

**Expected Outputs**:
- ApiUrl
- AudioBucketName
- UserPoolId
- UserPoolClientId
- MeetingsTableName

### Verify CloudWatch Dashboard

```bash
# List dashboards
aws cloudwatch list-dashboards --region ap-south-1

# Get dashboard details
aws cloudwatch get-dashboard \
  --dashboard-name MeetingMind-Production \
  --region ap-south-1
```

### Verify X-Ray Tracing

```bash
# Check if X-Ray is enabled for Lambda functions
aws lambda get-function-configuration \
  --function-name meetingmind-process-meeting \
  --region ap-south-1 \
  --query 'TracingConfig'
```

**Expected Output**:
```json
{
    "Mode": "Active"
}
```

## Step 5: Test the Implementation

### Test 1: Upload Audio File

1. Go to your MeetingMind frontend: `https://dcfx593ywvy92.cloudfront.net`
2. Log in with your credentials
3. Upload a test audio file (MP3, WAV, M4A, MP4, or WEBM)
4. Wait for processing to complete

### Test 2: Verify Email Notification

1. Check the inbox for `thecyberprinciples@gmail.com`
2. You should receive an email with subject: "✅ Meeting Analysis Complete: [Meeting Title]"
3. Email should include:
   - Meeting summary
   - Number of action items
   - Link to meeting detail page

### Test 3: View CloudWatch Dashboard

1. Go to AWS Console → CloudWatch → Dashboards
2. Open "MeetingMind-Production"
3. Verify all widgets are showing data:
   - Lambda Performance
   - Lambda Duration by Function
   - API Gateway Metrics
   - DynamoDB Metrics
   - Recent Errors
   - Lambda Concurrency

### Test 4: View X-Ray Traces

1. Go to AWS Console → X-Ray → Traces
2. Filter by service: `meetingmind-process-meeting`
3. Click on a trace to see:
   - Service map showing all AWS services called
   - Subsegments: parse_s3_event, transcribe_audio, bedrock_analysis, send_email_notification
   - Timing information for each subsegment

## Step 6: Monitor Logs

### View Lambda Logs

```bash
# Process Meeting Lambda logs
aws logs tail /aws/lambda/meetingmind-process-meeting \
  --follow \
  --region ap-south-1

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/meetingmind-process-meeting \
  --filter-pattern "ERROR" \
  --region ap-south-1
```

### View X-Ray Service Map

```bash
# Get service graph
aws xray get-service-graph \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --region ap-south-1
```

## Troubleshooting

### Issue: Email Not Received

**Check 1: Verify SES Email**
```bash
aws ses get-identity-verification-attributes \
  --identities thecyberprinciples@gmail.com \
  --region ap-south-1
```

**Check 2: Check Lambda Logs**
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/meetingmind-process-meeting \
  --filter-pattern "Email sent successfully" \
  --region ap-south-1
```

**Check 3: Check SES Sending Statistics**
```bash
aws ses get-send-statistics --region ap-south-1
```

### Issue: X-Ray Traces Not Appearing

**Check 1: Verify X-Ray is Enabled**
```bash
aws lambda get-function-configuration \
  --function-name meetingmind-process-meeting \
  --region ap-south-1 \
  --query 'TracingConfig'
```

**Check 2: Check IAM Permissions**
Ensure Lambda execution role has `xray:PutTraceSegments` and `xray:PutTelemetryRecords` permissions.

### Issue: CloudWatch Dashboard Not Showing Data

**Check 1: Verify Dashboard Exists**
```bash
aws cloudwatch list-dashboards --region ap-south-1
```

**Check 2: Wait for Metrics**
CloudWatch metrics can take 5-15 minutes to appear after first deployment.

### Issue: Lambda Deployment Failed

**Check 1: Review CloudFormation Events**
```bash
aws cloudformation describe-stack-events \
  --stack-name meetingmind-stack \
  --region ap-south-1 \
  --max-items 20
```

**Check 2: Validate Template**
```bash
sam validate --region ap-south-1
```

## Rollback

If you need to rollback the changes:

```bash
# Option 1: Rollback via CloudFormation
aws cloudformation cancel-update-stack \
  --stack-name meetingmind-stack \
  --region ap-south-1

# Option 2: Delete and recreate stack
aws cloudformation delete-stack \
  --stack-name meetingmind-stack \
  --region ap-south-1

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name meetingmind-stack \
  --region ap-south-1

# Then redeploy with previous version
```

## Cost Estimation

### New Costs from These Improvements

1. **CloudWatch Dashboard**: $3/month per dashboard
2. **X-Ray Traces**: 
   - First 100,000 traces/month: Free
   - Additional traces: $5 per 1 million traces
3. **SES Emails**:
   - First 62,000 emails/month: Free (if sent from EC2)
   - Additional emails: $0.10 per 1,000 emails
4. **CloudWatch Logs**: 
   - First 5GB/month: Free
   - Additional: $0.50/GB ingested

**Estimated Monthly Cost**: ~$3-5 for typical usage (100 meetings/month)

## Next Steps

1. ✅ Deploy the stack
2. ✅ Verify email notifications work
3. ✅ Check CloudWatch Dashboard
4. ✅ View X-Ray traces
5. 📧 Request SES production access (if needed for unrestricted sending)
6. 🔔 Set up CloudWatch Alarms for critical metrics
7. 📊 Create custom metrics for business KPIs

## Support

For issues or questions:
1. Check CloudWatch Logs for error messages
2. Review X-Ray traces for performance bottlenecks
3. Check AWS Service Health Dashboard
4. Review SAM deployment logs
