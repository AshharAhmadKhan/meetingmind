# Fix Priority List - Easiest First

**Baseline Test Results:** 37/38 tests passing ✅

---

## PHASE 1: Quick Wins (15-30 min each)

### Fix #1: Issue #16 - Remove Mock Speaker Names ⭐ EASIEST
- **Complexity:** LOW (just delete hardcoded array)
- **File:** `frontend/src/pages/MeetingDetail.jsx`
- **Change:** Remove SPEAKERS and SENTIMENT constants
- **Test:** Open any meeting detail page
- **Estimated Time:** 10 minutes

### Fix #2: Issue #1 - Empty State Error Message
- **Complexity:** LOW (simple conditional)
- **File:** `frontend/src/pages/Dashboard.jsx`
- **Change:** Handle empty meetings array gracefully
- **Test:** View dashboard with no meetings
- **Estimated Time:** 10 minutes

### Fix #3: Issue #5 - Cannot Open Meeting Details
- **Complexity:** LOW (check routes)
- **Files:** `frontend/src/App.jsx`, `frontend/src/pages/MeetingDetail.jsx`
- **Change:** Verify route configuration
- **Test:** Click meeting card
- **Estimated Time:** 15 minutes

---

## PHASE 2: Medium Complexity (30-45 min each)

### Fix #4: Issue #19 - Leaderboard Shows Task Names
- **Complexity:** MEDIUM (data aggregation logic)
- **File:** `frontend/src/components/Leaderboard.jsx`
- **Change:** Aggregate by owner instead of task
- **Test:** View leaderboard
- **Estimated Time:** 30 minutes

### Fix #5: Issue #14 - Health Scores Too Lenient
- **Complexity:** MEDIUM (formula adjustment)
- **File:** `backend/functions/process-meeting/app.py`
- **Change:** Adjust scoring to penalize unassigned
- **Test:** Check meeting health scores
- **Estimated Time:** 20 minutes

### Fix #6: Issue #15 - ROI Ignores Unassigned
- **Complexity:** MEDIUM (calculation logic)
- **File:** `backend/functions/process-meeting/app.py`
- **Change:** Only count assigned items in value
- **Test:** Check meeting ROI
- **Estimated Time:** 20 minutes

---

## PHASE 3: Complex Fixes (45-60 min each)

### Fix #7: Issue #17 - Team Filtering Not Working ⭐ CRITICAL
- **Complexity:** MEDIUM (3 files to change)
- **Files:** 
  - `backend/functions/list-meetings/app.py`
  - `frontend/src/utils/api.js`
  - `frontend/src/pages/Dashboard.jsx`
- **Change:** Add teamId query parameter support
- **Test:** Switch teams and verify data separation
- **Estimated Time:** 45 minutes

### Fix #8: Issue #18 - Kanban Drag-and-Drop Broken
- **Complexity:** HIGH (event handlers + API)
- **File:** `frontend/src/components/KanbanBoard.jsx`
- **Change:** Fix drag handlers and API calls
- **Test:** Drag cards between columns
- **Estimated Time:** 45 minutes

### Fix #9: Issue #21 - Debt Dashboard Mock Data
- **Complexity:** HIGH (multiple charts)
- **File:** `frontend/src/pages/DebtDashboard.jsx`
- **Change:** Remove mock data, use real API data
- **Test:** View debt dashboard
- **Estimated Time:** 45 minutes

---

## PHASE 4: Backend Fixes (30 min each)

### Fix #10: Issue #6 - Resurrect Function Fails
- **Complexity:** MEDIUM (API endpoint)
- **File:** Backend resurrect endpoint
- **Change:** Fix resurrect logic
- **Test:** Click resurrect button
- **Estimated Time:** 30 minutes

---

## Testing Protocol

**Before Each Fix:**
1. Run: `python scripts/testing/comprehensive-test-suite.py`
2. Document baseline state
3. Understand affected components

**After Each Fix:**
1. Run: `python scripts/testing/comprehensive-test-suite.py`
2. Verify no regressions
3. Test specific feature manually
4. Document results

---

## Current Status

- ✅ Baseline tests run: 37/38 passing
- 🎯 Starting with: Fix #1 (Mock Speaker Names)
- 📊 Total fixes planned: 10
- ⏱️ Estimated total time: 4-5 hours
