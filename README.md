# MeetingMind

**AI-Powered Meeting Intelligence Platform**

[![AWS](https://img.shields.io/badge/AWS-14_Services-FF9900?logo=amazon-aws)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor%20Covenant-purple.svg)](CODE_OF_CONDUCT.md)

MeetingMind processes meeting audio to extract decisions, action items, and risk predictions using AWS serverless architecture. The system uses Amazon Transcribe for speech-to-text and Amazon Bedrock for analysis.

**Live Demo:** [dcfx593ywvy92.cloudfront.net](https://dcfx593ywvy92.cloudfront.net)

---

## Key Features

### The Graveyard
Action items abandoned for more than 30 days are moved to a "Graveyard" view with tombstones showing abandonment duration.

### AI Processing
- **Transcription:** Amazon Transcribe with speaker diarization
- **Analysis:** Multi-model fallback (Claude Haiku → Nova Lite → Nova Micro)
- **Duplicate Detection:** Semantic search using Titan Embeddings (1536-dim vectors)
- **Risk Prediction:** 4-factor algorithm (deadline proximity, owner assignment, task clarity, staleness)

### Analytics
- **Meeting Debt:** Calculates cost of incomplete actions based on $75/hour × estimated blocked time
- **Pattern Detection:** Identifies 5 recurring patterns (Planning Paralysis, Action Item Amnesia, etc.)
- **Team Leaderboard:** Weighted scoring with achievement tracking
- **Completion Tracking:** Progress monitoring against 67% industry benchmark

### UI Design
- Dark charcoal + lime green color scheme
- Playfair Display + DM Mono typography
- Drag-and-drop Kanban board
- Grain texture overlay

---

## Testing

**Test Coverage:** 36 automated tests covering infrastructure, APIs, features, security, and data integrity.

MeetingMind uses pre-commit hooks to run tests automatically before each commit. The full test suite executes in under 2 minutes.

### Quick Start
```bash
# Install git hooks (runs tests before commits)
./scripts/setup/install-git-hooks.sh  # Linux/Mac
.\scripts\setup\install-git-hooks.ps1  # Windows

# Run tests manually
python scripts/testing/run-ci-tests.py
```

See [docs/testing/TESTING.md](docs/testing/TESTING.md) for complete testing documentation.

---

## Architecture

**14 AWS Services | 18 Lambda Functions | Serverless**

```
Audio Upload → S3 → SQS → Lambda → Transcribe → Bedrock → DynamoDB → SES
                                      ↓
                                  CloudFront ← React SPA
```

### Tech Stack
- **Frontend:** React 19, Vite, React Router, AWS Amplify, React DnD
- **Backend:** Python 3.11, AWS SAM, Boto3
- **AI/ML:** Amazon Transcribe, Bedrock (Claude/Nova/Titan)
- **Data:** DynamoDB (pay-per-request), S3 (encrypted)
- **Auth:** Cognito (JWT tokens)
- **Notifications:** SES (email), SNS (reminders), EventBridge (cron)
- **Monitoring:** CloudWatch (12 alarms), X-Ray (tracing)

### AWS Services
S3 • Lambda • API Gateway • DynamoDB • Cognito • Transcribe • Bedrock • SES • SNS • SQS • EventBridge • CloudFront • CloudWatch • X-Ray

---

## Quick Start

### Prerequisites
- AWS Account with Bedrock access
- AWS CLI configured
- Python 3.11+
- Node.js 18+
- AWS SAM CLI

### Backend Deployment
```bash
cd backend
sam build
sam deploy --guided
```

### Frontend Deployment
```bash
cd frontend
cp .env.example .env.production
# Edit .env.production with your API Gateway URL and Cognito IDs
npm install
npm run build
aws s3 sync dist/ s3://YOUR_FRONTEND_BUCKET --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Detailed Instructions:** See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

---

## Project Structure

```
meetingmind/
├── backend/
│   ├── functions/          # 18 Lambda functions
│   │   ├── process-meeting/    # Main AI pipeline
│   │   ├── get-all-actions/    # Action aggregation
│   │   ├── check-duplicate/    # Semantic search
│   │   └── ...
│   ├── template.yaml       # SAM infrastructure
│   └── tests/              # Unit tests
├── frontend/
│   ├── src/
│   │   ├── components/     # Kanban, Leaderboard, Patterns
│   │   ├── pages/          # Dashboard, Graveyard, Debt
│   │   └── utils/          # API client, auth
│   ├── .env.example        # Environment template
│   └── package.json
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # Technical deep-dive
│   ├── FEATURES.md         # Feature documentation
│   ├── DEPLOY.md           # Deployment guide
│   └── PROJECT_BOOTSTRAP.md # Single source of truth
├── scripts/                # Utility scripts
└── README.md               # You are here
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/guides/AI_AGENT_HANDBOOK.md`](docs/guides/AI_AGENT_HANDBOOK.md) | For AI agents - architecture, common issues |
| [`docs/PROJECT_BOOTSTRAP.md`](docs/PROJECT_BOOTSTRAP.md) | Single source of truth - start here |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Technical architecture deep-dive |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Deployment guide |
| [`docs/testing/TESTING.md`](docs/testing/TESTING.md) | Testing procedures |

---

## Competition

**AWS AIdeas Competition 2026**
- **Category:** AI-Powered Productivity Tools
- **Timeline:** March 1-13 (article submission), March 13-20 (voting)

---

## Contributing

This is a competition entry. Feedback is welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Status

**Production Readiness:** 95/100  
**Feature Completeness:** All 11 core features functional  
**Test Coverage:** 36 automated tests  
**Last Updated:** February 20, 2026

**Recent Updates (Feb 19-20, 2026):**
- Phase 1-4 fixes complete (18 issues resolved)
- Team member access working (Kanban, Graveyard, Actions)
- Debt Dashboard showing real data
- View Team Invite Code feature added
- Health Score & ROI formulas verified
- Duplicate Detection documented
- Repository reorganized

---

## Contact

**Developer:** Ashhar Ahmad Khan  
**Email:** itzashhar@gmail.com  
**GitHub:** [github.com/AshharAhmadKhan](https://github.com/AshharAhmadKhan)  
**LinkedIn:** [linkedin.com/in/ashhar-ahmad-khan](https://www.linkedin.com/in/ashhar-ahmad-khan/)  
**AWS Account:** 707411439284  
**Region:** ap-south-1 (Mumbai)

---

## License

MIT License - see LICENSE file for details

---

Built using AWS Serverless
