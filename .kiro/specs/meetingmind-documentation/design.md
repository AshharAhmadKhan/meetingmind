# Design Document

## Overview

MeetingMind is a serverless meeting intelligence platform built entirely on AWS managed services. The system follows an event-driven architecture where audio uploads trigger an automated processing pipeline that transcribes audio and extracts actionable intelligence using AI. The platform consists of three main layers:

1. **Frontend Layer**: React single-page application with AWS Amplify for authentication
2. **API Layer**: API Gateway with Cognito authorizer routing to Lambda functions
3. **Processing Layer**: Event-driven Lambda functions orchestrating AWS Transcribe and Amazon Bedrock

The architecture prioritizes serverless scalability, cost efficiency, and resilience through fallback mechanisms.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Dashboard   │  │ MeetingDetail│  │   LoginPage          │  │
│  │  - Upload    │  │ - Summary    │  │   - Cognito Auth     │  │
│  │  - List      │  │ - Actions    │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTPS + JWT
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway + Cognito                         │
│  POST /upload-url  │  GET /meetings  │  PUT /actions/{id}       │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Lambda Functions                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │get-upload-url│  │list-meetings │  │  update-action       │  │
│  │get-meeting   │  │send-reminders│  │  process-meeting     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Storage Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  DynamoDB    │  │  S3 Bucket   │  │  SNS Topic           │  │
│  │  (Meetings)  │  │  (Audio)     │  │  (Reminders)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Services                                 │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐ │
│  │AWS Transcribe│  │  Amazon Bedrock (Claude/Nova)            │ │
│  └──────────────┘  └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Processing Pipeline Flow


```
User Upload → Presigned URL → S3 Upload → S3 Event → Lambda Trigger
                                                            │
                                                            ▼
                                                    Update: TRANSCRIBING
                                                            │
                                                            ▼
                                                    AWS Transcribe Job
                                                    (Speaker Labeling)
                                                            │
                                                            ▼
                                                    Update: ANALYZING
                                                            │
                                                            ▼
                                            ┌───────────────┴───────────────┐
                                            │   Amazon Bedrock Analysis     │
                                            │   Try: Claude Haiku           │
                                            │   Fallback: Nova Lite         │
                                            │   Fallback: Nova Micro        │
                                            │   Fallback: Mock Analysis     │
                                            └───────────────┬───────────────┘
                                                            │
                                                            ▼
                                                    Update: DONE
                                                    Store: Summary, Decisions,
                                                           Actions, Follow-ups
```

### Data Flow Patterns

1. **Upload Flow**: Frontend → get-upload-url Lambda → DynamoDB (PENDING) → Presigned URL → Frontend → S3
2. **Processing Flow**: S3 Event → process-meeting Lambda → Transcribe → Bedrock → DynamoDB (DONE)
3. **Retrieval Flow**: Frontend → list-meetings/get-meeting Lambda → DynamoDB → Frontend
4. **Action Update Flow**: Frontend → update-action Lambda → DynamoDB → Frontend
5. **Reminder Flow**: EventBridge Schedule → send-reminders Lambda → DynamoDB Query → SNS Publish

## Components and Interfaces

### Frontend Components

#### Dashboard Component
- **Purpose**: Main interface for viewing meetings and uploading new recordings
- **State Management**: 
  - `meetings`: Array of meeting objects
  - `uploading`: Boolean upload state
  - `uploadPct`: Upload progress percentage (0-100)
  - `dragOver`: Boolean drag-and-drop state
- **Key Functions**:
  - `fetchMeetings()`: Polls backend every 8 seconds for meeting updates
  - `handleFile(file)`: Orchestrates upload flow (request URL → upload to S3 → refresh list)
  - `onDrop(e)`: Handles drag-and-drop file events
- **UI Features**:
  - Real-time status indicators with color coding
  - Animated waveform bars for processing meetings
  - Progress bars for transcription/analysis stages
  - Empty state with ghost UI for first-time users

#### MeetingDetail Component
- **Purpose**: Displays comprehensive meeting analysis and action tracking
- **State Management**:
  - `meeting`: Full meeting object with analysis
  - `loading`: Boolean loading state
  - `error`: Error message string
- **Key Functions**:
  - `toggleAction(id, current)`: Updates action item completion status
  - `dlInfo(deadline)`: Calculates deadline urgency and color coding
  - `fmtDate(iso)`: Formats ISO dates for display
