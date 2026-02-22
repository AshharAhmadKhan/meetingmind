# Demo Mode Implementation

**Last Updated:** February 22, 2026

## Overview

MeetingMind includes a demo mode that allows users to try the platform without signing up. The demo account is shared among all users, but uploaded meetings are automatically deleted after 30 minutes to prevent interference and maintain a clean demo environment.

## How It Works

### Backend Implementation

1. **Demo User Identification**
   - Demo user ID: `c1c38d2a-1081-7088-7c71-0abc19a150e9`
   - Demo email: `demo@meetingmind.app`
   - Defined in `backend/constants.py`

2. **Automatic Expiration (TTL)**
   - When demo user uploads a meeting, a TTL (Time To Live) attribute is added
   - TTL is set to 30 minutes from upload time
   - DynamoDB automatically deletes expired meetings
   - Regular users' meetings have no TTL (never expire)

3. **Implementation Details**
   ```python
   # backend/constants.py
   DEMO_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
   DEMO_MEETING_TTL_MINUTES = 30
   
   # backend/functions/process-meeting/app.py
   if user_id == DEMO_USER_ID:
       ttl_timestamp = int((datetime.now(timezone.utc) + 
           timedelta(minutes=DEMO_MEETING_TTL_MINUTES)).timestamp())
       item['ttl'] = ttl_timestamp
       item['isDemoMeeting'] = True
   ```

4. **DynamoDB TTL Configuration**
   - TTL enabled on `meetingmind-meetings` table
   - Attribute name: `ttl`
   - Deletion typically happens within minutes (can take up to 48 hours)
   - Script: `scripts/setup/enable-ttl.py`

### Frontend Implementation

1. **Demo Warning Banner**
   - Component: `frontend/src/components/DemoWarningBanner.jsx`
   - Shows on Dashboard for demo users
   - Dismissible per session (uses sessionStorage)
   - Includes "Sign Up Free" call-to-action

2. **Banner Features**
   - Detects demo user by email (`demo@meetingmind.app`)
   - Clear warning about 30-minute expiration
   - Prominent sign-up button
   - Dismissible with × button
   - Animated slide-down entrance

3. **User Experience**
   - Demo users see warning banner on dashboard
   - Banner explains data will be deleted after 30 minutes
   - Encourages sign-up for permanent data storage
   - Can be dismissed but reappears on page reload

## User Flow

### Demo User Journey

1. **Access Demo**
   - User logs in with `demo@meetingmind.app`
   - Sees existing demo meetings (permanent showcase data)
   - Warning banner appears at top of dashboard

2. **Upload Meeting**
   - User uploads their own meeting audio
   - Meeting is processed normally (transcription + AI analysis)
   - TTL is automatically set to 30 minutes from now
   - Meeting appears in their dashboard

3. **Explore Features**
   - User can interact with their meeting
   - View actions, drag-and-drop on Kanban board
   - See graveyard, debt analytics, patterns
   - Full functionality available

4. **Automatic Cleanup**
   - After 30 minutes, DynamoDB deletes the meeting
   - No manual cleanup needed
   - Demo account stays clean for next user

5. **Sign Up Prompt**
   - Banner encourages sign-up throughout session
   - "Sign Up Free" button navigates to `/signup`
   - User can create permanent account anytime

### Regular User Journey

1. **Sign Up**
   - User creates account with their email
   - Gets their own user ID (not demo user ID)
   - No TTL on their meetings

2. **Permanent Storage**
   - All meetings saved indefinitely
   - No automatic deletion
   - Full team collaboration features
   - No warning banners

## Configuration

### Demo User Credentials

```
Email: demo@meetingmind.app
Password: [Set in AWS Cognito]
User ID: c1c38d2a-1081-7088-7c71-0abc19a150e9
```

### TTL Settings

```python
# backend/constants.py
DEMO_MEETING_TTL_MINUTES = 30  # Adjust expiration time here
```

### Enable TTL on DynamoDB

```bash
# Run once during setup
python scripts/setup/enable-ttl.py
```

## Maintenance

### Monitoring Demo Account

```bash
# List all meetings for demo user
python tests/integration/check-user-recent-meetings.py

# Remove specific team from demo user
python scripts/data/remove-team.py [team_name_or_id]

# Clear all demo data (use with caution)
python scripts/data/clear-test-data.py
```

### Adjusting TTL Duration

1. Edit `DEMO_MEETING_TTL_MINUTES` in `backend/constants.py`
2. Redeploy Lambda functions:
   ```bash
   cd backend
   sam build
   sam deploy
   ```

### Disabling Demo Mode

To disable automatic deletion:

1. Remove TTL logic from `backend/functions/process-meeting/app.py`
2. Or set `DEMO_MEETING_TTL_MINUTES` to a very large value (e.g., 525600 for 1 year)

## Benefits

### For Users
- Try platform without commitment
- No email verification required
- Full feature access
- Safe experimentation

### For Platform
- Clean demo environment
- No storage bloat from test uploads
- Consistent demo experience
- Encourages sign-ups

### For Competition
- Judges can test freely
- No interference between testers
- Professional presentation
- Scalable demo solution

## Technical Notes

### DynamoDB TTL Behavior

- TTL deletion is eventual (not immediate)
- Typically happens within minutes
- Can take up to 48 hours in rare cases
- Deleted items don't count toward storage costs
- No additional charges for TTL

### Edge Cases

1. **Meeting in Progress**
   - If meeting is being processed when TTL expires, it may complete
   - DynamoDB waits for write operations to finish

2. **Multiple Demo Users**
   - All share same account
   - Can see each other's uploads temporarily
   - Each upload gets its own 30-minute TTL

3. **Team Creation**
   - Demo users can create teams
   - Teams don't auto-delete (manual cleanup needed)
   - Use `scripts/data/remove-team.py` to clean up

## Future Enhancements

### Potential Improvements

1. **Countdown Timer**
   - Show remaining time on meeting cards
   - "Expires in 25 minutes" indicator
   - Visual urgency as expiration approaches

2. **Session-Based Isolation**
   - Each demo session gets unique temporary user ID
   - Complete isolation between users
   - More complex but better UX

3. **Extended Demo**
   - "Extend by 30 minutes" button
   - Limited extensions (e.g., max 2 hours)
   - Requires backend API changes

4. **Demo Analytics**
   - Track demo usage patterns
   - Conversion rate to sign-ups
   - Popular features in demo mode

## Security Considerations

- Demo account has same permissions as regular users
- Cannot access other users' data
- Team features work normally
- No elevated privileges
- Standard authentication required

## Support

For issues with demo mode:
1. Check DynamoDB TTL status: `scripts/setup/enable-ttl.py`
2. Verify demo user ID in constants
3. Check Lambda logs for TTL assignment
4. Test with non-demo account to isolate issue

---

**Implementation Date:** February 22, 2026  
**Status:** Production Ready  
**Tested:** ✅ Backend TTL, ✅ Frontend Banner, ✅ DynamoDB Configuration
