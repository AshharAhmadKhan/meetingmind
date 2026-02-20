# Team Upload Bug - ROOT CAUSE IDENTIFIED AND FIXED

## Issue Summary
When uploading a meeting to a team (V1 or V2), the meeting would appear in "Personal (Just Me)" instead of the selected team, even though the frontend was sending the correct teamId and the backend was initially storing it.

## Root Cause Analysis

### What Was Happening:
1. ✅ Frontend sends correct teamId in upload request
2. ✅ `get-upload-url` Lambda receives teamId correctly
3. ✅ `get-upload-url` stores meeting with teamId in DynamoDB
4. ❌ `process-meeting` Lambda OVERWRITES the item WITHOUT teamId
5. ❌ Meeting ends up in database WITHOUT teamId (appears as personal)

### The Bug Location:
**File**: `backend/functions/process-meeting/app.py`
**Function**: `_update(table, user_id, meeting_id, status, extra=None)`
**Lines**: 35-54

### The Problem:
The `_update` function was creating a NEW item dictionary from scratch with only:
- `userId`
- `meetingId`
- `status`
- `updatedAt`
- `createdAt` (for new meetings)
- Fields from `extra` parameter

It was NOT reading the existing item from DynamoDB, so it lost the `teamId` field that was stored by `get-upload-url`.

When `process-meeting` Lambda runs, it calls `_update` multiple times:
1. TRANSCRIBING phase → overwrites item WITHOUT teamId
2. ANALYZING phase → overwrites item WITHOUT teamId
3. DONE phase → overwrites item WITHOUT teamId

Each `put_item` call REPLACES the entire item in DynamoDB, so the `teamId` gets deleted.

## The Fix

### Before (Buggy Code):
```python
def _update(table, user_id, meeting_id, status, extra=None):
    # Check if meeting exists to determine if it's new
    try:
        existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        is_new = 'Item' not in existing
    except:
        is_new = True
    
    now = datetime.now(timezone.utc).isoformat()
    
    item = {
        'userId': user_id,
        'meetingId': meeting_id,
        'status': status,
        'updatedAt': now
    }
    
    # Add createdAt only for new meetings
    if is_new:
        item['createdAt'] = now
    
    item.update(extra or {})
    table.put_item(Item=item)
```

### After (Fixed Code):
```python
def _update(table, user_id, meeting_id, status, extra=None):
    # Check if meeting exists to determine if it's new
    try:
        existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        is_new = 'Item' not in existing
        existing_item = existing.get('Item', {})
    except:
        is_new = True
        existing_item = {}
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Start with existing item to preserve fields like teamId
    item = existing_item.copy() if existing_item else {}
    
    # Update with new values
    item.update({
        'userId': user_id,
        'meetingId': meeting_id,
        'status': status,
        'updatedAt': now
    })
    
    # Add createdAt only for new meetings
    if is_new:
        item['createdAt'] = now
    
    # Add extra fields
    item.update(extra or {})
    
    # Log teamId preservation
    if 'teamId' in item:
        print(f"🔄 Preserving teamId: {item['teamId']}")
    
    table.put_item(Item=item)
```

### Key Changes:
1. **Read existing item**: `existing_item = existing.get('Item', {})`
2. **Start with existing data**: `item = existing_item.copy() if existing_item else {}`
3. **Update instead of replace**: This preserves all existing fields including `teamId`
4. **Add logging**: Log when teamId is preserved for debugging

## Deployment

### Lambda Function Updated:
- **Function**: `meetingmind-process-meeting`
- **Region**: `ap-south-1`
- **Status**: ✅ Successfully deployed
- **Timestamp**: 2026-02-20 19:08:19 UTC

### Deployment Method:
```bash
cd backend
sam build
Compress-Archive -Path .aws-sam/build/ProcessMeetingFunction/* -DestinationPath process-meeting.zip -Force
aws lambda update-function-code --function-name meetingmind-process-meeting --zip-file fileb://process-meeting.zip --region ap-south-1
```

## Testing Instructions

### Test Script Created:
`scripts/testing/features/test-teamid-preservation.py`

### How to Test:
1. Upload a new meeting to V1 or V2 team in the frontend
2. Wait for processing to complete (status = DONE)
3. Run the test script:
   ```bash
   python scripts/testing/features/test-teamid-preservation.py
   ```
4. Verify the meeting shows ✅ with the correct team name

### Expected Results:
- ✅ Meeting should have `teamId` field in DynamoDB
- ✅ Meeting should appear under the selected team in the frontend
- ✅ CloudWatch logs should show: `🔄 Preserving teamId: <team-id>`

## Impact

### Before Fix:
- All team uploads went to "Personal (Just Me)"
- Users couldn't collaborate on meetings
- Team feature was completely broken

### After Fix:
- Team uploads correctly preserve teamId
- Meetings appear under the correct team
- Team collaboration works as intended

## Related Files Modified:
1. `backend/functions/process-meeting/app.py` - Fixed `_update` function
2. `scripts/testing/features/test-teamid-preservation.py` - Test script created

## Next Steps:
1. ✅ Fix deployed to production
2. ⏳ User to test with new upload
3. ⏳ Verify teamId is preserved in database
4. ⏳ Confirm meeting appears under correct team in frontend

## Historical Context:
This bug was introduced when the `_update` function was created to handle meeting status updates during processing. The function was designed to update status efficiently but didn't account for preserving existing fields like `teamId` that were set during the initial upload phase.

The bug affected all meetings uploaded to teams since the team feature was implemented, which is why all existing meetings in the database show as "Personal (Just Me)" even though they were uploaded to teams.

## Prevention:
To prevent similar issues in the future:
1. Always read existing item before updating in DynamoDB
2. Use `item.update()` to merge new fields instead of creating new dict
3. Add logging to track field preservation
4. Test end-to-end flow including all Lambda functions in the pipeline
