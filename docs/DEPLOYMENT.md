# Deployment Guide

**Last Updated:** February 20, 2026

Complete guide for deploying MeetingMind to AWS.

## Prerequisites

### Required Tools
- AWS CLI (configured with credentials)
- AWS SAM CLI
- Python 3.11+
- Node.js 18+
- Git

### AWS Account Requirements
- Bedrock access enabled (Claude, Nova, Titan models)
- SES verified email address
- Sufficient service quotas for Lambda, DynamoDB, S3

### Environment Setup
```bash
# Verify AWS CLI
aws --version
aws sts get-caller-identity

# Verify SAM CLI
sam --version

# Verify Python
python --version

# Verify Node.js
node --version
npm --version
```

## Backend Deployment

### 1. Configure Environment
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
```

### 2. Build Backend
```bash
sam build
```

### 3. Deploy Backend
```bash
# First time deployment (guided)
sam deploy --guided

# Subsequent deployments
sam deploy --stack-name meetingmind-backend \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1 \
  --resolve-s3
```

### 4. Note Outputs
After deployment, note these outputs:
- API Gateway URL
- Cognito User Pool ID
- Cognito Client ID
- S3 Audio Bucket Name
- CloudFront Distribution ID

## Frontend Deployment

### 1. Configure Environment
```bash
cd frontend
cp .env.example .env.production
```

Edit `.env.production`:
```env
VITE_API_URL=https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/Prod
VITE_COGNITO_USER_POOL_ID=ap-south-1_XXXXXXXXX
VITE_COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_COGNITO_REGION=ap-south-1
VITE_S3_AUDIO_BUCKET=meetingmind-audio-XXXXXXXXXXXX
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Build Frontend
```bash
npm run build
```

### 4. Deploy to S3
```bash
# Sync to S3 bucket
aws s3 sync dist/ s3://meetingmind-frontend-XXXXXXXXXXXX --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id EXXXXXXXXXXXXX \
  --paths "/*"
```

### 5. Verify Deployment
Open your CloudFront URL in a browser and verify:
- Login page loads
- Can create account
- Can upload audio
- Dashboard displays correctly

## Post-Deployment Configuration

### 1. Verify SES Email
```bash
aws ses verify-email-identity --email-address your-email@example.com --region ap-south-1
```

Check your email and click the verification link.

### 2. Create Test Team
```bash
python scripts/setup/create-test-team.py
```

### 3. Seed Test Data (Optional)
```bash
python scripts/data/seed-v1-historical.py
```

### 4. Run Verification Tests
```bash
python scripts/testing/core/comprehensive-test-suite.py
```

## Updating Existing Deployment

### Update Single Lambda Function
```bash
cd backend
sam build

# Update specific function
cd .aws-sam/build
Compress-Archive -Path FunctionName/* -DestinationPath ../../function.zip -Force
cd ../..
aws lambda update-function-code \
  --function-name meetingmind-FUNCTION_NAME \
  --zip-file fileb://function.zip \
  --region ap-south-1
```

### Update All Lambda Functions
```bash
cd backend
sam build
sam deploy
```

### Update Frontend Only
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-XXXXXXXXXXXX --delete
aws cloudfront create-invalidation --distribution-id EXXXXXXXXXXXXX --paths "/*"
```

## Rollback Procedures

### Rollback Lambda Function
```bash
# List previous versions
aws lambda list-versions-by-function \
  --function-name meetingmind-FUNCTION_NAME \
  --region ap-south-1

# Update alias to previous version
aws lambda update-alias \
  --function-name meetingmind-FUNCTION_NAME \
  --name PROD \
  --function-version PREVIOUS_VERSION \
  --region ap-south-1
```

### Rollback Frontend
```bash
# List previous S3 versions
aws s3api list-object-versions \
  --bucket meetingmind-frontend-XXXXXXXXXXXX \
  --prefix assets/index

# Copy previous version
aws s3 cp s3://meetingmind-frontend-XXXXXXXXXXXX/assets/index-PREVIOUS.js \
  s3://meetingmind-frontend-XXXXXXXXXXXX/assets/index.js

# Invalidate cache
aws cloudfront create-invalidation --distribution-id EXXXXXXXXXXXXX --paths "/*"
```

## Monitoring

### CloudWatch Logs
```bash
# Tail Lambda logs
aws logs tail /aws/lambda/meetingmind-FUNCTION_NAME \
  --follow \
  --region ap-south-1

# View recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/meetingmind-FUNCTION_NAME \
  --filter-pattern "ERROR" \
  --region ap-south-1
```

### CloudWatch Alarms
Monitor these alarms in CloudWatch console:
- Lambda errors
- API Gateway 5xx errors
- DynamoDB throttling
- SQS dead letter queue depth

### X-Ray Tracing
View traces in AWS X-Ray console to debug performance issues.

## Troubleshooting

### Common Issues

#### 502 Bad Gateway
- Check Lambda logs for errors
- Verify CORS headers in Lambda response
- Check API Gateway configuration

#### CORS Errors
- Verify CloudFront domain in CORS headers
- Check OPTIONS preflight handler
- Ensure CORS headers in all response paths

#### Bedrock Throttling
- Check CloudWatch metrics for throttling
- Verify exponential backoff in code
- Consider requesting quota increase

#### Frontend Not Loading
- Check CloudFront distribution status
- Verify S3 bucket policy
- Check browser console for errors
- Verify .env.production values

#### Email Not Sending
- Verify SES email address
- Check SES sending limits
- Review Lambda logs for SES errors

## Security Checklist

- [ ] Cognito user pool configured with MFA
- [ ] S3 buckets have encryption enabled
- [ ] Lambda functions use least-privilege IAM roles
- [ ] API Gateway has throttling enabled
- [ ] CloudFront uses HTTPS only
- [ ] Secrets stored in AWS Secrets Manager (not environment variables)
- [ ] CloudWatch alarms configured
- [ ] X-Ray tracing enabled

## Cost Optimization

### Estimated Monthly Costs
- Lambda: $5-10 (1M requests)
- DynamoDB: $2-5 (pay-per-request)
- S3: $1-2 (100GB storage)
- Transcribe: $10-20 (100 hours)
- Bedrock: $5-15 (varies by model)
- CloudFront: $1-3 (100GB transfer)
- **Total: $24-55/month**

### Cost Reduction Tips
- Use Nova models instead of Claude (10x cheaper)
- Enable S3 lifecycle policies for old audio files
- Use DynamoDB on-demand pricing
- Set CloudWatch log retention to 7 days
- Monitor Bedrock usage and optimize prompts

## Support

For issues or questions:
- **Developer:** Ashhar Ahmad Khan
- **Email:** thecyberprinciples@gmail.com
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [AI_AGENT_HANDBOOK.md](../AI_AGENT_HANDBOOK.md)

---

**Next Steps:**
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Check [TESTING.md](TESTING.md) for testing procedures
- See [FEATURES.md](FEATURES.md) for feature documentation
