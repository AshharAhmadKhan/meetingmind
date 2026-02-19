# MeetingMind 7-Day Transformation - Requirements

## Overview
Transform MeetingMind from a meeting summarizer into a category-defining Action Item Lifecycle Management Platform.

**Timeline:** 7 days
**Budget:** 2477 Kiro credits (~2200 needed)
**Constraint:** 100% compliant with original competition submission

---

## Original Submission Compliance

### Submitted Solution
1. Users upload meeting audio (MP3/MP4/WAV)
2. Amazon Transcribe converts speech to text with speaker identification
3. Kiro AI + Amazon Bedrock extract:
   - Action items (with owner, deadline, task)
   - Key decisions made
   - Meeting summary
4. DynamoDB stores all data
5. EventBridge + SNS send automated email reminders for approaching deadlines
6. Web dashboard shows meeting history, action items, completion tracking

### Submitted Architecture
- S3 + CloudFront (frontend hosting)
- API Gateway + Lambda (backend)
- Amazon Transcribe (speech-to-text)
- Kiro AI + Amazon Bedrock (extraction)
- DynamoDB (storage)
- SNS (email notifications)
- EventBridge (scheduled reminders)
- Cognito (auth)

**All new features MUST be extensions of the above, not deviations.**

---

## Requirements by Day

### Day 1: Meeting Debt Dashboard
**Extension of:** "completion tracking"

**User Story:**
As a team lead, I want to see the total cost of incomplete action items across all my meetings, so I can understand the scale of our meeting debt problem.

**Acceptance Criteria:**
1. Dashboard shows total meeting debt in dollars
2. Breakdown by category (forgotten, overdue, unassigned, at-risk)
3. Trend graph showing debt over time
4. Comparison to industry benchmark
5. Team completion rate vs benchmark
6. Visual debt counter (animated)

**Technical Requirements:**
- New frontend page: `/debt-dashboard`
- New backend Lambda: `get-debt-analytics`
- DynamoDB scan of all meetings for user
- Calculate metrics from action items
- Real-time calculation (no caching needed for MVP)

---

### Day 2: Enhanced Meeting Summary (Autopsy Report)
**Extension of:** "Meeting summary"

**User Story:**
As a meeting organizer, I want to see an ROI analysis of each meeting, so I can understand if the meeting was worth the time investment.

**Acceptance Criteria:**
1. Each meeting shows quality score (0-10)
2. ROI calculation (cost vs value created)
3. Comparison to user's historical average
4. Comparison to industry benchmark
5. Specific recommendations for improvement
6. Predicted impact of recommendations

**Technical Requirements:**
- Modify existing meeting detail page
- New backend Lambda: `calculate-meeting-roi`
- Use Bedrock to generate recommendations
- Store ROI data in DynamoDB meeting record
- Calculate on meeting completion

---

### Day 3: Cross-Meeting Action Item View
**Extension of:** "meeting history, action items"

**User Story:**
As a team member, I want to see all my action items across all meetings in one place, so I can prioritize my work effectively.

**Acceptance Criteria:**
1. Kanban board view (To Do, In Progress, Blocked, Done)
2. Filter by owner, deadline, risk level, meeting
3. Bulk operations (reassign, reschedule, mark complete)
4. Timeline view option
5. Drag-and-drop to change status
6. Search functionality

**Technical Requirements:**
- New frontend page: `/actions-overview`
- New backend Lambda: `get-all-actions`
- DynamoDB query all meetings, extract all action items
- Frontend state management for drag-and-drop
- Bulk update API endpoint

---

### Day 4: Action Item Decay Prediction
**Extension of:** "action items with owner, deadline, task"

**User Story:**
As a project manager, I want to know which action items are at risk of failing, so I can intervene before they become blockers.

**Acceptance Criteria:**
1. Each action item has risk score (0-100)
2. Risk badge (Low/Medium/High/Critical)
3. Risk factors explained
4. Predicted completion probability
5. Recommended interventions
6. Risk score updates daily

**Technical Requirements:**
- Modify action item data model (add riskScore field)
- New backend Lambda: `calculate-decay-risk`
- Risk calculation algorithm
- EventBridge rule to recalculate daily
- Frontend displays risk badges

---

### Day 5: Duplicate Action Detection (Bedrock Embeddings)
**Extension of:** "Kiro AI + Amazon Bedrock extract"

**User Story:**
As a team lead, I want to be alerted when we create duplicate action items, so we don't waste time on redundant work.

