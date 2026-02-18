# Deployment & Testing Commands

Quick reference for all deployment, testing, and maintenance commands.

## AWS Configuration

```bash
# Configure AWS CLI (first time only)
aws configure
# Region: ap-south-1
# Output: json

# Verify AWS account
aws sts get-caller-identity

# Check credits
aws ce get-cost-and-usage --time-period Start=2026-02-01,End=2026-02-28 --granularity MONTHLY --metrics BlendedCost
```

## Backend Deployment

### Full Deployment

```bash
cd backend
sam build
sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --resolve-s3
```

### Update Single Lambda

```bash
# Example: Update get-all-actions function
cd backend/functions/get-all-actions
Compress-Archive -Path * -DestinationPath function.zip -Force
aws lambda update-function-code --function-name meetingmind-get-all-actions --zip-file fileb://function.zip
```

### Validate Template

```bash
cd backend
sam validate
sam validate --lint  # Additional validation
```

## Frontend Deployment

### Full Deployment

```bash
cd frontend
npm install
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### Quick Deploy (after build)

```bash
cd frontend
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### Development Server

```bash
cd frontend
npm run dev
# Opens on http://localhost:5173
```

## Testing

### Comprehensive Test Suite

```bash
python scripts/comprehensive-test-suite.py
```

### Individual Tests

```bash
# Test AWS services
python scripts/test-aws-services.py

# Test duplicate detection
python scripts/test-duplicate-detection.py

# Test Lambda directly
python scripts/test-lambda-direct.py

# Test API endpoint
python scripts/test-api-endpoint.py
```

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

## AWS Service Management

### Lambda Functions

```bash
# List all functions
aws lambda list-functions --query "Functions[].FunctionName"

# Get function details
aws lambda get-function --function-name meetingmind-get-all-actions

# View logs
aws logs tail /aws/lambda/meetingmind-process-meeting --follow

# Check function status
aws lambda get-function --function-name meetingmind-get-all-actions --query "Configuration.LastUpdateStatus" --output text
```

### DynamoDB

```bash
# List tables
aws dynamodb list-tables

# Scan meetings table
aws dynamodb scan --table-name meetingmind-meetings --max-items 10

# Get item
aws dynamodb get-item --table-name meetingmind-meetings --key '{"userId":{"S":"user@email.com"},"meetingId":{"S":"meeting-id"}}'
```

### S3

```bash
# List buckets
aws s3 ls

# List files in audio bucket
aws s3 ls s3://meetingmind-audio-707411439284/

# List files in frontend bucket
aws s3 ls s3://meetingmind-frontend-707411439284/
```

### CloudFront

```bash
# Get distribution details
aws cloudfront get-distribution --id E3CAAI97MXY83V

# List invalidations
aws cloudfront list-invalidations --distribution-id E3CAAI97MXY83V

# Check invalidation status
aws cloudfront get-invalidation --distribution-id E3CAAI97MXY83V --id <invalidation-id>
```

### Cognito

```bash
# List user pools
aws cognito-idp list-user-pools --max-results 10

# List users
aws cognito-idp list-users --user-pool-id ap-south-1_mkFJawjMp

# Approve user (admin)
python scripts/approve-user.py <email>
```

### SES

```bash
# Verify email
aws ses verify-email-identity --email-address thecyberprinciples@gmail.com --region ap-south-1

# Check verification status
aws ses get-identity-verification-attributes --identities thecyberprinciples@gmail.com --region ap-south-1

# List verified emails
aws ses list-identities --region ap-south-1
```

## Monitoring

### CloudWatch Logs

```bash
# Tail Lambda logs
aws logs tail /aws/lambda/meetingmind-process-meeting --follow

# Get recent errors
aws logs filter-log-events --log-group-name /aws/lambda/meetingmind-process-meeting --filter-pattern "ERROR" --max-items 20
```

### X-Ray Traces

```bash
# Get service graph
aws xray get-service-graph --start-time $(date -u -d '1 hour ago' +%s) --end-time $(date -u +%s) --region ap-south-1

# Get trace summaries
aws xray get-trace-summaries --start-time $(date -u -d '1 hour ago' +%s) --end-time $(date -u +%s) --region ap-south-1
```

### CloudWatch Dashboard

```bash
# View dashboard
aws cloudwatch get-dashboard --dashboard-name MeetingMind-Production --region ap-south-1
```

## Utility Scripts

### User Management

```bash
# Approve user
python scripts/approve-user.py user@email.com

# Update user email
python scripts/update-email.py old@email.com new@email.com
```

### Data Management

```bash
# Clear test data
python scripts/clear-test-data.py

# Generate embeddings for existing actions
python scripts/generate-embeddings.py
```

### AWS Service Checks

```bash
# Check AWS account
python scripts/check-aws-account.py

# Check Bedrock model access
python scripts/check-bedrock-model-access.py

# Add Transcribe permissions
python scripts/add-transcribe-permissions.py
```

## Troubleshooting

### Backend Issues

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name meetingmind-backend --query "Stacks[0].StackStatus"

# Get stack events (for deployment failures)
aws cloudformation describe-stack-events --stack-name meetingmind-backend --max-items 20

# Check Lambda function errors
aws lambda get-function --function-name meetingmind-process-meeting --query "Configuration.LastUpdateStatus"
```

### Frontend Issues

```bash
# Check S3 bucket
aws s3 ls s3://meetingmind-frontend-707411439284/

# Check CloudFront distribution
aws cloudfront get-distribution --id E3CAAI97MXY83V --query "Distribution.Status"

# Force cache clear
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### API Issues

```bash
# Test API Gateway
curl https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod/meetings

# Check API Gateway logs
aws logs tail /aws/apigateway/meetingmind-api --follow
```

## Git Commands

```bash
# Commit changes
git add -A
git commit -m "Description of changes"

# Push to remote
git push origin master

# View commit history
git log --oneline -10

# Check status
git status
```

## Common Workflows

### Deploy Full Stack

```bash
# 1. Deploy backend
cd backend
sam build && sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --resolve-s3

# 2. Deploy frontend
cd ../frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"

# 3. Test
python scripts/comprehensive-test-suite.py
```

### Quick Frontend Update

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### Quick Backend Lambda Update

```bash
cd backend/functions/<function-name>
Compress-Archive -Path * -DestinationPath function.zip -Force
aws lambda update-function-code --function-name meetingmind-<function-name> --zip-file fileb://function.zip
```

## Important Notes

- Always run `sam build` before `sam deploy`
- CloudFront invalidation takes 1-2 minutes to propagate
- Lambda updates take 10-15 seconds to become active
- Use `--no-fail-on-empty-changeset` flag if no changes detected
- Region is always `ap-south-1` (Mumbai)
- Stack name is always `meetingmind-backend`
- S3 bucket is always `meetingmind-frontend-707411439284`
- CloudFront distribution is always `E3CAAI97MXY83V`
