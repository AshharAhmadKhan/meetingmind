# MeetingMind Architecture

Technical architecture documentation for the MeetingMind platform.

**Last Updated:** February 22, 2026

**See Also:** [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md) - Comprehensive visual diagrams of the system

## System Overview

MeetingMind is a serverless application built entirely on AWS services. It processes meeting audio through a multi-stage pipeline: upload → transcribe → analyze → store → notify.

## AWS Services (11 Total)

### Frontend Layer
- **S3**: Static website hosting for React build
- **CloudFront**: Global CDN for low-latency access
- **Cognito**: Email-based user authentication with JWT tokens

### API Layer
- **API Gateway**: RESTful API with Cognito authorizer
- **Lambda**: 18 serverless functions for business logic

### Data Layer
- **DynamoDB**: NoSQL database with pay-per-request billing
  - `meetingmind-meetings` table (userId + meetingId composite key)
  - `meetingmind-teams` table (teamId primary key)

### AI/ML Layer
- **Amazon Transcribe**: Speech-to-text with speaker diarization
- **Amazon Bedrock**: AI analysis with multi-model fallback
  - Claude Haiku (primary)
  - Nova Lite (fallback 1)
  - Nova Micro (fallback 2)
  - Intelligent mock (fallback 3)

### Notification Layer
- **SES**: Email notifications for meeting completion
- **SNS**: Scheduled reminders for action item deadlines
- **EventBridge**: Cron jobs for daily risk recalculation

## Lambda Functions

### Core Functions

**get-upload-url**
- Generates presigned S3 URL for direct browser upload
- Timeout: 30s | Memory: 256MB
- Avoids routing large files through API Gateway

**process-meeting**
- Main processing pipeline (transcribe → analyze → extract)
- Timeout: 900s | Memory: 512MB
- Handles S3 event trigger
- Multi-model AI fallback with graceful degradation
- X-Ray tracing with subsegments

**get-meeting**
- Retrieves single meeting details
- Timeout: 30s | Memory: 256MB
- Returns full meeting object with action items

**list-meetings**
- Lists all meetings for authenticated user
- Timeout: 60s | Memory: 256MB
- Sorted by createdAt descending

**get-all-actions**
- Aggregates action items across all meetings
- Timeout: 60s | Memory: 256MB
- Returns flattened list with meeting context
- Includes status field for Kanban board

**update-action**
- Updates action item status, owner, or deadline
- Timeout: 30s | Memory: 256MB
- Syncs completed field with status field

### Feature Functions

**get-debt-analytics**
- Calculates meeting debt metrics
- Timeout: 60s | Memory: 256MB
- Real-time calculation (no caching)

**check-duplicate**
- Finds duplicate action items using embeddings
- Timeout: 60s | Memory: 512MB
- Cosine similarity calculation
- Identifies chronic blockers (repeated 3+ times)

**send-reminders**
- Sends email reminders for approaching deadlines
- Timeout: 60s | Memory: 256MB
- Triggered by EventBridge daily at 9 AM

### Team Functions

**create-team**
- Creates new team with invite code
- Timeout: 30s | Memory: 256MB

**join-team**
- Adds user to team via invite code
- Timeout: 30s | Memory: 256MB

**get-team**
- Retrieves team details and members
- Timeout: 30s | Memory: 256MB

**list-user-teams**
- Lists all teams user belongs to
- Timeout: 30s | Memory: 256MB

### Auth Functions

**pre-signup**
- Cognito pre-signup trigger
- Auto-approves users (no admin approval required)
- Timeout: 30s | Memory: 256MB

**post-confirmation**
- Cognito post-confirmation trigger
- Creates user record in DynamoDB
- Timeout: 30s | Memory: 256MB

**send-welcome-email**
- Sends welcome email after signup
- Timeout: 30s | Memory: 256MB

### Infrastructure Functions

**dlq-handler**
- Processes failed messages from Dead Letter Queue
- Timeout: 60s | Memory: 256MB
- Logs errors and sends admin notifications

**daily-digest**
- Sends daily email digest to users
- Timeout: 60s | Memory: 256MB
- Triggered by EventBridge daily at 9 AM

## Data Model

### Meetings Table

```json
{
  "userId": "user@email.com",           // Partition key
  "meetingId": "uuid",                  // Sort key
  "title": "Q1 Planning Meeting",
  "status": "DONE",                     // PENDING | TRANSCRIBING | ANALYZING | DONE | FAILED
  "s3Key": "user-id__meeting-id__title.mp3",
  "transcript": "Full transcript text...",
  "summary": "Meeting summary...",
  "decisions": [
    "Launch beta on March 15",
    "Defer mobile app to v2"
  ],
  "actionItems": [
    {
      "id": "action-1",
      "task": "Finalize API documentation",
      "owner": "Ashhar",
      "deadline": "2026-02-25",
      "completed": false,
      "status": "todo",                 // todo | in_progress | blocked | done
      "completedAt": null,
      "riskScore": 45,
      "riskLevel": "MEDIUM",
      "createdAt": "2026-02-18T10:30:00Z",
      "embedding": [0.123, -0.456, ...]  // 1536 dimensions
    }
  ],
  "followUps": [
    "Confirm budget approval",
    "Schedule next milestone review"
  ],
  "roi": {
    "cost": 150.00,
    "value": 1200.00,
    "roi": 700.0,
    "decision_count": 2,
    "clear_action_count": 3,
    "meeting_duration_minutes": 30
  },
  "teamId": "team-uuid",                // Optional
  "email": "user@email.com",
  "createdAt": "2026-02-18T10:00:00Z",
  "updatedAt": "2026-02-18T10:35:00Z"
}
```

### Teams Table

