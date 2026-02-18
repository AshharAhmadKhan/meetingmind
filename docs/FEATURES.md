# MeetingMind Features

Complete feature documentation for the MeetingMind platform.

## Core Features

### 1. Meeting Upload & Processing

**Upload Audio**
- Drag-and-drop or browse to upload
- Supported formats: MP3, MP4, WAV, M4A, WEBM
- Max file size: 500MB
- Direct browser-to-S3 upload (no server bottleneck)

**Processing Pipeline**
- Transcription with speaker identification (Amazon Transcribe)
- AI analysis for structured extraction (Amazon Bedrock)
- Email notification when complete
- Processing time: 2-5 minutes for 30-minute meeting

**Extracted Data**
- Meeting summary (2-3 sentences)
- Key decisions made
- Action items with owner, deadline, risk score
- Follow-up items
- Meeting ROI calculation

### 2. Dashboard

**Overview Stats**
- Total meetings processed
- Total action items
- Completion rate
- Meeting debt (dollar value of incomplete work)

**Recent Meetings**
- Last 10 meetings with status
- Quick access to meeting details
- Upload new meeting button

**Team Leaderboard**
- Rankings by completion rate
- Medals for top 3 performers (🥇🥈🥉)
- Achievements (Perfectionist, Speed Demon, Workhorse, Consistent)
- Color-coded completion rates

**Pattern Detection**
- Identifies 5 toxic meeting patterns
- Shows symptoms, prescriptions, impact, success rate
- Expandable cards with full details

### 3. Meeting Detail View

**Meeting Information**
- Title, date, status
- Transcript (first 5000 characters)
- Full summary

**Decisions**
- List of all decisions made
- Numbered for easy reference

**Action Items**
- Task description
- Owner assignment
- Deadline
- Risk score and level (Low/Medium/High/Critical)
- Completion status
- Mark complete button

**Follow-ups**
- List of follow-up items
- Numbered for easy reference

**ROI Analysis**
- Meeting cost (attendees × duration × hourly rate)
- Meeting value (decisions + action items)
- ROI percentage
- Comparison to average

### 4. Actions Overview (Kanban Board)

**View Modes**
- List view: Grouped by meeting
- Kanban view: Grouped by status

**Kanban Columns**
- To Do (yellow border)
- In Progress (blue border)
- Blocked (red border)
- Done (green border)

**Drag-and-Drop**
- Move cards between columns
- Automatic status update
- Optimistic UI update (no refresh needed)
- Persists across page refreshes

**Filtering**
- By status (all, incomplete, complete)
- By owner (dropdown of all owners)
- By team (if team feature enabled)

**Duplicate Detection**
- "🔍 Check Duplicates" button
- Scans all incomplete actions
- Shows similarity scores (0-100%)
- Identifies chronic blockers (repeated 3+ times)
- Shows duplicate history

**Action Card Details**
- Task description
- Owner name
- Deadline with days remaining
- Risk score with gradient background
- Meeting source

### 5. Meeting Debt Dashboard

**Total Debt**
- Dollar value of all incomplete action items
- Animated counter
- Comparison to industry benchmark

**Breakdown by Category**
- Forgotten (>30 days old)
- Overdue (past deadline)
- Unassigned (no owner)
- At-Risk (high risk score)

**Trend Graph**
- Debt over last 30 days
- Line chart showing increase/decrease

**Team Stats**
- Completion rate vs benchmark
- Total actions vs completed

### 6. Graveyard

**Tombstone Visualization**
- Shows action items >30 days old, incomplete
- Tombstone icon with details
- Owner name (who abandoned it)
- Days buried
- Meeting source
- "ANCIENT" badge for items >90 days old

**Statistics**
- Total buried items
- Average days buried
- Oldest item

**Resurrection**
- Click tombstone to resurrect
- Reassign owner
- Set new deadline
- Moves back to active status

### 7. Team Features

**Create Team**
- Team name
- Generates 6-character invite code
- Creator becomes team admin

**Join Team**
- Enter invite code
- Added to team members list
- Access to team meetings and leaderboard

**Team Selector**
- Dropdown on Dashboard and Actions pages
- Switch between personal and team views
- Filters all data by selected team

**Team Leaderboard**
- Shows all team members
- Ranked by completion rate
- Medals for top performers
- Achievements

## AI-Powered Features

### Risk Prediction

**Risk Score (0-100)**
- Calculated for each action item
- Factors:
  - Days until deadline (closer = higher risk)
  - Owner assignment (unassigned = higher risk)
  - Task vagueness (short/vague = higher risk)
  - Days since created (older = higher risk)

**Risk Levels**
- Low (0-24): Green badge
- Medium (25-49): Yellow badge
- High (50-74): Orange badge
- Critical (75-100): Red badge

**Risk Gradient**
- Visual gradient on action cards
- Intensity increases with risk score
- Left border color matches risk level

### Duplicate Detection

**Semantic Similarity**
- Uses AI embeddings (1536 dimensions)
- Cosine similarity calculation
- Threshold: 85% similarity = duplicate

**Chronic Blocker Detection**
- Identifies tasks repeated 3+ times
- Shows repeat count
- Highlights in duplicate results

