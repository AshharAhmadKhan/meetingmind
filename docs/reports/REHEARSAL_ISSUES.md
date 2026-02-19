# Rehearsal Issues Tracker

**Date:** February 19, 2026  
**Purpose:** Track all bugs/issues found during full demo rehearsal

---

## PHASE 1: SETUP - Issues Found

### Issue 1: Empty Dashboard Shows "Failed to Load Meetings"
- **Severity:** LOW (cosmetic)
- **Description:** When tab is open for long time with no meetings uploaded, shows error message instead of empty state
- **Expected:** Should show "No meetings yet. Upload your first meeting!" message
- **Fix Required:** Update Dashboard.jsx to handle empty state gracefully

### Issue 2: Cannot See Team Invite Code After Creation
- **Severity:** MEDIUM (usability)
- **Description:** After clicking "Done" on team creation, invite code disappears. No way to retrieve it later.
- **Expected:** Should be able to view invite code from team settings/details page
- **Fix Required:** Add "View Invite Code" button in team management

### Issue 3: No Way to Set Display Name
- **Severity:** MEDIUM (demo blocker)
- **Description:** User accounts have no way to set/edit display name. Names show as email addresses.
- **Expected:** Should be able to set name during registration or in profile settings
- **Impact:** Leaderboard will show emails instead of "Zeeshan", "Alishba", "Aayush"
- **Fix Required:** Add name field to registration OR profile settings page

### Issue 4: No Admin Notification for New Signups
- **Severity:** LOW (operational)
- **Description:** When someone new signs up, admin (Ashhar) receives no notification. No way to know who tried the demo.
- **Expected:** Admin should receive email when new user registers
- **Workaround:** Check Cognito manually with: `python scripts/setup/approve-user.py <email>`
- **Fix Required:** Add admin notification to pre-signup Lambda OR disable pre-signup validation during competition

---

## PHASE 2: V1 DATA SEEDING - Issues Found

### Issue 5: Cannot Open Meeting Details ✅ RESOLVED
- **Severity:** HIGH (demo blocker)
- **Status:** ✅ FIXED (February 20, 2026)
- **Description:** Team member accounts could see meetings but clicking them returned 404 error
- **Root Cause:** get-meeting API only queried by userId (uploader), so team members couldn't access meetings
- **Fix Applied:**
  - Modified `backend/functions/get-meeting/app.py` to scan for meetings by meetingId
  - Added team membership validation before allowing access
  - Returns 403 if user is not a team member
- **Files Modified:**
  - `backend/functions/get-meeting/app.py` - Added fallback scan for team members
- **Verification:** ✅ Team members can now click and view meeting details

### Issue 6: Resurrect Function Fails
- **Severity:** MEDIUM (feature broken)
- **Description:** Graveyard shows "Resurrect" button but clicking it shows "Failed to resurrect"
- **Expected:** Should be able to resurrect old action items back to active
- **Fix Required:** Check resurrect API endpoint and error handling

### Issue 7: Debt Dashboard Shows Mock/Placeholder Data
- **Severity:** MEDIUM (data accuracy)
- **Description:** Debt dashboard shows:
  - 8-week trend graph (possibly mock data)
  - Completion rate chart
  - Action summary
  - Quick wins section with "Assign owner" suggestions
- **Question:** Is this real calculated data or placeholder UI?
- **Verify:** Check if data matches actual V1 meetings (3 meetings, $825 total)
- **Fix Required:** If mock data, replace with real calculations

### Issue 8: No Duplicate Detection Showing
- **Severity:** LOW (feature verification)
- **Description:** "No duplicates detected" message shows
- **Expected:** Meeting 2 has "Fix the backend setup" which is 87% similar to Meeting 1's "Handle the backend architecture" - should be flagged as Chronic Blocker
- **Question:** Is duplicate detection working or is the similarity threshold too high?
- **Fix Required:** Verify semantic search is running and threshold is appropriate (should be ~85%)

---

## PHASE 3: AUDIO UPLOAD - Issues Found

### Issue 9: Single-Voice Recordings Break Owner Assignment
- **Severity:** CRITICAL (demo blocker)
- **Description:** When one person records all voices in a meeting, Transcribe labels everything as "Speaker 0". The AI cannot distinguish between different people, so it assigns all tasks to "Speaker 0" or "Unassigned".
- **Impact:** 
  - Leaderboard will show only 1 person or nobody
  - Choreography (Zeeshan 100%, Alishba 60%, Aayush 67%) is impossible
  - Demo story breaks completely
