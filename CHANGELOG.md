# MeetingMind - Changelog

## 2026-02-21 - CORS & Error Handling Fixes

### Fixed Issues

#### 1. CORS Wildcard Security Issue (CRITICAL)
**Issue:** API Gateway was configured with `AllowOrigin: '*'` allowing any website to call the API.

**Fix:**
- Changed CORS origin from wildcard to specific CloudFront domain: `https://dcfx593ywvy92.cloudfront.net`
- Added Gateway Responses for DEFAULT_4XX and DEFAULT_5XX to ensure CORS headers are returned even on error responses
- This fixes both the security vulnerability AND the CORS blocking issue on errors

**Impact:** 
- Security: Prevents unauthorized websites from calling the API
- UX: Browser can now show actual error messages instead of CORS errors

**Files Changed:**
- `backend/template.yaml` - Updated API Gateway CORS configuration

**Deployed:** ✅ Backend deployed at 20:21 IST

---

#### 2. Graveyard Resurrection - Better Error Messages
**Issue:** When resurrection failed, showed generic "Failed to resurrect action" with no details.

**Fix:**
- Added specific error messages for different failure scenarios:
  - 401: "Your session expired. Please logout and login again."
  - 403: "Not authorized to update this action."
  - 404: "Action item not found."
  - Network errors: "Connection lost. Check your internet and try again."
- Added success alert: "✅ Action resurrected successfully! It will appear in your Kanban board."
- Log errors to console for debugging

**Impact:** Users now know exactly why resurrection failed and what to do about it.

**Files Changed:**
- `frontend/src/pages/Graveyard.jsx` - Improved error handling in resurrect() function

**Deployed:** ✅ Frontend deployed at 20:28 IST, CloudFront invalidated

---

### Testing Instructions

1. **Test CORS fix:**
   - Open browser DevTools Network tab
   - Try to resurrect an action with expired token
   - You should now see the actual error (401 Unauthorized) instead of CORS error
   - Error response should include `Access-Control-Allow-Origin` header

2. **Test error messages:**
   - Try resurrecting with expired token → Should show "Your session expired" message
   - Logout and login to get fresh token
   - Try resurrecting again → Should show success alert

3. **Test resurrection functionality:**
   - Login with fresh credentials
   - Go to Graveyard page
   - Click "Resurrect" on any item
   - Update owner and deadline
   - Click "Resurrect" button
   - Should see success alert
   - Item should disappear from graveyard
   - Item should appear in Kanban board under "To Do"

---

### Next Steps

**Remaining Critical Issues (from POLISH_ISSUES.md):**

1. **Token Expiration - No User Feedback** (1-2 hours)
   - Implement automatic token refresh
   - Or show friendly message before token expires
   - Auto-redirect to login when token expires

2. **No Loading States on Buttons** (2-3 hours)
   - Add loading spinners to all action buttons
   - Disable buttons while processing
   - Prevents duplicate requests

3. **Graveyard Resurrection - No Success Feedback** (30 minutes)
   - ✅ DONE - Added success alert
   - Could improve with toast notification instead of alert

**Quick Wins (from ISSUES_PRIORITIZED.md):**

1. ✅ CORS wildcard (5 min) - DONE
2. Failing test (1-2 hours)
3. S3 lifecycle policies (10 min)
4. Extract magic numbers to constants (2 hours)
5. Add DLQ monitoring (1 hour)
6. Cache health scores (2-3 hours)

---

### Notes

- The resurrection feature itself was working correctly all along
- The issue was CORS blocking the error messages
- Now that CORS is fixed, users can see the real errors (token expiration)
- Next priority: Implement automatic token refresh to prevent this UX issue
