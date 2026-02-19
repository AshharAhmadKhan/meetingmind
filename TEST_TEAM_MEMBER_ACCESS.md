# Test Team Member Access - Step by Step

## What We Fixed
1. ✅ Fixed polling to use current teamId
2. ✅ Added cache-busting timestamps to API calls
3. ✅ Added V1/V2 visual indicators (📦 and 🚀)
4. ✅ Deployed frontend and cleared CloudFront cache

## What Should Work Now
- Main account: Can see V1 and V2 meetings separated ✅ CONFIRMED WORKING
- Team members: Should also see team meetings (needs testing)

## Testing Instructions

### Test with thehidden@gmail.com

1. **Open browser in Incognito/Private mode** (to avoid cache issues)
2. Go to: https://dcfx593ywvy92.cloudfront.net
3. Login as: `thehiddenif@gmail.com`
4. Check team selector - should show:
   - 📋 Personal (Just Me)
   - 📦 Project V1 - Legacy (3 members)
   - 🚀 Project V2 - Active (3 members)

5. **Select "📦 Project V1 - Legacy"**
   - Expected: 3 meetings (V1 Meeting 1, 2, 3)
   - If empty: Open DevTools (F12) → Console tab
   - Look for errors (especially 403 Forbidden)

6. **Select "🚀 Project V2 - Active"**
   - Expected: 3 meetings (33, V2 - The Comeback, 5666)
   - If empty: Check console for errors

7. **Select "📋 Personal (Just Me)"**
   - Expected: 0 meetings (they haven't uploaded any)

### Test with whisperbehind@gmail.com

Repeat the same steps with `whispersbehindthecode@gmail.com`

## If Still Seeing Empty State

### Check 1: Browser Console
Open DevTools (F12) → Console tab
Look for:
- ❌ Red errors
- 🟡 Yellow warnings
- Any messages about "403" or "Forbidden"

### Check 2: Network Tab
Open DevTools (F12) → Network tab
1. Select a team
2. Look for request to `/meetings?teamId=xxx&_t=timestamp`
3. Click on it
4. Check Response:
   - If 403: Team membership validation failing
   - If 200 with empty array: GSI query returning no results
   - If 200 with meetings: Frontend not displaying them

### Check 3: Hard Refresh
If using same browser session as before:
1. Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. This clears browser cache completely
3. Try selecting teams again

## Possible Issues and Solutions

### Issue: 403 Forbidden Error
**Cause:** User not recognized as team member
**Solution:** 
```bash
python scripts/testing/check-team-members.py
```
Verify the userId in the error matches the userId in team members list

### Issue: Empty array returned (200 OK)
**Cause:** Meetings don't have teamId or GSI not working
**Solution:**
```bash
python scripts/testing/check-meetings-teamid.py
```
Verify all 6 meetings have teamId

### Issue: Meetings returned but not displayed
**Cause:** Frontend rendering issue
**Solution:** Check browser console for JavaScript errors

## Expected API Responses

### When selecting V1 team:
```json
{
  "meetings": [
    {"title": "V1 Meeting 1: The Kickoff", "status": "DONE", ...},
    {"title": "V1 Meeting 2: The Cracks", "status": "DONE", ...},
    {"title": "V1 Meeting 3: The Quiet Funeral", "status": "DONE", ...}
  ]
}
```

### When selecting V2 team:
```json
{
  "meetings": [
    {"title": "33", "status": "DONE", ...},
    {"title": "V2 - The Comeback", "status": "DONE", ...},
    {"title": "5666", "status": "DONE", ...}
  ]
}
```

### When selecting Personal:
```json
{
  "meetings": []
}
```

## Report Back

Please test and report:
1. ✅ or ❌ for thehidden account
2. ✅ or ❌ for whisperbehind account
3. Any error messages from console
4. Screenshots of Network tab if issues persist

## Next Steps

If tests pass:
- Move to fixing other critical issues (Kanban, Leaderboard, Debt Dashboard)

If tests fail:
- Share console errors
- Share network tab responses
- We'll debug the specific issue
