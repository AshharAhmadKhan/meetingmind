# MeetingMind - Polish & Small Issues

**Last Updated:** February 21, 2026

This document tracks small UX issues, polish items, and minor bugs that don't break functionality but should be fixed for a better user experience.

---

## 🔴 Critical Polish (Fix Before Competition)

### 1. Token Expiration - No User Feedback
**Issue:** When Cognito token expires (after 1 hour), API returns 403 Forbidden with no user-facing error message. User sees "Failed to load meetings" with no explanation.

**Impact:** Confusing UX - users don't know why app stopped working

**Fix:**
- Detect 403 errors in frontend
- Show friendly message: "Your session expired. Please login again."
- Auto-redirect to login page
- Or implement automatic token refresh

**Effort:** 1-2 hours

**Files:**
- `frontend/src/utils/auth.js` - Add token refresh logic
- `frontend/src/utils/api.js` - Add 403 error handling

---

### 2. Graveyard Resurrection - No Success Feedback
**Issue:** After clicking "Resurrect", modal closes but no confirmation that action succeeded. User doesn't know if it worked.

**Impact:** Uncertainty - did it work?

**Fix:**
- Show toast notification: "✅ Action resurrected successfully!"
- Or keep modal open with success message for 1 second

**Effort:** 30 minutes

**Files:**
- `frontend/src/pages/Graveyard.jsx` - Add success toast

---

### 3. No Loading States on Buttons
**Issue:** When clicking buttons (Create Team, Upload Meeting, etc.), no visual feedback that action is processing.

**Impact:** Users click multiple times, causing duplicate requests

**Fix:**
- Add loading spinners to all action buttons
- Disable button while processing
- Show "Processing..." text

**Effort:** 2-3 hours (across all pages)

