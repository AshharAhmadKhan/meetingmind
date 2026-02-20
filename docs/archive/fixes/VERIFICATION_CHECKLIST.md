# Verification Checklist - Team Visibility Fixes

## Changes Made

### 1. Fixed Team Selection Polling Issue
**File:** `frontend/src/pages/Dashboard.jsx`
**Change:** Combined useEffect hooks so polling interval uses current `selectedTeamId`
**Why:** The polling was calling `fetchMeetings()` without the current team context

### 2. Added Cache-Busting
**File:** `frontend/src/utils/api.js`
**Change:** Added `_t: Date.now()` timestamp to all `listMeetings()` calls
**Why:** Prevents CloudFront from serving stale cached responses

### 3. Added V1/V2 Visual Indicators
**File:** `frontend/src/components/TeamSelector.jsx`
**Change:** 
- Added emoji indicators: 📦 for V1/Legacy, 🚀 for V2/Active, 👥 for other teams
- Changed "Personal (Just Me)" to "📋 Personal (Just Me)"
**Why:** Makes it clear which team is V1 vs V2

### 4. Deployed Changes
- ✅ Built frontend: `npm run build`
- ✅ Synced to S3: `s3://meetingmind-frontend-707411439284`
- ✅ Cleared CloudFront cache: Distribution E3CAAI97MXY83V
- ✅ Cache invalidation status: **Completed**

---

## Verification Steps

### Test 1: Main Account (itzashhar@gmail.com)
**Expected:** Should see all 6 meetings when selecting teams

1. [ ] Login to https://dcfx593ywvy92.cloudfront.net
2. [ ] Check team selector shows:
   - 📋 Personal (Just Me)
   - 📦 Project V1 - Legacy (3 members)
   - 🚀 Project V2 - Active (3 members)
3. [ ] Select "📦 Project V1 - Legacy"
4. [ ] Should see 3 meetings:
   - V1 Meeting 1: The Kickoff
   - V1 Meeting 2: The Cracks
   - V1 Meeting 3: The Quiet Funeral
5. [ ] Select "🚀 Project V2 - Active"
6. [ ] Should see 3 meetings:
   - 33
   - V2 - The Comeback
   - 5666
7. [ ] Select "📋 Personal (Just Me)"
8. [ ] Should see 6 meetings (all uploaded by main account)

### Test 2: Team Member Account (thehidden@example.com)
**Expected:** Should see team meetings even though they didn't upload them

1. [ ] Login as thehidden@example.com
2. [ ] Check team selector shows same teams with emojis
3. [ ] Select "📦 Project V1 - Legacy"
4. [ ] **CRITICAL:** Should see 3 V1 meetings (not empty!)
5. [ ] Select "🚀 Project V2 - Active"
6. [ ] **CRITICAL:** Should see 3 V2 meetings (not empty!)
7. [ ] Select "📋 Personal (Just Me)"
8. [ ] Should see 0 meetings (they haven't uploaded any)

### Test 3: Another Team Member (whisperbehind@example.com)
**Expected:** Same as Test 2

1. [ ] Login as whisperbehind@example.com
2. [ ] Select "📦 Project V1 - Legacy"
3. [ ] **CRITICAL:** Should see 3 V1 meetings
4. [ ] Select "🚀 Project V2 - Active"
5. [ ] **CRITICAL:** Should see 3 V2 meetings
6. [ ] Select "📋 Personal (Just Me)"
7. [ ] Should see 0 meetings

---

## What to Check in Browser

### Browser Console
Open DevTools (F12) and check:
1. [ ] No JavaScript errors
2. [ ] Network tab shows API calls to `/meetings?teamId=xxx&_t=timestamp`
3. [ ] API responses contain meetings array with data
4. [ ] No 403 Forbidden errors (team membership validation working)

### Visual Checks
1. [ ] Team selector dropdown shows emojis correctly
2. [ ] Meeting cards display properly
3. [ ] No "Failed to load meetings" error
4. [ ] Empty state only shows when truly no meetings exist

---

## If Tests Fail

### Issue: Still seeing empty state for team members
**Possible causes:**
1. Browser cache - Try hard refresh (Ctrl+Shift+R)
2. CloudFront still propagating - Wait 2-3 minutes
3. Team membership not set up - Run: `python scripts/testing/check-teams.py`

### Issue: API returns 403 Forbidden
**Possible causes:**
1. User not in team members list
2. Team membership validation too strict
3. Check: `python scripts/testing/check-team-members.py`

### Issue: API returns empty array
**Possible causes:**
1. Meetings missing teamId - Run: `python scripts/testing/check-meetings-teamid.py`
2. GSI not working - Check DynamoDB console
3. Backend not querying by teamId - Check Lambda logs

---

## Success Criteria

✅ **Fix is successful if:**
1. Team members can see all team meetings (not just their own)
2. V1 and V2 teams are visually distinct with emojis
3. Personal view shows only user's own meetings
4. No console errors or API failures
5. Cache-busting prevents stale data

❌ **Fix failed if:**
1. Team members still see empty state
2. Only uploader can see meetings
3. Team selector doesn't show emojis
4. API returns 403 or empty arrays

---

## Next Steps After Verification

If tests pass:
- [ ] Mark Issue #22 as RESOLVED in REHEARSAL_ISSUES.md
- [ ] Update tasks.md to mark 8.1-8.4 as complete
- [ ] Move to next critical issue (Issue #5, #18, #19, or #21)

If tests fail:
- [ ] Document exact failure in REHEARSAL_ISSUES.md
- [ ] Check browser console and network tab
- [ ] Run diagnostic scripts
- [ ] Investigate root cause before proceeding
