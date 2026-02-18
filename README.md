# MeetingMind

AI-powered meeting intelligence platform that transforms audio into actionable insights. Built on AWS serverless architecture.

**Live Demo:** https://dcfx593ywvy92.cloudfront.net

## What It Does

- Transcribes meeting audio with speaker identification
- Extracts decisions, action items, and follow-ups using AI
- Tracks action item completion with risk prediction
- Detects duplicate work across meetings
- Identifies toxic meeting patterns
- Calculates meeting ROI and debt

## Quick Start

### Prerequisites

- AWS Account with credits activated
- AWS CLI configured
- SAM CLI installed
- Node.js 18+ and npm

### Deploy Backend

```bash
cd backend
sam build
sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --resolve-s3
```

### Deploy Frontend

```bash
cd frontend
npm install
npm run build
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

## Architecture

**AWS Services:** S3, Lambda, API Gateway, Transcribe, Bedrock, DynamoDB, Cognito, CloudFront, SES, SNS, EventBridge

**Frontend:** React 18 + Vite + React Router  
**Backend:** Python 3.11 + AWS SAM  
**AI:** Amazon Bedrock (Claude Haiku, Nova Lite, Nova Micro)

## Key Features

- **Kanban Board:** Drag-and-drop action item management
- **Risk Prediction:** AI-powered risk scores for each action item
- **Duplicate Detection:** Semantic similarity using embeddings
- **Meeting Debt:** Quantify cost of incomplete work
- **Pattern Analysis:** Identify toxic meeting patterns
- **Team Leaderboard:** Gamification with achievements

## Project Structure

```
meetingmind/
├── backend/              # AWS SAM application
│   ├── functions/        # Lambda functions
│   ├── template.yaml     # Infrastructure as code
│   └── tests/            # Backend tests
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── utils/        # API client & auth
│   └── dist/             # Build output
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── COMMANDS.md           # Deployment commands reference
```

## Documentation

- [COMMANDS.md](COMMANDS.md) - All deployment and testing commands
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture details
- [docs/FEATURES.md](docs/FEATURES.md) - Feature documentation
- [scripts/README.md](scripts/README.md) - Utility scripts guide

## Development

### Backend

```bash
cd backend
sam build
sam local start-api  # Test locally
```

### Frontend

```bash
cd frontend
npm run dev  # Development server on http://localhost:5173
```

## Testing

```bash
# Test AWS services
python scripts/test-aws-services.py

# Test duplicate detection
python scripts/test-duplicate-detection.py

# Comprehensive test suite
python scripts/comprehensive-test-suite.py
```

## Configuration

### AWS Resources

- **Region:** ap-south-1 (Mumbai)
- **Stack:** meetingmind-backend
- **S3 Bucket:** meetingmind-frontend-707411439284
- **CloudFront:** E3CAAI97MXY83V
- **User Pool:** ap-south-1_mkFJawjMp

### Environment Variables

Backend Lambda functions use these environment variables (set in template.yaml):
- `MEETINGS_TABLE`: meetingmind-meetings
- `TEAMS_TABLE`: meetingmind-teams
- `AUDIO_BUCKET`: meetingmind-audio-707411439284
- `FRONTEND_URL`: https://dcfx593ywvy92.cloudfront.net
- `SES_FROM_EMAIL`: thecyberprinciples@gmail.com
- `REGION`: ap-south-1

## License

MIT

## Contact

Built for AWS AIdeas Competition 2026