**Files:**
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/Teams.jsx`
- `frontend/src/pages/Graveyard.jsx`
- All other pages with action buttons

---

### 4. Graveyard Resurrection - CORS/Network Errors Not Handled
**Issue:** When resurrection fails due to network/CORS errors, shows generic "Failed to resurrect action" with no details or retry option.

**Status:** ✅ FIXED (2026-02-21)

**What was fixed:**
- Added Gateway Responses to API Gateway for DEFAULT_4XX and DEFAULT_5XX
- Now CORS headers are returned even on error responses (502, 403, etc.)
- Changed CORS origin from wildcard `*` to specific CloudFront domain (security fix)
- Browser can now show actual error messages instead of CORS blocking

**Impact:** User doesn't know why it failed or how to fix it

**Fix:**
- Catch network errors separately from API errors
- Show specific error messages:
  - Network error: "Connection lost. Check your internet."
  - CORS error: "Please refresh the page and try again."
  - API error: Show actual error message from backend
- Add "Retry" button
- Log errors to console for debugging

**Effort:** 1-2 hours

**Files:**
- `backend/template.yaml` - Added Gateway Responses (DONE)
- `frontend/src/pages/Graveyard.jsx` - Better error handling (TODO)
- `frontend/src/utils/api.js` - Error classification (TODO)

---

## 🟡 Medium Priority Polish

### 4. Meeting Upload - No Progress Indicator
**Issue:** When uploading large audio files, no progress bar. User doesn't know if upload is working or stuck.

**Impact:** Anxiety during long uploads

**Fix:**
- Add progress bar showing upload percentage
- Show estimated time remaining
- Display file size being uploaded

**Effort:** 2-3 hours

**Files:**
- `frontend/src/pages/Dashboard.jsx` - Add upload progress UI
- `frontend/src/utils/api.js` - Track upload progress

---

### 5. Kanban Drag-and-Drop - No Visual Feedback
**Issue:** When dragging action items, no visual indication of drop zones or drag state.

**Impact:** Unclear where item can be dropped

**Fix:**
- Highlight drop zones when dragging
- Show ghost/preview of item being dragged
- Add smooth animations

**Effort:** 3-4 hours

**Files:**
- `frontend/src/components/KanbanBoard.jsx` - Add drag feedback

---

### 6. Empty States - Generic Messages
**Issue:** Empty states show generic "No items" messages without helpful guidance.

**Impact:** Users don't know what to do next

**Fix:**
- Add contextual empty states with actions
- Example: "No meetings yet. Upload your first recording to get started!"
- Include relevant icon/illustration

**Effort:** 2 hours

**Files:**
- All pages with lists (Dashboard, Graveyard, Teams, etc.)

---

### 7. Error Messages - Too Technical
**Issue:** Error messages show technical details (API errors, stack traces) instead of user-friendly messages.

**Impact:** Confusing for non-technical users

**Fix:**
- Map technical errors to friendly messages
- Example: "Failed to fetch" → "Couldn't load meetings. Check your internet connection."
- Add "Try Again" button

**Effort:** 3-4 hours

**Files:**
- `frontend/src/utils/api.js` - Add error mapping
- All pages - Update error displays

---

## 🟢 Low Priority Polish (Nice to Have)

### 8. No Keyboard Shortcuts
**Issue:** All actions require mouse clicks. Power users can't use keyboard shortcuts.

**Impact:** Slower workflow for frequent users

**Fix:**
- Add common shortcuts:
  - `Ctrl+U` - Upload meeting
  - `Ctrl+K` - Open Kanban
  - `Esc` - Close modals
  - Arrow keys - Navigate lists

**Effort:** 4-5 hours

**Files:**
- Create `frontend/src/hooks/useKeyboardShortcuts.js`
- Add to all pages

---

### 9. Mobile Responsiveness - Not Optimized
**Issue:** App works on mobile but layout is cramped. Some buttons are hard to tap.

**Impact:** Poor mobile experience

**Fix:**
- Optimize layouts for mobile screens
- Increase touch target sizes
- Add mobile-specific navigation

**Effort:** 8-10 hours

**Files:**
- All frontend pages - Add responsive CSS

---

### 10. No Dark Mode
**Issue:** Only light theme available. Hard on eyes in dark environments.

**Impact:** Eye strain for some users

**Fix:**
- Add dark mode toggle
- Store preference in localStorage
- Update all color schemes

**Effort:** 6-8 hours

**Files:**
- All frontend pages - Add dark mode styles
- Create theme context

---

### 11. Action Items - No Bulk Operations
**Issue:** Can only update one action at a time. No way to mark multiple as complete.

**Impact:** Tedious for users with many actions

**Fix:**
- Add checkboxes for bulk selection
- Add "Mark all as complete" button
- Add "Delete selected" option

**Effort:** 4-5 hours

**Files:**
- `frontend/src/pages/ActionsOverview.jsx`
- `frontend/src/components/KanbanBoard.jsx`

---

### 12. No Search/Filter on Meetings List
**Issue:** Can't search or filter meetings. Hard to find specific meeting in long list.

**Impact:** Time wasted scrolling

**Fix:**
- Add search bar (search by title, date, participants)
- Add filters (date range, status, team)
- Add sorting options

**Effort:** 3-4 hours

**Files:**
- `frontend/src/pages/Dashboard.jsx` - Add search/filter UI

---

### 13. Meeting Details - No Edit Title
**Issue:** Can't edit meeting title after upload. Stuck with filename.

**Impact:** Ugly meeting names like "WhatsApp Audio 2026-02-17.mp3"

**Fix:**
- Add inline edit for meeting title
- Add "Rename" button
- Update backend to support title updates

**Effort:** 2-3 hours

**Files:**
- `frontend/src/pages/MeetingDetail.jsx` - Add edit UI
- `backend/functions/update-meeting/app.py` - Add update endpoint

---

### 14. No Undo for Destructive Actions
**Issue:** Deleting meetings/actions is permanent. No undo option.

**Impact:** Accidental deletions can't be recovered

**Fix:**
- Add "Undo" toast after delete
- Keep deleted items for 30 seconds before permanent delete
- Or add "Trash" feature with restore option

**Effort:** 4-5 hours

**Files:**
- All pages with delete actions
- Backend - Add soft delete logic

---

### 15. Team Invite - No Copy Button
**Issue:** Have to manually select and copy invite code. Error-prone.

**Impact:** Friction when sharing with team

**Fix:**
- Add "Copy to Clipboard" button
- Show success toast: "Invite code copied!"
- Add "Share via Email" option

**Effort:** 1 hour

**Files:**
- `frontend/src/pages/Teams.jsx` - Add copy button

---

## 📊 Summary

**Total Issues:** 16

**By Priority:**
- Critical: 4 issues (~6-8 hours)
- Medium: 4 issues (~10-13 hours)
- Low: 8 issues (~32-42 hours)

**Recommended for Competition:**
Fix all Critical issues (4-5 hours total) before demo.

---

## Notes

- This list will grow as we discover more issues
- Add new issues at the end of appropriate priority section
- Mark as FIXED when completed
- Update effort estimates based on actual time spent
