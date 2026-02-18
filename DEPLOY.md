# Deployment Guide - MeetingMind

**Date:** February 19, 2026  
**Status:** Ready for deployment after fixes applied

---

## Pre-Deployment Checklist

Run these commands to verify everything is ready:

### 1. Backend Pre-Deployment Checks

```bash
# Navigate to backend directory
cd backend

# Check Python syntax for all Lambda functions
python -m py_compile functions/process-meeting/app.py
python -m py_compile functions/check-duplicate/app.py
python -m py_compile functions/get-meeting/app.py
python -m py_compile functions/get-all-actions/app.py
python -m py_compile functions/update-action/app.py
python -m py_compile functions/list-meetings/app.py
python -m py_compile functions/get-upload-url/app.py
python -m py_compile functions/get-debt-analytics/app.py
python -m py_compile functions/daily-digest/app.py
python -m py_compile functions/send-reminders/app.py
python -m py_compile functions/dlq-handler/app.py
python -m py_compile functions/create-team/app.py
python -m py_compile functions/join-team/app.py
python -m py_compile functions/get-team/app.py
python -m py_compile functions/list-user-teams/app.py

# Verify SAM template is valid
sam validate

# Check AWS credentials
aws sts get-caller-identity
```

**Expected Output:**
- All Python files compile without errors
- SAM template is valid
- AWS credentials show correct account (707411439284)

---

### 2. Frontend Pre-Deployment Checks

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if needed)
npm install

# Run build test
npm run build

# Check build output
dir dist
```

**Expected Output:**
- Build completes successfully
- `dist/` folder contains:
  - `index.html`
  - `assets/` folder with JS and CSS files
- No errors or warnings (chunk size warning is OK)

---

## Backend Deployment

### Step 1: Build Lambda Functions

```bash
cd backend

# Build all Lambda functions
sam build
```

**Expected Output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

---

### Step 2: Deploy to AWS

```bash
# Deploy with confirmation prompts
sam deploy --guided

# OR deploy with existing config
sam deploy
```

**Deployment Parameters:**
- Stack Name: `meetingmind-backend`
- AWS Region: `ap-south-1`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N`
- Save arguments to config: `Y`

**Expected Output:**
```
Successfully created/updated stack - meetingmind-backend in ap-south-1
```

---

### Step 3: Verify Backend Deployment

```bash
# Get API Gateway URL
aws cloudformation describe-stacks \
  --stack-name meetingmind-backend \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text

# Test API health (replace with your API URL)
curl https://YOUR_API_URL/meetings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Output:**
- API URL is returned
- API responds with 200 or 401 (auth required)

---

## Frontend Deployment

### Step 1: Update API URL

```bash
cd frontend

# Check current API URL in .env.production
type .env.production
```

**Verify:**
- `VITE_API_URL` matches your deployed API Gateway URL

---

### Step 2: Build Frontend

```bash
# Build for production
npm run build
```

**Expected Output:**
```
✓ built in 10-15s
dist/index.html
dist/assets/index-*.css
dist/assets/index-*.js
```

---

### Step 3: Deploy to S3

```bash
# Get S3 bucket name
aws cloudformation describe-stacks \
  --stack-name meetingmind-backend \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" \
  --output text

# Sync build to S3 (replace YOUR_BUCKET_NAME)
aws s3 sync dist/ s3://YOUR_BUCKET_NAME --delete

# OR use the deploy script
bash ../deploy-frontend.sh
```

**Expected Output:**
```
upload: dist/index.html to s3://...
upload: dist/assets/index-*.css to s3://...
upload: dist/assets/index-*.js to s3://...
```

---

### Step 4: Invalidate CloudFront Cache

```bash
# Get CloudFront distribution ID
aws cloudformation describe-stacks \
  --stack-name meetingmind-backend \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
  --output text

# Create invalidation (replace YOUR_DIST_ID)
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

**Expected Output:**
```
{
    "Invalidation": {
        "Id": "...",
        "Status": "InProgress",
        "CreateTime": "..."
    }
}
```

---

## Post-Deployment Verification

### 1. Backend Health Checks

```bash
# Check Lambda function status
aws lambda list-functions \
  --query "Functions[?starts_with(FunctionName, 'meetingmind')].FunctionName" \
  --output table

# Check recent Lambda errors
aws logs tail /aws/lambda/meetingmind-ProcessMeetingFunction --since 5m

# Verify DynamoDB table
aws dynamodb describe-table \
  --table-name meetingmind-meetings \
  --query "Table.TableStatus"
```

**Expected Output:**
- All Lambda functions listed
- No recent errors in logs
- DynamoDB table status: `ACTIVE`

---

### 2. Frontend Health Checks

```bash
# Get CloudFront URL
aws cloudformation describe-stacks \
  --stack-name meetingmind-backend \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" \
  --output text

# Test frontend (replace YOUR_CLOUDFRONT_URL)
curl -I https://YOUR_CLOUDFRONT_URL
```

**Expected Output:**
```
HTTP/2 200
content-type: text/html
```

---

### 3. End-to-End Testing

**Manual Tests:**

1. **Login Test**
   - Navigate to CloudFront URL
   - Login with test credentials
   - Verify redirect to dashboard

2. **Meeting Upload Test**
   - Upload a small audio file
   - Verify status changes: UPLOADING → TRANSCRIBING → ANALYZING → DONE
   - Check for any errors

