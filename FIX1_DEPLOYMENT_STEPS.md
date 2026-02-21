# Fix #1 Deployment Steps

## Status: ✅ CODE COMPLETE - Ready for Deployment

All code changes have been committed. The build directory has a file lock - close any editors/terminals that might be holding files open, then deploy.

## Pre-Deployment Checklist:

✅ Constants extracted to Lambda layer
✅ 4 Lambda functions updated to use constants
✅ Test script passes (all 16 constants verified)
✅ Changes committed to git
✅ Zero logic changes (pure refactoring)

## Deployment Steps:

### 1. Close File Locks
```powershell
# Close any VS Code, editors, or terminals that might have backend files open
# Wait 10 seconds for file handles to release
```

### 2. Clean Build Directory
```powershell
cd backend
Remove-Item -Recurse -Force .aws-sam\build -ErrorAction SilentlyContinue
```

### 3. Build SAM Application
```powershell
sam build
```

### 4. Deploy to AWS
```powershell
sam deploy --no-confirm-changeset
```

### 5. Verify Deployment
```powershell
# Check Lambda layer was created
aws lambda list-layers --query 'Layers[?LayerName==`meetingmind-shared-constants`]'

# Check functions have the layer attached
aws lambda get-function --function-name meetingmind-process-meeting --query 'Configuration.Layers'
```

## Post-Deployment Testing:

### Test 1: Upload a Meeting
- Upload a test audio file
- Verify processing completes successfully
- Check CloudWatch logs for any import errors

### Test 2: Check Graveyard
- Navigate to Graveyard page
- Verify items >30 days old appear (GRAVEYARD_THRESHOLD_DAYS constant)
- Verify epitaphs are generated

### Test 3: Check Debt Analytics
- Navigate to Debt Analytics page
- Verify calculations use correct constants (AVG_HOURLY_RATE, AVG_BLOCKED_TIME_HOURS)

### Test 4: Check Duplicate Detection
- Try creating a duplicate action item
- Verify similarity threshold works (DUPLICATE_SIMILARITY_THRESHOLD = 0.85)

## Expected Results:

✅ All Lambda functions deploy successfully
✅ Shared constants layer is attached to all functions
✅ No functional changes (behavior identical to before)
✅ CloudWatch logs show no import errors
✅ All features work exactly as before

## Rollback Plan (if needed):

```powershell
# Revert to previous commit
git revert HEAD

# Redeploy
cd backend
sam build
sam deploy --no-confirm-changeset
```

## Success Criteria:

- [ ] SAM build completes without errors
- [ ] SAM deploy completes without errors
- [ ] Lambda layer created successfully
- [ ] All functions have layer attached
- [ ] Test meeting processes successfully
- [ ] Graveyard shows items correctly
- [ ] Debt analytics calculates correctly
- [ ] Duplicate detection works correctly

## Next Steps After Fix #1:

Once Fix #1 is deployed and tested:
1. Commit any deployment notes
2. Move to Fix #2: Epitaph Pre-Generation (4 hours)
3. Then Fix #3: Frontend Loading States (2 hours)

---

**Note:** If you encounter file lock issues during `sam build`, close all editors and terminals, wait 10 seconds, then try again. Windows file locks can persist briefly after closing applications.
