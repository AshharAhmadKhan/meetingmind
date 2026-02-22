# MeetingMind User Features Guide

**Last Updated:** February 22, 2026

A comprehensive guide to everything users can do in MeetingMind.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Demo Mode](#demo-mode)
3. [User Registration & Sign Up](#user-registration--sign-up)
4. [Dashboard](#dashboard)
5. [Meeting Upload & Processing](#meeting-upload--processing)
6. [Meeting Detail View](#meeting-detail-view)
7. [Health Scoring System](#health-scoring-system)
8. [Kanban Board (Actions Overview)](#kanban-board-actions-overview)
9. [Meeting Graveyard](#meeting-graveyard)
10. [Team Collaboration](#team-collaboration)
11. [Meeting Debt Analytics](#meeting-debt-analytics)

---

## Getting Started

### Access MeetingMind
- **URL:** https://dcfx593ywvy92.cloudfront.net
- **Region:** AWS ap-south-1 (Mumbai)
- **Supported Formats:** MP3, MP4, WAV, M4A, WEBM (max 500MB)

---

## Demo Mode

### Try Without Signing Up
Users can instantly try MeetingMind using the shared demo account.

**Features:**
- Full access to all platform features
- Pre-loaded sample meetings to explore
- No credit card or email required

**Limitations:**
- Meetings auto-delete after 30 minutes (TTL-based cleanup)
- Shared account with other demo users
- Data is not permanently saved

**How to Access:**
1. Go to login page
2. Click "Try Demo →" button
3. Automatically logs in as `demo@meetingmind.com`

**Demo Warning Banner:**
- Appears at top of dashboard for demo users
- Shows 30-minute expiration notice
- "Sign Up Free" button to create permanent account

---

## User Registration & Sign Up

### Create Your Account

**Registration Flow:**
1. Click "Sign Up Free" from demo banner or login page
2. Fill in:
   - Full Name
   - Email Address
   - Password
3. Submit registration
4. Receive confirmation message

**Admin Approval Process:**
- All accounts require manual approval (security measure)
- Admin receives email notification
- Approval typically within 24 hours
- User receives welcome email when approved

**Email Sequence:**
1. **Admin Notification** - Admin gets notified of new signup
2. **SES Verification** - User verifies email address
3. **Congratulations Email** - Confirmation of verification
4. **Welcome Email** - Account activated, ready to use

**Benefits of Registered Account:**
- Permanent data storage (no 30-min expiration)
- Create and join teams
- Full meeting history
- Email notifications for deadlines
- Daily digest emails

---

## Dashboard

### Your Meeting Hub

**Overview Section:**
- Total meetings count
- All actions overview
- Graveyard access
- Meeting Debt view

**Meeting List:**
- All your uploaded meetings
- Real-time status indicators:
  - ● Transcribing (yellow)
  - ● Done (green)
  - ● Failed (red)
- Meeting grades (A, B, C, D, F)
- Date uploaded
- Summary preview

**Team Selector:**
- Switch between Personal and Team workspaces
- "📋 Personal (Just Me)" - Your private meetings
- Team workspaces - Shared with team members

**Team Leaderboard:**
- Ranked by weighted performance score
- Shows completion rate
- Average completion time
- Risk score
- Toxic pattern detection

**Quick Actions:**
- Upload new recording
- View all actions (Kanban board)
- Access graveyard
- Check meeting debt

---

## Meeting Upload & Processing

### Upload a Recording

**Step 1: Prepare Recording**
- Supported formats: MP3, MP4, WAV, M4A, WEBM
- Max file size: 500MB
- Best practices: Clear audio, named speakers

**Step 2: Upload**
1. Click "New Recording" button
2. Enter meeting title
3. Select upload destination:
   - 📋 Personal (Just Me)
   - Team workspace (if member of teams)
4. Drop file or click to browse
5. Click upload

**Step 3: Processing**
- **Transcribe** - AWS Transcribe with speaker diarization
- **Analyze** - Bedrock Claude extracts insights
- **Notify** - Email sent when complete

**Processing Time:**
- Typically 2-5 minutes for 30-min meeting
- Status updates in real-time on dashboard

**What Gets Extracted:**
- Meeting summary
- Action items with owners and deadlines
- Decisions made
- Follow-up items
- Risk scores for each action
- Health score and grade
- Meeting autopsy (for failed meetings)

---

## Meeting Detail View

### Comprehensive Meeting Analysis

**Header:**
- Meeting title
- Date
- Status badge
- Back to meetings button

**Hero Section:**
- Meeting summary
- Health score (0-10 scale)
- Health grade (A-F)
- Sub-scores:
  - Decision Clarity
  - Action Ownership
  - Risk Management
- ROI calculation (if applicable)
- Stats: Actions, Decisions, Follow-ups
- Completion progress bar

**Unassigned Warning Banner:**
- Shows if action items lack owners
- Explains 3× lower completion rate
- Tips for better task assignment

**Meeting Autopsy:**
- Only shows for D/F grades (< 70%)
- Updates dynamically as you complete tasks
- Provides specific diagnosis and prescription
- Disappears when meeting improves to C or better

**Charts & Insights:**
- Task distribution by team member
- AI analysis with actionable recommendations
- Risk alerts for high-risk actions

**Action Items:**
- Click to mark complete/incomplete
- Shows owner, deadline, risk score
- Age indicator for old tasks
- Deadline countdown with color coding:
  - Green: 4+ days away
  - Yellow: 1-3 days away
  - Red: Overdue

**Decisions:**
- Numbered list of all decisions made
- Extracted from meeting discussion

**Follow-ups:**
- Items requiring future attention
- Not assigned to specific people

**Transcript:**
- Full meeting transcript
- Speaker-labeled
- Searchable

---

## Health Scoring System

### How Meetings Are Graded

**Scoring Formula (0-100 scale):**
- **40%** - Completion Rate (how many tasks done)
- **30%** - Owner Assignment (tasks have clear owners)
- **20%** - Risk Management (inverted risk score)
- **10%** - Recency Bonus (meetings < 7 days old)

**Letter Grades:**
- **A (90-100)** - Excellent meeting
- **B (80-89)** - Strong meeting
- **C (70-79)** - Average meeting
- **D (60-69)** - Poor meeting
- **F (< 60)** - Failed meeting

**Dashboard vs Detail Page:**
- **Dashboard:** Shows fixed grade from creation (0-100 scale)
- **Detail Page:** Shows dynamic health score (0-10 scale)
- **Both aligned:** 7/10 = 70/100 = C grade

**Dynamic Recalculation:**
- Health score updates in real-time as you complete tasks
- Completing 5/6 tasks can improve F → B grade
- Autopsy appears/disappears based on current score

**What Affects Your Score:**
- ✓ Completing action items (biggest impact - 40%)
- ✓ Assigning clear owners to tasks (30%)
- ✓ Managing high-risk items (20%)
- ✓ Recent meetings get bonus (10%)

---

## Kanban Board (Actions Overview)

### Manage All Action Items

**Access:** Click "✓ All Actions" from dashboard

**Board Columns:**
- **To Do** - Pending tasks
- **In Progress** - Currently being worked on
- **Done** - Completed tasks

**Card Information:**
- Task description
- Owner name
- Deadline with countdown
- Risk score and label
- Source meeting
- Age indicator

**Filtering:**
- View all actions across all meetings
- Filter by team/personal
- Sort by deadline, risk, age

**Drag & Drop:**
- Move cards between columns
- Updates status automatically
- Syncs with meeting detail view

**Risk Indicators:**
- **CRITICAL (75-100)** - Red, immediate attention
- **HIGH RISK (50-74)** - Red, urgent
- **MEDIUM RISK (25-49)** - Yellow, watch closely
- **LOW RISK (0-24)** - Blue, on track

**Quick Actions:**
- Click card to view details
- Mark complete from board
- Navigate to source meeting

---

## Meeting Graveyard

### Failed Meetings Archive

**Access:** Click "🪦 Graveyard" from dashboard

**What's in the Graveyard:**
- Meetings with F grade (< 60%)
- Ghost meetings (zero decisions + zero actions)
- Meetings with critical failures

**Graveyard Card Information:**
- Meeting title
- Death date
- Cause of death (autopsy)
- Prescription for improvement
- Epitaph (AI-generated)

**Epitaph Generation:**
- Darkly humorous AI-generated epitaphs
- Based on meeting failure patterns
- Examples:
  - "Here lies a meeting that could have been an email"
  - "Died of diffusion of responsibility"
  - "Killed by lack of follow-through"

**Resurrection:**
- Improve meeting by completing tasks
- When score reaches C or better, meeting leaves graveyard
- Automatically removed from graveyard view

**Analytics:**
- Total meetings in graveyard
- Common failure patterns
- Team-wide graveyard rate

---

## Team Collaboration

### Work Together on Meetings

**Create a Team:**
1. Click "Create Team" from dashboard
2. Enter team name
3. Receive invite code
4. Share code with team members

**Join a Team:**
1. Click "Join Team" from dashboard
2. Enter invite code
3. Instant access to team workspace

**Team Features:**
- Shared meeting workspace
- All team members see same meetings
- Upload meetings to team
- Collaborative action tracking
- Team leaderboard

**Team Leaderboard:**
- Ranked by performance score
- Metrics:
  - Completion rate (X/Y completed)
  - Average completion time
  - Risk score
- Identifies top performers
- Detects toxic patterns

**Team Selector:**
- Switch between personal and team workspaces
- Upload to specific workspace
- Filter meetings by workspace

**Permissions:**
- All team members can:
  - View all team meetings
  - Upload new meetings
  - Mark actions complete
  - View team analytics

---

## Meeting Debt Analytics

### Track Productivity Costs

**Access:** Click "💰 View Debt" from dashboard

**What is Meeting Debt:**
- Accumulated cost of incomplete action items
- Calculated based on:
  - Number of pending tasks
  - Age of tasks
  - Risk scores
  - Team member time

**Debt Metrics:**
- **Total Debt** - Dollar value of incomplete work
- **High-Risk Items** - Critical tasks at risk
- **Overdue Count** - Tasks past deadline
- **Average Age** - How long tasks sit incomplete

**Debt Breakdown:**
- By team member
- By meeting
- By risk level
- Trend over time

**Pattern Detection:**
- **Ghost Meetings** - Zero output meetings
- **Diffusion of Responsibility** - No clear owners
- **Deadline Drift** - Consistently missed deadlines
- **Meeting Overload** - Too many meetings
- **Action Item Inflation** - Too many tasks per meeting
- **Follow-Through Failure** - Low completion rates

**Actionable Insights:**
- Which meetings to cancel
- Which tasks to prioritize
- Team members needing support
- Process improvements needed

---

## Additional Features

### Email Notifications
- Meeting processing complete
- Approaching deadlines
- Overdue action items
- Daily digest of pending tasks

### Professional Email Templates
- Clean, Gmail-style design
- No emojis (professional appearance)
- Clear call-to-actions
- Mobile-responsive

### Data Privacy
- Audio processed and discarded
- Only transcripts and insights stored
- Private by default
- Team data shared only with team members

### AWS Infrastructure
- Powered by AWS Bedrock (Claude)
- AWS Transcribe for speech-to-text
- S3 for audio storage
- DynamoDB for data
- CloudFront CDN for fast delivery
- Region: ap-south-1 (Mumbai)

---

## Tips for Best Results

### Recording Best Practices
1. **Use clear audio** - Minimize background noise
2. **Name speakers** - Say names explicitly ("As John mentioned...")
3. **State decisions clearly** - "We've decided to..."
4. **Assign tasks explicitly** - "Sarah will handle X by Friday"
5. **Set deadlines** - Always mention specific dates
6. **Keep meetings focused** - Shorter meetings = better extraction

### Improving Meeting Health
1. **Complete action items** - Biggest impact on score (40%)
2. **Assign clear owners** - Avoid "someone should..."
3. **Set realistic deadlines** - Achievable dates
4. **Follow up regularly** - Check Kanban board daily
5. **Review autopsy** - Learn from failed meetings
6. **Cancel ghost meetings** - If no decisions/actions, skip it

### Team Collaboration Tips
1. **Use team workspaces** - Keep work organized
2. **Check leaderboard** - Identify who needs support
3. **Share invite codes** - Easy onboarding
4. **Review debt together** - Team accountability
5. **Celebrate wins** - Acknowledge completed work

---

## Support & Resources

### Getting Help
- **Documentation:** Check docs/ folder
- **Demo Mode:** Try features risk-free
- **Email Support:** Contact admin for account issues

### System Status
- **Uptime:** 99.9% availability
- **Processing Speed:** 2-5 minutes per meeting
- **Max File Size:** 500MB
- **Supported Formats:** MP3, MP4, WAV, M4A, WEBM

---

**MeetingMind** - Transform Meetings Into Action

*Powered by AWS • Region: ap-south-1 • © 2026 MeetingMind. All rights reserved.*
