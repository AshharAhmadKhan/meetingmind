# PROJECT BOOTSTRAP — MeetingMind

**Single Source of Truth for New Sessions**  
**Last Updated:** February 19, 2026  
**Architecture Score:** 72/100 (Functional MVP with production gaps)

---

## 🎯 WHAT IS THIS PROJECT?

MeetingMind is an AI-powered meeting intelligence platform that transforms audio into actionable insights.

**Live URL:** https://dcfx593ywvy92.cloudfront.net  
**Status:** Production MVP — Functional but needs hardening for scale

**Core Features:**
- Transcribes meeting audio with speaker identification
- Extracts decisions, action items, and follow-ups using AI
- Tracks action item completion with risk prediction
- Detects duplicate work across meetings using embeddings
- Identifies toxic meeting patterns with statistical analysis
- Calculates meeting ROI and debt metrics
- Team collaboration with invite codes
- Kanban board for action item management

---

## 🏗️ ARCHITECTURE OVERVIEW

### Technology Stack
- **Frontend:** React 19 + Vite + React Router + AWS Amplify
- **Backend:** Python 3.11 + AWS SAM (Serverless Application Model)
- **AI:** Amazon Bedrock (Claude Haiku, Nova Lite, Nova Micro) + Amazon Transcribe
- **Database:** DynamoDB (pay-per-request billing)
- **Auth:** Cognito (email-based JWT tokens)
- **Hosting:** S3 + CloudFront CDN
- **Notifications:** SES (email) + SNS (reminders) + EventBridge (cron)

### AWS Services (11 Total)
1. **S3** - Audio storage + static website hosting
2. **Lambda** - 18 serverless functions
3. **API Gateway** - RESTful API with Cognito authorizer
4. **DynamoDB** - 2 tables (meetings, teams)
5. **Cognito** - User authentication
6. **Transcribe** - Speech-to-text with diarization
7. **Bedrock** - AI analysis + embeddings (Titan v2)
8. **SES** - Email notifications
9. **SNS** - Action item reminders
10. **EventBridge** - Daily cron jobs
11. **CloudFront** - Global CDN

---

## 📊 AWS RESOURCES (EXACT VALUES)

### Region
**ap-south-1** (Mumbai) — ALL resources in this region

### Backend Infrastructure
- **CloudFormation Stack:** meetingmind-backend
- **API Gateway ID:** 25g9jf8sqa
- **API Base URL:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod

### Storage
- **Audio Bucket:** meetingmind-audio-707411439284
- **Frontend Bucket:** meetingmind-frontend-707411439284


### Database Tables
**Meetings Table:** meetingmind-meetings
- Primary Key: userId (HASH) + meetingId (RANGE)
- GSI 1: status-createdAt-index
- GSI 2: teamId-createdAt-index
- Billing: Pay-per-request

**Teams Table:** meetingmind-teams
- Primary Key: teamId (HASH)
- GSI: inviteCode-index
- Billing: Pay-per-request

### Authentication
- **User Pool ID:** ap-south-1_mkFJawjMp
- **User Pool Client ID:** 150n899gkc651g6e0p7hacguac
- **Token Expiry:** 1 hour (access token), 30 days (refresh token)

### CDN
- **CloudFront Distribution ID:** E3CAAI97MXY83V
- **CloudFront URL:** https://dcfx593ywvy92.cloudfront.net
- **Cache Invalidation:** Required after frontend deployments

### Email Service
- **SES From Email:** thecyberprinciples@gmail.com
- **SES Region:** ap-south-1 (must match Lambda region)
- **Status:** Production (verified)

### Message Queues
- **Processing Queue:** meetingmind-processing-queue
  - Visibility Timeout: 960s (16 minutes)
  - Message Retention: 4 days
  - Max Receive Count: 3 (then → DLQ)
- **Dead Letter Queue:** meetingmind-processing-dlq
  - Message Retention: 14 days

### SNS Topics
- **Reminder Topic:** meetingmind-reminders
- **ARN:** arn:aws:sns:ap-south-1:707411439284:meetingmind-reminders

### AWS Account
- **Account ID:** 707411439284
- **IAM User:** (configured via AWS CLI)

---

## 🔧 LAMBDA FUNCTIONS (18 Total)

### Core API Functions

