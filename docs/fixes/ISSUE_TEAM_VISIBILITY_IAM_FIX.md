# Team Visibility Issue - IAM Permission Fix

**Date:** February 20, 2026  
**Status:** FIXED  
**Root Cause:** IAM permissions missing for list-meetings Lambda

---

## Problem

Team members (non-uploaders) could not see team meetings. Frontend showed "Failed to load meetings" error.

**Symptoms:**
- Uploader (thecyberprinciples@gmail.com) could see all meetings
- Team members (thehiddenif@gmail.com, ashkagakoko@gmail.com) got "Failed to load meetings"
- Browser console showed CORS errors or 403/500 errors

---

## Root Cause

The `list-meetings` Lambda function was missing IAM permissions to read from the `meetingmind-teams` table.

**Error in CloudWatch:**
```
AccessDeniedException: User: arn:aws:sts::707411439284:assumed-role/meetingmind-stack-ListMeetingsFunctionRole-no3OOZD1z9RF/meetingmind-list-meetings 
is not authorized to perform: dynamodb:GetItem on resource: arn:aws:dynamodb:ap-south-1:707411439284:table/meetingmind-teams
```

**Why this happened:**
- The `template.yaml` had correct permissions (DynamoDBReadPolicy for both tables)
- But the deployed CloudFormation stack had outdated IAM policy
- The policy only allowed reading from `meetingmind-meetings`, not `meetingmind-teams`
- When a team member tried to list meetings, the Lambda tried to verify team membership by reading from `meetingmind-teams` table
- This failed with AccessDeniedException, causing the API to return 500 error

---

## How Team Visibility Works

### Backend Flow (list-meetings Lambda)

```python
# When user requests meetings with teamId parameter:

1. Get team from meetingmind-teams table
   teams_table.get_item(Key={'teamId': team_id})  # ← NEEDS PERMISSION

2. Check if user is a member
   members = team.get('members', [])
   if user_id not in member_ids:
       return 403 Forbidden

3. Query meetings by teamId
   meetings_table.query(
       IndexName='teamId-createdAt-index',
       KeyConditionExpression='teamId = :tid'
   )

4. Return meetings to user
```

**The Lambda needs permissions for BOTH tables:**
- `meetingmind-meetings` - to query meetings
- `meetingmind-teams` - to verify team membership

---

## Fix Applied

### Step 1: Identified Missing Permission

```bash
# Checked deployed IAM policy
aws iam get-role-policy \
  --role-name meetingmind-stack-ListMeetingsFunctionRole-no3OOZD1z9RF \
  --policy-name ListMeetingsFunctionRolePolicy0

# Result: Only had permission for meetingmind-meetings table
```

### Step 2: Updated IAM Policy

```bash
# Created new policy with both tables
aws iam put-role-policy \
  --role-name meetingmind-stack-ListMeetingsFunctionRole-no3OOZD1z9RF \
  --policy-name ListMeetingsFunctionRolePolicy0 \
  --policy-document file://scripts/fix-iam-permissions.json
```

**New Policy:**
```json
{
  "Statement": [
    {
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:BatchGetItem",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-south-1:707411439284:table/meetingmind-meetings",
        "arn:aws:dynamodb:ap-south-1:707411439284:table/meetingmind-meetings/index/*",
        "arn:aws:dynamodb:ap-south-1:707411439284:table/meetingmind-teams",
        "arn:aws:dynamodb:ap-south-1:707411439284:table/meetingmind-teams/index/*"
      ],
      "Effect": "Allow"
    }
  ]
}
```

### Step 3: Verified Fix

```bash
# Tested all 3 users with direct Lambda invocation
python scripts/testing/features/test-list-meetings-lambda.py

# Results:
✅ thecyberprinciples@gmail.com: Can see 5 meetings
✅ thehiddenif@gmail.com: Can see 5 meetings  
✅ ashkagakoko@gmail.com: Can see 5 meetings
```

---