```json
{
  "teamId": "uuid",                     // Partition key
  "name": "Engineering Team",
  "createdBy": "user@email.com",
  "members": [
    "user1@email.com",
    "user2@email.com"
  ],
  "inviteCode": "ABC123",               // 6-character code
  "createdAt": "2026-02-18T10:00:00Z",
  "updatedAt": "2026-02-18T10:00:00Z"
}
```

## Processing Pipeline

### 1. Upload Flow

```
User → React App → API Gateway → get-upload-url Lambda
                                       ↓
                                  Presigned S3 URL
                                       ↓
User → Browser → S3 (direct upload)
```

### 2. Processing Flow

```
S3 Event → process-meeting Lambda
              ↓
         Transcribe Audio (Amazon Transcribe)
              ↓
         Analyze Transcript (Amazon Bedrock)
              ↓
         Extract Structure (decisions, actions, follow-ups)
              ↓
         Generate Embeddings (Bedrock Titan)
              ↓
         Calculate Risk Scores
              ↓
         Calculate ROI
              ↓
         Store in DynamoDB
              ↓
         Send Email (SES)
```

### 3. Query Flow

```
User → React App → API Gateway → Lambda → DynamoDB
                                    ↓
                              JSON Response
                                    ↓
                              React App → UI Update
```

## AI Pipeline

### Multi-Model Fallback Strategy

**Tier 1: Amazon Transcribe**
- Converts audio to text with speaker labels
- Polls every 15 seconds until complete
- Fallback: Placeholder text if unavailable

**Tier 2: Bedrock Multi-Model**
- Claude Haiku (primary) → Nova Lite → Nova Micro
- Each model gets same prompt demanding JSON output
- Fallback: Next model if current fails

**Tier 3: Intelligent Mock**
- Analyzes meeting title keywords
- Generates contextually appropriate output
- Planning meetings → roadmap-style decisions
- Standups → blocker escalations
- Client meetings → proposal tasks
- Identical schema to Bedrock output

**Tier 4: Output Normalization**
- Ensures consistent schema across all tiers
- Assigns unique IDs to action items
- Normalizes null owners to "Unassigned"
- Validates deadline formats

### Prompt Engineering

```
Analyze this meeting and return ONLY valid JSON:
{
  "summary": "2-3 sentence summary",
  "decisions": ["decision 1"],
  "action_items": [{
    "id": "action-1",
    "task": "task description",
    "owner": "person name",
    "deadline": "YYYY-MM-DD or null",
    "completed": false
  }],
  "follow_ups": ["follow up item"]
}

Meeting: {title}
Date: {today}
Transcript: {transcript_text[:6000]}

Return ONLY JSON.
```

## Security

### Authentication
- Cognito JWT tokens in Authorization header
- Token expiration: 1 hour
- Refresh token: 30 days

### Authorization
- API Gateway Cognito authorizer on all endpoints
- User can only access their own data
- DynamoDB queries filtered by userId

### Data Protection
- S3 presigned URLs expire after 5 minutes
- CORS configured for CloudFront domain only
- No PII in CloudWatch logs
- Sensitive data redacted in X-Ray traces

## Performance

### Latency Targets
- Dashboard load: <2 seconds
- API response: <500ms
- Transcription: 2-5 minutes for 30-min meeting
- Embedding generation: <1 second per action item
- Risk calculation: <100ms per action item

### Scalability
- Lambda: 1000 concurrent executions (default)
- DynamoDB: Auto-scaling with pay-per-request
- CloudFront: Global edge locations
- S3: Unlimited storage

### Cost Optimization
- DynamoDB: Pay-per-request (no provisioned capacity)
- Lambda: Pay per invocation (no idle costs)
- S3: Lifecycle policies for old audio files
- CloudFront: Free tier covers most usage

## Monitoring

### X-Ray Tracing
- Enabled on all Lambda functions and API Gateway
- Subsegments: parse_event, transcribe_audio, bedrock_analysis, send_email_notification
- Distributed tracing across entire pipeline

### CloudWatch Logs
- All Lambda functions log to CloudWatch
- Log retention: 7 days
- Structured logging with JSON format

### CloudWatch Dashboard
- Lambda performance (invocations, errors, duration)
- API Gateway metrics (requests, 4xx/5xx, latency)
- DynamoDB metrics (read/write capacity, errors)
- Recent errors (last 20 from process-meeting)

## Deployment

### Infrastructure as Code
- AWS SAM template (template.yaml)
- CloudFormation stack: meetingmind-backend
- Automated resource provisioning

### CI/CD
- Manual deployment via SAM CLI
- Build: `sam build`
- Deploy: `sam deploy --stack-name meetingmind-backend --capabilities CAPABILITY_IAM --resolve-s3`

### Environment Variables
- Set in template.yaml Globals section
- Injected into all Lambda functions
- No secrets in code (use AWS Secrets Manager for production)

## Disaster Recovery

### Backup Strategy
- DynamoDB: Point-in-time recovery enabled
- S3: Versioning enabled on audio bucket
- Lambda: Code stored in S3 by SAM

### Failure Handling
- Lambda: Automatic retries (3 attempts)
- SQS: Dead Letter Queue for failed messages
- DLQ Handler: Processes failed messages and alerts admin
- Graceful degradation: Mock tier ensures system never fails completely

## Future Improvements

### Performance
- Add DynamoDB caching layer (ElastiCache)
- Implement GraphQL for efficient queries
- Add WebSocket support for real-time updates

### Scalability
- Add SQS queue between S3 and Lambda
- Implement Step Functions for orchestration
- Add OpenSearch for full-text search

### Features
- Multi-region deployment
- Real-time collaboration
- Mobile apps (iOS/Android)
- Calendar integrations
