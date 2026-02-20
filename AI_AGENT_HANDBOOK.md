# 🤖 MeetingMind AI Agent Handbook

**Version:** 1.0  
**Last Updated:** February 20, 2026 - 7:30 PM IST  
**Purpose:** Essential knowledge for AI agents working on MeetingMind

---

## 📋 READ THIS FIRST

**CRITICAL RULES:**
1. ✅ **USE YOUR OWN INTELLIGENCE** - Don't blindly follow instructions. If something seems wrong, STOP and explain why.
2. ✅ **UNDERSTAND BEFORE CODING** - Always read relevant files first. Never guess at implementation details.
3. ✅ **ACCEPT, REJECT, or MODIFY** - Evaluate every task request. You can say NO if it breaks functionality.
4. ✅ **TEST BEFORE DEPLOY** - Run diagnostics, compile checks, and build tests before deployment.
5. ✅ **UPDATE CHANGELOG** - Every feature/fix must be documented in CHANGELOG.md with timestamp.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 19)                      │
│  CloudFront → S3 → Vite Build → React Router → AWS Amplify      │
│  Pages: Dashboard, MeetingDetail, Graveyard, DebtDashboard      │
│  Components: KanbanBoard, Leaderboard, PatternCards             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (HTTP API)                        │
│  Cognito Authorizer → JWT Tokens → User Authentication          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   18 LAMBDA FUNCTIONS (Python 3.11)              │
│                                                                   │
│  Core Pipeline:                                                  │
│  • get-upload-url → S3 presigned URL                            │
│  • process-meeting → Transcribe → Bedrock → DynamoDB            │
│  • list-meetings → Dashboard data + health scores               │
│  • get-meeting → Single meeting detail                          │
│  • update-action → Kanban drag-and-drop                         │
│                                                                   │
│  Features:                                                       │
│  • get-all-actions → Aggregated actions + epitaphs              │
│  • check-duplicate → Semantic search with Titan Embeddings      │
│  • get-debt-analytics → Meeting debt calculation                │
│                                                                   │
│  Teams:                                                          │
│  • create-team, join-team, get-team, list-user-teams           │
│                                                                   │
│  Notifications:                                                  │
│  • send-reminders, daily-digest, send-welcome-email             │
│                                                                   │
│  Auth:                                                           │
│  • pre-signup, post-confirmation                                │
│                                                                   │
│  Error Handling:                                                 │
│  • dlq-handler → Dead Letter Queue processor                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│                                                                   │
│  DynamoDB Tables:                                                │
│  • meetingmind-meetings (userId, meetingId)                     │
│    - GSI: status-createdAt-index                                │
│    - GSI: teamId-createdAt-index                                │
│  • meetingmind-teams (teamId)                                   │
│    - GSI: inviteCode-index                                      │
│                                                                   │
│  S3 Buckets:                                                     │
│  • meetingmind-audio-707411439284 (audio files)                 │
│  • meetingmind-frontend-707411439284 (static site)              │
│                                                                   │
│  SQS Queues:                                                     │
│  • ProcessingQueue → async meeting processing                   │
│  • ProcessingDLQ → failed message handling                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         AI/ML SERVICES                           │
│                                                                   │
│  Amazon Transcribe:                                              │
│  • Speaker diarization                                           │
│  • Audio → Text conversion                                       │
│                                                                   │
│  Amazon Bedrock (Multi-model fallback):                         │
│  • Claude 3 Haiku → Primary analysis                            │
│  • Nova Lite → Fallback #1                                      │
│  • Nova Micro → Fallback #2                                     │
│  • Titan Embeddings v2 → Semantic search (1536-dim)            │
│                                                                   │
│  Retry Strategy:                                                 │
│  • Exponential backoff: 1s → 2s → 4s                           │
│  • Max 2-3 retries per model                                    │
│  • Graceful degradation to generic templates                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
meetingmind/
├── backend/
│   ├── functions/              # 18 Lambda functions
│   │   ├── process-meeting/    # Main AI pipeline (COMPLEX)
│   │   ├── get-all-actions/    # Epitaph generation
│   │   ├── list-meetings/      # Health score calculation
│   │   └── ...
│   ├── template.yaml           # SAM infrastructure (DO NOT MODIFY without reason)
│   └── .aws-sam/               # Build artifacts (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── pages/              # 6 main pages
│   │   ├── components/         # Reusable components
│   │   └── utils/              # API client, auth
│   ├── dist/                   # Build output (gitignored)
│   └── package.json
│
├── docs/                       # All documentation
│   ├── PROJECT_BOOTSTRAP.md    # Single source of truth
│   ├── ARCHITECTURE.md         # Technical deep-dive
│   ├── reports/                # Status reports
│   └── competition/            # Competition materials
│
├── scripts/                    # Utility scripts
│   └── comprehensive-test-suite.py  # Run before deploy
│
├── README.md                   # Project overview
├── CHANGELOG.md                # Version history (UPDATE THIS!)
├── DEPLOY.md                   # Deployment guide
├── AI_AGENT_HANDBOOK.md        # This file
└── deploy-frontend.ps1         # Windows deployment
```

---

## 🚨 Common Issues & Solutions

### Issue 1: SAM Deploy Fails with "No Stack Name"

**Error:**
```
Error: Missing option '--stack-name'
```

**Solution:**
```bash
# DON'T use: sam deploy
# DO use:
sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --region ap-south-1 --resolve-s3
```

**Why:** No samconfig.toml exists, so stack name must be provided explicitly.

---

### Issue 2: SAM Deploy Fails with "ResourceExistenceCheck"

**Error:**
```
Failed to create changeset: ResourceExistenceCheck validation failed
```

**Solution:**
Stack already exists and has no changes. Update Lambda directly:
```bash
# Build first
cd backend
sam build