- **UI Sections**:
  - Hero: Title, summary, statistics (actions/decisions/follow-ups count)
  - Progress bar: Visual completion percentage
  - Action items: Interactive checkboxes with deadline indicators
  - Decisions: Numbered list with visual separators
  - Follow-ups: Secondary list for future items
  - Transcript: Scrollable pre-formatted text

#### LoginPage Component
- **Purpose**: Handles user authentication via AWS Cognito
- **Authentication Flow**:
  1. User enters email and password
  2. Call `signIn()` from aws-amplify/auth
  3. Store session in localStorage
  4. Redirect to dashboard

### Backend Lambda Functions



#### get-upload-url Function
- **Trigger**: API Gateway POST /upload-url
- **Input**: `{ title: string, contentType: string, fileSize: number }`
- **Process**:
  1. Extract userId from Cognito JWT claims (sub field)
  2. Validate file type against ALLOWED_TYPES map
  3. Validate file size ≤ 500MB
  4. Generate unique meetingId (UUID v4)
  5. Construct S3 key: `audio/{userId}__{meetingId}__{title}.{ext}`
  6. Generate presigned URL with 3600s expiration
  7. Force regional endpoint in URL (replace global with regional)
  8. Create DynamoDB record with status PENDING
- **Output**: `{ meetingId: string, uploadUrl: string, s3Key: string }`
- **Error Handling**: Returns 400 for invalid file type/size, 500 for internal errors

#### process-meeting Function
- **Trigger**: S3 ObjectCreated event (audio/ prefix)
- **Timeout**: 900 seconds (15 minutes)
- **Memory**: 512MB
- **Process**:
  1. Parse S3 event to extract bucket, key, userId, meetingId
  2. Update status to TRANSCRIBING
  3. Start AWS Transcribe job with speaker labeling (max 5 speakers)
  4. Poll transcription job every 15 seconds (max 48 iterations = 12 minutes)
  5. Extract transcript text from Transcribe output JSON
  6. Update status to ANALYZING
  7. Attempt Bedrock analysis with model fallback chain
  8. If all Bedrock models fail, generate mock analysis based on title keywords
  9. Normalize action items (assign IDs, handle null owners/deadlines)
  10. Update status to DONE with full analysis
- **Fallback Logic**:
  - Transcribe failure → Use placeholder transcript
  - Bedrock failure → Generate mock analysis with realistic data
- **Error Handling**: Sets status to FAILED and stores error message

#### list-meetings Function
- **Trigger**: API Gateway GET /meetings
- **Input**: userId from Cognito claims
- **Process**:
  1. Query DynamoDB with userId as partition key
  2. Sort by createdAt descending
  3. Return all meetings with summary (exclude full transcript)
- **Output**: `{ meetings: Array<Meeting> }`

#### get-meeting Function
- **Trigger**: API Gateway GET /meetings/{meetingId}
- **Input**: meetingId from path, userId from Cognito claims
- **Process**:
  1. Get item from DynamoDB with userId + meetingId composite key
  2. Return full meeting details including decisions, actions, follow-ups
  3. Exclude raw transcript from response (performance optimization)
- **Output**: `Meeting` object

#### update-action Function
- **Trigger**: API Gateway PUT /meetings/{meetingId}/actions/{actionId}
- **Input**: `{ completed: boolean }`
- **Process**:
  1. Get meeting from DynamoDB
  2. Find action item by actionId
  3. Update completed field
  4. Write updated meeting back to DynamoDB
- **Output**: `{ success: boolean }`

#### send-reminders Function
- **Trigger**: EventBridge Schedule (cron: 0 8 * * ? * - daily at 8 AM UTC)
- **Process**:
  1. Scan DynamoDB for all meetings with status DONE
  2. Filter action items with deadlines within notification window
  3. For each matching action, publish SNS message with:
     - Meeting title
     - Action task description
     - Owner name
     - Deadline date
- **Output**: SNS message count

## Data Models

### DynamoDB Schema

**Table Name**: meetingmind-meetings  
**Billing Mode**: PAY_PER_REQUEST  
**Key Schema**:
- **HASH Key**: userId (String) - Cognito user sub
- **RANGE Key**: meetingId (String) - UUID v4