**Acceptance Criteria:**
1. When creating action item, check for duplicates
2. Show similarity score (0-100%)
3. Display history of similar items
4. Identify chronic blockers (repeated >3 times)
5. Suggest breaking down vague tasks
6. Option to merge or create anyway

**Technical Requirements:**
- Use Bedrock Titan Embeddings model
- Generate embedding for each action item
- Store embeddings in DynamoDB
- Cosine similarity calculation
- Real-time duplicate check on creation
- Modify process-meeting Lambda

---

### Day 6: Action Item Graveyard + Team Leaderboard
**Extension of:** "completion tracking"

**User Story:**
As a team member, I want to see abandoned action items visualized emotionally, so I feel motivated to complete my commitments.

**Acceptance Criteria:**
1. Graveyard shows items >30 days old, incomplete
2. Tombstone visualization with details
3. Total buried count and cost
4. "Resurrect" functionality
5. Team leaderboard with rankings
6. Completion rate per person
7. Achievements and badges

**Technical Requirements:**
- New frontend page: `/graveyard`
- New frontend component: Leaderboard on dashboard
- Query old incomplete action items
- Calculate per-person stats
- Achievement logic
- Resurrection = reassign + reset deadline

---

### Day 7: Pattern Detection + Article Rewrite
**Extension of:** "meeting history"

**User Story:**
As a team lead, I want to understand toxic meeting patterns, so I can fix our meeting culture systematically.

**Acceptance Criteria:**
1. Detect common patterns (Planning Paralysis, Silent Majority, etc.)
2. Show pattern symptoms
3. Provide prescriptions
4. Show success rate of fixes
5. Predicted impact
6. Pattern library grows over time

**Technical Requirements:**
- New backend Lambda: `detect-patterns`
- Pattern detection algorithms
- Use Bedrock for pattern analysis
- Store detected patterns in DynamoDB
- Frontend pattern cards
- Article rewrite (markdown file)

---

## Non-Functional Requirements

### Performance
- Dashboard loads in <2 seconds
- Action item queries return in <500ms
- Embedding generation <1 second per item
- Risk calculation <100ms per item

### Scalability
- Support 100+ meetings per user
- Support 1000+ action items per user
- Efficient DynamoDB queries (use indexes)

### Security
- All APIs require Cognito authentication
- User can only see their own data
- No PII in logs

### Usability
- Mobile responsive
- Accessible (WCAG AA)
- Intuitive navigation
- Clear error messages

---

## Success Metrics

### Competition Judging Criteria
- Visual Impact: 10/10
- Innovation: 10/10
- Technical Sophistication: 10/10
- Real-World Impact: 10/10
- Submission Compliance: 10/10

### User Metrics
- Completion rate improvement: +50%
- Meeting debt reduction: -60%
- User engagement: Daily active usage
- Time saved: 2+ hours/week per user

---

## Day 8: Team Meeting Visibility Fix (CRITICAL)

**Extension of:** "meeting history" + team collaboration

**User Story:**
As a team member, I want to see all meetings uploaded by my team, not just my own meetings, so I can stay informed about team decisions and action items.

**Acceptance Criteria:**
1. When a team is selected, show ALL meetings uploaded to that team
2. When "Personal" is selected, show only meetings without teamId
3. Team selector clearly distinguishes between V1 and V2 teams
4. Team members can view (but not edit) meetings uploaded by others
5. Meeting uploader is clearly indicated on each meeting card

**Technical Requirements:**
- Backend already queries by teamId (GSI exists)
- Frontend already passes teamId to API
- **Problem:** Meetings show in API response but frontend filters them out
- **Root Cause:** Frontend may be filtering by userId client-side
- **Fix:** Remove any client-side userId filtering in Dashboard.jsx

**Current Status:**
- ✅ Backend: list-meetings queries by teamId correctly
- ✅ DynamoDB: All 6 meetings have teamId
- ✅ GSI: teamId-createdAt-index exists
- ❌ Frontend: May be filtering results by userId
- ❌ UX: No visual distinction between V1/V2 teams

---

## Out of Scope

### Explicitly NOT Included (Would violate submission)
- ❌ Pre-meeting blocking/prevention
- ❌ Real-time collaboration features
- ❌ Calendar integration
- ❌ Slack/Teams integration
- ❌ Mobile apps
- ❌ New AWS services not in submission

### Future Enhancements (Post-Competition)
- Multi-team support
- Admin dashboard
- Custom pattern definitions
- Export to PDF/CSV
- API for third-party integrations