3. **Action Items Test** ✅ CRITICAL
   - Navigate to Actions Overview page
   - Click checkbox on an action item
   - Verify:
     - Checkbox toggles immediately
     - Status persists after page refresh
     - No redirect to old screen
     - No console errors

4. **Duplicate Detection Test**
   - Click "Check Duplicates" button
   - Verify scan completes without errors
   - Check results display correctly

5. **Team Features Test**
   - Create a new team
   - Join team with invite code
   - Switch between teams
   - Verify data isolation

---

## Rollback Procedure

If deployment fails or issues are detected:

### Backend Rollback

```bash
# List previous stack versions
aws cloudformation list-stack-resources \
  --stack-name meetingmind-backend

# Rollback to previous version
aws cloudformation rollback-stack \
  --stack-name meetingmind-backend
```

---

### Frontend Rollback

```bash
# List S3 object versions
aws s3api list-object-versions \
  --bucket YOUR_BUCKET_NAME \
  --prefix index.html

# Restore previous version (replace VERSION_ID)
aws s3api copy-object \
  --bucket YOUR_BUCKET_NAME \
  --copy-source YOUR_BUCKET_NAME/index.html?versionId=VERSION_ID \
  --key index.html

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

---

## Monitoring Commands

### Check Lambda Logs

```bash
# Process Meeting function
aws logs tail /aws/lambda/meetingmind-ProcessMeetingFunction --follow

# Check Duplicate function
aws logs tail /aws/lambda/meetingmind-CheckDuplicateFunction --follow

# Update Action function
aws logs tail /aws/lambda/meetingmind-UpdateActionFunction --follow
```

---

### Check CloudWatch Metrics

```bash
# Lambda invocations (last hour)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=meetingmind-ProcessMeetingFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum

# Lambda errors (last hour)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=meetingmind-ProcessMeetingFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

---

### Check DynamoDB Metrics

```bash
# Table item count
aws dynamodb describe-table \
  --table-name meetingmind-meetings \
  --query "Table.ItemCount"

# Recent read/write capacity
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=meetingmind-meetings \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

---

## Critical Warnings

### ⚠️ Bedrock Testing

**DO NOT RUN** any Bedrock test scripts until payment issue is resolved:

```bash
# DISABLED - DO NOT RUN:
# python scripts/test-aws-services.py
# python scripts/detailed-bedrock-test.py
# python scripts/monitor-bedrock-access.py
# python scripts/resolve-bedrock-payment.py
# python scripts/check-bedrock-model-access.py
```

**Reason:** Each invocation triggers AWS Marketplace subscription validation.

**Safe to run:**
```bash
# These are safe:
python scripts/comprehensive-test-suite.py
python scripts/test-api-endpoint.py
python scripts/test-duplicate-detection.py
```

---

### ⚠️ Post-Deployment Monitoring

After deployment, monitor for:

1. **No new Marketplace agreement emails** ✅
   - Check email for AWS Marketplace notifications
   - Should see ZERO new agreements after deployment

2. **Lambda execution success rate** ✅
   - Monitor CloudWatch for errors
   - Check logs for any Bedrock payment errors

3. **Frontend functionality** ✅
   - Test checkbox functionality immediately
   - Verify no redirects occur
   - Check browser console for errors

---

## Quick Deployment Script

Save this as `deploy-all.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting MeetingMind Deployment..."

# Backend
echo "📦 Building backend..."
cd backend
sam build
echo "☁️  Deploying backend..."
sam deploy
cd ..

# Frontend
echo "🎨 Building frontend..."
cd frontend
npm run build
echo "☁️  Deploying frontend..."
bash ../deploy-frontend.sh
cd ..

echo "✅ Deployment complete!"
echo "🔍 Run post-deployment checks..."
```

Make executable:
```bash
chmod +x deploy-all.sh
```

Run:
```bash
./deploy-all.sh
```

---

## Troubleshooting

### Issue: SAM build fails

```bash
# Clean build artifacts
rm -rf backend/.aws-sam

# Rebuild
cd backend
sam build --use-container
```

---

### Issue: Frontend build fails

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

### Issue: CloudFront not updating

```bash
# Force invalidation of all paths
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"

# Wait for invalidation to complete (5-10 minutes)
aws cloudfront get-invalidation \
  --distribution-id YOUR_DIST_ID \
  --id INVALIDATION_ID
```

---

### Issue: Lambda function errors

```bash
# Check function configuration
aws lambda get-function-configuration \
  --function-name meetingmind-ProcessMeetingFunction

# Check environment variables
aws lambda get-function-configuration \
  --function-name meetingmind-ProcessMeetingFunction \
  --query "Environment.Variables"

# Test function directly
aws lambda invoke \
  --function-name meetingmind-ProcessMeetingFunction \
  --payload '{"test": true}' \
  response.json
```

---

## Success Criteria

Deployment is successful when:

- ✅ All Lambda functions deploy without errors
- ✅ Frontend builds and deploys to S3
- ✅ CloudFront invalidation completes
- ✅ Login works
- ✅ Meeting upload works
- ✅ **Action item checkboxes work (no redirect)** ← CRITICAL
- ✅ No new Marketplace agreement emails
- ✅ No errors in CloudWatch logs
- ✅ All API endpoints respond correctly

---

## Support

If issues persist:

1. Check `TEST_REPORT.md` for test results
2. Check `BEDROCK_ISSUE_ANALYSIS.md` for Bedrock status
3. Review CloudWatch logs for errors
4. Contact AWS Support if needed (Account: 707411439284)

---

**Last Updated:** February 19, 2026  
**Deployment Status:** Ready ✅