**1. meetingmind-get-upload-url** (30s, 256MB)
- Generates presigned S3 URL for direct browser upload
- Creates meeting record in DynamoDB with PENDING status
- Supports optional teamId for team meetings
- Endpoint: `POST /upload-url`
- Body: `{title, contentType, fileSize, teamId?}`

**2. meetingmind-process-meeting** (900s, 512MB) ⚠️ CRITICAL
- Main processing pipeline triggered by SQS
- Flow: S3 event → SQS → Lambda → Transcribe → Bedrock → DynamoDB → SES
- Multi-model AI fallback: Claude Haiku → Nova Lite → Nova Micro → Intelligent Mock
- Generates 1536-dim embeddings (Titan v2) for duplicate detection
- Calculates risk scores (0-100) based on deadline, owner, vagueness, staleness
- Calculates ROI metrics (cost vs value)
- Sends email notification on completion/failure
- X-Ray tracing enabled with subsegments

**3. meetingmind-list-meetings** (60s, 256MB)
- Lists all meetings for authenticated user
- Sorted by createdAt descending (newest first)
- Returns: meetingId, title, status, createdAt, updatedAt, summary
- ⚠️ No pagination - will fail with >1MB of meetings
- Endpoint: `GET /meetings`

**4. meetingmind-get-meeting** (30s, 256MB)
- Retrieves single meeting with full details
- Strips transcript field (too large for UI)
- Returns 404 if meeting not found
- Endpoint: `GET /meetings/{meetingId}`

**5. meetingmind-update-action** (30s, 256MB)
- Updates action item status or completion
- Syncs completed field with status field (done = completed)
- Supports status: todo, in_progress, blocked, done
- ⚠️ No optimistic locking - race condition possible
- Endpoint: `PUT /meetings/{meetingId}/actions/{actionId}`
- Body: `{completed?, status?}`


**6. meetingmind-get-all-actions** (60s, 256MB)
- Aggregates action items across all meetings
- Supports filtering: status (all/incomplete/complete), owner, teamId
- Returns actions with meeting context (meetingId, meetingTitle, meetingDate)
- Sorted by deadline (soonest first), then risk score (highest first)
- ⚠️ No pagination - will fail with >1MB of actions
- Endpoint: `GET /all-actions?status=&owner=&teamId=`

**7. meetingmind-get-debt-analytics** (60s, 256MB)
- Calculates meeting debt metrics in real-time
- Debt categories: forgotten (>30 days), overdue, unassigned, at-risk
- Cost calculation: $75/hour × 3.2 hours blocked per incomplete action
- Returns: totalDebt, breakdown, trend (8 weeks), completionRate, velocity
- ⚠️ No pagination - scans all meetings
- Endpoint: `GET /debt-analytics?teamId=`

**8. meetingmind-check-duplicate** (30s, 512MB)
- Finds duplicate action items using cosine similarity
- Similarity thresholds: 0.85 (duplicates), 0.70 (history)
- Identifies chronic blockers (repeated 3+ times)
- Fallback: TF-IDF if Bedrock embeddings unavailable
- ⚠️ Scans all meetings - O(n) complexity
- Endpoint: `POST /check-duplicate`
- Body: `{task}`

### Team Functions

**9. meetingmind-create-team** (30s, 256MB)
- Creates team with 6-character alphanumeric invite code
- Creator becomes owner with full permissions
- Endpoint: `POST /teams`
- Body: `{teamName}`

**10. meetingmind-join-team** (30s, 256MB)
- Adds user to team via invite code
- Validates invite code using inviteCode-index GSI
- Prevents duplicate membership
- User role: member (not owner)
- Endpoint: `POST /teams/join`
- Body: `{inviteCode}`

**11. meetingmind-get-team** (30s, 256MB)
- Retrieves team details and member list
- Validates user is team member (403 if not)
- Returns: teamId, teamName, inviteCode, members, createdAt
- Endpoint: `GET /teams/{teamId}`

**12. meetingmind-list-user-teams** (30s, 256MB)
- Lists all teams user belongs to
- ⚠️ Uses SCAN (inefficient) - needs userId-teamId GSI
- Returns: teamId, teamName, memberCount, role
- Endpoint: `GET /teams`

### Scheduled Functions

