# MeetingMind Signup & Approval Workflow

## Complete Flow

### 1. User Signs Up
- User visits: https://dcfx593ywvy92.cloudfront.net
- Clicks "Sign up" link on login page
- Enters email and password
- Clicks "Create account"
- Sees success message:
  > ✓ Registration received!
  > 
  > Thank you for registering. We'll send you an email once your account is approved. This usually takes a few hours.

### 2. You Get Notified
**YOU receive an email at `itzashhar@gmail.com`:**

Subject: `🔔 New MeetingMind Signup: user@email.com`

Email contains:
- User's email address
- Step-by-step approval instructions
- Ready-to-copy command: `python scripts/approve-user.py user@email.com`

### 3. You Approve the User
Open terminal and run:
```bash
python scripts/approve-user.py user@email.com
```

This does 3 things automatically:
1. ✅ Verifies email in SES (sends verification email to user)
2. ✅ Enables Cognito account (user can now log in)
3. ✅ Sends welcome email to user

### 4. User Verifies Email
User receives 2 emails:

**Email 1: AWS SES Verification**
- Subject: "Amazon SES Email Address Verification Request"
- User clicks verification link
- Email is now verified for daily digests

**Email 2: Welcome Email**
- Subject: "🎉 Your MeetingMind account is approved!"
- Contains "Sign In Now" button
- User can now log in

### 5. User Logs In
- User clicks "Sign In Now" or visits the app
- Logs in with their credentials
- Can now upload meetings and use all features
- Will receive daily digest emails at 9 AM IST

## Why This Works

**Problem:** AWS SES sandbox mode only sends to verified emails

**Solution:** Manual approval workflow
- You verify each user's email in SES before they can receive digests
- Users think it's a normal approval process (common for beta products)
- No need to request SES production access (saves 24 hours)
- Perfect for competition with 5-6 test users

## Email Addresses

**Sender (verified):**
- `thecyberprinciples@gmail.com` - Sends all emails (digests, welcome, etc.)

**Admin (verified):**
- `itzashhar@gmail.com` - Receives signup notifications

**Users:**
- Each user's email gets verified when you approve them
- They receive daily digests after verification

## Testing the Workflow

Test with a friend's email:

1. Ask them to sign up at https://dcfx593ywvy92.cloudfront.net
2. You'll get notification email within seconds
3. Run: `python scripts/approve-user.py their@email.com`
4. They get 2 emails (SES verification + welcome)
5. They click SES verification link
6. They log in and use the app
7. Tomorrow at 9 AM, they get daily digest

## Commands Reference

### Approve a user
```bash
python scripts/approve-user.py user@email.com
```

### Check SES verification status
```bash
aws ses get-identity-verification-attributes --identities user@email.com --region ap-south-1
```

### List all users
```bash
aws cognito-idp list-users --user-pool-id ap-south-1_mkFJawjMp --region ap-south-1
```

### Check if user is enabled
```bash
aws cognito-idp admin-get-user --user-pool-id ap-south-1_mkFJawjMp --username <username> --region ap-south-1
```

## What Happens Behind the Scenes

### When User Signs Up:
1. **PreSignupFunction** runs
   - Auto-confirms user (no email verification code needed)
   - User is created in Cognito

2. **PostConfirmationFunction** runs
   - Immediately disables the account
   - Sends YOU an email notification
   - User cannot log in yet

### When You Approve:
1. **approve-user.py script** runs
   - Verifies email in SES
   - Enables Cognito account
   - Triggers SendWelcomeEmailFunction

2. **SendWelcomeEmailFunction** runs
   - Sends welcome email to user
   - User can now log in

### Daily Digest:
1. **DailyDigestFunction** runs at 9 AM IST
   - Scans all meetings
   - Groups by user
   - Sends digest to verified emails only
   - Users with unverified emails are skipped

## For Day 7 (Get Real Users)

When recruiting your 5 test users:

1. **Tell them:**
   > "I'm testing my app for a competition. Sign up at [link] and I'll approve your account within a few minutes. You'll get an email when it's ready."

2. **When they sign up:**
   - You get instant notification
   - Run approval command
   - They're ready in 2-3 minutes

3. **Ask them to:**
   - Upload 3 meeting recordings
   - Check their daily digest tomorrow morning
   - Give you feedback

This workflow makes you look professional while solving the SES sandbox limitation!

## Moving to Production Later

After the competition, request SES production access:
1. AWS Console → SES → Account dashboard → Request production access
2. Takes 24 hours
3. Then you can send to any email without verification
4. Remove the manual approval workflow

