# MeetingMind Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React App<br/>Vite + Tailwind]
        B[CloudFront CDN<br/>Global Distribution]
        C[S3 Static Hosting<br/>meetingmind-frontend]
    end
    
    subgraph "Authentication"
        D[AWS Cognito<br/>User Pool]
        E[JWT Tokens<br/>1hr expiry]
    end
    
    subgraph "API Layer"
        F[API Gateway<br/>REST API]
        G[Cognito Authorizer<br/>Token Validation]
    end
    
    subgraph "Lambda Functions - Core"
        H1[get-upload-url<br/>256MB 30s]
        H2[process-meeting<br/>512MB 900s]
        H3[get-meeting<br/>256MB 30s]
        H4[list-meetings<br/>256MB 60s]
        H5[get-all-actions<br/>256MB 60s]
        H6[update-action<br/>256MB 30s]
    end
    
    subgraph "Lambda Functions - Features"
        I1[check-duplicate<br/>512MB 60s]
        I2[get-debt-analytics<br/>256MB 60s]
        I3[send-reminders<br/>256MB 60s]
        I4[generate-epitaphs<br/>256MB 60s]
    end
    
    subgraph "Lambda Functions - Teams"
        J1[create-team<br/>256MB 30s]
        J2[join-team<br/>256MB 30s]
        J3[get-team<br/>256MB 30s]
        J4[list-user-teams<br/>256MB 30s]
    end
    
    subgraph "Lambda Functions - Auth"
        K1[pre-signup<br/>256MB 30s]
        K2[post-confirmation<br/>256MB 30s]
        K3[send-welcome-email<br/>256MB 30s]
    end
    
    subgraph "Lambda Functions - Infrastructure"
        L1[dlq-handler<br/>256MB 60s]
        L2[daily-digest<br/>256MB 60s]
    end
    
    subgraph "AI/ML Services"
        M1[Amazon Transcribe<br/>Speech-to-Text]
        M2[Amazon Bedrock<br/>Claude Haiku]
        M3[Bedrock Fallback<br/>Nova Lite]
        M4[Bedrock Fallback<br/>Nova Micro]
        M5[Intelligent Mock<br/>Fallback Tier]
        M6[Titan Embeddings<br/>1536 dimensions]
    end
    
    subgraph "Data Layer"
        N1[DynamoDB<br/>meetingmind-meetings]
        N2[DynamoDB<br/>meetingmind-teams]
        N3[S3 Audio Bucket<br/>meetingmind-audio]
    end
    
    subgraph "Notification Layer"
        O1[Amazon SES<br/>Email Service]
        O2[Amazon SNS<br/>Push Notifications]
        O3[EventBridge<br/>Cron Scheduler]
    end
    
    subgraph "Monitoring"
        P1[CloudWatch Logs<br/>7-day retention]
        P2[X-Ray Tracing<br/>Distributed Tracing]
        P3[CloudWatch Dashboard<br/>Metrics]
    end
    
    %% Frontend Flow
    A -->|HTTPS| B
    B -->|Cache Miss| C
    A -->|API Calls| F
    
    %% Authentication Flow
    A -->|Sign Up/In| D
    D -->|JWT Token| E
    E -->|Authorize| G
    
    %% API Gateway Flow
    F -->|Validate Token| G
    G -->|Authorized| H1
    G -->|Authorized| H3
    G -->|Authorized| H4
    G -->|Authorized| H5
    G -->|Authorized| H6
    G -->|Authorized| I1
    G -->|Authorized| I2
    G -->|Authorized| J1
    G -->|Authorized| J2
    G -->|Authorized| J3
    G -->|Authorized| J4
    
    %% Upload Flow
    H1 -->|Presigned URL| N3
    A -->|Direct Upload| N3
    N3 -->|S3 Event| H2
    
    %% Processing Pipeline
    H2 -->|Transcribe| M1
    H2 -->|Analyze| M2
    M2 -.->|Fallback| M3
    M3 -.->|Fallback| M4
    M4 -.->|Fallback| M5
    H2 -->|Generate Embeddings| M6
    H2 -->|Store| N1
    H2 -->|Send Email| O1
    
    %% Data Access
    H3 -->|Query| N1
    H4 -->|Query| N1
    H5 -->|Query| N1
    H6 -->|Update| N1
    I1 -->|Query Embeddings| N1
    I2 -->|Calculate Debt| N1
    
    %% Team Operations
    J1 -->|Create| N2
    J2 -->|Join| N2
    J3 -->|Query| N2
    J4 -->|Query| N2
    
    %% Auth Triggers
    D -->|Pre-Signup| K1
    D -->|Post-Confirmation| K2
    K2 -->|Create User| N1
    K2 -->|Send Welcome| K3
    K3 -->|Email| O1
    
    %% Scheduled Jobs
    O3 -->|Daily 9 AM| I3
    O3 -->|Daily 9 AM| L2
    O3 -->|Nightly 3 AM| I4
    I3 -->|Send Reminders| O1
    L2 -->|Send Digest| O1
    I4 -->|Generate Epitaphs| N1
    
    %% Monitoring
    H2 -->|Logs| P1
    H2 -->|Traces| P2
    F -->|Metrics| P3
    
    %% Error Handling
    H2 -.->|Failed| L1
    L1 -->|Alert| O2
    
    style A fill:#c8f04a,stroke:#333,stroke-width:2px
    style B fill:#c8f04a,stroke:#333,stroke-width:2px
    style D fill:#ff9900,stroke:#333,stroke-width:2px
    style F fill:#ff9900,stroke:#333,stroke-width:2px
    style H2 fill:#ff9900,stroke:#333,stroke-width:3px
    style M2 fill:#9b59b6,stroke:#333,stroke-width:2px
    style N1 fill:#3498db,stroke:#333,stroke-width:2px
    style O1 fill:#e74c3c,stroke:#333,stroke-width:2px
