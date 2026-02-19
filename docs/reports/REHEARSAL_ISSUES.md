# Rehearsal Issues Tracker

**Date:** February 20, 2026  
**Purpose:** Track remaining bugs/issues found during demo rehearsal

---

## RESOLVED ISSUES ✅

### Phase 1 Quick Wins - COMPLETE
- ✅ Issue #1: Empty Dashboard Shows Error
- ✅ Issue #5: Cannot Open Meeting Details (Team member access)
- ✅ Issue #16: Mock Speaker Names / Charts
- ✅ Issue #19: Leaderboard Shows Task Names
- ✅ Issue #22: Team Members Can't See Team Meetings

---

## REMAINING ISSUES - Category A (Can Fix with Existing Data)

### Issue #2: Cannot See Team Invite Code After Creation
- **Severity:** MEDIUM (usability)
- **Description:** After clicking "Done" on team creation, invite code disappears. No way to retrieve it later.
- **Expected:** Should be able to view invite code from team settings/details page
- **Fix Required:** Add "View Invite Code" button in team management

### Issue #6: Resurrect Function Fails
- **Severity:** MEDIUM (feature broken)
- **Description:** Graveyard shows "Resurrect" button but clicking it shows "Failed to resurrect"
- **Expected:** Should be able to resurrect old action items back to active
- **Fix Required:** Check resurrect API endpoint and error handling

### Issue #18: Kanban Drag-and-Drop Completely Broken
- **Severity:** HIGH (core feature broken)
- **Description:** Cannot drag any cards on Kanban board. Cards are completely stuck in place. No drag cursor, no movement.
- **Expected:** Should be able to drag cards between columns (To Do → In Progress → Blocked → Done)
- **Impact:** Cannot demonstrate choreography, cannot update task status
- **Fix Required:** Check KanbanBoard.jsx drag handlers (onDragStart, onDragOver, onDrop)

### Issue #20: Graveyard Has 13 Items (Expected 11 for V1, 0 for V2)
- **Severity:** MEDIUM (data accuracy)
- **Description:** Graveyard shows 13 tombstones. V1 seeding created 11. Where did 2 extra come from?
- **Possible Causes:** Old test data not cleaned, duplicate items
- **Fix Required:** Check graveyard query logic, clean test data

### Issue #21: All Debt Dashboard Charts Show Mock Data
- **Severity:** HIGH (demo blocker)
- **Description:** Every chart and section on Debt Dashboard shows placeholder/mock data that doesn't change
- **Expected:** Should show real calculated data from meetings
- **Fix Required:** Check DebtDashboard.jsx for hardcoded data, implement real calculations

### Issue #14: Health Score Doesn't Penalize Unassigned Tasks Enough
- **Severity:** MEDIUM (scoring accuracy)
- **Description:** Meeting with all unassigned tasks gets 8/10 health score
- **Expected:** Unassigned tasks should heavily penalize the score (should be 4/10 or 5/10)
- **Fix Required:** Adjust health scoring algorithm in process-meeting Lambda

### Issue #15: ROI Calculation Doesn't Account for Unassigned Items
- **Severity:** MEDIUM (metric accuracy)
- **Description:** Meeting with all unassigned tasks shows +1433% ROI
- **Expected:** Unassigned items should have $0 value, ROI should be -100%
- **Fix Required:** Adjust ROI calculation in process-meeting Lambda

---

## REMAINING ISSUES - Category B (Requires New Audio Recordings)

### Issue #3: No Way to Set Display Name
- **Severity:** MEDIUM (demo blocker)
- **Description:** User accounts have no way to set/edit display name. Names show as email addresses.
- **Expected:** Should be able to set name during registration or in profile settings
- **Impact:** Leaderboard will show emails instead of "Zeeshan", "Alishba", "Aayush"
- **Fix Required:** Add name field to registration OR profile settings page

### Issue #9: Single-Voice Recordings Break Owner Assignment
- **Severity:** CRITICAL (demo blocker)
- **Description:** When one person records all voices, AI assigns tasks to "Unassigned" or task descriptions
- **Root Cause:** Transcribe uses voice characteristics for speaker diarization, not names
- **Solution:** Re-record with explicit name mentions OR use 3 real voices
- **Example:** "Zeeshan, you'll handle the repo, right?" "Yes, Zeeshan here - I'll do it by the 23rd"

### Issue #11: Warning System for Ambiguous Assignments
- **Severity:** LOW (feature enhancement)
- **Description:** Need to detect when names not mentioned in recordings
- **Fix Required:** Add UI warning when owner is "Unassigned"

### Issue #12: No Fuzzy Name Matching
- **Severity:** MEDIUM (usability)
- **Description:** "Abdul Zeeshan" won't match "Zeeshan"
- **Fix Required:** Implement fuzzy matching algorithm

### Issue #13: No Per-Task Notifications
- **Severity:** MEDIUM (missing feature)
- **Description:** Task owners don't get emails when assigned
- **Fix Required:** Send emails after meeting processing

---

## REMAINING ISSUES - Category C (Documentation/Operational)

### Issue #4: No Admin Notification for New Signups
- **Severity:** LOW (operational)
- **Description:** Admin receives no notification when new user registers
- **Workaround:** Check Cognito manually with: `python scripts/setup/approve-user.py <email>`
- **Fix Required:** Add admin notification to pre-signup Lambda

### Issue #7: Verify Debt Dashboard Calculations
- **Severity:** MEDIUM (verification)
- **Description:** Need to verify debt dashboard calculations are accurate
- **Fix Required:** Manual verification of calculations

### Issue #8: No Duplicate Detection Showing
- **Severity:** LOW (feature verification)
- **Description:** "No duplicates detected" message shows
- **Expected:** Meeting 2 has "Fix the backend setup" which is 87% similar to Meeting 1's "Handle the backend architecture"
- **Fix Required:** Verify semantic search is running and threshold is appropriate

### Issue #10: Document Explicit Name Requirement
- **Severity:** MEDIUM (documentation)
- **Description:** Users need to know to explicitly mention names in recordings
- **Fix Required:** Add to user guide

---

## PRIORITY ORDER FOR REMAINING FIXES

### Phase 2: High-Impact Fixes (Next)
1. Issue #18 - Kanban drag-and-drop (45 min)
2. Issue #21 - Debt dashboard real data (45 min)

### Phase 3: Backend Fixes
3. Issue #6 - Resurrect function (60 min)
4. Issue #14 - Health score formula (45 min)
5. Issue #15 - ROI calculation (45 min)

### Phase 4: Polish
6. Issue #2 - View invite code (30 min)
7. Issue #20 - Graveyard cleanup (30 min)

---

## NOTES

- Phase 1 Quick Wins: COMPLETE (5 issues fixed)
- Main account (itzashhar@gmail.com) intentionally NOT in teams
- All 3 test accounts successfully in both teams
- V1 data seeded correctly with teamId
- V2 data has teamId assigned
