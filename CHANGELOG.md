# Changelog

All notable changes to MeetingMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Walk of Shame on leaderboard (planned)

## [1.0.9] - 2026-02-19

### Added
- **PRE-DEPLOY TEST SUITE** - Comprehensive CI-style checks before deployment
  - 7 test categories: Python syntax, Frontend build, AWS connectivity, API endpoints, Data integrity, Frontend config, Feature verification
  - 80 total tests covering all aspects of the system
  - Clear output with green ticks and red X
  - Exit code 0 for safe deployment, 1 for blocked
  - Run with: `python scripts/testing/run-all-tests.py`
  - Typical results: 75/80 passed (5 non-blocking warnings)
  - Runtime: ~30-45 seconds

### Changed
- **REPOSITORY REORGANIZATION** - Complete cleanup and restructuring
  - Moved all scattered files into logical folders
  - Root now contains only: README.md, CHANGELOG.md, .gitignore, .env.example, AI_AGENT_HANDBOOK.md
  - Organized docs/ into: architecture/, reports/, competition/, archive/
  - Organized scripts/ into: setup/, testing/, data/, deploy/
  - Deleted build artifacts (*.zip files, __pycache__ folders)
  - Deleted empty folders (backend/shared/, backend/functions/notify-admin-signup/)
  - Updated .gitignore to exclude build artifacts
  - Created .env.example with all required environment variables

### Removed
- 15 scattered markdown files from root (moved to docs/)
- 4 test scripts from root (moved to scripts/testing/)
- 3 deployment scripts from root (moved to scripts/deploy/)
- 1 setup script from root (moved to scripts/setup/)
- All build artifacts and cache folders

## [1.0.8] - 2026-02-19

### Added
- **COMPREHENSIVE_TEST_REPORT.md** - Complete system verification
  - Tested all 18 Lambda functions (syntax validation)
  - Tested all 12 frontend files (diagnostics clean)
  - Verified all 438 markdown documentation files
  - Validated CORS configuration across all functions
  - Verified Decimal serialization in all DynamoDB functions
  - Tested API Gateway endpoints (all OPTIONS requests working)
  - Overall score: 98.5% (Excellent)

### Verified
- All Python files compile without syntax errors
- All JavaScript files have no diagnostic issues
- Frontend builds successfully (13.35s, 928.99 kB bundle)
- All Lambda functions deployed with correct timestamps
- CORS headers present in all 18 API-triggered functions
- Decimal serialization working in all DynamoDB functions
- API Gateway OPTIONS requests working (5/5 endpoints)
- Real AI data confirmed (no mock data in production)
- CloudFront invalidation completed

### Status
- Production-ready: 98.5% score
- 36/38 AWS infrastructure tests passed
- 2 non-blocking failures (Claude payment pending, old meeting schema)

## [1.0.7] - 2026-02-19

### Fixed
- **CRITICAL**: Fixed CORS configuration across all 18 Lambda functions
  - Changed from wildcard `*` to CloudFront domain `https://dcfx593ywvy92.cloudfront.net`
  - Added OPTIONS preflight handler to all endpoints
  - Ensured CORS headers in all response paths (success and error)
- **CRITICAL**: Fixed Decimal serialization across all Lambda functions
  - Added `decimal_to_float()` function to all functions using DynamoDB
  - Updated all `json.dumps()` calls to use `default=decimal_to_float`
  - Prevents "Float types are not supported" errors
- Fixed 502 Bad Gateway errors preventing frontend from loading
- Fixed CORS preflight request handling
- Fixed missing error response headers

### Changed
- Standardized CORS header configuration across all Lambda functions
- Improved error handling consistency
- Enhanced JSON serialization for DynamoDB compatibility

### Deployment
- Deployed all 18 Lambda functions with fixes
- Created CloudFront invalidation for cache refresh

## [1.0.6] - 2026-02-19

### Fixed
- **CRITICAL BUG**: Fixed Float/Decimal type error in process-meeting Lambda
  - `_calculate_health_score()` now returns Decimal types for DynamoDB compatibility
  - `_generate_embedding()` now converts Bedrock embedding floats to Decimals
  - Meeting uploads were failing with "Float types are not supported" error
  - Health score data and embeddings now properly stored in DynamoDB
- Meeting processing pipeline now completes successfully with autopsy generation

### Changed
- Removed redundant Decimal conversion in lambda_handler (already handled in function)
- Enhanced embedding generation to handle DynamoDB Decimal requirements

## [1.0.5] - 2026-02-19