```

## Data Flow Diagrams

### 1. Meeting Upload & Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant React
    participant API Gateway
    participant GetUploadURL
    participant S3
    participant ProcessMeeting
    participant Transcribe
    participant Bedrock
    participant DynamoDB
    participant SES
    
    User->>React: Upload Audio File
    React->>API Gateway: POST /upload-url
    API Gateway->>GetUploadURL: Invoke
    GetUploadURL->>S3: Generate Presigned URL
    GetUploadURL-->>React: Return URL + meetingId
    React->>S3: Direct Upload (bypasses API Gateway)
    S3-->>React: Upload Complete
    
    S3->>ProcessMeeting: S3 Event Trigger
    ProcessMeeting->>Transcribe: Start Transcription Job
    Transcribe-->>ProcessMeeting: Job ID
    
    loop Poll Every 15s
        ProcessMeeting->>Transcribe: Check Status
        Transcribe-->>ProcessMeeting: IN_PROGRESS
    end
    
    Transcribe-->>ProcessMeeting: COMPLETED + Transcript
    ProcessMeeting->>Bedrock: Analyze Transcript
    
    alt Claude Haiku Success
        Bedrock-->>ProcessMeeting: Analysis JSON
    else Claude Haiku Fails
        ProcessMeeting->>Bedrock: Try Nova Lite
        alt Nova Lite Success
            Bedrock-->>ProcessMeeting: Analysis JSON
        else Nova Lite Fails
            ProcessMeeting->>Bedrock: Try Nova Micro
            alt Nova Micro Success
                Bedrock-->>ProcessMeeting: Analysis JSON
            else All Models Fail
                ProcessMeeting->>ProcessMeeting: Intelligent Mock
            end
        end
    end
    
    ProcessMeeting->>Bedrock: Generate Embeddings
    Bedrock-->>ProcessMeeting: Embedding Vectors
    ProcessMeeting->>ProcessMeeting: Calculate Risk Scores
    ProcessMeeting->>ProcessMeeting: Calculate ROI
    ProcessMeeting->>DynamoDB: Store Meeting Data
    ProcessMeeting->>SES: Send Completion Email
    SES-->>User: Email Notification
```

### 2. Action Item Management Flow

```mermaid
sequenceDiagram
    participant User
    participant React
    participant API Gateway
    participant GetAllActions
    participant UpdateAction
    participant DynamoDB
    participant CheckDuplicate
    
    User->>React: View Actions Dashboard
    React->>API Gateway: GET /actions
    API Gateway->>GetAllActions: Invoke
    GetAllActions->>DynamoDB: Query All Meetings
    DynamoDB-->>GetAllActions: Meeting Data
    GetAllActions->>GetAllActions: Flatten Action Items
    GetAllActions-->>React: Action Items List
    React-->>User: Display Kanban Board
    
    User->>React: Drag Action to "Done"
    React->>API Gateway: PATCH /actions/{id}
    API Gateway->>UpdateAction: Invoke
    UpdateAction->>DynamoDB: Update Action Status
    DynamoDB-->>UpdateAction: Success
    UpdateAction-->>React: Updated Action
    React-->>User: UI Update
    
    User->>React: Check for Duplicates
    React->>API Gateway: POST /actions/check-duplicates
    API Gateway->>CheckDuplicate: Invoke
    CheckDuplicate->>DynamoDB: Query All Actions
    CheckDuplicate->>CheckDuplicate: Calculate Cosine Similarity
    CheckDuplicate-->>React: Duplicate Actions
    React-->>User: Show Chronic Blockers
```