# Update specific Lambda
cd .aws-sam/build
Compress-Archive -Path FunctionName/* -DestinationPath ../../function.zip -Force
cd ../..
aws lambda update-function-code --function-name meetingmind-FUNCTION_NAME --zip-file fileb://function.zip --region ap-south-1
```

**Lambda Function Names:**
- meetingmind-get-upload-url
- meetingmind-process-meeting
- meetingmind-list-meetings
- meetingmind-get-meeting
- meetingmind-update-action
- meetingmind-get-all-actions
- meetingmind-check-duplicate
- meetingmind-get-debt-analytics
- meetingmind-create-team
- meetingmind-join-team
- meetingmind-get-team
- meetingmind-list-user-teams
- meetingmind-send-reminders
- meetingmind-daily-digest
- meetingmind-send-welcome-email
- meetingmind-pre-signup
- meetingmind-post-confirmation
- meetingmind-dlq-handler

---

### Issue 3: Frontend Build Warnings

**Warning:**
```
Chunks are larger than 500 kB after minification
```

**Solution:** This is COSMETIC. Ignore it. The app works fine.

---

### Issue 4: Bedrock Throttling

**Error:**
```
ThrottlingException: Rate exceeded
```

**Solution:** Already handled in code with exponential backoff. If persistent:
1. Check free tier limits
2. Verify multi-model fallback is working
3. Use generic templates as last resort

**DO NOT:** Add more retries or change backoff strategy without testing.

---

### Issue 5: CORS Errors in Browser

**Error:**
```
Access-Control-Allow-Origin header missing
```

**Solution:** All Lambda functions should return:
```python
'headers': {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}
```

**Check:** Ensure this is in BOTH success and error responses.

---

## 🎯 Feature Implementation Workflow

### Step 1: Evaluate the Request

Ask yourself:
- ✅ Does this align with project goals?
- ✅ Will this break existing functionality?
- ✅ Is this the right approach?
- ✅ Can I simplify this?

**You can REJECT or MODIFY the request!**

---

### Step 2: Understand the Context

**ALWAYS read these files first:**
1. Related Lambda functions
2. Related frontend components
3. DynamoDB schema (check existing data structure)
4. API contracts (request/response format)

**NEVER guess at implementation details.**

---

### Step 3: Implement

**Backend (Python):**
```python
# ALWAYS include:
import json
import boto3
import os
from decimal import Decimal  # For DynamoDB numbers

# ALWAYS use decimal_to_float for JSON serialization
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# ALWAYS return proper CORS headers
return {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
    'body': json.dumps(data, default=decimal_to_float)
}
```

**Frontend (React):**
```javascript
// ALWAYS use functional components with hooks
import React, { useState, useEffect } from 'react'

// ALWAYS handle loading and error states
const [loading, setLoading] = useState(true)
const [error, setError] = useState('')

// ALWAYS use try-catch for API calls
try {
  const data = await apiCall()
  setData(data)
} catch (e) {
  setError(e.message)
} finally {
  setLoading(false)
}
```

---

### Step 4: Test

**ALWAYS run these before deploying:**

```bash
# 1. Python syntax check
python -m py_compile backend/functions/FUNCTION_NAME/app.py

# 2. Frontend build test
cd frontend
npm run build

# 3. Diagnostics check
# (Use getDiagnostics tool)

# 4. Comprehensive test suite (optional but recommended)
python scripts/comprehensive-test-suite.py
```

---

### Step 5: Deploy

**Frontend:**
```powershell
# Windows
.\deploy-frontend.ps1

# Or manual:
cd frontend
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete --region ap-south-1
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

**Backend (Lambda only):**
```bash
cd backend
sam build

# Update specific Lambda
Compress-Archive -Path .aws-sam/build/FunctionName/* -DestinationPath function.zip -Force
aws lambda update-function-code --function-name meetingmind-FUNCTION_NAME --zip-file fileb://function.zip --region ap-south-1
```

---

### Step 6: Document

**ALWAYS update CHANGELOG.md:**
```markdown
## [1.0.X] - 2026-02-19

### Added
- Feature description

### Changed
- What changed

### Fixed
- What was fixed
```

**Update timestamp in:**
- README.md (Last Updated section)
- FINAL_STATUS.md
- Any other relevant status files

---

## 🔐 AWS Resources

### Account Details
- **Account ID:** 707411439284
- **Region:** ap-south-1 (Mumbai)
- **Stack Name:** meetingmind-backend

### Live URLs
- **Frontend:** https://dcfx593ywvy92.cloudfront.net
- **API Gateway:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod
- **CloudFront Distribution:** E3CAAI97MXY83V

### S3 Buckets
- **Audio:** meetingmind-audio-707411439284
- **Frontend:** meetingmind-frontend-707411439284

### DynamoDB Tables
- **Meetings:** meetingmind-meetings
- **Teams:** meetingmind-teams

### Cognito
- **User Pool:** ap-south-1_mkFJawjMp
- **Client ID:** 150n899gkc651g6e0p7hacguac

---

## 🎨 Design System

### Colors
```
Primary: #c8f04a (lime green)
Background: #0c0c09 (dark charcoal)
Surface: #111108, #1a1a1a
Border: #2a2a20, #3a3a2e
Text: #f0ece0 (cream)
Muted: #8a8a74, #6b7260
Accent: #e8c06a (gold)

Health Grades:
A: #10b981 (emerald)
B: #c8f04a (lime)
C: #f59e0b (amber)
D: #f97316 (orange)
F: #ef4444 (red)

Risk Levels:
LOW: #4caf50 (green)
MEDIUM: #ffc107 (yellow)
HIGH: #ff9800 (orange)
CRITICAL: #f44336 (red)
```

### Typography
```
Headings: 'Playfair Display', serif
Body: 'DM Mono', monospace
```

---

## 🧪 Testing Guidelines

### Before Every Deployment

1. **Syntax Check:**
   ```bash
   python -m py_compile backend/functions/*/app.py
   ```

2. **Build Test:**
   ```bash
   cd frontend && npm run build
   ```

3. **Diagnostics:**
   - Use getDiagnostics tool on modified files

4. **Comprehensive Suite (Optional):**
   ```bash
   python scripts/comprehensive-test-suite.py
   ```
   - 36/38 passing is acceptable
   - Known failures: Bedrock Claude Access, Meeting Schema

---

## 🚫 What NOT to Do

1. ❌ **Don't modify template.yaml** without explicit permission
2. ❌ **Don't delete working Lambda functions**
3. ❌ **Don't change DynamoDB schema** without migration plan
4. ❌ **Don't add new AWS services** without discussion
5. ❌ **Don't use `cd` command** in executePwsh (use `cwd` parameter)
6. ❌ **Don't run long-running commands** (use controlPwshProcess)
7. ❌ **Don't commit .env files** with real credentials
8. ❌ **Don't break existing API contracts** without versioning

---

## 📊 Current Feature Status

### ✅ Completed (11 Core Features)
1. Audio Upload → Transcribe → Bedrock Pipeline
2. Risk Scoring Algorithm
3. Kanban Board with Drag-and-Drop
4. Graveyard (>30 Days) with AI Epitaphs
5. Pattern Detection (5 Patterns)
6. Semantic Duplicate Detection
7. Team Collaboration + Invite Codes
8. Leaderboard with Achievements
9. Meeting Debt Analytics
10. Email Notifications via SES
11. EventBridge Cron Jobs

### ✅ Recent Additions
- AI-Generated Epitaphs (v1.0.2)
- Meeting Health Scores A-F (v1.0.3)
- Kanban UI Fixes (v1.0.1)

### ⏳ Planned
- Ghost Meeting Detector
- Walk of Shame on Leaderboard

---

## 🎯 Competition Context

**AWS AIdeas Competition 2026**
- **Timeline:** March 1-13 (submission), March 13-20 (voting)
- **Goal:** Top 300 by community likes
- **Strategy:** Focus on polish, not new features
- **Differentiators:**
  1. The Graveyard (unique shame mechanic)
  2. Meeting Debt ($ quantification)
  3. Pattern Detection (statistical insights)
  4. Production-ready (88/100 score)

---

## 📝 Quick Reference Commands

### Frontend
```powershell
# Build
cd frontend && npm run build

