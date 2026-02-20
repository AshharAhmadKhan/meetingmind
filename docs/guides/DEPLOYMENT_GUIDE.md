# MeetingMind Deployment Guide

**Last Updated:** February 20, 2026  
**Author:** Ashhar Ahmad Khan

---

## SAM Deployment Commands

### ✅ CORRECT: Full Stack Deployment

```bash
cd backend
sam deploy --stack-name meetingmind-stack --resolve-s3 --no-confirm-changeset --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
```

**Why this works:**
- `--resolve-s3`: Automatically creates/uses managed S3 bucket for deployment artifacts
- `--no-confirm-changeset`: Skips manual confirmation (useful for CI/CD)
- `--no-fail-on-empty-changeset`: Succeeds even if no changes detected
- `--capabilities CAPABILITY_IAM`: Required when template creates/modifies IAM roles

**When to use:**
- Deploying template.yaml changes (IAM policies, environment variables, new resources)
- First-time deployment
- After modifying Lambda permissions or configurations

---

### ❌ INCORRECT: Missing S3 Bucket

```bash
sam deploy --stack-name meetingmind-stack --no-confirm-changeset
```

**Error:**
```
Error: Unable to upload artifact referenced by CodeUri parameter.
S3 Bucket not specified, use --s3-bucket to specify a bucket name
```

**Why it fails:**
- SAM needs an S3 bucket to upload Lambda code packages
- Without `--resolve-s3` or `--s3-bucket`, deployment fails

---

### Quick Lambda Code Update (No Template Changes)

```bash
# Build specific function
sam build PreSignupFunction

# Package and deploy just the code
aws lambda update-function-code \
  --function-name meetingmind-pre-signup \
  --zip-file fileb://.aws-sam/build/PreSignupFunction.zip \
  --region ap-south-1
```

**When to use:**
- Only Lambda code changed (no template.yaml modifications)
- Faster than full stack deployment
- Testing code changes quickly

**Limitations:**
- Doesn't update environment variables
- Doesn't update IAM permissions
- Doesn't update Lambda configuration (timeout, memory, etc.)

---

## SES Email Configuration

### Issue: Email Address Not Verified

**Error in CloudWatch Logs:**
```
MessageRejected: Email address is not verified. 
The following identities failed the check: noreply@meetingmind.app
```

**Root Cause:**
- SES requires FROM email addresses to be verified
- In sandbox mode, both FROM and TO addresses must be verified

**Solution:**
1. Use already verified email as FROM address
2. OR verify new email in SES:

```bash
# Verify email address
aws ses verify-email-identity \
  --email-address noreply@meetingmind.app \
  --region ap-south-1

# Check verification status
aws ses get-identity-verification-attributes \
  --identities noreply@meetingmind.app \
  --region ap-south-1
```

**Current Configuration:**
- FROM: `thecyberprinciples@gmail.com` (verified ✅)
- TO: `thecyberprinciples@gmail.com` (verified ✅)

---

## IAM Permission Issues

### Issue: Lambda Can't Send Emails

**Error in CloudWatch Logs:**
```
AccessDenied: User 'arn:aws:sts::707411439284:assumed-role/...' 
is not authorized to perform 'ses:SendEmail'
```

**Root Cause:**
- Lambda execution role missing SES permissions
- Policy not attached in template.yaml

**Solution:**
Add SESCrudPolicy to Lambda in template.yaml:

```yaml
PreSignupFunction:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - SESCrudPolicy:
          IdentityName: thecyberprinciples@gmail.com
```

**Important:** Must deploy full stack to update IAM roles:
```bash
sam deploy --stack-name meetingmind-stack --resolve-s3 --capabilities CAPABILITY_IAM
```

---

## Testing Workflow

### 1. Make Code Changes
```bash
# Edit Lambda function code
vim backend/functions/pre-signup/app.py
```

### 2. Build Function
```bash
cd backend
sam build PreSignupFunction
```

### 3. Deploy Changes

**If only code changed:**
```bash
aws lambda update-function-code \
  --function-name meetingmind-pre-signup \
  --zip-file fileb://.aws-sam/build/PreSignupFunction.zip \
  --region ap-south-1
```

**If template.yaml changed (env vars, permissions, etc.):**
```bash
sam deploy --stack-name meetingmind-stack --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
```

### 4. Test Function
```bash
python scripts/testing/features/test-admin-notification.py
```

### 5. Check Logs
```bash
aws logs tail /aws/lambda/meetingmind-pre-signup --since 5m --region ap-south-1
```

### 6. Verify in App
- Check email inbox for notification
- Verify email content and formatting
- Test all links and commands

### 7. Commit Changes
```bash
git add -A
git commit -m "feat: description of changes"
```

---

## Common Pitfalls

### 1. Forgetting to Deploy Template Changes
**Symptom:** Environment variables not updated, permissions still missing  
**Solution:** Always use full `sam deploy` when template.yaml changes

### 2. Using Unverified Email Addresses
**Symptom:** Emails not sent, MessageRejected errors  
**Solution:** Verify all FROM addresses in SES first

### 3. Missing IAM Capabilities Flag
**Symptom:** Deployment fails with IAM error  
**Solution:** Add `--capabilities CAPABILITY_IAM` to deploy command

### 4. Not Checking CloudWatch Logs
**Symptom:** Function seems to work but emails not received  
**Solution:** Always check logs to see actual errors

---

## Email Template Best Practices

### Premium Email Design Principles

1. **Clean, Professional Layout**
   - Use AWS-style color scheme (#232f3e header, #ff9900 accents)
   - Proper spacing and padding
   - Clear visual hierarchy

2. **Typography**
   - System fonts: 'Amazon Ember', 'Helvetica Neue', Roboto, Arial
   - Readable font sizes (14-16px body, 18-24px headers)
   - Proper line height (1.5-1.6)

3. **Color Palette**
   - Dark header: #232f3e
   - Accent: #ff9900 (orange)
   - Text: #111111 (primary), #555555 (secondary)
   - Background: #f7f7f7
   - Borders: #e7e7e7

4. **Structure**
   - Header with logo/branding
   - Clear content sections
   - Action items in highlighted boxes
   - Footer with company info

5. **No Unnecessary Emojis**
   - Use emojis only if they add value
   - Professional emails should be clean and minimal
   - Let design and content speak for themselves

---

## Deployment Checklist

Before deploying to production:

- [ ] All Lambda functions built successfully
- [ ] Template.yaml validated (`sam validate`)
- [ ] Environment variables configured correctly
- [ ] IAM permissions properly set
- [ ] SES email addresses verified
- [ ] Test scripts pass
- [ ] CloudWatch logs checked for errors
- [ ] Email templates tested and verified
- [ ] Changes committed to git
- [ ] Documentation updated

---

## Quick Reference

### Build Single Function
```bash
sam build FunctionName
```

### Build All Functions
```bash
sam build
```

### Deploy Full Stack
```bash
sam deploy --stack-name meetingmind-stack --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
```

### Update Lambda Code Only
```bash
aws lambda update-function-code --function-name <name> --zip-file fileb://.aws-sam/build/<FunctionName>.zip --region ap-south-1
```

### Check Logs
```bash
aws logs tail /aws/lambda/<function-name> --since 5m --region ap-south-1
```

### Verify SES Email
```bash
aws ses verify-email-identity --email-address <email> --region ap-south-1
```

---

**Region:** ap-south-1  
**Account:** 707411439284  
**Stack:** meetingmind-stack
