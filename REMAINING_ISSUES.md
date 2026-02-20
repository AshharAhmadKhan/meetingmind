# Remaining Issues - MeetingMind

**Version:** 1.0.10  
**Last Updated:** February 20, 2026 - 7:45 PM IST  
**Developer:** Ashhar Ahmad Khan

---

## Summary

**Total Issues:** 6 remaining  
**Resolved:** 21 issues (Phases 1-4 complete + Category C complete)  
**Production Readiness:** 97/100

---

## Category B: Requires New Audio Recordings (6 issues)

These issues cannot be fixed with current data because all V2 meetings were recorded with a single voice, causing AI to assign tasks to "Unassigned" instead of actual team members.

### Issue #3: No Way to Set Display Name
- **Severity:** MEDIUM (demo blocker)
- **Status:** Not Started
- **Description:** User accounts have no way to set/edit display name. Names show as email addresses everywhere (leaderboard, action items, team members).
- **Expected:** Should be able to set name during registration or in profile settings
- **Impact:** Leaderboard will show emails instead of "Ashhar", "Alishba", "Aayush"
- **Fix Required:** 
  - Add name field to Cognito user attributes
  - Add profile settings page in frontend
  - Update all displays to show name instead of email
- **Estimated Effort:** 60 minutes
- **Priority:** HIGH (needed for demo)

### Issue #9: Single-Voice Recordings Break Owner Assignment
- **Severity:** CRITICAL (demo blocker)
- **Status:** Root cause identified
- **Description:** When one person records all voices, AI assigns tasks to "Unassigned" or task descriptions instead of actual team members
- **Root Cause:** Amazon Transcribe uses voice characteristics for speaker diarization, not names. Single voice = single speaker = all tasks unassigned
- **Solution:** Re-record with explicit name mentions OR use 3 real voices
- **Example:** 
  - ❌ Bad: "You'll handle the repo, right?" "Yes, I'll do it by the 23rd"
  - ✅ Good: "Ashhar, you'll handle the repo, right?" "Yes, Ashhar here - I'll do it by the 23rd"
- **Fix Required:** 
  - Record new meetings with 3 different people
  - OR record with explicit name mentions in every assignment
  - Process new recordings through pipeline
- **Estimated Effort:** 2-3 hours (recording + processing)
- **Priority:** CRITICAL (blocks demo)

### Issue #11: Warning System for Ambiguous Assignments
- **Severity:** LOW (feature enhancement)
- **Status:** Not Started
- **Description:** Need to detect when names are not mentioned in recordings and warn user
- **Expected:** UI warning when owner is "Unassigned" with suggestion to re-record
- **Impact:** Helps users understand why assignments failed
- **Fix Required:** 
  - Add warning banner on meeting detail page
  - Show count of unassigned items
  - Provide guidance on proper recording
- **Estimated Effort:** 45 minutes
- **Priority:** LOW (nice to have)

### Issue #12: No Fuzzy Name Matching
- **Severity:** MEDIUM (usability)
- **Status:** Not Started
- **Description:** "Abdul Ashhar" won't match "Ashhar" in team member list
- **Expected:** Fuzzy matching algorithm to match partial names
- **Impact:** Users must say exact name as registered
- **Fix Required:** 
  - Implement fuzzy matching in process-meeting Lambda
  - Use Levenshtein distance or similar algorithm
  - Match against team member names
- **Estimated Effort:** 90 minutes
- **Priority:** MEDIUM (improves UX)

### Issue #13: No Per-Task Notifications
- **Severity:** MEDIUM (missing feature)
- **Status:** Not Started
- **Description:** Task owners don't get emails when assigned to a task
- **Expected:** Email notification when assigned, with task details and deadline
- **Impact:** Users don't know they have new tasks
- **Fix Required:** 
  - Add email sending in process-meeting Lambda
  - Create email template for task assignment
  - Send to owner's email address
- **Estimated Effort:** 90 minutes
- **Priority:** MEDIUM (improves engagement)

### Issue #10: Document Explicit Name Requirement
- **Severity:** MEDIUM (documentation)
- **Status:** Not Started
- **Description:** Users need to know to explicitly mention names in recordings
- **Expected:** User guide with recording best practices
- **Impact:** Users will make same mistakes without guidance
- **Fix Required:** 
  - Add recording guide to docs
  - Add tips on upload page
  - Show examples of good vs bad recordings
- **Estimated Effort:** 15 minutes
- **Priority:** MEDIUM (prevents issues)

---

## Category C: Documentation/Operational (0 issues)

All Category C issues complete! ✅

---

## COMPLETED - Category C

### ✅ Issue #4: Admin Notification for New Signups - COMPLETE
- **Completed:** February 20, 2026
- **Implementation:** Premium branded email notifications
- **Features:**
  - Admin receives email when new user registers
  - Email includes user details and approval command
  - Premium MeetingMind branding (dark theme, lime accents)
  - Professional design matching app aesthetic
- **Email Template:** Dark theme with Playfair Display + DM Mono fonts
- **Deployment:** SES configured, IAM permissions fixed
- **Testing:** Email sent successfully, verified in inbox