**Attributes**:
```typescript
interface Meeting {
  userId: string;           // Partition key
  meetingId: string;        // Sort key
  title: string;            // User-provided or filename
  status: 'PENDING' | 'TRANSCRIBING' | 'ANALYZING' | 'DONE' | 'FAILED';
  s3Key: string;            // S3 object key for audio file
  createdAt: string;        // ISO 8601 timestamp
  updatedAt: string;        // ISO 8601 timestamp
  email: string;            // User email from Cognito
  transcript?: string;      // First 5000 chars (optional)
  summary?: string;         // AI-generated summary (optional)
  decisions?: string[];     // Array of decision strings (optional)
  actionItems?: ActionItem[]; // Array of action objects (optional)
  followUps?: string[];     // Array of follow-up strings (optional)
  errorMessage?: string;    // Error details if FAILED (optional)
}

interface ActionItem {
  id: string;               // Format: "action-N"
  task: string;             // Task description
  owner: string;            // Person responsible (or "Unassigned")
  deadline: string | null;  // ISO date string or null
  completed: boolean;       // Completion status
}
```

### S3 Storage

**Bucket Name**: meetingmind-audio-{AWS::AccountId}  
**Key Format**: `audio/{userId}__{meetingId}__{title}.{ext}`  
**Lifecycle Policy**: Delete objects after 30 days  
**CORS Configuration**: Allow all origins, GET/PUT/POST/HEAD methods

### API Request/Response Models



**POST /upload-url**
```typescript
Request: {
  title: string;
  contentType: string;  // MIME type
  fileSize: number;     // Bytes
}

Response: {
  meetingId: string;
  uploadUrl: string;    // Presigned S3 URL
  s3Key: string;
}
```

**GET /meetings**
```typescript
Response: {
  meetings: Array<{
    meetingId: string;
    title: string;
    status: string;
    createdAt: string;
    updatedAt: string;
    summary?: string;
  }>
}
```

**GET /meetings/{meetingId}**
```typescript
Response: Meeting  // Full object with analysis
```

