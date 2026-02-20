# Issue Categorization & Action Plan

**Date:** February 20, 2026  
**Purpose:** Categorize all 21 issues by testability and priority

---

## CATEGORY A: Can Fix & Test with Current Data ✅

These issues can be fixed and tested with existing 6 meetings (3 V1 + 3 V2) without re-recording:

### CRITICAL (Must Fix First)

1. **Issue #17 - Team Filtering Not Working**
   - **Problem:** Team selector shows identical data for both teams
   - **Impact:** Demo story impossible - can't show V1 vs V2 contrast
   - **Fix:** 
     - Backend: Add teamId query parameter to `list-meetings` API
     - Frontend: Update `listMeetings(teamId)` in api.js
     - Frontend: Pass selectedTeamId in Dashboard.jsx
   - **Test:** Switch teams and verify data separation
   - **Complexity:** LOW (GSI already exists, just need to use it)

### HIGH Priority

2. **Issue #5 - Cannot Open Meeting Details**
   - **Problem:** Clicking meeting cards doesn't navigate to detail page
   - **Fix:** Check App.jsx routes and MeetingDetail.jsx for errors
   - **Test:** Click any meeting card
   - **Complexity:** LOW

3. **Issue #16 - Mock Speaker Names**
   - **Problem:** Shows "Ashhar, Priya, Zara" instead of real data
   - **Fix:** Remove hardcoded SPEAKERS array in MeetingDetail.jsx
   - **Test:** Open any meeting detail page
   - **Complexity:** LOW

4. **Issue #18 - Kanban Drag-and-Drop Broken**
   - **Problem:** Cannot drag cards between columns
   - **Fix:** Check drag handlers in KanbanBoard.jsx
   - **Test:** Try dragging cards on Kanban board
   - **Complexity:** MEDIUM

5. **Issue #19 - Leaderboard Shows Task Names**
   - **Problem:** Displays task names instead of people names
   - **Fix:** Aggregate by owner instead of task in Leaderboard.jsx
   - **Test:** View leaderboard
   - **Complexity:** LOW

6. **Issue #21 - Debt Dashboard Mock Data**
   - **Problem:** All charts show hardcoded placeholder data
   - **Fix:** Remove mock data, use real calculations from API
   - **Test:** View debt dashboard
   - **Complexity:** MEDIUM

### MEDIUM Priority

7. **Issue #6 - Resurrect Function Fails**
   - **Problem:** "Failed to resurrect" error when clicking button
   - **Fix:** Check resurrect API endpoint and error handling
   - **Test:** Click resurrect on graveyard item
   - **Complexity:** LOW

8. **Issue #14 - Health Scores Too Lenient**
   - **Problem:** Meetings with all unassigned tasks get 8/10 score
   - **Fix:** Adjust scoring formula to heavily penalize unassigned
   - **Test:** Check V2 meeting health scores (should be 4/10 or lower)
   - **Complexity:** LOW

9. **Issue #15 - ROI Ignores Unassigned Items**
   - **Problem:** Shows +1433% ROI despite zero real value
   - **Fix:** Only count assigned items toward value calculation
   - **Test:** Check V2 meeting ROI (should be -100%)
   - **Complexity:** LOW

### LOW Priority

10. **Issue #1 - Empty State Shows Error**
    - **Problem:** Shows "Failed to load meetings" instead of empty state
    - **Fix:** Handle empty array gracefully in Dashboard.jsx
    - **Test:** Clear all meetings and reload
    - **Complexity:** LOW

11. **Issue #2 - Cannot View Invite Code**
    - **Problem:** Code disappears after clicking "Done"
    - **Fix:** Add "View Code" button in team management
    - **Test:** Create team and try to view code later
    - **Complexity:** LOW

---

## CATEGORY B: Requires New Recordings ❌

These issues CANNOT be fixed with current data - require re-recording with explicit name mentions:

### CRITICAL (Blocks Demo)

12. **Issue #9 - All V2 Tasks Unassigned**
    - **Problem:** Single-voice recordings assign everything to "Unassigned"
    - **Root Cause:** Transcribe uses voice characteristics, not names
    - **Solution Options:**
      - A) Re-record with explicit names: "Zeeshan, you'll do X"
      - B) Use 3 real voices (Zeeshan, Alishba, Aayush)
      - C) Manually edit action items in DynamoDB (temporary)
    - **Cannot fix with current data:** YES
    - **Blocks:** Leaderboard, choreography, entire demo narrative

### MEDIUM Priority (Nice to Have)