### Added
- Meeting Autopsy feature for failed meetings (D/F grades or ghost meetings)
  - AI-generated 2-sentence autopsy using Bedrock multi-model fallback
  - Analyzes speaking time distribution, unowned actions, decisions, duration, duplicates
  - Displays in red-bordered card on MeetingDetail page with 🔬 icon
  - Generated during meeting processing and stored in DynamoDB
  - Format: "Cause of death: [diagnosis]. Prescription: [solution]."
- Health score calculation in process-meeting Lambda
- `autopsy` and `autopsyGeneratedAt` fields in DynamoDB

### Changed
- Enhanced process-meeting Lambda with health score and autopsy generation
- Updated MeetingDetail page to display autopsy for failed meetings

## [1.0.4] - 2026-02-19

### Added
- Ghost Meeting Detection pattern (6th pattern)
  - Detects meetings with zero decisions AND zero actions
  - Displays count, percentage, and estimated cost ($75/hour per person)
  - Shows "👻 GHOST" badge on qualifying meeting cards
  - Prescription: Require agendas, cancel unnecessary meetings, track ROI
- `isGhost` flag in list-meetings Lambda response
- Grey ghost badge on Dashboard meeting cards

### Changed
- Enhanced pattern detection with Ghost Meeting analysis
- Updated Dashboard to display ghost meeting badges

## [1.0.3] - 2026-02-19

### Added
- Meeting Health Score (A-F grading system)
  - Calculated based on completion rate (40%), owner assignment (30%), risk score (20%), recency (10%)
  - Displayed as colored badge on meeting cards
  - Labels: Excellent/Strong/Average/Poor/Failed meeting
- Grade colors: A (emerald), B (lime), C (amber), D (orange), F (red)
- **AI_AGENT_HANDBOOK.md** - Comprehensive guide for AI agents
  - Architecture diagrams
  - Common issues & solutions
  - Deployment workflows
  - Testing guidelines
  - Design system reference

### Changed
- Enhanced Dashboard with health grade badges
- Updated list-meetings Lambda to calculate health scores
- Updated README with AI Agent Handbook reference

## [1.0.2] - 2026-02-19

### Added
- AI-generated epitaphs for Graveyard items (>30 days old)
  - Multi-model fallback chain (Haiku → Nova Lite → Nova Micro)
  - Automatic generation with 7-day cache
  - Fallback templates when Bedrock unavailable
  - Displayed in italic with muted color on tombstones
- Epitaph fields in DynamoDB (epitaph, epitaphGeneratedAt)

### Changed
- Enhanced Graveyard UI with AI-generated epitaphs
- Updated get-all-actions Lambda to generate epitaphs on-demand

## [1.0.1] - 2026-02-19

### Added
- PowerShell deployment script (deploy-frontend.ps1) for Windows
- DEPLOY.md with cross-platform deployment instructions

### Fixed
- Kanban board card text truncation (2-line ellipsis)
- Kanban board drag ghost z-index (now appears above all content)
- Kanban board column width optimization (280px minimum)
- Removed unused arrayMove import

### Changed
- Updated deployment workflow for Windows compatibility

## [1.0.0] - 2026-02-19

### Added
- Complete audio upload → Transcribe → Bedrock pipeline
- Multi-model AI fallback (Claude Haiku → Nova Lite → Nova Micro)
- Exponential backoff retry logic for throttling
- Risk scoring algorithm (4 factors, 0-100 scale)
- Semantic duplicate detection with Titan Embeddings
- Pattern detection (5 toxic patterns)
- Graveyard feature for abandoned items (>30 days)
- Team collaboration with invite codes
- Leaderboard with weighted scoring and achievements
- Meeting debt analytics with $ quantification
- Email notifications via SES (completion, failure, digest, reminders)
- EventBridge cron jobs (daily digest, reminders)
- Kanban board with drag-and-drop
- CloudWatch monitoring with X-Ray tracing
- SQS processing queue with DLQ

### Changed
- Removed mock fallbacks (now fails loudly)
- Updated Nova model IDs to use APAC inference profiles
- Improved error handling across all Lambda functions

### Fixed
- Nova Lite and Nova Micro access issues
- Bedrock throttling with exponential backoff
- Lambda deployment with proper dependency packaging

### Security
- JWT authentication via Cognito
- Presigned S3 URLs (5-minute expiry)
- HTTPS only (TLS 1.2+)
- IAM least-privilege policies

## [0.1.0] - 2026-02-12

### Added
- Initial project setup
- Basic meeting processing pipeline
- Frontend dashboard
- Backend Lambda functions
- DynamoDB schema
- Cognito authentication

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

---

**Last Updated:** February 19, 2026 - 10:25 PM IST