**PUT /meetings/{meetingId}/actions/{actionId}**
```typescript
Request: {
  completed: boolean;
}

Response: {
  success: boolean;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication Properties

**Property 1: Invalid credentials rejection**  
*For any* invalid email/password combination, authentication should fail and return an error message without issuing tokens.  
**Validates: Requirements 1.3**

**Property 2: Session persistence**  
*For any* valid authentication token stored in localStorage, retrieving it should return the same token value.  
**Validates: Requirements 1.4**

### Upload Properties

**Property 3: Supported file type acceptance**  
*For any* file with MIME type in [audio/mpeg, audio/wav, audio/m4a, audio/mp4, audio/webm], the system should accept the upload request and generate a presigned URL.  
**Validates: Requirements 2.1**

**Property 4: Presigned URL generation**  
*For any* valid upload request, the generated presigned URL should contain the regional S3 endpoint and have a valid signature.  
**Validates: Requirements 2.2, 2.8**

**Property 5: Unsupported file type rejection**  
*For any* file with MIME type not in the supported list, the system should reject the upload and return an error.  
**Validates: Requirements 2.4**

**Property 6: DynamoDB record creation**  
*For any* successful presigned URL generation, a DynamoDB record with status PENDING should exist for that meetingId.  
**Validates: Requirements 2.5**

**Property 7: Upload progress tracking**  
*For any* file upload in progress, the displayed progress percentage should be between 0 and 100 inclusive.  
**Validates: Requirements 2.7**

### Processing Pipeline Properties

**Property 8: Status transition to TRANSCRIBING**  
*For any* meeting that begins transcription, its status should change from PENDING to TRANSCRIBING.  
**Validates: Requirements 3.2**

**Property 9: Status transition to ANALYZING**  
*For any* meeting where transcription completes successfully, its status should change from TRANSCRIBING to ANALYZING.  
**Validates: Requirements 3.4**

**Property 10: Bedrock fallback chain**  
*For any* meeting analysis attempt, if Claude Haiku fails, the system should try Nova Lite, then Nova Micro, then mock analysis.  
**Validates: Requirements 3.5**

**Property 11: Mock analysis generation**  
*For any* meeting where all Bedrock models fail, the system should generate mock analysis containing summary, decisions, actionItems, and followUps fields.  
**Validates: Requirements 3.6**

**Property 12: Status transition to DONE**  
*For any* meeting where analysis completes successfully, its status should change from ANALYZING to DONE.  
**Validates: Requirements 3.7**

**Property 13: Error status on failure**  
*For any* meeting where processing fails at any stage, its status should be set to FAILED and an errorMessage should be stored.  
**Validates: Requirements 3.8**

**Property 14: Transcript truncation**  
*For any* transcript stored in DynamoDB, its length should not exceed 5000 characters.  
**Validates: Requirements 3.9, 12.5**

### AI Analysis Properties

**Property 15: Summary extraction**  
*For any* completed meeting analysis, the summary field should exist and contain text.  
**Validates: Requirements 4.1**

**Property 16: Decisions extraction**  
*For any* completed meeting analysis, the decisions field should exist as an array (may be empty).  
**Validates: Requirements 4.2**

**Property 17: Action item structure**  
*For any* action item in a completed meeting, it should have id, task, owner, deadline, and completed fields.  
**Validates: Requirements 4.3**

**Property 18: Follow-ups extraction**  
*For any* completed meeting analysis, the followUps field should exist as an array (may be empty).  
**Validates: Requirements 4.4**

**Property 19: Unassigned owner default**  
*For any* action item with null or missing owner, the owner field should be set to "Unassigned".  
**Validates: Requirements 4.5**

**Property 20: Null deadline handling**  
*For any* action item with no specified deadline, the deadline field should be null.  
**Validates: Requirements 4.6**

**Property 21: Unique action IDs**  
*For any* meeting with multiple action items, all action item IDs should be unique and follow the format "action-N".  
**Validates: Requirements 4.7**

**Property 22: JSON serialization round trip**  
*For any* valid analysis object, serializing to JSON then deserializing should produce an equivalent object.  
**Validates: Requirements 4.8**

### Meeting Retrieval Properties

**Property 23: Meeting list sorting**  
*For any* user's meeting list, meetings should be ordered by createdAt timestamp in descending order (newest first).  
**Validates: Requirements 5.1**

**Property 24: Meeting list fields**  
*For any* meeting in the list response, it should include meetingId, title, status, createdAt, updatedAt, and summary fields.  
**Validates: Requirements 5.2**

**Property 25: Status display**  
*For any* meeting displayed in the UI, its status should be one of [PENDING, TRANSCRIBING, ANALYZING, DONE, FAILED].  
**Validates: Requirements 5.3**

**Property 26: Meeting detail completeness**  
*For any* single meeting retrieval, the response should include decisions, actionItems, and followUps arrays.  
**Validates: Requirements 5.4**

**Property 27: Transcript exclusion from list**  
*For any* meeting in the list response, the transcript field should not be present.  
**Validates: Requirements 5.5**

### Action Management Properties

**Property 28: Action completion toggle**  
*For any* action item toggle operation, the completed field should change from its current value to the opposite boolean value.  
**Validates: Requirements 6.1**

**Property 29: Completion percentage calculation**  
*For any* meeting with N total actions and C completed actions, the displayed percentage should equal (C / N) × 100 rounded to nearest integer.  
**Validates: Requirements 6.2**

**Property 30: Completed action styling**  
*For any* completed action item, it should have reduced opacity and strikethrough text decoration applied.  
**Validates: Requirements 6.3**

**Property 31: Overdue deadline color**  
*For any* action item with deadline before current date, it should display with red color (#e87a6a).  
**Validates: Requirements 6.4**

**Property 32: Warning deadline color**  
*For any* action item with deadline within 3 days of current date, it should display with yellow color (#e8c06a).  
**Validates: Requirements 6.5**

**Property 33: Future deadline color**  
*For any* action item with deadline more than 3 days from current date, it should display with green color (#c8f04a).  
**Validates: Requirements 6.6**

### Reminder Properties

**Property 34: Deadline filtering**  
*For any* reminder scan, only action items with deadlines within the notification window should be selected.  
**Validates: Requirements 7.2**

**Property 35: SNS message publishing**  
*For any* action item with approaching deadline, an SNS message should be published to the reminder topic.  
**Validates: Requirements 7.3**

**Property 36: Reminder message content**  
*For any* reminder message, it should include meeting title, action task, owner, and deadline fields.  
**Validates: Requirements 7.4**

### Storage Properties

**Property 37: S3 key format**  
*For any* audio file stored in S3, its key should match the pattern `audio/{userId}__{meetingId}__{title}.{ext}`.  
**Validates: Requirements 8.3**

### Security Properties

**Property 38: Authentication requirement**  
*For any* API endpoint except OPTIONS, unauthenticated requests should be rejected with 401 status.  
**Validates: Requirements 9.1**

**Property 39: UserId extraction**  
*For any* authenticated request, the userId should be extracted from the JWT sub claim.  
**Validates: Requirements 9.2**

**Property 40: CORS header presence**  
*For any* API response, it should include Access-Control-Allow-Origin, Access-Control-Allow-Headers, and Access-Control-Allow-Methods headers.  
**Validates: Requirements 9.3, 9.5**

**Property 41: HTTP method support**  
*For any* API endpoint, it should accept GET, POST, PUT, and OPTIONS methods as appropriate.  
**Validates: Requirements 9.4**

### UI Properties

**Property 42: Processing status indicators**  
*For any* meeting with status TRANSCRIBING or ANALYZING, visual indicators (colors, progress bars) should be displayed.  
**Validates: Requirements 10.2**

**Property 43: Waveform animation**  
*For any* meeting with processing status, animated waveform bars should be visible.  
**Validates: Requirements 10.3**

**Property 44: Empty state display**  
*For any* user with zero meetings, the empty state with ghost UI should be rendered.  
**Validates: Requirements 10.7**

**Property 45: Upload progress display**  
*For any* file upload in progress, the percentage indicator should update to reflect transfer progress.  
**Validates: Requirements 10.8**

### Error Handling Properties

**Property 46: Bedrock fallback to mock**  
*For any* meeting where Bedrock is unavailable, mock analysis should be generated based on title keywords.  
**Validates: Requirements 11.1**

**Property 47: Transcribe fallback to placeholder**  
*For any* meeting where Transcribe fails, placeholder transcript text should be used.  
**Validates: Requirements 11.2**

**Property 48: Error message display**  
*For any* failed API request, a user-friendly error message should be displayed in the UI.  
**Validates: Requirements 11.3**

**Property 49: Upload state reset**  
*For any* failed file upload, the upload state should be cleared to allow retry.  
**Validates: Requirements 11.4**

**Property 50: Error logging**  
*For any* error that occurs, it should be logged to console/CloudWatch with error details.  
**Validates: Requirements 11.5**

**Property 51: Failed status with error message**  
*For any* meeting that fails processing, its status should be FAILED and errorMessage field should contain failure details.  
**Validates: Requirements 11.6**

## Error Handling

### Frontend Error Handling



**Network Errors**:
- Catch axios errors and display user-friendly messages
- Extract error details from response.data.error when available
- Fall back to generic "Request failed" message

**Authentication Errors**:
- Redirect to login page on 401 Unauthorized
- Clear localStorage on authentication failure
- Display specific error messages for invalid credentials

**Upload Errors**:
- Reset upload state (uploading=false, uploadPct=0)
- Display error message in error box
- Allow user to retry upload

**State Management Errors**:
- Use try-catch blocks around state updates
- Prevent UI crashes with error boundaries (future enhancement)
- Log errors to console for debugging

### Backend Error Handling

**Lambda Function Errors**:
- Wrap all Lambda handlers in try-catch blocks
- Return appropriate HTTP status codes (400, 401, 500)
- Include error details in response body
- Log full stack traces to CloudWatch

**AWS Service Errors**:
- **Transcribe Failures**: Use placeholder transcript, continue processing
- **Bedrock Failures**: Try fallback models, then use mock analysis
- **DynamoDB Errors**: Return 500 status, log error details
- **S3 Errors**: Return 500 status, log error details

**Validation Errors**:
- Check file size before generating presigned URL
- Validate MIME types against allowed list
- Return 400 Bad Request with descriptive error message

**Processing Timeout**:
- Set process-meeting timeout to 900 seconds (15 minutes)
- If timeout occurs, Lambda will be terminated and meeting status remains in intermediate state
- User can retry by re-uploading (future enhancement: add retry mechanism)

### Resilience Patterns

**Graceful Degradation**:
- Mock analysis when Bedrock unavailable
- Placeholder transcript when Transcribe unavailable
- System remains functional even if AI services fail

**Retry Logic**:
- Bedrock: Try 3 models before falling back to mock
- Transcribe: Poll up to 48 times (12 minutes) before timeout
- No automatic retries for user-facing API calls (user can manually retry)

**Idempotency**:
- Upload URL generation creates new meetingId each time (not idempotent by design)
- Action updates use PUT with explicit completed value (idempotent)
- Meeting retrieval is naturally idempotent

## Testing Strategy

### Dual Testing Approach

The MeetingMind platform requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests**: Validate specific examples, edge cases, and integration points
- Authentication flow with valid/invalid credentials
- File upload with specific file types and sizes
- S3 key format generation with various title inputs
- Date formatting and deadline calculation edge cases
- Mock analysis generation for specific title keywords
- DynamoDB record creation and retrieval
- API endpoint integration with mocked AWS services

**Property-Based Tests**: Verify universal properties across all inputs
- File type validation for all supported MIME types
- Status transitions for all processing stages
- Action item structure for all generated analyses
- Completion percentage calculation for all action counts
- Deadline color coding for all date ranges
- CORS header presence for all API responses
- Transcript truncation for all transcript lengths

### Property-Based Testing Configuration

**Library Selection**:
- **Python (Backend)**: Use `hypothesis` library for property-based testing
- **JavaScript (Frontend)**: Use `fast-check` library for property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: meetingmind-documentation, Property N: [property text]`

