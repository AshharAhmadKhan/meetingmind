# Team Filtering - Testing Checklist

**Date:** 2026-02-20  
**Deployment Status:** ✅ Backend deployed, ✅ Frontend deployed  
**CloudFront Invalidation:** In progress (1-2 minutes)

## What Was Fixed

### Backend Fixes
1. ✅ Fixed team membership validation (dict vs string issue)
2. ✅ Added createdAt to V2 meetings (GSI requirement)
3. ✅ Deployed all 18 Lambda functions

### Frontend Fixes
1. ✅ Fixed Dashboard useEffect to fetch on all team changes
2. ✅ Deployed frontend with CloudFront invalidation

## Testing Steps

### Step 1: Wait for CloudFront (2 minutes)
CloudFront cache invalidation takes 1-2 minutes. Wait before testing.

### Step 2: Hard Refresh Browser
1. Open https://dcfx593ywvy92.cloudfront.net
2. Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac) to hard refresh
3. This clears browser cache and gets latest version

### Step 3: Open Browser DevTools
1. Press `F12` to open DevTools
2. Go to **Network** tab
3. Keep it open while testing

### Step 4: Test Team Filtering

#### Test A: Switch to V1 Team
1. Select "Project V1 - Legacy" from dropdown
2. **Check Network tab:**
   - Look for request to `/meetings?teamId=95febcb2-97e2-4395-bdde-da8475dbae0d`
   - Response should show 3 meetings
3. **Check UI:**
   - Should show 3 meetings: "The Kickoff", "The Cracks", "The Quiet Funeral"
   - Leaderboard should show team members with tasks
   - Meeting count should say "3 recordings"

#### Test B: Switch to V2 Team
1. Select "Project V2 - Active" from dropdown
2. **Check Network tab:**
   - Look for request to `/meetings?teamId=df29c543-a4d0-4c80-a086-6c11712d66f3`
   - Response should show 3 meetings
3. **Check UI:**
   - Should show 3 meetings: "33", "V2 - The Comeback", "5666"
   - Leaderboard might be empty (V2 has no assigned tasks)
   - Meeting count should say "3 recordings"

#### Test C: Switch to Personal
1. Select "Personal (Just Me)" from dropdown
2. **Check Network tab:**
   - Look for request to `/meetings` (no teamId parameter)
   - Response should show all 6 meetings
3. **Check UI:**
   - Should show all 6 meetings
   - Meeting count should say "6 recordings"

### Step 5: Check Other Pages

#### Actions Overview
1. Go to "All Actions" page
2. Switch between teams
3. Verify actions filter by team

#### Debt Dashboard
1. Go to "View Debt" page
2. Switch between teams
3. Verify debt analytics filter by team

## Expected Results

### Database State
```
✅ All 6 meetings have teamId
✅ All 6 meetings have createdAt
✅ V1 team: 3 meetings
✅ V2 team: 3 meetings
✅ User is member of both teams
```

### API Responses
```
✅ V1 query returns 3 meetings
✅ V2 query returns 3 meetings
✅ Personal query returns 6 meetings
✅ Team membership validation passes
```

### UI Behavior
```
✅ Team selector shows both teams
✅ Switching teams triggers new API call
✅ Meetings list updates correctly
✅ Leaderboard filters by team
✅ No 403 errors in console
```

## Troubleshooting

### Issue: Still seeing all 6 meetings for every team
**Cause:** CloudFront cache not cleared yet  
**Solution:** Wait 2 minutes, then hard refresh (Ctrl+Shift+R)

### Issue: 403 "Not a member" error
**Cause:** Backend membership validation failing  
**Solution:** Check CloudWatch logs for list-meetings Lambda

### Issue: Network request has no teamId parameter
**Cause:** Frontend not passing teamId  
**Solution:** Check browser console for errors

### Issue: V2 team shows 0 meetings
**Cause:** GSI not updated yet (eventual consistency)  
**Solution:** Wait 30 seconds and refresh

## Verification Commands

### Check DynamoDB Data
```powershell
python scripts/testing/check-meetings-teamid.py
python scripts/testing/check-teams.py
```

### Test GSI Queries
```powershell
python scripts/testing/test-team-filtering.py
```

### Trace Request Flow
```powershell
python scripts/testing/trace-full-request-flow.py
```

## Success Criteria

- [ ] V1 team shows exactly 3 meetings
- [ ] V2 team shows exactly 3 meetings
- [ ] Personal shows all 6 meetings
- [ ] No 403 errors in console
- [ ] Network requests have correct teamId parameter
- [ ] Leaderboard filters by team
- [ ] Debt dashboard filters by team

## Timeline

- **Backend deployed:** 01:39 UTC
- **Frontend deployed:** 01:42 UTC
- **CloudFront invalidation:** 01:42 UTC (complete by 01:44 UTC)
- **Ready for testing:** 01:44 UTC

## Contact

If issues persist after following this checklist:
1. Check browser console for errors
2. Check Network tab for failed requests
3. Run diagnostic scripts above
4. Check CloudWatch logs for Lambda errors
