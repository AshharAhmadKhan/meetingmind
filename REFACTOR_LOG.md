# Repository Refactor & Hardening Log
**Date Started**: February 21, 2026  
**Status**: Phase 0 - Baseline Analysis

---

## PHASE 0: SAFETY & BASELINE

### Project Structure Analysis

**Project Type**: Full-stack serverless application (AWS SAM + React)

#### Current Structure:
```
meetingmind/
├── backend/              # AWS SAM Lambda functions
├── frontend/             # React + Vite application
├── scripts/              # Utility and testing scripts
├── docs/                 # Documentation (heavily nested)
├── .kiro/                # Kiro AI specs
├── .githooks/            # Git hooks
└── [Root MD files]       # 14 markdown files at root
```

### File Categorization

#### SOURCE CODE (Production)
**Backend** (18 Lambda functions):
- backend/functions/check-duplicate/
- backend/functions/create-team/
- backend/functions/daily-digest/
- backend/functions/dlq-handler/
- backend/functions/get-all-actions/
- backend/functions/get-debt-analytics/
- backend/functions/get-meeting/
- backend/functions/get-team/
- backend/functions/get-upload-url/
- backend/functions/join-team/
- backend/functions/list-meetings/
- backend/functions/list-user-teams/
- backend/functions/post-confirmation/
- backend/functions/pre-signup/
- backend/functions/process-meeting/
- backend/functions/send-reminders/
- backend/functions/send-welcome-email/
- backend/functions/update-action/

**Frontend** (React components):
- frontend/src/components/ (7+ components)
- frontend/src/pages/ (5+ pages)
- frontend/src/utils/ (auth, api utilities)

#### TESTS
- backend/tests/test_lambdas.py (1 file)
- scripts/testing/ (50+ test scripts - EXCESSIVE)
  - scripts/testing/features/ (30+ feature tests)
  - scripts/testing/core/ (core tests)
  - scripts/testing/api/ (API tests)
  - scripts/testing/archive/ (archived tests)

#### CONFIGURATION
- backend/template.yaml (SAM template)
- frontend/vite.config.js
- frontend/package.json
- .env.example
- .gitignore
- .vscode/settings.json

#### DOCUMENTATION (EXCESSIVE - 60+ files)
**Root Level** (14 files - TOO MANY):
- README.md ✓
- CHANGELOG.md ✓
- AI_AGENT_HANDBOOK.md
- CLEANUP_SUMMARY.md
- DIAGNOSIS_TEAM_UPLOAD_ISSUE.md
- FINAL_STATUS_AND_NEXT_STEPS.md
- ISSUE_RESOLVED_PROCESSING_STUCK.md
- ISSUE_RESOLVED_TEAM_VISIBILITY.md
- ISSUES_VISUAL_SUMMARY.md
- REMAINING_ISSUES.md
- TEAM_UPLOAD_BUG_FIXED.md
- TEAM_UPLOAD_FIX_DEPLOYED.md
- TEST_RESULTS_TEAM_UPLOAD.md
- TEST_SUITE_SUMMARY.md
- TESTING.md

