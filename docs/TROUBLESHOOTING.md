# Troubleshooting Guide

**Last Updated:** February 20, 2026

Common issues and solutions for MeetingMind.

## Table of Contents
- [Deployment Issues](#deployment-issues)
- [Backend Issues](#backend-issues)
- [Frontend Issues](#frontend-issues)
- [AWS Service Issues](#aws-service-issues)
- [Testing Issues](#testing-issues)

---

## Deployment Issues

### SAM Deploy Fails with "Stack already exists"

**Problem:** `sam deploy` fails because stack exists but has no changes.

**Solution:** Update Lambda directly instead:
```bash
cd backend
sam build
cd .aws-sam/build
Compress-Archive -Path FunctionName/* -DestinationPath ../../function.zip -Force
cd ../..
aws lambda update-function-code \
  --function-name meetingmind-FUNCTION_NAME \
  --zip-file fileb://function.zip \
  --region ap-south-1
```

### Frontend Build Fails

**Problem:** `npm run build` fails with errors.

**Solution:**
1. Check Node.js version (requires 18+)
2. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
3. Check for syntax errors with diagnostics
4. Verify all imports are correct

### CloudFront Not Updating

**Problem:** Changes deployed but not visible in browser.

**Solution:**
1. Create cache invalidation:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id EXXXXXXXXXXXXX \
     --paths "/*"
   ```
2. Wait 2-3 minutes for invalidation to complete
3. Hard refresh browser (Ctrl+Shift+R)
4. Try incognito mode to bypass local cache

---

## Backend Issues

### 502 Bad Gateway Errors

**Problem:** API requests return 502 errors.

**Causes & Solutions:**

1. **Lambda Timeout**
   - Check CloudWatch logs for timeout errors
   - Increase Lambda timeout in template.yaml
   - Optimize code to reduce execution time

2. **Missing CORS Headers**
   - Verify CORS headers in Lambda response
   - Check OPTIONS preflight handler exists
   - Ensure headers in all response paths (success and error)

3. **Lambda Crash**
   - Check CloudWatch logs for exceptions
   - Verify all imports are correct
   - Check for syntax errors

### Float/Decimal Type Errors

**Problem:** "Float types are not supported" error in DynamoDB operations.

**Solution:** Always use Decimal for DynamoDB numbers:
```python
from decimal import Decimal

# Convert float to Decimal
value = Decimal(str(float_value))

# Convert Decimal to float for JSON
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Use in json.dumps
json.dumps(data, default=decimal_to_float)
```

### CORS Errors

**Problem:** Browser shows CORS errors in console.

**Solution:**
1. Verify CORS headers match CloudFront domain:
   ```python
   CORS_HEADERS = {
       'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
       'Access-Control-Allow-Headers': 'Content-Type,Authorization',
       'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
       'Content-Type': 'application/json'
   }
   ```
2. Add OPTIONS handler:
   ```python
   if event.get('httpMethod') == 'OPTIONS':
       return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
   ```
3. Include headers in all responses (success and error)

### Bedrock Throttling

**Problem:** "ThrottlingException" errors from Bedrock.

**Solution:**
1. Implement exponential backoff:
   ```python
   import time
   
   max_retries = 3
   for attempt in range(max_retries):
       try:
           response = bedrock.invoke_model(...)
           break
       except ClientError as e:
           if e.response['Error']['Code'] == 'ThrottlingException':
               if attempt < max_retries - 1:
                   time.sleep(2 ** attempt)  # 1s, 2s, 4s
               else:
                   raise
   ```
2. Use multi-model fallback (Claude → Nova Lite → Nova Micro)
3. Request quota increase from AWS Support

### SES Email Not Sending

**Problem:** Emails not being sent or received.

**Solution:**
1. Verify email address in SES:
   ```bash
   aws ses verify-email-identity \
     --email-address your-email@example.com \
     --region ap-south-1
   ```
2. Check SES sending limits (sandbox vs production)
3. Review Lambda logs for SES errors
4. Verify IAM permissions for SES

---

## Frontend Issues

### Login Not Working

**Problem:** Cannot log in or create account.

**Causes & Solutions:**

1. **Wrong Cognito Configuration**
   - Verify User Pool ID in .env.production
   - Verify Client ID in .env.production
   - Check region matches (ap-south-1)

2. **CORS Issues**
   - Check browser console for CORS errors
   - Verify API Gateway CORS configuration
   - Ensure Lambda returns correct CORS headers

3. **Network Errors**
   - Check API Gateway URL in .env.production
   - Verify API Gateway is deployed
   - Test API endpoint directly with curl

### Dashboard Shows "Pending"

**Problem:** Meetings show as "pending" instead of "done".

**Solution:**
1. Check meeting has `status: 'DONE'` field in DynamoDB
2. Verify API response includes status field
3. Check browser console for errors
4. Hard refresh browser (Ctrl+Shift+R)

### Meeting Not Clickable

**Problem:** Cannot click on meeting card to view details.

**Solution:**
1. Verify meeting has `status: 'DONE'` in database
2. Check Dashboard.jsx logic: `done && navigate(...)`
3. Verify meeting route exists in App.jsx
4. Check browser console for navigation errors

### Kanban Drag Not Working

**Problem:** Cannot drag cards between columns.

**Solution:**
1. Check browser console for errors
2. Verify react-dnd is installed
3. Check DndProvider wraps KanbanBoard
4. Verify update-action API is working

---

## AWS Service Issues

### Transcribe Fails

**Problem:** Audio transcription fails or times out.

**Solution:**
1. Check audio file format (MP3, MP4, WAV, M4A supported)
2. Verify file size < 500MB
3. Check S3 bucket permissions
4. Review Transcribe job logs in CloudWatch
5. Verify IAM permissions for Transcribe

### Bedrock Access Denied

**Problem:** "AccessDeniedException" from Bedrock.

**Solution:**
1. Verify Bedrock access enabled in AWS account
2. Check model IDs are correct:
   - Claude: `anthropic.claude-3-haiku-20240307-v1:0`
   - Nova Lite: `us.amazon.nova-lite-v1:0`
   - Nova Micro: `us.amazon.nova-micro-v1:0`
3. Verify IAM permissions for Bedrock
4. Check region supports Bedrock (ap-south-1)

### DynamoDB Throttling

**Problem:** "ProvisionedThroughputExceededException" errors.

**Solution:**
1. Switch to on-demand billing mode
2. Increase provisioned capacity
3. Implement exponential backoff
4. Review access patterns and optimize queries

### S3 Upload Fails

**Problem:** Audio upload fails or times out.

**Solution:**
1. Check presigned URL expiry (5 minutes)
2. Verify S3 bucket CORS configuration
3. Check file size < 500MB
4. Review browser console for errors
5. Verify IAM permissions for S3

---

## Testing Issues

### Tests Fail with Import Errors

**Problem:** Python tests fail with "ModuleNotFoundError".

**Solution:**
1. Install required packages:
   ```bash
   pip install boto3 requests python-dotenv
   ```
2. Verify Python path includes project root
3. Check imports use correct paths

### API Tests Fail with 403

**Problem:** API tests return 403 Forbidden.

**Solution:**
1. Verify AWS credentials are configured
2. Check Cognito user exists and is confirmed
3. Verify JWT token is valid
4. Check IAM permissions for API Gateway

### Test Meeting Not Visible

**Problem:** Created test meeting doesn't appear in UI.

**Solution:**
1. Verify meeting has `status: 'DONE'` field
2. Check meeting has correct `teamId`
3. Verify user is member of team
4. Clear CloudFront cache
5. Hard refresh browser

---

## Debug Checklist

When troubleshooting any issue:

1. **Check CloudWatch Logs**
   ```bash
   aws logs tail /aws/lambda/meetingmind-FUNCTION_NAME --follow
   ```

2. **Check Browser Console**
   - Open DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

3. **Verify Environment Variables**
   - Backend: Check Lambda environment variables
   - Frontend: Check .env.production values

4. **Test API Directly**
   ```bash
   curl -X GET https://API_URL/meetings \
     -H "Authorization: Bearer JWT_TOKEN"
   ```

5. **Check AWS Service Status**
   - Visit AWS Service Health Dashboard
   - Check for regional outages

6. **Review Recent Changes**
   - Check git log for recent commits
   - Review CHANGELOG.md for breaking changes

---

## Getting Help

If you're still stuck:

1. Check [AI_AGENT_HANDBOOK.md](../AI_AGENT_HANDBOOK.md) for AI-specific guidance
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment steps
4. **Contact:** Ashhar Ahmad Khan - thecyberprinciples@gmail.com

---

**Last Updated:** February 20, 2026 - 7:10 PM IST