**13. meetingmind-send-reminders** (60s, 256MB)
- Sends email reminders for approaching deadlines
- Triggers: 2 days before deadline or overdue
- Uses SNS topic for notifications
- Scheduled: EventBridge cron(0 8 * * ? *) — 8 AM UTC daily

**14. meetingmind-daily-digest** (300s, 512MB)
- Sends HTML email digest to all users with incomplete actions
- Sections: Critical (due today/tomorrow), Overdue, Upcoming (this week)
- Includes completion rate and stats
- Scheduled: EventBridge cron(0 3 * * ? *) — 3 AM UTC (9 AM IST) daily

### Auth Functions

**15. meetingmind-pre-signup** (10s, 256MB)
- Cognito pre-signup Lambda trigger
- Auto-approves all users (no admin approval required)

**16. meetingmind-post-confirmation** (10s, 256MB)
- Cognito post-confirmation Lambda trigger
- Creates user record in DynamoDB
- Can disable user if needed (admin control)

**17. meetingmind-send-welcome-email** (30s, 256MB)
- Sends welcome email after user signup
- Uses SES for email delivery

### Infrastructure Functions

**18. meetingmind-dlq-handler** (60s, 256MB)
- Processes failed messages from Dead Letter Queue
- Logs errors to CloudWatch
- Sends admin notifications via SES
- Triggered by SQS DLQ events


---

## 🗄️ DATA MODELS

### Meetings Table Schema
```json
{
  "userId": "cognito-sub-uuid",
  "meetingId": "uuid",
  "title": "Q1 Planning Meeting",
  "status": "DONE",
  "s3Key": "audio/userId__meetingId__title.mp3",
  "transcript": "Full transcript text...",
  "summary": "Meeting summary...",
  "decisions": ["Launch beta on March 15", "Defer mobile app to v2"],
  "actionItems": [
    {
      "id": "action-1",
      "task": "Finalize API documentation",
      "owner": "Ashhar",
      "deadline": "2026-02-25",
      "completed": false,
      "status": "todo",
      "completedAt": null,
      "riskScore": 45,
      "riskLevel": "MEDIUM",
      "createdAt": "2026-02-18T10:30:00Z",
      "embedding": [0.123, -0.456, ...]
    }
  ],
  "followUps": ["Confirm budget approval", "Schedule next review"],
  "roi": {
    "cost": 150.00,
    "value": 1200.00,
    "roi": 700.0,
    "decision_count": 2,
    "clear_action_count": 3,
    "meeting_duration_minutes": 30
  },
  "teamId": "team-uuid",
  "email": "user@email.com",
  "createdAt": "2026-02-18T10:00:00Z",
  "updatedAt": "2026-02-18T10:35:00Z"
}
```

**Field Notes:**
- `status`: PENDING | TRANSCRIBING | ANALYZING | DONE | FAILED
- `actionItems.status`: todo | in_progress | blocked | done
- `actionItems.riskLevel`: LOW | MEDIUM | HIGH | CRITICAL
- `actionItems.embedding`: 1536 dimensions (Titan Embeddings v2)
- `transcript`: Stripped from API responses (too large)

### Teams Table Schema
```json
{
  "teamId": "uuid",
  "teamName": "Engineering Team",
  "inviteCode": "ABC123",
  "createdBy": "cognito-sub-uuid",
  "members": [
    {
      "userId": "cognito-sub-uuid",
      "email": "user@email.com",
      "role": "owner",
      "joinedAt": "2026-02-18T10:00:00Z"
    }
  ],
  "createdAt": "2026-02-18T10:00:00Z"
}
```

**Field Notes:**
- `inviteCode`: 6-character alphanumeric (uppercase + digits)
- `members.role`: owner | member
- Invite codes are permanent (no expiration)

---

## 🚀 DEPLOYMENT PROCEDURES

### Backend Deployment (Full Stack)
```bash
cd backend
sam build
sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --resolve-s3
```
**Duration:** 5-10 minutes  
**Validation:** `aws cloudformation describe-stacks --stack-name meetingmind-backend`