**Example Property Test Structure** (Python):
```python
from hypothesis import given, strategies as st

# Feature: meetingmind-documentation, Property 14: Transcript truncation
@given(st.text(min_size=0, max_size=10000))
def test_transcript_truncation(transcript):
    """For any transcript, stored length should not exceed 5000 characters."""
    stored = truncate_transcript(transcript)
    assert len(stored) <= 5000
    if len(transcript) <= 5000:
        assert stored == transcript
```

**Example Property Test Structure** (JavaScript):
```javascript
import fc from 'fast-check';

// Feature: meetingmind-documentation, Property 29: Completion percentage calculation
test('completion percentage is correctly calculated', () => {
  fc.assert(
    fc.property(
      fc.nat(100), // total actions
      fc.nat(100), // completed actions
      (total, completed) => {
        fc.pre(completed <= total); // precondition
        const pct = calculateCompletionPercentage(completed, total);
        if (total === 0) {
          expect(pct).toBe(0);
        } else {
          expect(pct).toBe(Math.round((completed / total) * 100));
        }
      }
    ),
    { numRuns: 100 }
  );
});
```

### Testing Priorities

**High Priority** (Core Functionality):
1. Authentication and authorization
2. File upload and presigned URL generation
3. Processing pipeline status transitions
4. AI analysis structure and validation
5. Action item management and completion tracking

