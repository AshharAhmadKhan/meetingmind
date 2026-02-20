# Issue Priority Plan - Fix Order

## Category A: Can Fix with Existing Data (Fix These First)

These issues can be fixed and tested with the current 6 meetings without re-recording audio.

### EASIEST FIXES (Frontend Only - 15-30 min each)

#### 1. Issue #1 (LOW) - Empty Dashboard Shows Error ⭐ EASIEST
**Severity:** LOW (cosmetic)  
**Effort:** 5 minutes  
**Fix:** Update Dashboard.jsx to show proper empty state message  
**Test:** Clear all meetings, reload page  
**Why Easy:** Simple conditional rendering change

#### 2. Issue #16 (HIGH) - Mock Speaker Names ⭐ EASY
**Severity:** HIGH (demo blocker)  
**Effort:** 10 minutes  
**Fix:** Remove hardcoded speaker names from MeetingDetail.jsx  
**Test:** Open any meeting detail page  
**Why Easy:** Just remove mock data, display real data

#### 3. Issue #19 (HIGH) - Leaderboard Shows Task Names ⭐ EASY
**Severity:** HIGH (feature broken)  
**Effort:** 15 minutes  
**Fix:** Change Leaderboard.jsx to aggregate by owner instead of task  
**Test:** View dashboard leaderboard  
**Why Easy:** Simple data aggregation logic change

### MEDIUM FIXES (Frontend + Some Logic - 30-60 min each)

#### 4. Issue #21 (HIGH) - Debt Dashboard Mock Data ⭐ MEDIUM
**Severity:** HIGH (demo blocker)  
**Effort:** 45 minutes  
**Fix:** Replace hardcoded charts in DebtDashboard.jsx with real calculations  
**Test:** View debt dashboard  
**Why Medium:** Need to implement real chart data calculations

#### 5. Issue #18 (HIGH) - Kanban Drag-and-Drop Broken ⭐ MEDIUM
**Severity:** HIGH (core feature broken)  
**Effort:** 45 minutes  
**Fix:** Fix drag handlers in KanbanBoard.jsx  
**Test:** Try dragging cards between columns  
**Why Medium:** Need to debug event handlers and state updates

#### 6. Issue #5 (HIGH) - Cannot Open Meeting Details ⭐ MEDIUM
**Severity:** HIGH (demo blocker)  
**Effort:** 30 minutes  
**Fix:** Check routes and MeetingDetail.jsx for errors  
**Test:** Click any meeting card  
**Why Medium:** Need to investigate why navigation fails

### HARDER FIXES (Backend Changes - 60+ min each)

#### 7. Issue #6 (MEDIUM) - Resurrect Function Fails
**Severity:** MEDIUM (feature broken)  
**Effort:** 60 minutes  
**Fix:** Check resurrect API endpoint and error handling  
**Test:** Click resurrect on graveyard item  
**Why Hard:** Backend API debugging required

#### 8. Issue #14 (MEDIUM) - Health Scores Too Lenient
**Severity:** MEDIUM (scoring accuracy)  
**Effort:** 45 minutes  
**Fix:** Adjust scoring formula in process-meeting Lambda  
**Test:** Check V2 meeting health scores  
**Why Hard:** Need to redeploy Lambda and recalculate

#### 9. Issue #15 (MEDIUM) - ROI Doesn't Account for Unassigned
**Severity:** MEDIUM (metric accuracy)  
**Effort:** 45 minutes  
**Fix:** Adjust ROI calculation in process-meeting Lambda  
**Test:** Check V2 meeting ROI  
**Why Hard:** Need to redeploy Lambda and recalculate

### COSMETIC FIXES (Low Priority - 15-30 min each)

#### 10. Issue #2 (LOW) - Cannot See Invite Code After Creation
**Severity:** MEDIUM (usability)  
**Effort:** 30 minutes  
**Fix:** Add "View Code" button in team management  
**Test:** Create team, try to view code later  
**Why Low:** Workaround exists (create new team)

#### 11. Issue #20 (MEDIUM) - Graveyard Has 13 Items (Expected 11)
**Severity:** MEDIUM (data accuracy)  
**Effort:** 30 minutes  
**Fix:** Check graveyard query logic, clean test data  
**Test:** View graveyard  
**Why Low:** Not blocking demo

---

## Category B: Requires New Audio Recordings (Fix After Category A)

These issues cannot be fixed with current data because all V2 meetings have unassigned tasks.

#### 12. Issue #9 (CRITICAL) - Single-Voice Recordings Break Owner Assignment
**Severity:** CRITICAL (demo blocker)  
**Effort:** 2-3 hours (recording + processing)  
**Fix:** Re-record with explicit name mentions OR use 3 real voices  
**Why Blocked:** Need new audio with proper speaker diarization