13. **Issue #3 - No Display Names**
    - **Problem:** Leaderboard shows emails instead of names
    - **Fix:** Add name field to registration or profile settings
    - **Workaround:** Use email addresses that look like names
    - **Cannot fix with current data:** Partially (can add feature, but won't help existing accounts)

14. **Issue #11 - No Warning for Ambiguous Assignments**
    - **Problem:** No UI warning when names not mentioned
    - **Fix:** Add warning badge when owner is "Unassigned"
    - **Cannot fix with current data:** Can implement, but won't help V2 meetings

15. **Issue #12 - No Fuzzy Name Matching**
    - **Problem:** "Abdul Zeeshan" won't match "Zeeshan"
    - **Fix:** Implement fuzzy matching algorithm
    - **Cannot fix with current data:** Won't help V2 (all Unassigned)

16. **Issue #13 - No Per-Task Notifications**
    - **Problem:** Task owners don't get email notifications
    - **Fix:** Send emails after meeting processing
    - **Cannot fix with current data:** Won't help V2 (no owners)

---

## CATEGORY C: Documentation/Verification 📝

Not bugs - need investigation or documentation:

17. **Issue #4 - No Admin Notifications**
    - **Type:** Operational convenience
    - **Action:** Document approval process in handbook

18. **Issue #7 - Verify Debt Dashboard Calculations**
    - **Type:** Data accuracy check
    - **Action:** Verify calculations match expected values

19. **Issue #8 - Verify Duplicate Detection**
    - **Type:** Feature verification
    - **Action:** Check if semantic search threshold is correct

20. **Issue #10 - Document Explicit Name Requirement**
    - **Type:** User documentation
    - **Action:** Add to user guide and best practices

21. **Issue #20 - Graveyard Has 13 Items**
    - **Type:** Data accuracy check
    - **Action:** Verify graveyard query logic and clean test data

---

## WHY TEAM MEMBERS CAN'T SEE MEETINGS 🔍

### Root Cause Analysis

**Current Architecture:**
```
DynamoDB Table: meetingmind-meetings
├── Partition Key: userId (the uploader)
├── Sort Key: meetingId
└── GSI: teamId-createdAt-index ✅ (already exists!)
```

**The Problem:**
1. Meetings are stored by `userId` (partition key)
2. Only the uploader can query their own meetings
3. Team members can't see meetings uploaded by others
4. Frontend doesn't use the teamId GSI

**Current State:**
- Zeeshan (uploader): Can see all 6 meetings
- Alishba: Sees ZERO meetings (didn't upload any)
- Aayush: Sees ZERO meetings (didn't upload any)

**Why Team Selector Doesn't Work:**
- Frontend calls `listMeetings()` without teamId parameter
- Backend queries by userId only (ignores teamId)
- GSI exists but isn't being used

### The Fix (3 Steps)

**Step 1: Backend API**
```python
# backend/functions/list-meetings/app.py
def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    params = event.get('queryStringParameters') or {}
    team_id = params.get('teamId')  # NEW
    
    if team_id:
        # Query by teamId using GSI
        response = table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': team_id}
        )
    else:
        # Query by userId (personal meetings)
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
```

**Step 2: Frontend API Utility**
```javascript
// frontend/src/utils/api.js
export async function listMeetings(teamId = null) {
  const headers = await authHeaders()
  const params = {}
  if (teamId) params.teamId = teamId
  const res = await axios.get(`${BASE}/meetings`, { headers, params })
  return res.data.meetings
}
```

**Step 3: Frontend Dashboard**
```javascript
// frontend/src/pages/Dashboard.jsx
async function fetchMeetings() {
  try { 
    setMeetings(await listMeetings(selectedTeamId))  // Pass teamId
  }
  catch { setError('Failed to load meetings') }
  finally { setLoading(false) }
}

// Re-fetch when team changes
useEffect(() => {
  if (selectedTeamId !== null) {
    fetchMeetings()
  }
}, [selectedTeamId])
```

---

## V1 vs V2 DATA SEPARATION 🔄

### Current State

**V1 Meetings (3):**
- ✅ Have `teamId` = "Project V1 - Legacy" team ID
- ✅ Seeded correctly by script
- ✅ Uploaded by Zeeshan account

**V2 Meetings (3):**
- ❌ Missing `teamId` attribute
- ❌ Uploaded from main account (itzashhar@gmail.com)
- ❌ Uploaded before team selector existed

### Data Correction Required

**Option A: Manual DynamoDB Update**
```python
# Update V2 meetings to add teamId
import boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Get V2 team ID
v2_team_id = "get-from-teams-table"

# Update each V2 meeting
for meeting_id in ['meeting-1-id', 'meeting-2-id', 'meeting-3-id']:
    table.update_item(
        Key={'userId': 'main-account-user-id', 'meetingId': meeting_id},
        UpdateExpression='SET teamId = :tid',
        ExpressionAttributeValues={':tid': v2_team_id}
    )
```

**Option B: Re-upload V2 Meetings**
- Delete current V2 meetings
- Re-upload with team selector set to "Project V2 - Active"
- Requires explicit name mentions in recordings

---

## RECOMMENDED FIX ORDER 🎯

### Phase 1: Critical Fixes (Can Test Immediately)
1. Fix Issue #17 (team filtering) - 30 min
2. Fix Issue #5 (meeting details) - 15 min
3. Fix Issue #16 (mock speaker names) - 10 min
4. Add teamId to V2 meetings manually - 10 min
5. **TEST:** Verify team switching works

### Phase 2: High Priority Fixes (Same Day)
6. Fix Issue #19 (leaderboard) - 20 min
7. Fix Issue #18 (Kanban drag-drop) - 30 min
8. Fix Issue #21 (debt dashboard) - 30 min
9. **TEST:** Verify all dashboards work

### Phase 3: Medium Priority Fixes (Next Day)
10. Fix Issue #14 (health scores) - 15 min
11. Fix Issue #15 (ROI calculation) - 15 min
12. Fix Issue #6 (resurrect) - 20 min
13. **TEST:** Verify metrics accurate

### Phase 4: Re-record V2 Meetings (Final Step)
14. Write scripts with explicit name mentions
15. Record with 3 real voices OR explicit names
16. Upload and verify owner assignment works
17. **TEST:** Full demo rehearsal

---

## ESTIMATED TIME TO FIX

**Category A (Can Fix Now):** 3-4 hours
**Category B (Requires Re-recording):** 2-3 hours (recording + upload)
**Category C (Documentation):** 1 hour

**Total:** 6-8 hours to production-ready demo

---

## NEXT STEPS

1. **Immediate:** Fix Issue #17 (team filtering) - this unblocks everything
2. **Then:** Fix Issues #5, #16, #19 (quick wins)
3. **Then:** Add teamId to V2 meetings in DynamoDB
4. **Test:** Verify team switching works correctly
5. **Then:** Fix remaining Category A issues
6. **Finally:** Re-record V2 meetings with explicit names

Ready to start fixing?
