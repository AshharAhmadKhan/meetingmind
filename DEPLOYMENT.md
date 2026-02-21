# MeetingMind Deployment Guide

**Last Updated:** February 22, 2026

## 🚀 Quick Deployment (Recommended)

### Deploy Everything
```bash
# Windows PowerShell
.\scripts\deploy-all.ps1

# Linux/Mac
bash scripts/deploy-all.sh
```

### Deploy Backend Only
```bash
# Windows PowerShell
.\scripts\deploy-backend.ps1

# Linux/Mac
bash scripts/deploy-backend.sh
```

### Deploy Frontend Only
```bash
# Windows PowerShell
.\scripts\deploy-frontend.ps1

# Linux/Mac
bash scripts/deploy-frontend.sh
```

## 📋 Deployment Configuration

### AWS Resources
- **Stack Name:** meetingmind-stack
- **Region:** ap-south-1 (Mumbai)
- **Account:** 707411439284
- **S3 Deployment Bucket:** aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2

### Frontend
- **S3 Bucket:** meetingmind-frontend-707411439284
- **CloudFront ID:** E3CAAI97MXY83V
- **URL:** https://dcfx593ywvy92.cloudfront.net

### Backend
- **API Gateway:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod
- **DynamoDB Tables:** meetingmind-meetings, meetingmind-teams
- **S3 Audio Bucket:** meetingmind-audio-707411439284

## 🔧 Manual Deployment Commands

### Frontend (Manual)
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --region ap-south-1 --delete --cache-control "public, max-age=31536000, immutable" --exclude "index.html"
aws s3 cp dist/index.html s3://meetingmind-frontend-707411439284/index.html --region ap-south-1 --cache-control "no-cache, no-store, must-revalidate"
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### Backend (Manual)
```bash
cd backend
sam build
sam deploy --stack-name meetingmind-stack --region ap-south-1 --capabilities CAPABILITY_IAM --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2 --no-confirm-changeset --no-fail-on-empty-changeset
```

### Single Lambda Update (Code Only - Fast)
```bash
cd backend/functions/FUNCTION_NAME
Compress-Archive -Path * -DestinationPath ../../function.zip -Force
cd ../..
aws lambda update-function-code --function-name meetingmind-FUNCTION_NAME --zip-file fileb://function.zip --region ap-south-1
```

## 📊 When to Use Each Method

### Use Automated Scripts When:
- ✅ Regular deployments
- ✅ Want consistent, error-free deploys
- ✅ Don't want to remember all the parameters

### Use Full SAM Deploy When:
- Template.yaml changed (IAM, env vars, new resources)
- First-time deployment
- Lambda configuration changed (timeout, memory)
- New API Gateway endpoints

### Use Lambda Update When:
- Only function code changed
- Need faster deployment (30 seconds vs 3 minutes)
- No template changes
- Testing quick fixes

## 🐛 Common Issues & Solutions

### CloudFront Cache Not Updating
**Problem:** Changes not visible after deployment  
**Solution:** Wait 1-2 minutes for invalidation, or check status:
```bash
aws cloudfront get-invalidation --distribution-id E3CAAI97MXY83V --id <ID>
```

### Email Not Sending
**Problem:** Welcome emails or notifications not arriving  
**Solutions:**
- Verify SES email: `aws ses verify-email-identity --email-address EMAIL --region ap-south-1`
- Check Lambda logs: `aws logs tail /aws/lambda/meetingmind-send-welcome-email --since 5m --region ap-south-1`
- Check SES sending limits: `aws ses get-send-quota --region ap-south-1`

### SAM Build Fails (File Lock Error)
**Problem:** `[WinError 32] The process cannot access the file`  
**Solution:**
```powershell
# Close any open terminals/editors in backend folder
Remove-Item -Recurse -Force backend/.aws-sam/build -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
sam build
```