### Frontend Deployment (Full)
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete --region ap-south-1
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```
**Duration:** 2-3 minutes (+ 1-2 min for CloudFront propagation)  
**Validation:** Visit https://dcfx593ywvy92.cloudfront.net

### Quick Lambda Update (Single Function)
```bash
cd backend/functions/<function-name>
Compress-Archive -Path * -DestinationPath function.zip -Force
aws lambda update-function-code --function-name meetingmind-<function-name> --zip-file fileb://function.zip
```
**Duration:** 10-15 seconds  
**Note:** Windows PowerShell command (use `zip` on Linux/Mac)


---

## 🔐 ENVIRONMENT VARIABLES

### Backend (Lambda Functions)
Set in `backend/template.yaml` Globals.Function.Environment.Variables:
```yaml
MEETINGS_TABLE: meetingmind-meetings
TEAMS_TABLE: meetingmind-teams
AUDIO_BUCKET: meetingmind-audio-707411439284
REGION: ap-south-1
SNS_TOPIC_ARN: arn:aws:sns:ap-south-1:707411439284:meetingmind-reminders
FRONTEND_URL: https://dcfx593ywvy92.cloudfront.net
SES_FROM_EMAIL: thecyberprinciples@gmail.com
```

### Frontend (Vite Build)
Set in `frontend/.env.production`:
```bash
VITE_API_URL=https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod
VITE_USER_POOL_ID=ap-south-1_mkFJawjMp
VITE_USER_POOL_CLIENT_ID=150n899gkc651g6e0p7hacguac
```

---

## 🧪 TESTING

### Safe Tests (No AWS Marketplace Triggers)
```bash
# Comprehensive infrastructure test
python scripts/comprehensive-test-suite.py

# Test duplicate detection
python scripts/test-duplicate-detection.py

# Test Lambda directly
python scripts/test-lambda-direct.py

# Test API endpoint
python scripts/test-api-endpoint.py