- **Root Cause:** Transcribe uses voice characteristics for speaker diarization, not names
- **Solution 1 (RECOMMENDED):** Explicitly mention names in recordings:
  - "Zeeshan, you'll handle the repo, right?"
  - "Yes, Zeeshan here - I'll do it by the 23rd"
  - "Alishba, can you do wireframes?"
  - "Alishba speaking - I'll have them done by the 24th"
- **Solution 2:** Have 3 different people record (Zeeshan, Alishba, Aayush with real voices)
- **Solution 3:** Manually edit action items after upload to assign correct owners
- **Fix Required:** Re-record with explicit name mentions OR use real 3-person recordings

### Issue 10: AI Owner Extraction Relies on Context Clues
- **Severity:** MEDIUM (accuracy concern)
- **Description:** Bedrock extracts owners by analyzing phrases like "I'll do X" or "Person Y will handle Z". If the meeting doesn't explicitly state names, tasks get assigned to "Unassigned".
- **Expected:** AI should be smart enough to infer from context
- **Reality:** AI needs explicit mentions for accuracy
- **Best Practice:** Always say names when assigning tasks in meetings
- **Documentation:** Add this to user guide - "For best results, explicitly mention names when assigning tasks"

---

## PHASE 4: CHOREOGRAPHY - Issues Found

(To be filled as we progress)

---

## PHASE 5: VERIFICATION - Issues Found

(To be filled as we progress)

---

## PHASE 6: VIDEO REHEARSAL - Issues Found

(To be filled as we progress)

---

## CRITICAL FIXES NEEDED BEFORE REAL DEMO

### MUST FIX (Demo Blockers)
1. **Issue 9 (Single-Voice Recordings)** - Need 3 real voices OR explicit name mentions in script
2. **Issue 3 (Display Names)** - Leaderboard needs proper names, not emails
3. **Issue 5 (Meeting Details)** - Cannot view meeting details, core feature broken

### SHOULD FIX (Important Features)
4. **Issue 13 (Per-Task Notifications)** - Task owners should get notified when assigned
5. **Issue 12 (Name Matching)** - Fuzzy matching for "Abdul Zeeshan" vs "Zeeshan"
6. Issue 6 (Resurrect Function) - Feature advertised but doesn't work
7. Issue 7 (Debt Dashboard Data) - Verify real data vs mock data
8. Issue 8 (Duplicate Detection) - Should show chronic blocker

### DOCUMENT & ACCEPT (Reasonable Limitations)
9. **Issue 11 (Explicit Names Required)** - Document as best practice, add warning system
10. Issue 2 (Invite Code) - Makes team management easier
11. Issue 4 (Admin Notifications) - Operational convenience
12. Issue 1 (Empty State) - Cosmetic only

---

## HOW TO APPROVE NEW USERS (For AI Agent Handbook)

When someone new signs up and gets "Thanks for registering, we will verify your account":

```powershell
# Get their email from them directly, then run:
python scripts/setup/approve-user.py <their-email@example.com>

# This will:
# 1. Verify their email in SES
# 2. Enable their Cognito account
# 3. Send them a welcome email
# 4. They can then log in
```

**For Competition:** Consider disabling pre-signup validation entirely during voting period (March 13-20) to maximize engagement.

---

## ISSUE CATEGORIZATION

### Category A: Can Test with Current Data (Fix Without Re-recording)

These issues can be fixed and tested with the existing 6 meetings (3 V1 + 3 V2):

1. **Issue #17 (CRITICAL)** - Team filtering not working
   - Fix: Add teamId filtering to list-meetings API + frontend
   - Test: Switch teams and verify data separation

2. **Issue #5 (HIGH)** - Cannot open meeting details
   - Fix: Check routes and MeetingDetail.jsx
   - Test: Click any meeting card

3. **Issue #16 (HIGH)** - Mock speaker names (Ashhar, Priya, Zara)
   - Fix: Remove hardcoded SPEAKERS array in MeetingDetail.jsx
   - Test: Open any meeting detail page

4. **Issue #18 (HIGH)** - Kanban drag-and-drop broken
   - Fix: Check drag handlers in KanbanBoard.jsx
   - Test: Try dragging cards

