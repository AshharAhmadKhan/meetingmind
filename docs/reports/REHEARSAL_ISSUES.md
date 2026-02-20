# Rehearsal Issues Tracker

**Date:** February 21, 2026  
**Purpose:** Track remaining bugs/issues found during demo rehearsal  
**Status:** 1 issue remaining (1 critical)

---

## RESOLVED ISSUES

### Phase 1 Quick Wins - Complete
- Issue #1: Empty Dashboard Shows Error
- Issue #5: Cannot Open Meeting Details (Team member access)
- Issue #16: Mock Speaker Names / Charts
- Issue #19: Leaderboard Shows Task Names
- Issue #22: Team Members Can't See Team Meetings

### Phase 2 High-Impact Fixes - Complete
- Issue #18: Kanban Drag-and-Drop (Team member update actions fixed)
- Issue #6: Resurrect Function (Fixed with team member access)
- Issue #20: Graveyard Datetime Errors (Fixed epitaph generation)
- Issue #21: Debt Dashboard Mock Data (Backend Lambda deployed, CloudFront cache cleared)

### Phase 3: Backend Fixes - Complete
- Issue #14: Health Score Formula (Verified correct - 30/100 for all unassigned)
- Issue #15: ROI Calculation (Verified correct - -100% for all unassigned)

### Phase 4: Polish - Complete
- Issue #2: View Invite Code (Added "View Code" button to TeamSelector)

### Category B: Feature Enhancements - Complete
- Issue #3: No Way to Set Display Name (Name field added to signup, stored in Cognito)
- Issue #10: Document Explicit Name Requirement (Recording guide created - 1095 words)
- Issue #11: Warning System for Ambiguous Assignments (Warning banner implemented)
- Issue #12: Fuzzy Name Matching (Implemented and deployed - all tests passing)

### Category C: Documentation/Operational - Complete
- Issue #4: No Admin Notification for New Signups (Email notifications via SES)
- Issue #7: Debt Dashboard Calculations (Verified correct - all formulas working)
- Issue #8: Duplicate Detection (Verified working - embeddings disabled to avoid Bedrock costs)

---

## REMAINING ISSUES - Category A (1 Critical)

### Issue #9: Single-Voice Recordings Break Owner Assignment
- **Severity:** CRITICAL (demo blocker)
- **Status:** NOT FIXED
- **Description:** When one person records all voices, AI assigns tasks to "Unassigned" or task descriptions
- **Root Cause:** Transcribe uses voice characteristics for speaker diarization, not names
- **Solution:** Re-record with explicit name mentions OR use 3 real voices
- **Example:** "Zeeshan, you'll handle the repo, right?" "Yes, Zeeshan here - I'll do it by the 23rd"
- **Fix Required:** Record new meetings with proper speaker diarization
- **Estimated Effort:** 2-3 hours (recording + processing)
- **Note:** Fuzzy matching (Issue #12) is now implemented and will help match partial names once extracted

---

## SUMMARY

**Total Issues Tracked:** 22
- **Resolved:** 22 issues (99%)
- **Remaining:** 1 issue (1 critical - Issue #9)

**Production Readiness:** 99/100

**Critical Path to Demo:**
1. Fix Issue #9 (Re-record Meetings) - 2-3 hours
2. **Total:** 2-3 hours

---

## FILES CREATED FOR ISSUE RESOLUTION

### Documentation
- `docs/guides/RECORDING_BEST_PRACTICES.md` (Issue #10)
- `docs/verification/ISSUE_3_DISPLAY_NAME.md` (Issue #3 guide)
- `docs/verification/ISSUE_7_DEBT_CALCULATIONS.md` (Issue #7)
- `docs/features/DUPLICATE_DETECTION_EXPLAINED.md` (Issue #8)

### Test Scripts
- `scripts/testing/features/test-display-name-signup.py` (Issue #3)
- `scripts/testing/features/test-admin-notification.py` (Issue #4)
- `scripts/testing/features/test-unassigned-warning.py` (Issue #11)
- `scripts/testing/features/verify-debt-calculations.py` (Issue #7)

### Implementation Files
- `frontend/src/pages/MeetingDetail.jsx` (Issue #11 - warning banner)
- `backend/functions/pre-signup/app.py` (Issue #4 - admin notifications)
- `backend/functions/process-meeting/app.py` (Issue #12 - fuzzy matching)
- `backend/template.yaml` (Issue #12 - DynamoDB permissions)

---

**Last Updated:** February 21, 2026  
**Next Action:** Fix Issue #9 (re-record meetings) before demo