# Backend unit tests
cd backend && python -m pytest tests/ -v
```

### ⚠️ DISABLED TESTS (DO NOT RUN)
These trigger AWS Marketplace subscription prompts for Bedrock:
- `scripts/test-aws-services.py.DISABLED`
- `scripts/check-bedrock-model-access.py.DISABLED`
- `scripts/detailed-bedrock-test.py.DISABLED`
- `scripts/monitor-bedrock-access.py.DISABLED`
- `scripts/resolve-bedrock-payment.py.DISABLED`

**Reason:** Each invocation triggers Bedrock marketplace validation.  
**See:** `scripts/BEDROCK_TESTS_DISABLED.txt` for full explanation.

---

## 🔴 CRITICAL ISSUES (Architecture Score: 72/100)

### Scalability Issues (High Priority)

**1. No Pagination in Multiple Lambdas**
- Affected: get-all-actions, list-meetings, get-debt-analytics
- Impact: Will fail with >1MB of data (DynamoDB limit)
- Fix: Implement LastEvaluatedKey pagination
- Severity: HIGH

**2. list-user-teams Uses SCAN**
- Impact: O(n) complexity, inefficient for large team counts
- Fix: Add userId-teamId GSI to teams table
- Severity: MEDIUM

**3. check-duplicate Scans All Meetings**
- Impact: O(n) complexity, slow with many meetings
- Fix: Add DynamoDB GSI for efficient embedding queries
- Severity: MEDIUM

### Security Issues (High Priority)

**4. No API Gateway Throttling**
- Impact: Vulnerable to abuse/DDoS attacks
- Fix: Add throttling limits in template.yaml (e.g., 1000 req/sec)
- Severity: HIGH

**5. No Virus Scanning on S3 Uploads**
- Impact: Malicious files can be uploaded
- Fix: Add S3 virus scanning (ClamAV Lambda or AWS solution)
- Severity: HIGH

**6. localStorage for Auth Tokens**
- Impact: XSS vulnerable (tokens accessible to JavaScript)
- Fix: Use httpOnly cookies for token storage
- Severity: MEDIUM

**7. Presigned URLs Expire in 3600s**
- Impact: 1-hour window is too long for security
- Fix: Reduce to 300s (5 minutes)
- Severity: LOW


### Observability Issues (Medium Priority)

**8. No CloudWatch Alarms**
- Impact: Blind to failures, no proactive monitoring
- Fix: Add alarms for Lambda errors, API 5xx, DynamoDB throttling
- Severity: HIGH

**9. No Optimistic Locking in update-action**
- Impact: Race conditions when multiple users update same action
- Fix: Add version field for optimistic locking
- Severity: MEDIUM

### Code Quality Issues (Medium Priority)

**10. Duplicate Utility Code Across Lambdas**
- Affected: decimal_to_float, cosine_similarity repeated in multiple functions
- Impact: Maintenance burden, inconsistency risk
- Fix: Create `backend/shared/utils.py` with shared utilities
- Severity: LOW

**11. Inline Lambda Code in template.yaml**
- Affected: S3NotificationSetupFunction (inline Python code)
- Impact: Untestable, no version control, hard to maintain
- Fix: Extract to proper function in `backend/functions/`
- Severity: MEDIUM

**12. 600+ Line process-meeting Function**
- Impact: Violates single responsibility principle, hard to test
- Fix: Split into modules (transcribe.py, analyze.py, risk.py, email.py)
- Severity: MEDIUM

---

## 📁 PROJECT STRUCTURE

```
meetingmind/
├── backend/
│   ├── functions/              # 18 Lambda functions
│   │   ├── process-meeting/    # ⚠️ CRITICAL - Main pipeline
│   │   ├── get-all-actions/
│   │   ├── check-duplicate/
│   │   ├── update-action/
│   │   ├── get-upload-url/
│   │   ├── list-meetings/
│   │   ├── get-meeting/
│   │   ├── get-debt-analytics/
│   │   ├── create-team/
│   │   ├── join-team/
│   │   ├── get-team/
│   │   ├── list-user-teams/
│   │   ├── send-reminders/
│   │   ├── daily-digest/
│   │   ├── pre-signup/
│   │   ├── post-confirmation/
│   │   ├── send-welcome-email/
│   │   └── dlq-handler/
│   ├── template.yaml           # ⚠️ CRITICAL - SAM infrastructure
│   ├── tests/
│   │   └── test_lambdas.py     # Unit tests (5/18 functions covered)
│   └── shared/                 # ⚠️ EMPTY - Should contain utils
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── KanbanBoard.jsx       # Drag-and-drop actions
│   │   │   ├── PatternCards.jsx      # Statistical analysis
│   │   │   ├── TeamSelector.jsx      # Team management
│   │   │   └── Leaderboard.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MeetingDetail.jsx
│   │   │   ├── ActionsOverview.jsx
│   │   │   ├── DebtDashboard.jsx
│   │   │   ├── Graveyard.jsx
│   │   │   └── LoginPage.jsx
│   │   ├── utils/
│   │   │   ├── api.js                # API client
│   │   │   └── auth.js               # Amplify auth
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.production
│   └── dist/                   # Build output (gitignored)
├── scripts/
│   ├── comprehensive-test-suite.py
│   ├── test-duplicate-detection.py
│   ├── approve-user.py
│   ├── clear-test-data.py
│   └── *.DISABLED              # 5 disabled Bedrock tests
├── docs/
│   ├── ARCHITECTURE.md         # Comprehensive architecture
│   ├── FEATURES.md
│   └── README.md
├── README.md                   # Project overview
├── COMMANDS.md                 # Deployment commands
├── DEPLOY.md                   # Deployment guide
├── deploy-frontend.sh          # Frontend deployment script
└── PROJECT_BOOTSTRAP.md        # ⚠️ THIS FILE - Single source of truth
```

---

## 🗑️ FILES TO DELETE (Phase 6 - After Extraction)

### Dead Code (Score: 0/100)
1. `backend/functions/notify-admin-signup/app.py` - Orphaned (not in template.yaml)
2. `backend/shared/` - Empty directory
3. `scripts/test-aws-services.py.DISABLED`
4. `scripts/check-bedrock-model-access.py.DISABLED`
5. `scripts/detailed-bedrock-test.py.DISABLED`
6. `scripts/monitor-bedrock-access.py.DISABLED`
7. `scripts/resolve-bedrock-payment.py.DISABLED`

### Documentation Bloat (Score: 30-40/100)
Move to `docs/archive/`:
1. `COMPREHENSIVE_CODEBASE_ANALYSIS.md` - Snapshot, outdated
2. `POST_DEPLOYMENT_TEST_REPORT.md` - Point-in-time report
3. `TEST_REPORT.md` - Redundant with above
4. `BEDROCK_ISSUE_ANALYSIS.md` - Historical issue (resolved)
5. `CODEBASE_REVIEW.md` - Snapshot review
6. `KANBAN_PRODUCTION_IMPROVEMENTS.md` - Extract to issues, then archive

**Total Files to Remove/Archive:** 13 files


---

## 🎯 NEXT STEPS (7-Phase Audit Process)

### ✅ Phase 1: Complete File Inventory - COMPLETE
- Categorized all 65+ files
- Identified core logic, infrastructure, deployment, config, docs, dead code

### ✅ Phase 2: File-by-File Deep Review - COMPLETE
- Scored every file (0-100)
- Provided action recommendations (Keep/Refactor/Merge/Remove)
- Identified 12 critical issues

### ✅ Phase 3: Extract Operational Truth - COMPLETE
- Documented all AWS resources with exact values
- Extracted deployment procedures
- Captured environment variables
- Identified data models

### ✅ Phase 4: Create PROJECT_BOOTSTRAP.md - COMPLETE
- This file is the single source of truth
- Contains 100% accurate operational details
- Ready for new sessions

### ⏳ Phase 5: Architecture Validation - NEXT
- [ ] Check for circular dependencies
- [ ] Identify redundant layers
- [ ] Security audit (IAM policies, CORS, auth flows)
- [ ] Anti-pattern detection (God objects, tight coupling)
- [ ] Performance bottlenecks

### ⏳ Phase 6: Cleanup - ONLY AFTER EXTRACTION
- [ ] Delete dead code (7 files)
- [ ] Create `docs/archive/` directory
- [ ] Move old documentation (6 files)
- [ ] Update `.gitignore` if needed
- [ ] Commit changes with clear message

### ⏳ Phase 7: Final Report
- [ ] Generate clean file tree
- [ ] List deleted files with reasons
- [ ] Architecture score breakdown
- [ ] Improvement roadmap with priorities
- [ ] Estimated effort for each fix

---

## 📞 SUPPORT & CONTACT

**AWS Account ID:** 707411439284  
**Primary Region:** ap-south-1 (Mumbai)  
**Contact Email:** thecyberprinciples@gmail.com  
**Built For:** AWS AIdeas Competition 2026

---

## 🔄 MAINTENANCE NOTES

### Regular Tasks
- **Daily:** Monitor CloudWatch logs for errors
- **Weekly:** Review DynamoDB capacity metrics
- **Monthly:** Audit S3 storage costs, clean old audio files
- **Quarterly:** Review and update dependencies

### Known Limitations
1. No multi-region support (single region: ap-south-1)
2. No real-time collaboration (polling-based updates)
3. No mobile apps (web-only)
4. No calendar integrations
5. No SSO/SAML support (email-only auth)
6. No audit logs (no compliance tracking)
7. No data export functionality
8. No API rate limiting per user
9. No webhook support
10. No custom branding/white-labeling

### Future Enhancements (Roadmap)
**Q1 2026:**
- Add pagination to all list endpoints
- Implement CloudWatch alarms
- Add API Gateway throttling
- Create shared utilities module

**Q2 2026:**
- Add virus scanning for uploads
- Implement optimistic locking
- Add real-time WebSocket updates
- Mobile-responsive improvements

**Q3 2026:**
- Multi-region deployment
- Advanced analytics dashboard
- Calendar integrations (Google, Outlook)
- Slack/Teams notifications

**Q4 2026:**
- Mobile apps (iOS, Android)
- SSO/SAML support
- Audit logs and compliance
- Custom branding

---

## 📚 ADDITIONAL DOCUMENTATION

**Primary Docs:**
- `README.md` - Project overview and quick start
- `docs/ARCHITECTURE.md` - Comprehensive technical architecture
- `COMMANDS.md` - All deployment and testing commands
- `DEPLOY.md` - Step-by-step deployment guide

**Archived Docs:**
- `docs/archive/` - Historical analysis and reports (after Phase 6)

**Code Documentation:**
- Lambda functions: Inline docstrings in each `app.py`
- Frontend components: JSDoc comments in React files
- SAM template: Inline comments in `template.yaml`

---

**END OF BOOTSTRAP DOCUMENT**

*This document is the single source of truth for MeetingMind. Update it whenever infrastructure, resources, or critical processes change.*
