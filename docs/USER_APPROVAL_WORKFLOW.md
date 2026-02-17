# User Approval Workflow

## Overview

MeetingMind uses a manual approval workflow for new users while in SES sandbox mode. This ensures only verified emails receive daily digest emails.

## How It Works

### 1. User Signs Up
- User visits https://dcfx593ywvy92.cloudfront.net
- Clicks "Sign up" link
- Enters email and password
- Sees message: "Thank you for registering! We'll send you an email once your account is approved."
- Account is created but **disabled** (cannot log in yet)

### 2. You Approve the User

Run the approval script:

```bash
python scripts/approve-user.py user@email.com
```

This script does 3 things:
1. **Verifies email in SES** - Sends verification email to user
2. **Enables Cognito account** - User can now log in
3. **Sends welcome email** - Notifies user they're approved

### 3. User Verifies Email
- User receives SES verification email
- Clicks verification link
- Email is now verified for sending daily digests

### 4. User Logs In
- User receives welcome email
- Clicks "Sign In Now" button
- Logs in with their credentials
- Can now use MeetingMind

## Manual Approval Commands

### Approve a user
```bash
python scripts/approve-user.py user@email.com
```

### Check if email is verified in SES
```bash
aws ses get-identity-verification-attributes --identities user@email.com --region ap-south-1
```

### List all Cognito users
```bash
aws cognito-idp list-users --user-pool-id ap-south-1_mkFJawjMp --region ap-south-1
```

### Enable a user manually
```bash
aws cognito-idp admin-enable-user --user-pool-id ap-south-1_mkFJawjMp --username <username> --region ap-south-1
```

### Disable a user
```bash
aws cognito-idp admin-disable-user --user-pool-id ap-south-1_mkFJawjMp --username <username> --region ap-south-1
```

## Why This Workflow?

**SES Sandbox Mode:**
- AWS SES starts in sandbox mode
- Can only send emails to verified addresses
- Manual verification required for each recipient

**Benefits:**
- Control who gets access during testing
- Ensure daily digest emails work for all users
- Prevent spam/abuse

## Moving to Production

To remove manual approval and allow anyone to sign up:

1. **Request SES Production Access:**
   ```bash
   # Submit request via AWS Console
   # SES > Account dashboard > Request production access
   # Takes 24 hours for approval
   ```

2. **Remove Post-Confirmation Trigger:**
   - Update `backend/template.yaml`
   - Remove `PostConfirmation` from `LambdaConfig`
   - Redeploy backend

3. **Update Frontend Message:**
   - Change signup success message to "Check your email to verify your account"
   - Users can log in immediately after email verification

## Troubleshooting

### User can't log in after approval
- Check if account is enabled: `aws cognito-idp admin-get-user --user-pool-id ap-south-1_mkFJawjMp --username <username> --region ap-south-1`
- Enable manually if needed

### User not receiving welcome email
- Check CloudWatch logs for `meetingmind-send-welcome-email`
- Verify SES sender email is verified: `thecyberprinciples@gmail.com`

### User not receiving daily digest
- Check if their email is verified in SES
- Run verification again: `aws ses verify-email-identity --email-address user@email.com --region ap-south-1`
- User must click verification link

## Lambda Functions

### PreSignupFunction
- Triggered when user signs up
- Auto-confirms user (skips email verification code)
- Located: `backend/functions/pre-signup/app.py`

### PostConfirmationFunction
- Triggered after user is confirmed
- Immediately disables the account
- Requires manual approval to enable
- Located: `backend/functions/post-confirmation/app.py`

### SendWelcomeEmailFunction
- Sends welcome email when user is approved
- Triggered by approval script
- Located: `backend/functions/send-welcome-email/app.py`

## Testing

Test the full workflow:

1. Sign up with a test email
2. Verify account is disabled
3. Run approval script
4. Check SES verification email received
5. Click verification link
6. Check welcome email received
7. Log in successfully
8. Upload a meeting
9. Wait for daily digest (or trigger manually)

