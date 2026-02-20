# Repository Cleanup & Reorganization Plan

**Date:** February 20, 2026  
**Status:** In Progress

## Objectives

1. Consolidate scattered documentation
2. Remove outdated/redundant files
3. Organize files into logical structure
4. Update all documentation to reflect current state
5. Clean up test scripts and remove obsolete ones

## Current Issues

### Root Directory Clutter
- Multiple fix summary MDs scattered in root
- Temporary verification files in root
- Test result files in root

### Documentation Fragmentation
- Reports scattered across root and docs/reports
- Some docs outdated (references to old issues)
- Redundant information across multiple files

### Scripts Organization
- 60+ test scripts in scripts/testing
- Many are one-off debugging scripts
- No clear categorization

## Proposed Structure

```
meetingmind/
├── README.md                    # Main project readme
├── CHANGELOG.md                 # Version history
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── docs/
│   ├── README.md                # Documentation index
│   ├── ARCHITECTURE.md          # System architecture
│   ├── FEATURES.md              # Feature documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── TESTING.md               # Testing guide
│   ├── TROUBLESHOOTING.md       # Common issues & solutions
│   │
│   ├── architecture/            # Architecture diagrams & docs
│   ├── features/                # Feature-specific docs
│   ├── competition/             # Competition materials
│   └── archive/                 # Historical documents
│       ├── fixes/               # Fix summaries
│       ├── reports/             # Test reports
│       └── sessions/            # Session summaries
│
├── scripts/
│   ├── README.md                # Scripts documentation
│   ├── setup/                   # Setup & initialization
│   ├── deploy/                  # Deployment scripts
│   ├── data/                    # Data seeding
│   └── testing/
│       ├── README.md            # Testing guide
│       ├── core/                # Core test utilities
│       ├── api/                 # API tests
│       ├── features/            # Feature tests
│       └── archive/             # Old/deprecated tests
│
├── backend/                     # AWS SAM backend
├── frontend/                    # React frontend
└── .kiro/                       # Kiro specs
```

## Files to Archive

### Root Level (move to docs/archive/fixes/)
- FIXES_APPLIED_TODAY.md
- GRAVEYARD_FIX_SUMMARY.md
- HEALTH_ROI_VERIFICATION.md
- PHASE1_QUICK_WINS_COMPLETE.md
- TEAM_MEMBER_UPDATE_FIX.md
- TEST_RESULTS.md
- TEST_TEAM_MEMBER_ACCESS.md
- V1_DEPLOYMENT_COMPLETE.md
- VERIFICATION_CHECKLIST.md

### Keep in Root (update)
- README.md (update with current status)
- CHANGELOG.md (consolidate all changes)
- ISSUE_PRIORITY_PLAN.md (move to docs/reports/)

## Files to Remove

### Backend
- *.zip files (deployment artifacts)
- *-policy.json files (generated, not source)

### Test Scripts (consolidate/remove duplicates)
- Multiple check-* scripts doing similar things
- Old test-nova-* scripts (Nova testing complete)
- Simulation scripts (move to archive)

## Documentation Updates Needed

1. README.md - Update with:
   - Current deployment status
   - Latest features
   - Quick start guide
   - Link to full docs

2. CHANGELOG.md - Add:
   - All fixes from February 19-20
   - Feature additions
   - Bug fixes

3. docs/DEPLOYMENT.md - Create comprehensive guide

4. docs/TROUBLESHOOTING.md - Consolidate from AI_AGENT_HANDBOOK

5. scripts/testing/README.md - Document test categories

## Execution Order

1. Create new directory structure
2. Move files to archive
3. Remove obsolete files
4. Update documentation
5. Commit changes
6. Verify nothing broken