### 3. Team Collaboration Flow

```mermaid
sequenceDiagram
    participant UserA
    participant UserB
    participant React
    participant API Gateway
    participant CreateTeam
    participant JoinTeam
    participant GetTeam
    participant DynamoDB
    
    UserA->>React: Create Team
    React->>API Gateway: POST /teams
    API Gateway->>CreateTeam: Invoke
    CreateTeam->>CreateTeam: Generate Invite Code
    CreateTeam->>DynamoDB: Store Team
    CreateTeam-->>React: Team + Invite Code
    React-->>UserA: Display Invite Code
    
    UserA->>UserB: Share Invite Code (ABC123)
    
    UserB->>React: Join Team
    React->>API Gateway: POST /teams/join
    API Gateway->>JoinTeam: Invoke {inviteCode: "ABC123"}
    JoinTeam->>DynamoDB: Find Team by Code
    JoinTeam->>DynamoDB: Add UserB to Members
    JoinTeam-->>React: Success
    React-->>UserB: Joined Team
    
    UserA->>React: Upload Meeting (teamId)
    React->>API Gateway: POST /upload-url
    Note over API Gateway: Meeting stored with teamId
    
    UserB->>React: View Meetings
    React->>API Gateway: GET /meetings?teamId=xxx
    API Gateway->>GetTeam: Verify Membership
    GetTeam->>DynamoDB: Check UserB in Team
    GetTeam-->>API Gateway: Authorized
    API Gateway-->>React: Team Meetings
    React-->>UserB: Display Meetings
```

## Component Architecture

### Frontend Components

```mermaid
graph TD
    A[App.jsx] --> B[Router]
    B --> C[Dashboard]
    B --> D[ActionsOverview]
    B --> E[Graveyard]
    B --> F[MeetingDetail]
    
    C --> G[MeetingCard]
    C --> H[UploadModal]
    C --> I[TeamSelector]
    C --> J[SkeletonLoader]
    
    D --> K[KanbanBoard]
    K --> L[KanbanColumn]
    L --> M[ActionCard]
    
    D --> N[PatternCards]
    N --> O[PatternCard]
    
    E --> P[GraveyardCard]
    E --> Q[ResurrectionModal]
    
    F --> R[TranscriptView]
    F --> S[ActionsList]
    F --> T[DecisionsList]
    
    style A fill:#c8f04a
    style C fill:#ff9900
    style D fill:#ff9900
    style E fill:#ff9900
    style F fill:#ff9900
```

### Backend Lambda Organization

```mermaid
graph TD
    A[Lambda Functions] --> B[Core]
    A --> C[Features]
    A --> D[Teams]
    A --> E[Auth]
    A --> F[Infrastructure]
    
    B --> B1[get-upload-url]
    B --> B2[process-meeting]
    B --> B3[get-meeting]
    B --> B4[list-meetings]
    B --> B5[get-all-actions]
    B --> B6[update-action]
    
    C --> C1[check-duplicate]
    C --> C2[get-debt-analytics]
    C --> C3[send-reminders]
    C --> C4[generate-epitaphs]
    
    D --> D1[create-team]
    D --> D2[join-team]
    D --> D3[get-team]
    D --> D4[list-user-teams]
    
    E --> E1[pre-signup]
    E --> E2[post-confirmation]
    E --> E3[send-welcome-email]
    
    F --> F1[dlq-handler]
    F --> F2[daily-digest]
    
    style B2 fill:#ff9900,stroke:#333,stroke-width:3px
    style C1 fill:#9b59b6
    style C2 fill:#9b59b6
```

## Database Schema

### DynamoDB Tables

```mermaid
erDiagram
    MEETINGS ||--o{ ACTIONS : contains
    MEETINGS }o--|| USERS : "belongs to"
    MEETINGS }o--o| TEAMS : "optional team"
    TEAMS ||--o{ USERS : "has members"
    
    MEETINGS {
        string userId PK
        string meetingId SK
        string title
        string status
        string s3Key
        string transcript
        string summary
        array decisions
        array actionItems
        array followUps
        object roi
        string teamId
        string email
        datetime createdAt
        datetime updatedAt
    }
    
    ACTIONS {
        string id
        string task
        string owner
        date deadline
        boolean completed
        string status
        datetime completedAt
        number riskScore
        string riskLevel
        array embedding
        datetime createdAt
    }
    
    TEAMS {
        string teamId PK
        string name
        string createdBy
        array members
        string inviteCode
        datetime createdAt
        datetime updatedAt
    }
    
    USERS {
        string userId
        string email
        string name
        datetime createdAt
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        A1[Local Dev<br/>sam local]
        A2[Dev Stack<br/>meetingmind-dev]
    end
    
    subgraph "Production"
        B1[Prod Stack<br/>meetingmind-stack]
        B2[CloudFront<br/>E3CAAI97MXY83V]
        B3[S3 Frontend<br/>dcfx593ywvy92]
    end
    
    subgraph "CI/CD"
        C1[SAM Build]
        C2[SAM Deploy]
        C3[Frontend Build]
        C4[S3 Sync]
        C5[CloudFront Invalidation]
    end
    
    A1 -->|Test| A2
    A2 -->|Promote| C1
    C1 --> C2
    C2 --> B1
    
    C3 --> C4
    C4 --> B3
    C4 --> C5
    C5 --> B2
    
    style B1 fill:#27ae60,stroke:#333,stroke-width:2px
    style B2 fill:#27ae60,stroke:#333,stroke-width:2px
```