**Medium Priority** (User Experience):
1. UI component rendering and state management
2. Error message display and handling
3. Progress indicators and animations
4. Date formatting and deadline calculations

**Low Priority** (Edge Cases):
1. Large file handling (approaching 500MB limit)
2. Special characters in meeting titles
3. Concurrent action item updates
4. Network retry scenarios

### Test Data Strategies

**Generators for Property Tests**:
- **File Types**: Generate from supported MIME type list
- **File Sizes**: Generate integers from 0 to 600MB (including invalid sizes)
- **Meeting Titles**: Generate strings with various characters, lengths, special chars
- **Transcripts**: Generate text from 0 to 10,000 characters
- **Action Items**: Generate objects with random owners, deadlines, completion status
- **Dates**: Generate past, present, and future dates for deadline testing

**Mock Data for Unit Tests**:
- Sample meeting objects with all fields populated
- Sample Transcribe API responses
- Sample Bedrock API responses
- Sample DynamoDB query results
- Sample S3 event payloads

### Integration Testing

**AWS Service Mocking**:
- Use `moto` library for mocking AWS services in Python tests
- Mock S3, DynamoDB, Transcribe, Bedrock, SNS, Cognito
- Verify correct API calls with expected parameters

**End-to-End Scenarios**:
1. Complete upload-to-analysis flow
2. Meeting list retrieval with various statuses
3. Action item update and completion tracking
4. Error scenarios (Bedrock failure, Transcribe failure)
5. Authentication flow (login, session check, logout)

### Test Coverage Goals

- **Backend Lambda Functions**: 80%+ code coverage
- **Frontend Components**: 70%+ code coverage
- **Critical Paths**: 100% coverage (auth, upload, processing pipeline)
- **Property Tests**: All 51 correctness properties implemented