### SAM Deploy Fails
**Problem:** Deployment errors  
**Solutions:**
- Add `--capabilities CAPABILITY_IAM` for IAM changes
- Verify stack name: `aws cloudformation list-stacks --region ap-south-1 --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE`
- Run `sam validate` first
- Check CloudFormation events: `aws cloudformation describe-stack-events --stack-name meetingmind-stack --region ap-south-1 --max-items 10`

### Rate Limiting Errors (429)
**Problem:** Too many requests  
**Current Limits:**
- Burst: 100 requests
- Rate: 50 requests/second
- Quota: 10,000 requests/day

**Solution:** If legitimate traffic, increase limits in `backend/template.yaml` under `MeetingMindUsagePlan`

## 🛠️ Useful Scripts

### Deployment
- `scripts/deploy-all.{sh|ps1}` - Deploy everything
- `scripts/deploy-backend.{sh|ps1}` - Deploy backend only
- `scripts/deploy-frontend.{sh|ps1}` - Deploy frontend only

### Testing & Debugging
- `scripts/trigger-processing.py` - Manually trigger meeting processing
- `scripts/check-meeting-status.py` - Check meeting processing status
- `scripts/check-aws-credits.py` - Check AWS credit balance
- `scripts/testing/test-rate-limiting.py` - Test API rate limits

### Data Management
- `scripts/fix-duplicate-action-ids.py` - Fix duplicate action IDs (one-time)
- `scripts/regenerate-autopsies-rulebased.py` - Regenerate meeting autopsies
- `scripts/data/seed-v1-historical.py` - Seed historical data

### User Management
- `scripts/setup/approve-user.py` - Approve pending user accounts
- `scripts/setup/update-email.py` - Update user email addresses

## ✅ Post-Deployment Verification

Run through this checklist after each deployment:

1. **Authentication**
   - [ ] Login works
   - [ ] Signup works
   - [ ] Token refresh works

2. **Core Features**
   - [ ] Upload meeting audio
   - [ ] Dashboard loads correctly
   - [ ] Meeting details page works
   - [ ] Kanban drag-and-drop works

3. **Team Features**
   - [ ] Create team works
   - [ ] Join team works
   - [ ] Team meetings visible

4. **Notifications**
   - [ ] Welcome email sent
   - [ ] Daily digest sent (check next morning)
   - [ ] Meeting completion email sent

5. **Performance**
   - [ ] API response < 1 second
   - [ ] Frontend loads < 2 seconds
   - [ ] No console errors

## 📈 Monitoring

### CloudWatch Dashboards
- **Production Dashboard:** https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#dashboards:name=MeetingMind-Production

### Key Metrics to Watch
- API Gateway 4XX/5XX errors
- Lambda invocation errors
- DynamoDB throttling
- S3 bucket size
- Bedrock API costs

### Logs
```bash
# API Gateway logs
aws logs tail /aws/apigateway/meetingmind --since 5m --region ap-south-1

# Lambda logs (replace FUNCTION_NAME)
aws logs tail /aws/lambda/meetingmind-FUNCTION_NAME --since 5m --region ap-south-1

# All Lambda errors
aws logs filter-pattern "ERROR" --log-group-name-prefix /aws/lambda/meetingmind --since 1h --region ap-south-1
```

## 🔐 Security Notes

- All API endpoints require Cognito authentication
- Rate limiting active (100 burst, 50/sec, 10k/day)
- CORS restricted to CloudFront domain only
- S3 buckets not publicly accessible
- Secrets stored in environment variables (not in code)

## 💰 Cost Optimization

Current optimizations in place:
- S3 Lifecycle: Archive to Glacier after 7 days (68% savings)
- DynamoDB: Pay-per-request (no idle costs)
- Lambda: Right-sized memory allocations
- CloudFront: Caching enabled
- Rate limiting: Prevents cost spikes

## 📞 Support

If deployment issues persist:
1. Check CloudFormation events for detailed errors
2. Review CloudWatch logs
3. Verify AWS credentials and permissions
4. Check AWS service health dashboard