5. **Issue #19 (HIGH)** - Leaderboard shows task names not people
   - Fix: Aggregate by owner instead of task in Leaderboard.jsx
   - Test: View leaderboard

6. **Issue #21 (HIGH)** - Debt dashboard shows mock data
   - Fix: Remove hardcoded charts in DebtDashboard.jsx
   - Test: View debt dashboard

7. **Issue #6 (MEDIUM)** - Resurrect function fails
   - Fix: Check resurrect API endpoint
   - Test: Click resurrect on graveyard item

8. **Issue #14 (MEDIUM)** - Health scores too lenient
   - Fix: Adjust scoring formula in process-meeting
   - Test: Check V2 meeting health scores (should be lower)

9. **Issue #15 (MEDIUM)** - ROI doesn't account for unassigned
   - Fix: Adjust ROI calculation in process-meeting
   - Test: Check V2 meeting ROI (should be -100%)

10. **Issue #1 (LOW)** - Empty state shows error
    - Fix: Handle empty array in Dashboard.jsx
    - Test: Clear all meetings and reload

11. **Issue #2 (LOW)** - Cannot see invite code after creation
    - Fix: Add "View Code" button in team management
    - Test: Create team and try to view code later

### Category B: Requires New Recordings (Cannot Test with Current Data)

These issues require re-recording with explicit name mentions:

12. **Issue #9 (CRITICAL)** - All V2 tasks assigned to "Unassigned"
    - Problem: Single-voice recordings don't work
    - Solution: Re-record with explicit names OR use 3 real voices
    - Cannot fix with current data

13. **Issue #3 (MEDIUM)** - No display names (shows emails)
    - Problem: No profile settings to set names
    - Solution: Add name field to registration/profile
    - Workaround: Use account emails that look like names

14. **Issue #11 (LOW)** - Warning system for ambiguous assignments
    - Problem: Need to detect when names not mentioned
    - Solution: Add UI warning when owner is "Unassigned"
    - Can implement but won't help current V2 meetings

15. **Issue #12 (MEDIUM)** - No fuzzy name matching
    - Problem: "Abdul Zeeshan" won't match "Zeeshan"
    - Solution: Implement fuzzy matching algorithm
    - Won't help current V2 meetings (all Unassigned)

16. **Issue #13 (MEDIUM)** - No per-task notifications
    - Problem: Task owners don't get emails
    - Solution: Send emails after meeting processing
    - Won't help current V2 meetings (no owners assigned)

### Category C: Documentation/Operational (Not Bugs)

17. **Issue #4 (LOW)** - No admin notifications for signups
18. **Issue #7 (MEDIUM)** - Verify debt dashboard calculations
19. **Issue #8 (LOW)** - Verify duplicate detection threshold
20. **Issue #10 (MEDIUM)** - Document explicit name requirement
21. **Issue #20 (MEDIUM)** - Graveyard has 13 items (expected 11)

---

## WHY TEAM MEMBERS CAN'T SEE MEETINGS

**Root Cause:** Meetings are stored by `userId`, not `teamId`

**Current Architecture:**
- DynamoDB partition key: `userId` (the uploader)
- Meetings belong to the person who uploaded them
- Team members can't query meetings by teamId
- No GSI (Global Secondary Index) for teamId

