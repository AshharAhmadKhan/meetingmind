# API Documentation

Complete API reference for MeetingMind.

**Last Updated:** February 22, 2026

## Base URL

```
Production: https://api.meetingmind.com
```

## Authentication

All API requests require a valid JWT token from AWS Cognito.

```http
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Meetings

#### Get Upload URL
Generate a presigned S3 URL for uploading meeting audio.

```http
POST /upload-url
```

**Request Body:**
```json
{
  "title": "Q1 Planning Meeting",
  "teamId": "team-uuid" // Optional
}
```

**Response:**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "meetingId": "meeting-uuid",
  "s3Key": "user-id__meeting-id__title.mp3"
}
```

#### List Meetings
Get all meetings for the authenticated user.

```http
GET /meetings
```

**Query Parameters:**
- `teamId` (optional): Filter by team ID
- `status` (optional): Filter by status (PENDING, DONE, FAILED)
- `limit` (optional): Number of results (default: 50)

**Response:**
```json
{
  "meetings": [
    {
      "meetingId": "uuid",
      "title": "Q1 Planning",
      "status": "DONE",
      "createdAt": "2026-02-18T10:00:00Z",
      "healthGrade": "A",
      "healthScore": 95
    }
  ]
}
```

#### Get Meeting
Get details for a specific meeting.

```http
GET /meetings/{meetingId}
```

**Response:**
```json
{
  "meetingId": "uuid",
  "title": "Q1 Planning Meeting",
  "status": "DONE",
  "transcript": "Full transcript...",
  "summary": "Meeting summary...",
  "decisions": ["Decision 1", "Decision 2"],
  "actionItems": [
    {
      "id": "action-1",
      "task": "Finalize API docs",
      "owner": "Ashhar",
      "deadline": "2026-02-25",
      "completed": false,
      "status": "todo",
      "riskScore": 45,
      "riskLevel": "MEDIUM"
    }
  ],
  "followUps": ["Follow up 1"],
  "roi": {
    "cost": 150.00,
    "value": 1200.00,
    "roi": 700.0
  },
  "createdAt": "2026-02-18T10:00:00Z"
}
```

### Actions

#### Get All Actions
Get all action items across all meetings.

```http
GET /actions
```

**Query Parameters:**
- `status` (optional): Filter by status (todo, in_progress, blocked, done)
- `owner` (optional): Filter by owner name
- `teamId` (optional): Filter by team ID

**Response:**
```json
{
  "actions": [
    {
      "id": "action-1",
      "task": "Finalize API docs",
      "owner": "Ashhar",
      "deadline": "2026-02-25",
      "completed": false,
      "status": "todo",
      "riskScore": 45,
      "riskLevel": "MEDIUM",
      "meetingId": "meeting-uuid",
      "meetingTitle": "Q1 Planning"
    }
  ]
}
```

#### Update Action
Update an action item.

```http
PATCH /actions/{actionId}
```

**Request Body:**
```json
{
  "status": "done",
  "completed": true,
  "owner": "New Owner",
  "deadline": "2026-03-01"
}
```

**Response:**
```json
{
  "message": "Action updated successfully",
  "action": {
    "id": "action-1",
    "status": "done",
    "completed": true,
    "completedAt": "2026-02-20T15:30:00Z"
  }
}
```

### Teams

#### Create Team
Create a new team.

```http
POST /teams
```

**Request Body:**
```json
{
  "name": "Engineering Team"
}
```

**Response:**
```json
{
  "teamId": "team-uuid",
  "name": "Engineering Team",
  "inviteCode": "ABC123",
  "createdBy": "user@email.com",
  "members": ["user@email.com"]
}
```

#### Join Team
Join a team using an invite code.

```http
POST /teams/join
```

**Request Body:**
```json
{
  "inviteCode": "ABC123"
}
```

**Response:**
```json
{
  "message": "Successfully joined team",
  "team": {
    "teamId": "team-uuid",
    "name": "Engineering Team"
  }
}
```

#### Get Team
Get team details.

```http
GET /teams/{teamId}
```

**Response:**
```json
{
  "teamId": "team-uuid",
  "name": "Engineering Team",
  "createdBy": "user@email.com",
  "members": [
    "user1@email.com",
    "user2@email.com"
  ],
  "inviteCode": "ABC123",
  "createdAt": "2026-02-18T10:00:00Z"
}
```

#### List User Teams
Get all teams the user belongs to.

```http
GET /teams
```

**Response:**
```json
{
  "teams": [
    {
      "teamId": "team-uuid",
      "name": "Engineering Team",
      "memberCount": 5,
      "role": "admin"
    }
  ]
}
```

### Analytics

#### Get Debt Analytics
Get meeting debt analytics.

```http
GET /analytics/debt
```

**Query Parameters:**
- `teamId` (optional): Filter by team ID

**Response:**
```json
{
  "totalDebt": 2500.00,
  "overdueActions": 12,
  "highRiskActions": 8,
  "averageRiskScore": 45.5,
  "debtTrend": "increasing"
}
```

#### Check Duplicates
Find duplicate action items.

```http
POST /actions/check-duplicates
```

**Request Body:**
```json
{
  "actionId": "action-1"
}
```

**Response:**
```json
{
  "duplicates": [
    {
      "actionId": "action-2",
      "task": "Similar task",
      "similarity": 0.95,
      "meetingTitle": "Previous Meeting"
    }
  ],
  "isChronicBlocker": true,
  "occurrenceCount": 4
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "message": "Missing required field: title"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "Meeting not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

- **Rate Limit**: 100 requests per minute per user
- **Burst Limit**: 20 requests per second

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645123456
```

## Webhooks

### Meeting Completed
Triggered when a meeting finishes processing.

```json
{
  "event": "meeting.completed",
  "meetingId": "uuid",
  "userId": "user@email.com",
  "status": "DONE",
  "timestamp": "2026-02-18T10:35:00Z"
}
```

### Action Overdue
Triggered when an action item becomes overdue.

```json
{
  "event": "action.overdue",
  "actionId": "action-1",
  "task": "Finalize API docs",
  "owner": "Ashhar",
  "deadline": "2026-02-25",
  "daysOverdue": 3,
  "timestamp": "2026-02-28T09:00:00Z"
}
```

## SDK Examples

### JavaScript/TypeScript
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.meetingmind.com',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// List meetings
const meetings = await api.get('/meetings');

// Update action
await api.patch(`/actions/${actionId}`, {
  status: 'done',
  completed: true
});
```

### Python
```python
import requests

headers = {
    'Authorization': f'Bearer {token}'
}

# List meetings
response = requests.get(
    'https://api.meetingmind.com/meetings',
    headers=headers
)
meetings = response.json()

# Update action
requests.patch(
    f'https://api.meetingmind.com/actions/{action_id}',
    headers=headers,
    json={'status': 'done', 'completed': True}
)
```

### cURL
```bash
# List meetings
curl -X GET https://api.meetingmind.com/meetings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update action
curl -X PATCH https://api.meetingmind.com/actions/action-1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "done", "completed": true}'
```

## Changelog

### v1.0.0 (2026-02-18)
- Initial API release
- Meeting upload and processing
- Action item management
- Team collaboration
- Analytics endpoints
