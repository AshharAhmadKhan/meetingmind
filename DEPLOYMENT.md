# MeetingMind Deployment Guide

**Last Updated:** February 21, 2026

## Quick Commands

### Frontend Deployment
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

### Backend Deployment (Full Stack)
```bash
cd backend
sam build
sam deploy --stack-name meetingmind-stack --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
```

### Single Lambda Update (Code Only)
```bash
cd backend/functions/FUNCTION_NAME
Compress-Archive -Path * -DestinationPath ../../function.zip -Force
cd ../..
aws lambda update-function-code --function-name meetingmind-FUNCTION_NAME --zip-file fileb://function.zip --region ap-south-1
```

## Deployment URLs

- **Frontend:** https://dcfx593ywvy92.cloudfront.net
- **API Gateway:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod
- **Region:** ap-south-1 (Mumbai)
- **Account:** 707411439284

## When to Use Each Method

### Use Full SAM Deploy When:
- Template.yaml changed (IAM, env vars, new resources)
- First-time deployment
- Lambda configuration changed (timeout, memory)

### Use Lambda Update When:
- Only function code changed
- Need faster deployment
- No template changes

## Common Issues

### CloudFront Cache Not Updating
Wait 1-2 minutes for invalidation, or check status:
```bash
aws cloudfront get-invalidation --distribution-id E3CAAI97MXY83V --id <ID>
```

### Email Not Sending
- Verify SES email: `aws ses verify-email-identity --email-address EMAIL --region ap-south-1`
- Check Lambda logs: `aws logs tail /aws/lambda/meetingmind-FUNCTION --since 5m --region ap-south-1`

### SAM Deploy Fails
- Add `--capabilities CAPABILITY_IAM` for IAM changes
- Use `--resolve-s3` to auto-create S3 bucket
- Run `sam validate` first

## Useful Scripts

- `scripts/trigger-processing.py` - Manually trigger meeting processing
- `scripts/check-meeting-status.py` - Check meeting processing status
- `scripts/regenerate-autopsies-rulebased.py` - Regenerate meeting autopsies
- `scripts/setup/approve-user.py` - Approve pending user accounts
- `scripts/setup/update-email.py` - Update user email addresses

## Post-Deployment Verification

1. Login/signup flow works
2. Upload meeting audio
3. Dashboard loads correctly
4. Kanban drag-and-drop works
5. Team features functional
6. Emails sending properly