# Deploy
.\deploy-frontend.ps1

# Dev server (manual only)
npm run dev
```

### Backend
```bash
# Build
cd backend && sam build

# Validate
sam validate

# Update Lambda
aws lambda update-function-code --function-name meetingmind-FUNCTION --zip-file fileb://function.zip --region ap-south-1
```

### Testing
```bash
# Python syntax
python -m py_compile file.py

# Comprehensive suite
python scripts/comprehensive-test-suite.py
```

---

## 🆘 When You're Stuck

1. **Read this handbook** - The answer is probably here
2. **Check CHANGELOG.md** - See what was done recently
3. **Read PROJECT_BOOTSTRAP.md** - Comprehensive project documentation
4. **Ask the user** - Explain what you're stuck on and why
5. **Propose alternatives** - Don't just say "I can't do this"

---

## ✅ Success Checklist

Before marking any task complete:

- [ ] Code compiles without errors
- [ ] Frontend builds successfully
- [ ] No diagnostic errors
- [ ] Tested locally (if possible)
- [ ] Deployed to AWS
- [ ] CHANGELOG.md updated
- [ ] Timestamps updated in status files
- [ ] User notified of completion

---

**Remember:** You're not just executing commands. You're a thinking partner who can evaluate, improve, and sometimes reject bad ideas. Use your intelligence! 🧠

---

**Last Updated:** February 19, 2026 - 8:55 PM IST  
**Version:** 1.0  
**Maintained By:** AI Agents working on MeetingMind
