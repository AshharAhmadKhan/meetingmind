# Requirements Document

## Introduction

MeetingMind is an AWS serverless meeting intelligence platform that processes audio recordings of meetings and extracts actionable intelligence using AI. The system automatically transcribes audio, identifies key decisions, extracts action items with owners and deadlines, and provides follow-up recommendations. Built entirely on AWS managed services, the platform provides a scalable, cost-effective solution for meeting documentation and action tracking.

## Glossary

- **System**: The MeetingMind platform (backend + frontend + AWS infrastructure)
- **User**: An authenticated individual who uploads and manages meeting recordings
- **Meeting**: A single audio recording and its associated AI-generated analysis
- **Audio_File**: An uploaded audio recording in supported formats (MP3, WAV, M4A, MP4, WEBM)
- **Transcription**: Speaker-labeled text generated from audio via AWS Transcribe
- **Analysis**: AI-generated summary, decisions, action items, and follow-ups via Amazon Bedrock
- **Action_Item**: A task extracted from meeting analysis with owner, deadline, and completion status
- **Processing_Pipeline**: The automated workflow: Upload → Transcribe → Analyze → Store
- **Status**: Meeting processing state (PENDING, TRANSCRIBING, ANALYZING, DONE, FAILED)
- **Presigned_URL**: Time-limited S3 upload URL generated for secure direct-to-S3 uploads
- **Mock_Analysis**: Fallback AI-generated content when Bedrock is unavailable

## Requirements

### Requirement 1: User Authentication

**User Story:** As a user, I want to securely authenticate with email and password, so that only I can access my meeting recordings and data.

#### Acceptance Criteria

1. THE System SHALL provide email-based user registration via AWS Cognito
2. WHEN a user provides valid credentials, THE System SHALL authenticate them and issue session tokens
3. WHEN a user provides invalid credentials, THE System SHALL reject authentication and return an error message
4. THE System SHALL maintain user sessions across page refreshes using stored tokens
5. WHEN a user signs out, THE System SHALL invalidate their session and clear local storage

### Requirement 2: Audio Upload

**User Story:** As a user, I want to upload meeting audio files up to 500MB, so that the system can process and analyze my recordings.

#### Acceptance Criteria

1. THE System SHALL accept audio files in MP3, WAV, M4A, MP4, and WEBM formats
2. WHEN a user requests an upload, THE System SHALL generate a presigned S3 URL valid for 3600 seconds
3. WHEN a user uploads a file exceeding 500MB, THE System SHALL reject the upload and return an error
4. WHEN a user uploads an unsupported file type, THE System SHALL reject the upload and return an error
5. THE System SHALL create a DynamoDB record with status PENDING when generating an upload URL
6. THE System SHALL support drag-and-drop file upload in the web interface
7. THE System SHALL display upload progress percentage during file transfer
8. THE System SHALL use regional S3 endpoints to prevent CORS and signature issues

### Requirement 3: Meeting Processing Pipeline

**User Story:** As a user, I want my uploaded audio automatically processed, so that I receive transcription and AI analysis without manual intervention.

#### Acceptance Criteria

1. WHEN an audio file is uploaded to S3 under the audio/ prefix, THE System SHALL trigger the process-meeting Lambda function
2. THE System SHALL update meeting status to TRANSCRIBING when transcription begins
3. THE System SHALL use AWS Transcribe with speaker labeling enabled (max 5 speakers)
4. WHEN transcription completes, THE System SHALL update meeting status to ANALYZING
5. THE System SHALL attempt AI analysis using Amazon Bedrock with model fallback (Claude Haiku → Nova Lite → Nova Micro)
6. IF all Bedrock models fail, THE System SHALL generate mock analysis based on meeting title keywords
7. WHEN analysis completes, THE System SHALL update meeting status to DONE
8. IF any processing step fails, THE System SHALL update meeting status to FAILED and log the error
9. THE System SHALL store the first 5000 characters of transcript in DynamoDB
10. THE System SHALL complete processing within the 900-second Lambda timeout

### Requirement 4: AI Analysis Extraction

**User Story:** As a user, I want the system to extract structured information from my meetings, so that I can quickly understand outcomes and action items.

#### Acceptance Criteria

1. THE System SHALL extract a 2-3 sentence meeting summary from the transcript
2. THE System SHALL identify and list key decisions made during the meeting
3. THE System SHALL extract action items with task description, owner name, and deadline date
4. THE System SHALL extract follow-up items requiring future attention
5. WHEN an action item has no specified owner, THE System SHALL assign "Unassigned" as the owner
6. WHEN an action item has no deadline, THE System SHALL store null for the deadline field
7. THE System SHALL assign unique identifiers to each action item (format: "action-N")
8. THE System SHALL return analysis in valid JSON format

### Requirement 5: Meeting List and Retrieval

**User Story:** As a user, I want to view all my meetings and their processing status, so that I can track progress and access completed analyses.

#### Acceptance Criteria