**docs/** (50+ files in 10 subdirectories):
- docs/architecture/ (1 file)
- docs/archive/ (15+ files)
- docs/competition/ (4 files)
- docs/diagnosis/ (1 file)
- docs/features/ (2 files)
- docs/fixes/ (3 files)
- docs/guides/ (2 files)
- docs/issues/ (2 files)
- docs/reports/ (9 files)
- docs/verification/ (2 files)

#### TEMPORARY/BUILD ARTIFACTS
- backend/.aws-sam/build/ (SAM build artifacts)
- backend/pre-signup.zip ⚠️ (orphan zip file)
- backend/process-meeting.zip ⚠️ (orphan zip file)
- backend/get-all-actions-policy-updated.json ⚠️ (orphan policy file)
- frontend/dist/ (build output)
- frontend/node_modules/ (dependencies)

#### SCRIPTS (100+ files)
- scripts/data/ (5 data manipulation scripts)
- scripts/deploy/ (3 deployment scripts)
- scripts/setup/ (8 setup scripts)
- scripts/testing/ (50+ test scripts - EXCESSIVE)

---

## CLEANUP CANDIDATES (Phase 0 Analysis)

### 🔴 HIGH PRIORITY - Immediate Cleanup

#### Orphan Files (Not in .gitignore):
1. **backend/pre-signup.zip** - Build artifact, should not be committed
2. **backend/process-meeting.zip** - Build artifact, should not be committed
3. **backend/get-all-actions-policy-updated.json** - Temporary policy file

#### Excessive Root Documentation (14 files → Target: 3-5):
**CONSOLIDATE INTO**:
- README.md (keep)
- CHANGELOG.md (keep)
- CONTRIBUTING.md (create)
- ARCHITECTURE.md (move from docs/)

**FILES TO MERGE/ARCHIVE**:
1. DIAGNOSIS_TEAM_UPLOAD_ISSUE.md → docs/fixes/
2. TEAM_UPLOAD_BUG_FIXED.md → docs/fixes/
3. TEAM_UPLOAD_FIX_DEPLOYED.md → docs/fixes/
4. ISSUE_RESOLVED_PROCESSING_STUCK.md → docs/fixes/
5. ISSUE_RESOLVED_TEAM_VISIBILITY.md → docs/fixes/
6. TEST_RESULTS_TEAM_UPLOAD.md → docs/testing/
7. FINAL_STATUS_AND_NEXT_STEPS.md → docs/status/
8. REMAINING_ISSUES.md → docs/issues/
9. ISSUES_VISUAL_SUMMARY.md → docs/issues/
10. TEST_SUITE_SUMMARY.md → docs/testing/
11. TESTING.md → docs/testing/
12. CLEANUP_SUMMARY.md → docs/archive/
13. AI_AGENT_HANDBOOK.md → docs/guides/

#### Excessive Test Scripts (50+ → Target: 10-15):
**scripts/testing/** has 50+ ad-hoc test scripts
- Many are one-off diagnostic scripts
- Should consolidate into organized test suites
- Archive obsolete diagnostic scripts

### 🟡 MEDIUM PRIORITY - Structural Issues

#### Documentation Over-nesting:
- docs/ has 10 subdirectories (too many)
- Consolidate: fixes/, issues/, verification/ → issues/
- Consolidate: reports/, diagnosis/ → reports/
- Keep: architecture/, guides/, archive/

#### Script Organization:
- scripts/testing/ needs major consolidation
- scripts/data/ is good
- scripts/deploy/ is good
- scripts/setup/ is good

### 🟢 LOW PRIORITY - Minor Issues

#### Debug Files:
- scripts/debug-frontend-state.md (move to docs/troubleshooting/)
- scripts/debug-team-selection.md (move to docs/troubleshooting/)
- scripts/BEDROCK_TESTS_DISABLED.txt (move to docs/notes/)

---

## PROPOSED TARGET STRUCTURE

```
meetingmind/
├── backend/
│   ├── functions/           # Lambda functions (18)
│   ├── tests/               # Backend tests
│   └── template.yaml        # SAM template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   ├── public/
│   └── [config files]
├── scripts/
│   ├── data/                # Data manipulation
│   ├── deploy/              # Deployment scripts
│   ├── setup/               # Setup scripts
│   └── testing/             # Consolidated tests (10-15 files)
├── docs/
│   ├── architecture/        # System design
│   ├── guides/              # User guides
│   ├── issues/              # Issue tracking (consolidated)
│   ├── reports/             # Test/audit reports (consolidated)
│   ├── archive/             # Historical docs
│   └── [core docs]          # 5-7 essential docs
├── .kiro/                   # Kiro AI specs
├── .githooks/               # Git hooks
├── README.md                # Project overview
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guide
├── ARCHITECTURE.md          # High-level architecture
└── LICENSE                  # License file (TO ADD)
```

---

## RISK ASSESSMENT

### Low Risk:
- Moving documentation files
- Archiving diagnostic scripts
- Removing build artifacts

### Medium Risk:
- Consolidating test scripts (need to verify no CI dependencies)
- Merging documentation (need to preserve important info)

### High Risk:
- None identified (no source code changes planned)

---

## NEXT STEPS

1. ✅ Phase 0 Complete - Baseline established
2. ⏳ Phase 1 - Structural normalization
3. ⏳ Phase 2 - Deep file audit
4. ⏳ Phase 3 - Professional hardening
5. ⏳ Phase 4 - Global consistency check

---

## DECISIONS LOG

### Decision 1: Root Documentation Cleanup
**Rationale**: 14 root MD files is excessive. Professional repos have 3-5 max.
**Action**: Consolidate issue/fix docs into docs/ subdirectories
**Risk**: Low - all content preserved, just reorganized

### Decision 2: Test Script Consolidation
**Rationale**: 50+ ad-hoc test scripts is unmaintainable
**Action**: Archive diagnostic scripts, keep only active test suites
**Risk**: Medium - need to verify no CI dependencies

### Decision 3: Remove Build Artifacts
**Rationale**: .zip files and build artifacts shouldn't be in git
**Action**: Delete and add to .gitignore
**Risk**: Low - can be regenerated

---

*Log will be updated as refactor progresses*