**What This Means:**
- Only Zeeshan (uploader) can see all 6 meetings
- Alishba and Aayush see ZERO meetings (they didn't upload any)
- Team selector doesn't work because there's no way to query by team

**Fix Required:**
1. Add GSI: `teamId-createdAt-index` to DynamoDB table
2. Update list-meetings API to query by teamId using GSI
3. Update frontend to pass selectedTeamId to API

**Data Correction Needed:**
- V1 meetings: Already have `teamId` (seeding script added it)
- V2 meetings: Missing `teamId` (uploaded before team selector existed)
- Need to manually add `teamId` to V2 meetings in DynamoDB

---

## V1 vs V2 DATA SEPARATION

**Current State:**
- V1 meetings (3): Have `teamId` = "Project V1 - Legacy"
- V2 meetings (3): Missing `teamId` (need to add manually)

**Expected State:**
- V1 meetings: `teamId` = "Project V1 - Legacy" team ID
- V2 meetings: `teamId` = "Project V2 - Active" team ID

**Action Required:**
1. Get team IDs from DynamoDB teams table
2. Update V2 meetings to add correct `teamId`
3. Verify team filtering works after fixes

---

## NOTES

- Main account (itzashhar@gmail.com) intentionally NOT in teams - correct per DEMO_VISION.md
- All 3 test accounts successfully in both teams
- Phase 1 setup: COMPLETE with known issues
- V1 data seeded correctly with teamId
- V2 data missing teamId (uploaded from main account before team selector)



### Issue 11: Speaker Identity Requires Explicit Name Mentions (DOCUMENTED LIMITATION)
- **Severity:** LOW (acceptable limitation, needs documentation)
- **Description:** MeetingMind cannot automatically map speaker voices to team member names. Users must explicitly mention names when assigning tasks.
- **Why This Is Acceptable:**
  - This is how ALL meeting tools work (Otter.ai, Fireflies, etc.)
  - In real meetings, people DO say names: "Zeeshan, can you handle X?"
  - AI cannot read minds - it needs explicit context
  - This is a reasonable expectation to set with users
- **Best Practice Documentation:**
  - "For accurate task assignment, explicitly mention names when assigning work"
  - "Say: 'Zeeshan, you'll handle the repo, right?' instead of 'Can you do it?'"
  - "This helps the AI correctly attribute tasks to team members"
- **Warning System (NEW FEATURE IDEA):**
  - When AI detects ambiguous assignments ("I'll do it" without name context)
  - Show warning: "⚠️ Name not explicitly mentioned - assignment may be inaccurate"
  - Suggest: "Edit this action item to assign to the correct person"
- **Fix Required:** Add warning system to UI when owner is ambiguous

### Issue 12: Name Matching Is Exact (No Fuzzy Matching)
- **Severity:** MEDIUM (usability issue)
- **Description:** If meeting says "Abdul Zeeshan will do X" but account name is "Zeeshan", the system won't match them. Owner is stored as plain text "Abdul Zeeshan" which doesn't match account "Zeeshan".
- **Impact:**
  - Leaderboard won't attribute tasks correctly
  - Tasks show as assigned but don't count toward user's completion rate
  - Confusing for users who use full names vs nicknames
- **Current Behavior:**
  - AI extracts: `owner: "Abdul Zeeshan"` (exact text from transcript)
  - System stores: `owner: "Abdul Zeeshan"` (no validation)
  - Leaderboard looks for: exact match with account display names
  - Result: No match → task doesn't appear on leaderboard
- **Fix Required:** 
  - Option A: Fuzzy name matching (match "Abdul Zeeshan" to "Zeeshan")
  - Option B: Validate extracted names against team members and suggest corrections
  - Option C: Allow users to edit owner after extraction
- **Workaround:** Use consistent names in meetings that match account names exactly

### Issue 13: No Per-Task Assignment Notifications
- **Severity:** MEDIUM (missing feature)
- **Description:** When AI assigns a task to someone (e.g., "Zeeshan"), that person receives NO notification. It's just text in the database.
- **Current Behavior:**
  - Meeting uploader gets email: "Meeting processed, 5 action items created"
  - Task owners get: NOTHING
  - They only see their tasks if they log in and check dashboard
- **Expected Behavior:**
  - When "Zeeshan" is assigned a task, Zeeshan should get email:
    - "You've been assigned: Set up the repo (Due: Feb 23)"
    - Link to task details
  - This is how project management tools work (Asana, Jira, etc.)
- **Impact:**
  - Team members don't know they've been assigned work
  - Reduces accountability (the core value prop!)
  - Requires manual communication outside the tool
- **Fix Required:** 
  - After meeting processing, extract unique owners
  - Look up their email addresses from team membership
  - Send individual emails: "You've been assigned X tasks from meeting Y"
  - Include task list with deadlines
- **Workaround:** Meeting uploader manually notifies team members


### Issue 14: Health Score Doesn't Penalize Unassigned Tasks Enough
- **Severity:** MEDIUM (scoring accuracy)
- **Description:** Meeting with 3 decisions and 4 action items gets 8/10 health score, even though ALL action items are "Unassigned"
- **Expected:** Unassigned tasks should heavily penalize the score (should be 4/10 or 5/10)
- **Current Formula:** Seems to weight decisions + action count, but not ownership
- **Impact:** Misleading health scores make bad meetings look good
- **Fix Required:** Adjust health scoring algorithm to heavily penalize unassigned items
- **Suggested Formula:**
  ```
  base_score = (decisions * 20) + (actions * 10)
  ownership_penalty = (unassigned_count / total_actions) * 50
  final_score = max(0, base_score - ownership_penalty)
  ```

### Issue 15: ROI Calculation Doesn't Account for Unassigned Items
- **Severity:** MEDIUM (metric accuracy)
- **Description:** Meeting with all unassigned tasks shows +1433% ROI, suggesting high value generation. But unassigned tasks have zero real value.
- **Current Behavior:**
  - Cost: $225 (3 people × 1 hour × $75)
  - Value: $3,440 (4 items × $860 estimated value each)
  - ROI: +1,433%
- **Problem:** Unassigned items should have $0 value, not $860
- **Expected ROI:** -100% (cost $225, value $0, total waste)
- **Impact:** Misleading metrics make failed meetings look successful
- **Fix Required:** 
  - Only count assigned items toward value
  - Unassigned items = $0 value
  - Formula: `value = (assigned_count × $860) + (completed_count × bonus)`

### Issue 16: Speaker Names Show Mock Data ✅ RESOLVED (Replaced with Conditional Charts)
- **Severity:** HIGH (demo blocker)
- **Status:** ✅ FIXED (February 20, 2026)
- **Description:** Meeting detail page showed hardcoded mock speaker names. Charts were removed to fix this.
- **User Feedback:** User prefers having charts when there's data to show
- **Fix Applied:**
  - Restored Task Distribution chart with conditional logic
  - Chart only shows if there are assigned owners (not "Unassigned")
  - V1 meetings show the chart (have assigned owners)
  - V2 meetings don't show it (all unassigned)
  - AI Analysis section always shows
- **Files Modified:**
  - `frontend/src/pages/MeetingDetail.jsx` - Added conditional Task Distribution chart
- **Verification:** ✅ Charts display when there's data, hidden when there isn't


---

## PHASE 5: SYSTEMATIC TESTING - Issues Found

### Issue 17: Team Selector Doesn't Filter Data ✅ RESOLVED
- **Severity:** CRITICAL (demo blocker)
- **Status:** ✅ FIXED (Query 14)
- **Description:** Switching between teams showed identical data everywhere. Team selector appeared to do nothing.
- **Root Causes:**
  1. V2 meetings missing teamId (uploaded before team selector existed)
  2. Backend didn't validate team membership (security issue)
  3. Team members couldn't see meetings (data model issue)
- **Fix Applied:**
  1. ✅ Added teamId to 3 V2 meetings via data migration script
  2. ✅ Added team membership validation to 3 Lambda functions
  3. ✅ All 6 meetings now have teamId
  4. ✅ Security: Users can only access teams they're members of
- **Files Modified:**
  - `backend/functions/list-meetings/app.py` - Team validation
  - `backend/functions/get-all-actions/app.py` - Team validation
  - `backend/functions/get-debt-analytics/app.py` - Team validation
  - `scripts/data/add-teamid-to-meetings.py` - Data migration
- **Test Results:** 37/38 tests passing (no regressions)
- **Deployment:** ✅ All 18 Lambda functions deployed
- **Documentation:** `docs/reports/TEAM_FILTERING_FIX.md`

### Issue 18: Kanban Drag-and-Drop Completely Broken
- **Severity:** HIGH (core feature broken)
- **Description:** Cannot drag any cards on Kanban board. Cards are completely stuck in place. No drag cursor, no movement.
- **Expected:** Should be able to drag cards between columns (To Do → In Progress → Blocked → Done)
- **Impact:** 
  - Cannot demonstrate choreography (Zeeshan 100%, Alishba 60%)
  - Cannot update task status
  - Core feature advertised but doesn't work
- **Possible Causes:**
  - Drag event handlers not attached
  - CSS preventing drag (pointer-events: none?)
  - Update-action API failing silently
- **Fix Required:** 
  - Check KanbanBoard.jsx drag handlers (onDragStart, onDragOver, onDrop)
  - Check update-action API endpoint
  - Test in browser console for errors

### Issue 19: Leaderboard Shows Task Names Instead of People
- **Severity:** HIGH (feature broken)
- **Description:** Leaderboard displays task names ("handle file testing", "final testing", "write article draft") instead of team member names with completion rates
- **Expected:** Should show:
  ```
  🥇 Zeeshan  100%  (5/5)  ⚡🏆
  🥈 Alishba   60%  (3/5)
  🥉 Aayush    67%  (2/3)
  ```
- **Current:** Shows random task names as if they were people
- **Impact:** Core accountability feature is completely broken and confusing
- **Root Cause:** Leaderboard.jsx is aggregating by task name instead of owner name
- **Fix Required:** Check Leaderboard.jsx data aggregation logic

### Issue 20: Graveyard Has 13 Items (Expected 11 for V1, 0 for V2)
- **Severity:** MEDIUM (data accuracy)
- **Description:** Graveyard shows 13 tombstones. V1 seeding created 11. Where did 2 extra come from?
- **Possible Causes:**
  - V2 unassigned tasks going to graveyard immediately (shouldn't happen - they're new)
  - Old test data not cleaned
  - Duplicate items
  - Team filtering not working (Issue #17)
- **Fix Required:** 
  - Check graveyard query logic (should only show items >30 days old)
  - Clean test data
  - Verify team filtering

### Issue 21: All Debt Dashboard Charts Show Mock Data
- **Severity:** HIGH (demo blocker)
- **Description:** Every chart and section on Debt Dashboard shows placeholder/mock data that doesn't change:
  - 8-week trend graph (static mock chart)
  - Completion rate chart (static mock chart)
  - Action summary (fake numbers)
  - Quick wins section (generic suggestions)
- **Expected:** Should show real calculated data:
  - Trend: actual debt over time from meetings
  - Completion: real completion rates
  - Summary: actual action counts
  - Quick wins: real suggestions based on data
- **Impact:** Cannot demonstrate meeting debt feature (a key differentiator)
- **Root Cause:** 
  - DebtDashboard.jsx using hardcoded mock data
  - OR get-debt-analytics API returning mock data
  - OR API not implemented fully
- **Fix Required:** 
  - Check DebtDashboard.jsx for hardcoded data
  - Check get-debt-analytics API implementation
  - Implement real calculations if missing

---

## PHASE 6: DEMO VIDEO REHEARSAL - Skipped

Cannot proceed with demo video rehearsal until critical issues are fixed. Team filtering (Issue #17) must work before any demo is possible.



---

## NEW ISSUE DISCOVERED (February 20, 2026)

### Issue 22: Team Members Can't See Team Meetings ✅ RESOLVED
- **Severity:** CRITICAL (demo blocker) 
- **Status:** ✅ FIXED
- **Description:** When "thehidden" or "whisperbehind" accounts select a team, they see empty state instead of team meetings. Only the main account (uploader) can see meetings.
- **Root Cause Analysis:**
  1. ✅ Backend: list-meetings API correctly queries by teamId using GSI
  2. ✅ Frontend: Dashboard passes teamId to API correctly
  3. ✅ Data: All 6 meetings have teamId assigned
  4. ✅ **FIXED: Polling interval now uses current teamId**
  5. ✅ **FIXED: Added cache-busting timestamps**
- **Fix Applied:**
  1. Combined useEffect hooks so polling uses current selectedTeamId
  2. Added `_t: Date.now()` cache-busting to API calls
  3. Added visual indicators (📦 V1, 🚀 V2, 📋 Personal)
  4. Deployed frontend and cleared CloudFront cache
- **Verification:** ✅ Tested with team member accounts - all can see team meetings
- **Files Modified:**
  - `frontend/src/pages/Dashboard.jsx` - Fixed polling
  - `frontend/src/utils/api.js` - Added cache-busting
  - `frontend/src/components/TeamSelector.jsx` - Added emojis
- **Verification:** ✅ Tested with team member accounts - all can see team meetings
- **Files Modified:**
  - `frontend/src/pages/Dashboard.jsx` - Fixed polling
  - `frontend/src/utils/api.js` - Added cache-busting
  - `frontend/src/components/TeamSelector.jsx` - Added emojis

---

## SPEC CREATED

A new spec has been created to fix this issue:
- **Location:** `.kiro/specs/meetingmind-7day-transformation/`
- **New Requirement:** Day 8 - Team Meeting Visibility Fix
- **Tasks Added:** 8.1 through 8.4 in tasks.md
- **Priority:** CRITICAL - must be fixed before demo

