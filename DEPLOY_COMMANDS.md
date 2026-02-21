# MeetingMind Deployment Commands

Quick reference for deploying backend and frontend changes.

## Backend Deployment (Lambda Functions)

### Full Stack Deployment
```powershell
cd backend
sam build
sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset
cd ..
```

### One-Line Backend Deploy
```powershell
cd backend; sam build; sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset; cd ..
```

### Verify Deployment
```powershell
# Check stack status
aws cloudformation describe-stacks --stack-name meetingmind-stack --region ap-south-1 --query 'Stacks[0].StackStatus' --output text

# Check Lambda layer
aws lambda list-layers --region ap-south-1 --query "Layers[?LayerName=='meetingmind-shared-constants'].[LayerName,LatestMatchingVersion.Version]" --output table

# Check specific function
aws lambda get-function --function-name meetingmind-process-meeting --region ap-south-1 --query 'Configuration.[FunctionName,LastModified,Layers[0].Arn]' --output table
```

## Frontend Deployment (CloudFront/S3)

### Full Frontend Deploy
```powershell
.\scripts\deploy-frontend.ps1
```

### Manual Frontend Deploy
```powershell
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E1YJBE0IXHFWQO --paths "/*"
cd ..
```

## Common Workflows

### Deploy Backend Fix
```powershell
# 1. Make changes to backend/functions/*/app.py
# 2. Test locally (optional)
# 3. Deploy
cd backend
sam build
sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset
cd ..

# 4. Verify
aws lambda get-function --function-name meetingmind-FUNCTION-NAME --region ap-south-1 --query 'Configuration.LastModified'

# 5. Commit
git add -A
git commit -m "Fix: description"
```

### Deploy Frontend Fix
```powershell
# 1. Make changes to frontend/src/**
# 2. Test locally: npm run dev
# 3. Deploy
.\scripts\deploy-frontend.ps1

# 4. Wait 2-3 minutes for CloudFront invalidation
# 5. Test in browser (hard refresh: Ctrl+Shift+R)

# 6. Commit
git add -A
git commit -m "Fix: description"
```

### Deploy Full Stack Change
```powershell
# Backend first
cd backend
sam build
sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset
cd ..

# Then frontend
.\scripts\deploy-frontend.ps1

# Commit
git add -A
git commit -m "Feature: description"
```

## Troubleshooting

### Build Fails (File Lock)
```powershell
# Close all editors/terminals accessing backend files
# Delete build cache
Remove-Item -Recurse -Force backend/.aws-sam/build
cd backend
sam build
```

### Deployment Fails (Changeset Error)
```powershell
# Delete failed changeset
aws cloudformation list-change-sets --stack-name meetingmind-stack --region ap-south-1
aws cloudformation delete-change-set --stack-name meetingmind-stack --change-set-name CHANGESET_NAME --region ap-south-1

# Try again
sam deploy --no-confirm-changeset --stack-name meetingmind-stack --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3 --no-fail-on-empty-changeset
```

### Frontend Not Updating
```powershell
# Hard refresh browser: Ctrl+Shift+R
# Check CloudFront invalidation status
aws cloudfront get-invalidation --distribution-id E1YJBE0IXHFWQO --id INVALIDATION_ID

# Force new invalidation
aws cloudfront create-invalidation --distribution-id E1YJBE0IXHFWQO --paths "/*"
```

## Stack Information

- **Stack Name:** meetingmind-stack
- **Region:** ap-south-1
- **CloudFront Distribution:** E1YJBE0IXHFWQO
- **S3 Frontend Bucket:** meetingmind-frontend-707411439284
- **S3 Audio Bucket:** meetingmind-audio-707411439284

## Quick Checks

### Is Backend Live?
```powershell
curl https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod/
```

### Is Frontend Live?
```powershell
curl https://dcfx593ywvy92.cloudfront.net
```

### Check Recent Logs
```powershell
# Lambda logs
aws logs tail /aws/lambda/meetingmind-process-meeting --region ap-south-1 --follow

# CloudFormation events
aws cloudformation describe-stack-events --stack-name meetingmind-stack --region ap-south-1 --max-items 10 --query 'StackEvents[].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' --output table
```