## Test Results

### V1 - Legacy Team
- **TeamId:** `95febcb2-97e2-4395-bdde-da8475dbae0d`
- **Members:** 4 (whispersbehindthecode, thehiddenif, thecyberprinciples, ashkagakoko)
- **Meetings:** 5 (all uploaded by thecyberprinciples or ashkagakoko)

**Test Results:**
```
User: thecyberprinciples@gmail.com
  ✅ Can see all 5 meetings
  
User: thehiddenif@gmail.com  
  ✅ Can see all 5 meetings (including ones uploaded by others)
  
User: ashkagakoko@gmail.com
  ✅ Can see all 5 meetings (including ones uploaded by others)
```

### V2 - Active Team
- **TeamId:** `df29c543-a4d0-4c80-a086-6c11712d66f3`
- **Members:** 3 (thecyberprinciples, thehiddenif, whispersbehindthecode)
- **Meetings:** 3 (all uploaded by thecyberprinciples)

**Expected:** All 3 members can see all 3 meetings (same fix applies)

---

## Next Steps

### 1. CloudFront Cache Invalidation (REQUIRED)

The backend is fixed, but CloudFront may be caching old error responses.

```bash
aws cloudfront create-invalidation \
  --distribution-id E3CAAI97MXY83V \
  --paths "/*"
```

**Wait 5-10 minutes for invalidation to complete.**

### 2. User Testing

After cache invalidation, test with all 3 accounts:

1. **Clear browser cache completely**
   - Chrome: Ctrl+Shift+Delete → Clear all
   - Or use Incognito mode

2. **Log in as thehiddenif@gmail.com**
   - Select "V1 - Legacy" team
   - Should see 5 meetings
   - Click on any meeting → Should load details

3. **Log in as ashkagakoko@gmail.com**
   - Select "V1 - Legacy" team
   - Should see 5 meetings
   - Click on any meeting → Should load details

4. **Log in as thecyberprinciples@gmail.com**
   - Select "V1 - Legacy" team
   - Should see 5 meetings
   - Select "V2 - Active" team
   - Should see 3 meetings

### 3. Verify New Team Creation

Test the complete flow with a new team:

1. User A creates team "Alpha"
2. User A uploads meeting to Alpha
3. User B joins Alpha with invite code
4. User B should see User A's meeting
5. User B uploads meeting to Alpha
6. User A should see User B's meeting

---

## Why This Issue Occurred

### Timeline

1. **Initial deployment:** Template had correct permissions
2. **Some update:** CloudFormation stack got out of sync
3. **SAM deploy:** Said "no changes" because template hash matched
4. **Result:** Deployed IAM policy was outdated

### Prevention

To prevent this in the future:

1. **Always check deployed resources match template**
   ```bash
   aws cloudformation detect-stack-drift --stack-name meetingmind-stack
   ```

2. **Force update if needed**
   ```bash
   sam deploy --force-upload
   ```

3. **Verify IAM policies after deployment**
   ```bash
   aws iam get-role-policy --role-name <role> --policy-name <policy>
   ```

---

## Related Files

- `backend/template.yaml` - CloudFormation template (has correct permissions)
- `backend/functions/list-meetings/app.py` - Lambda that needs both table permissions
- `scripts/fix-iam-permissions.json` - Fixed IAM policy
- `scripts/testing/features/test-list-meetings-lambda.py` - Test script
- `scripts/testing/features/check-current-state.py` - Database state checker

---

## Conclusion

✅ **Backend is FIXED**
- All users can now see team meetings
- IAM permissions are correct
- Lambda tests pass for all users

⏳ **Waiting for CloudFront cache invalidation**
- Run: `aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"`
- Wait 5-10 minutes
- Then test in browser

🎯 **Expected Result**
- Team members can see all team meetings
- No more "Failed to load meetings" errors
- Full team collaboration works as designed

---

**Status:** Backend fixed, waiting for cache invalidation and user verification