## Cost Optimization Strategy

```mermaid
graph LR
    A[Cost Optimization] --> B[DynamoDB]
    A --> C[Lambda]
    A --> D[S3]
    A --> E[AI Services]
    
    B --> B1[Pay-per-request<br/>No provisioned capacity]
    B --> B2[No idle costs]
    
    C --> C1[Pay per invocation<br/>No idle costs]
    C --> C2[Right-sized memory<br/>256MB-512MB]
    C --> C3[Optimized cold starts<br/>Lambda layers]
    
    D --> D1[Lifecycle policies<br/>Archive old audio]
    D --> D2[Intelligent tiering]
    
    E --> E1[Multi-model fallback<br/>Cheaper models first]
    E --> E2[Intelligent mock<br/>Zero cost fallback]
    E --> E3[Batch embeddings<br/>Reduce API calls]
    
    style A fill:#27ae60
```

## Security Architecture

```mermaid
graph TB
    subgraph "Authentication Layer"
        A1[Cognito User Pool]
        A2[JWT Tokens<br/>1hr expiry]
        A3[Refresh Tokens<br/>30 days]
    end
    
    subgraph "Authorization Layer"
        B1[API Gateway<br/>Cognito Authorizer]
        B2[Lambda IAM Roles<br/>Least Privilege]
        B3[Resource Policies<br/>DynamoDB/S3]
    end
    
    subgraph "Data Protection"
        C1[Encryption at Rest<br/>S3/DynamoDB]
        C2[Encryption in Transit<br/>HTTPS/TLS]
        C3[Presigned URLs<br/>5min expiry]
    end
    
    subgraph "Monitoring & Compliance"
        D1[CloudWatch Logs<br/>No PII]
        D2[X-Ray Traces<br/>Redacted sensitive data]
        D3[CloudTrail<br/>Audit logs]
    end
    
    A1 --> A2
    A2 --> B1
    B1 --> B2
    B2 --> B3
    
    B3 --> C1
    B3 --> C2
    B3 --> C3
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    style A1 fill:#e74c3c
    style B1 fill:#e74c3c
    style C1 fill:#e74c3c
```

## Monitoring & Observability

```mermaid
graph TB
    subgraph "Logging"
        A1[CloudWatch Logs]
        A2[7-day Retention]
        A3[Structured JSON]
    end
    
    subgraph "Tracing"
        B1[X-Ray Tracing]
        B2[Subsegments]
        B3[Service Map]
    end
    
    subgraph "Metrics"
        C1[CloudWatch Metrics]
        C2[Custom Dashboard]
        C3[Alarms]
    end
    
    subgraph "Error Handling"
        D1[Dead Letter Queue]
        D2[DLQ Handler]
        D3[SNS Alerts]
    end
    
    A1 --> A2
    A2 --> A3
    
    B1 --> B2
    B2 --> B3
    
    C1 --> C2
    C2 --> C3
    
    D1 --> D2
    D2 --> D3
    
    style C3 fill:#e74c3c
    style D3 fill:#e74c3c
```

## Performance Optimization

```mermaid
graph LR
    A[Performance] --> B[Frontend]
    A --> C[Backend]
    A --> D[Database]
    
    B --> B1[Code Splitting<br/>React.lazy]
    B --> B2[CloudFront CDN<br/>Global edge]
    B --> B3[Image Optimization<br/>WebP format]
    
    C --> C1[Lambda Layers<br/>Shared code]
    C --> C2[Concurrent Execution<br/>1000 default]
    C --> C3[Optimized Memory<br/>Right-sized]
    
    D --> D1[DynamoDB<br/>Auto-scaling]
    D --> D2[Efficient Queries<br/>Composite keys]
    D --> D3[Batch Operations<br/>Reduce calls]
    
    style A fill:#3498db
```