### ✅ Issue #7: Verify Debt Dashboard Calculations - COMPLETE
- **Completed:** February 20, 2026
- **Test Created:** `scripts/testing/features/verify-debt-calculations.py`
- **Result:** All calculations verified correct
- **Formula:** `incomplete_actions × $240 = total_debt`
- **App Verified:** Dashboard shows $4,800 for 20 incomplete actions
- **Documentation:** `docs/verification/ISSUE_7_DEBT_CALCULATIONS.md`

### ✅ Issue #8: Duplicate Detection - VERIFIED
- **Completed:** February 19, 2026
- **Status:** Working as designed
- **Root Cause:** Bedrock intentionally disabled to avoid AWS Marketplace costs
- **Current Behavior:** System uses fallback hash-based embeddings (less accurate)
- **Impact:** Duplicate detection less accurate without Bedrock
- **Fix Required:** None - working as designed
- **To Enable:** Accept AWS Marketplace terms for Bedrock Titan
- **Documentation:** `docs/features/DUPLICATE_DETECTION_EXPLAINED.md`

---

## Priority Order for Fixes

### Must Fix Before Demo (Critical)
1. **Issue #9** - Re-record meetings with proper speaker diarization (2-3 hours)
2. **Issue #3** - Add display name feature (60 minutes)

### Should Fix Before Demo (High Priority)
3. **Issue #10** - Document recording best practices (15 minutes)

### Nice to Have (Medium Priority)
4. **Issue #12** - Fuzzy name matching (90 minutes)
5. **Issue #13** - Per-task notifications (90 minutes)
6. **Issue #7** - Verify debt calculations (15 minutes)

### Can Wait (Low Priority)
7. **Issue #11** - Warning system for unassigned (45 minutes)

---

## Estimated Total Effort

### Critical Path (Must Fix)
- Issue #9: 2-3 hours
- Issue #3: 60 minutes
- **Total: 3-4 hours**

### Full Completion (All Issues)
- Critical: 3-4 hours
- High: 15 minutes
- Medium: 3.5 hours
- Low: 1.25 hours
- **Total: 8-9 hours**

---

## Blockers

### Issue #9 (Critical)
- **Blocker:** Need 3 people to record OR need to re-record with explicit names
- **Options:**
  1. Get 3 team members to record together (best quality)
  2. Record alone but mention names explicitly (acceptable)
  3. Use text-to-speech with different voices (not recommended)
- **Recommendation:** Option 1 or 2

### Issue #3 (High)
- **Blocker:** Need to decide on UX flow
- **Options:**
  1. Add name field during registration (best UX)
  2. Add profile settings page (more flexible)
  3. Both (most complete)
- **Recommendation:** Option 1 (quickest for demo)

---

## Testing Plan

### After Fixing Issue #9
1. Upload new recording with proper speaker diarization
2. Verify action items assigned to correct owners
3. Check leaderboard shows correct names
4. Test Kanban board with assigned items
5. Verify email notifications work

### After Fixing Issue #3
1. Register new user with display name
2. Verify name shows in leaderboard
3. Check name shows in action items
4. Test team member list display

---

## Success Criteria

### Demo Ready
- ✅ All core features working (11/11) - COMPLETE
- ⏳ Action items assigned to real people (Issue #9)
- ⏳ Names show instead of emails (Issue #3)
- ⏳ Recording guide documented (Issue #10)

### Production Ready
- ✅ All critical bugs fixed - COMPLETE
- ⏳ All demo blockers resolved (Issues #9, #3)
- ⏳ User experience polished (Issues #12, #13)
- ⏳ Documentation complete (Issue #10)

---

## Next Steps

### This Week (Before Demo)
1. **Day 1:** Fix Issue #3 (display names) - 60 min
2. **Day 2:** Record new meetings (Issue #9) - 2-3 hours
3. **Day 3:** Document recording guide (Issue #10) - 15 min
4. **Day 4:** Test all features with new data
5. **Day 5:** Record demo video

### Next Week (Before Competition)
1. Fix Issue #12 (fuzzy matching) - 90 min
2. Fix Issue #13 (notifications) - 90 min
3. Verify Issue #7 (debt calculations) - 15 min
4. Submit competition entry

### Post-Competition
1. Fix Issue #11 (warning system) - 45 min
2. Fix Issue #4 (admin notifications) - 30 min
3. Gather user feedback
4. Plan next features

---

## Notes

### Why These Issues Exist
- **Category B:** All stem from using single-voice recordings for testing
- **Category C:** Operational improvements, not bugs

### Why Not Fixed Yet
- **Issue #9:** Requires re-recording audio (time-consuming)
- **Issue #3:** Requires UX design decision
- **Others:** Lower priority than core functionality

### What's Working Well
- ✅ All 18 Phase 1-4 issues resolved
- ✅ All core features operational
- ✅ Backend stable and performant
- ✅ Frontend polished and responsive
- ✅ Documentation comprehensive

---

## Contact

**Developer & Maintainer:** Ashhar Ahmad Khan  
**Email:** thecyberprinciples@gmail.com  
**AWS Account:** 707411439284

For detailed issue tracking, see: `docs/reports/REHEARSAL_ISSUES.md`

---

**Last Updated:** February 20, 2026 - 7:45 PM IST