1. THE System SHALL return all meetings for the authenticated user sorted by creation date
2. WHEN listing meetings, THE System SHALL include meetingId, title, status, createdAt, updatedAt, and summary
3. THE System SHALL display real-time processing status (PENDING, TRANSCRIBING, ANALYZING, DONE, FAILED)
4. WHEN retrieving a single meeting, THE System SHALL return full details including decisions, action items, and follow-ups
5. WHEN retrieving a single meeting, THE System SHALL exclude the raw transcript from the response (performance optimization)
6. THE System SHALL poll for meeting updates every 8 seconds when meetings are processing

### Requirement 6: Action Item Management

**User Story:** As a user, I want to mark action items as complete or incomplete, so that I can track progress on meeting outcomes.

#### Acceptance Criteria

1. WHEN a user toggles an action item, THE System SHALL update its completion status in DynamoDB
2. THE System SHALL calculate and display completion percentage (completed / total × 100)
3. THE System SHALL visually distinguish completed action items with reduced opacity and strikethrough text
4. WHEN an action item deadline is past, THE System SHALL display it as overdue with red color
5. WHEN an action item deadline is within 3 days, THE System SHALL display it with yellow warning color
6. WHEN an action item deadline is more than 3 days away, THE System SHALL display it with green color

### Requirement 7: Reminder Notifications

**User Story:** As a system administrator, I want automated reminders sent for approaching deadlines, so that users stay informed about upcoming action items.

#### Acceptance Criteria

1. THE System SHALL run a scheduled Lambda function daily at 8:00 AM UTC
2. WHEN the reminder function executes, THE System SHALL scan all meetings for action items with approaching deadlines
3. WHEN action items have deadlines within the notification window, THE System SHALL publish messages to the SNS topic
4. THE System SHALL include meeting title, action item details, and deadline in reminder messages

### Requirement 8: Data Storage and Lifecycle

**User Story:** As a system operator, I want efficient data storage with automatic cleanup, so that storage costs remain manageable.

#### Acceptance Criteria

1. THE System SHALL store meeting metadata in DynamoDB with userId as HASH key and meetingId as RANGE key
2. THE System SHALL use DynamoDB pay-per-request billing mode for cost efficiency
3. THE System SHALL store audio files in S3 with the key format: audio/{userId}__{meetingId}__{title}.{ext}
4. THE System SHALL automatically delete audio files from S3 after 30 days via lifecycle policy
5. THE System SHALL retain meeting metadata and analysis in DynamoDB indefinitely

### Requirement 9: API Security and CORS

**User Story:** As a developer, I want secure API access with proper CORS configuration, so that the frontend can communicate safely with the backend.

#### Acceptance Criteria

1. THE System SHALL require Cognito authentication for all API endpoints except OPTIONS
2. THE System SHALL extract userId from Cognito JWT claims (sub field)
3. THE System SHALL allow CORS requests from any origin with credentials
4. THE System SHALL support GET, POST, PUT, and OPTIONS HTTP methods
5. THE System SHALL return appropriate CORS headers in all API responses

### Requirement 10: User Interface

**User Story:** As a user, I want an elegant, responsive interface, so that I can efficiently manage meetings and view analysis.

#### Acceptance Criteria

1. THE System SHALL display a dashboard with meeting list and upload interface
2. THE System SHALL show real-time processing status with visual indicators (colors, progress bars, animations)
3. WHEN a meeting is processing, THE System SHALL display animated waveform bars
4. THE System SHALL provide a meeting detail page showing summary, decisions, action items, follow-ups, and transcript
5. THE System SHALL use custom typography (Playfair Display for headings, DM Mono for body text)
6. THE System SHALL apply a grain texture overlay for visual aesthetics
7. THE System SHALL display an empty state with ghost UI when no meetings exist
8. THE System SHALL show upload progress with percentage indicator during file transfer

### Requirement 11: Error Handling and Resilience

**User Story:** As a user, I want clear error messages and graceful degradation, so that I understand issues and the system remains functional.

#### Acceptance Criteria

1. WHEN Bedrock is unavailable, THE System SHALL generate mock analysis based on meeting title keywords
2. WHEN AWS Transcribe fails, THE System SHALL use placeholder transcript text
3. WHEN API requests fail, THE System SHALL display user-friendly error messages
4. WHEN file upload fails, THE System SHALL clear upload state and allow retry
5. THE System SHALL log all errors to CloudWatch for debugging
6. WHEN a meeting processing fails, THE System SHALL set status to FAILED and store error message

### Requirement 12: Performance and Scalability

**User Story:** As a system architect, I want the platform to scale automatically, so that it handles varying loads without manual intervention.

#### Acceptance Criteria

1. THE System SHALL use AWS Lambda for automatic scaling based on request volume
2. THE System SHALL configure process-meeting Lambda with 512MB memory and 900-second timeout
3. THE System SHALL configure other Lambda functions with 256MB memory and 60-second timeout
4. THE System SHALL use DynamoDB on-demand capacity for automatic scaling
5. THE System SHALL limit transcript storage to 5000 characters to optimize DynamoDB item size
6. THE System SHALL use S3 for audio storage to support files up to 500MB