## Deployment and Infrastructure

### AWS SAM Deployment

**Template Structure**:
- `template.yaml`: Infrastructure as Code defining all AWS resources
- Nested stacks: Not used (single template for simplicity)
- Parameters: None (uses AWS::AccountId pseudo-parameter)

**Deployment Commands**:
```bash
# Build Lambda functions
sam build

# Deploy to AWS
sam deploy --guided

# Outputs: API URL, Cognito Pool IDs, S3 Bucket name
```

**Resource Dependencies**:
1. Cognito User Pool and Client (no dependencies)
2. S3 Bucket (no dependencies)
3. DynamoDB Table (no dependencies)
4. Lambda Functions (depend on S3, DynamoDB, IAM roles)
5. API Gateway (depends on Lambda functions, Cognito)
6. S3 Notification (depends on S3 Bucket, Lambda, Permission)
7. Custom Resource for S3 Notification (depends on all above)

### Frontend Deployment

**Build Process**:
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Output: dist/ directory with static assets
```

**Configuration**:
- Environment variables injected at build time via `.env.production`
- Runtime configuration via `window.__MM_CONFIG__` for dynamic values
- Vite handles bundling, minification, and asset optimization

**Hosting Options**:
- S3 + CloudFront (static hosting)
- Amplify Hosting (CI/CD integration)
- Vercel/Netlify (alternative platforms)

### Environment Configuration

**Backend Environment Variables** (set by SAM template):
- `MEETINGS_TABLE`: DynamoDB table name
- `AUDIO_BUCKET`: S3 bucket name
- `REGION`: AWS region
- `SNS_TOPIC_ARN`: SNS topic ARN for reminders

**Frontend Environment Variables**:
- `VITE_API_URL`: API Gateway endpoint URL
- `VITE_USER_POOL_ID`: Cognito User Pool ID
- `VITE_USER_POOL_CLIENT_ID`: Cognito Client ID
- `VITE_REGION`: AWS region

### Security Configuration

**IAM Policies**:
- Lambda execution roles with least-privilege permissions
- S3 bucket policy allowing Lambda access
- DynamoDB table policy for Lambda read/write
- Cognito authorizer for API Gateway

**Secrets Management**:
- No secrets required (uses IAM roles and Cognito)
- API keys not needed (Cognito handles authentication)

**Network Security**:
- API Gateway with HTTPS only
- S3 presigned URLs with signature validation
- CORS configured for frontend origin

### Monitoring and Observability

**CloudWatch Logs**:
- All Lambda functions log to CloudWatch
- Log groups: `/aws/lambda/{function-name}`
- Retention: Default (never expire) - should be configured

**CloudWatch Metrics**:
- Lambda invocations, duration, errors
- API Gateway requests, latency, 4xx/5xx errors
- DynamoDB read/write capacity, throttles

**Alarms** (not currently configured):
- Lambda error rate > 5%
- API Gateway 5xx error rate > 1%
- DynamoDB throttling events
- S3 bucket size approaching limits

**Tracing** (not currently configured):
- AWS X-Ray for distributed tracing
- End-to-end request tracking
- Performance bottleneck identification

### Cost Optimization

**Current Cost Drivers**:
1. **AWS Transcribe**: $0.024 per minute of audio (largest cost)
2. **Amazon Bedrock**: Per-token pricing (Claude: ~$0.25/1M tokens)
3. **Lambda**: Compute time (minimal due to serverless)
4. **DynamoDB**: Pay-per-request (minimal for low volume)
5. **S3**: Storage + requests (minimal, 30-day lifecycle)

**Optimization Strategies**:
- S3 lifecycle policy deletes audio after 30 days
- DynamoDB on-demand pricing (no idle capacity costs)
- Lambda memory sized appropriately (256MB/512MB)
- Transcript truncation to 5000 chars (reduces DynamoDB item size)
- Mock analysis fallback (reduces Bedrock costs when unavailable)

**Estimated Monthly Cost** (100 meetings/month, 30 min avg):
- Transcribe: 100 × 30 × $0.024 = $72
- Bedrock: ~$5 (assuming 2M tokens)
- Lambda: ~$2
- DynamoDB: ~$1
- S3: ~$1
- **Total: ~$81/month**