**Duplicate Results**
- Similarity percentage
- Best match from history
- Full history of similar items (up to 5)
- Chronic blocker badge

### Pattern Detection

**5 Toxic Patterns**

1. **Planning Paralysis** (High Severity)
   - 3+ planning meetings
   - Low completion rate on planning actions
   - Prescription: Set hard deadlines, limit planning meetings

2. **Action Item Amnesia** (Critical Severity)
   - >70% actions incomplete
   - Team forgets commitments
   - Prescription: Automated reminders, explicit owners

3. **Meeting Debt Spiral** (High Severity)
   - 10+ meetings generating many actions
   - Average >5 actions per meeting
   - Prescription: Cancel unproductive meetings, limit actions

4. **Silent Majority** (Medium Severity)
   - Uneven action distribution (3:1 ratio)
   - Some members not contributing
   - Prescription: Round-robin assignment, rotate facilitator

5. **Chronic Blocker** (Critical Severity)
   - Same task repeated 3+ times
   - Underlying issue not addressed
   - Prescription: Break down tasks, escalate blockers

**Pattern Cards**
- Expandable UI
- Shows symptoms, prescriptions, impact, success rate
- Color-coded severity badges

## Gamification Features

### Leaderboard

**Rankings**
- Sorted by completion rate (highest first)
- Medals for top 3 (🥇🥈🥉)
- Color-coded rates:
  - ≥90%: Green (excellent)
  - ≥70%: Yellow (good)
  - <70%: Gray (needs improvement)

**Stats per Person**
- Total actions assigned
- Completed actions
- Completion rate percentage
- Average completion time

### Achievements

**🏆 Perfectionist**
- 100% completion rate
- Requires at least 1 action

**⚡ Speed Demon**
- Average completion time <3 days
- Requires at least 5 actions

**💪 Workhorse**
- >10 actions completed
- No minimum completion rate

**⭐ Consistent**
- >5 actions completed
- >80% completion rate

### Graveyard Motivation

**Emotional Impact**
- Tombstone visualization creates guilt/shame
- Owner name publicly visible
- Days buried shows neglect
- "ANCIENT" badge for extreme cases

**Resurrection Mechanic**
- Redemption opportunity
- Brings item back to life
- Resets deadline and owner

## Notification Features

### Email Notifications

**Meeting Complete**
- Subject: "✅ Meeting Analysis Complete: [Title]"
- Summary of meeting
- Action item count
- Link to view full analysis

**Meeting Failed**
- Subject: "❌ Meeting Processing Failed: [Title]"
- Error message
- Instructions to retry

**Daily Digest** (Future)
- Critical items (due today/tomorrow)
- Overdue items
- Upcoming items (this week)
- Your stats (completion rate, rank, streak)

### Reminders** (Future)
- 24 hours before deadline
- Day of deadline
- Overdue notifications

## User Experience Features

### Design System

**Colors**
- Background: #0c0c09 (dark charcoal)
- Text: #f0ece0 (cream)
- Accent: #c8f04a (lime green)
- Borders: #2a2a20 (dark gray)

**Typography**
- Headings: Playfair Display (serif)
- Body: DM Mono (monospace)
- Grain texture overlay for depth

**Animations**
- Fade-up on card load
- Smooth transitions on hover
- Animated counters for debt
- Drag-and-drop feedback

### Responsive Design

**Desktop**
- Full Kanban board (4 columns side-by-side)
- Wide dashboard layout
- Multi-column leaderboard

**Mobile** (Future)
- Stacked Kanban columns
- Vertical scrolling
- Touch-optimized drag-and-drop

### Accessibility

**Keyboard Navigation**
- Tab through all interactive elements
- Enter to activate buttons
- Arrow keys for Kanban navigation

**Screen Reader Support**
- ARIA labels on all interactive elements
- Semantic HTML structure
- Alt text on images

**Color Contrast**
- WCAG AA compliant
- High contrast mode support

## Integration Features (Future)

### Calendar Integration
- Google Calendar sync
- Outlook sync
- Auto-upload meeting recordings

### Communication Tools
- Slack notifications
- Teams notifications
- Discord webhooks

### Project Management
- Jira sync for action items
- Asana sync
- Monday.com sync

### Recording Tools
- Zoom auto-upload
- Google Meet auto-upload
- Teams auto-upload

## Performance Features

### Optimistic UI Updates
- Instant feedback on actions
- No waiting for server response
- Rollback on error

### Caching
- Browser caching for static assets
- CloudFront edge caching
- No backend caching (real-time data)

### Lazy Loading
- Load meetings on demand
- Paginated action items (future)
- Infinite scroll (future)

## Security Features

### Authentication
- Email-based signup
- Password requirements (8+ chars, uppercase, lowercase, number)
- JWT token authentication
- Automatic token refresh

### Authorization
- User can only see their own data
- Team members can see team data
- No cross-user data access

### Data Protection
- HTTPS only
- Presigned S3 URLs (5-minute expiration)
- No PII in logs
- CORS protection

## Admin Features (Future)

### User Management
- Approve/reject signups
- Disable users
- View user activity

### Analytics
- Usage metrics
- Popular features
- Error rates
- Performance metrics

### Configuration
- Feature flags
- A/B testing
- Rate limiting
- Cost monitoring