#### 13. Issue #3 (MEDIUM) - No Display Names (Shows Emails)
**Severity:** MEDIUM (demo blocker)  
**Effort:** 60 minutes  
**Fix:** Add name field to registration/profile  
**Why Blocked:** Even with fix, current data shows emails

#### 14. Issue #11 (LOW) - Warning System for Ambiguous Assignments
**Severity:** LOW (feature enhancement)  
**Effort:** 45 minutes  
**Fix:** Add UI warning when owner is "Unassigned"  
**Why Blocked:** Won't help current V2 meetings

#### 15. Issue #12 (MEDIUM) - No Fuzzy Name Matching
**Severity:** MEDIUM (usability)  
**Effort:** 90 minutes  
**Fix:** Implement fuzzy matching algorithm  
**Why Blocked:** Won't help current V2 meetings (all Unassigned)

#### 16. Issue #13 (MEDIUM) - No Per-Task Notifications
**Severity:** MEDIUM (missing feature)  
**Effort:** 90 minutes  
**Fix:** Send emails after meeting processing  
**Why Blocked:** Won't help current V2 meetings (no owners)

---

## Category C: Documentation/Operational (Not Bugs)

#### 17. Issue #4 (LOW) - No Admin Notifications for Signups
**Severity:** LOW (operational)  
**Effort:** 30 minutes  
**Fix:** Add admin notification to pre-signup Lambda  
**Why Low:** Operational convenience, not demo blocker

#### 18. Issue #7 (MEDIUM) - Verify Debt Dashboard Calculations
**Severity:** MEDIUM (verification)  
**Effort:** 15 minutes  
**Fix:** Manual verification of calculations  
**Why Low:** Verification task, not a bug

#### 19. Issue #8 (LOW) - Verify Duplicate Detection Threshold
**Severity:** LOW (verification)  
**Effort:** 15 minutes  
**Fix:** Test duplicate detection with known duplicates  
**Why Low:** Verification task, not a bug

#### 20. Issue #10 (MEDIUM) - Document Explicit Name Requirement
**Severity:** MEDIUM (documentation)  
**Effort:** 15 minutes  
**Fix:** Add to user guide  
**Why Low:** Documentation, not a bug

---

## Recommended Fix Order (Category A Only)

### Phase 1: Quick Wins (1-2 hours total)
1. ✅ Issue #22 - Team visibility (DONE)
2. ✅ Issue #1 - Empty state message (DONE)
3. ✅ Issue #16 - Mock speaker names / Charts restored (DONE)
4. ✅ Issue #5 - Meeting details navigation (DONE)
5. ✅ Issue #19 - Leaderboard aggregation (DONE)

### Phase 2: High-Impact Fixes (2-3 hours total) - COMPLETE
6. ✅ Issue #18 - Kanban drag-and-drop (DONE - Team member access fixed)
7. ✅ Issue #6 - Resurrect function (DONE - Team member access fixed)
8. ✅ Issue #20 - Graveyard datetime errors (DONE - Epitaph generation fixed)

### Phase 3: Backend Fixes (Next - 2-3 hours total)
9. ✅ Issue #21 - Debt dashboard real data (DONE - Backend deployed, cache cleared)
10. Issue #14 - Health score formula (45 min)
11. Issue #15 - ROI calculation (45 min)

### Phase 4: Polish (1 hour total)
12. Issue #2 - View invite code (30 min)

**Total Estimated Time:** 6-9 hours for all Category A fixes

---

## After Category A is Complete

Then we'll tackle Category B (requires new audio):
- Re-record meetings with explicit name mentions
- Process new recordings
- Verify owner assignment works
- Test leaderboard with real names
- Complete demo rehearsal

---

## Success Criteria

### Category A Complete When:
- ✅ All UI features work with existing data
- ✅ No mock/placeholder data visible
- ✅ All interactions (click, drag, navigate) work
- ✅ Calculations are accurate
- ✅ No console errors

### Ready for Category B When:
- ✅ All Category A issues resolved
- ✅ Full demo rehearsal with existing data passes
- ✅ Recording script prepared with explicit names
- ✅ Ready to record new audio

---

## Current Status

- ✅ Phase 1 Quick Wins: COMPLETE (5 issues)
- ✅ Phase 2 High-Impact Fixes: COMPLETE (4 issues)
- ⏳ Phase 3 Backend Fixes: IN PROGRESS
- 📋 3 issues in Category A remaining
- 🎤 6 issues in Category B (blocked on audio)
- 📝 4 issues in Category C (documentation)
