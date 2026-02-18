# How to Test MeetingMind - Real AI Verification

**Goal:** Verify Transcribe and Nova are working with real data (no mocks)

---

## Method 1: Upload via Web UI (Recommended)

### Step 1: Go to Your Live Site
```
https://dcfx593ywvy92.cloudfront.net
```

### Step 2: Login
- Use your existing account
- Or create a new one (auto-approved)

### Step 3: Upload a Meeting
1. Click "Upload Meeting" or "New Meeting"
2. Enter a title (e.g., "Test Planning Meeting")
3. Select an audio file (mp3, wav, m4a, mp4, webm)
4. Click Upload

**Where to get test audio:**
- Record a 2-3 minute voice memo on your phone
- Use any meeting recording you have
- Download a sample from YouTube (use youtube-dl or similar)

### Step 4: Watch the Processing
You should see status changes:
1. **PENDING** - Upload complete
2. **TRANSCRIBING** - Transcribe is working (takes 1-5 minutes)
3. **ANALYZING** - Nova is analyzing (takes 10-30 seconds)
4. **DONE** - Complete with real AI output

### Step 5: Verify Real AI Output
Click on the meeting and check:

**✅ Real Transcribe Output:**
- Full transcript text (not "[Audio transcription pending]")
- Actual words from your audio
- Speaker labels if multiple people

**✅ Real Nova Output:**
- Summary that matches your meeting content
- Decisions that were actually discussed
- Action items that make sense
- Follow-ups that are relevant

**❌ Fake Output (Should NOT see):**
- Generic summaries like "The team reviewed the agenda..."
- Action items with names like "Ashhar", "Priya", "Zara" (unless those are real names in your audio)
- Decisions that don't match your content

### Step 6: Check Email
You should receive an email:
- Subject: "✅ Meeting Analysis Complete: [Your Title]"
- Contains summary and action count
- Link to view meeting

---

## Method 2: Check CloudWatch Logs

### View Lambda Logs
```bash
aws logs tail /aws/lambda/meetingmind-process-meeting --follow --region ap-south-1
```

**What to look for:**

**✅ Success Indicators:**
```
Processing: [meeting-id] | [title]
Transcribe: COMPLETED
Transcript: 1234 chars
Bedrock success with apac.amazon.nova-lite-v1:0 (attempt 1)
✅ Meeting [meeting-id] → DONE
```

**❌ Failure Indicators (Should NOT see):**
```
❌ TRANSCRIPTION FAILED: Transcription failed - no audio transcript available
❌ BEDROCK ANALYSIS FAILED: AI analysis failed - all Bedrock models unavailable
```

**❌ Mock Indicators (Should NEVER see):**
```
using mock embedding
using mock analysis
All Bedrock models failed — using mock analysis
```

---

## Method 3: Check DynamoDB Directly

### List Recent Meetings
```bash
aws dynamodb scan --table-name meetingmind-meetings --region ap-south-1 --max-items 5 --query "Items[*].[meetingId.S,title.S,status.S,createdAt.S]" --output table
```

### Get Specific Meeting Details
```bash
# Replace with your userId and meetingId
aws dynamodb get-item --table-name meetingmind-meetings --region ap-south-1 --key '{"userId":{"S":"YOUR_USER_ID"},"meetingId":{"S":"YOUR_MEETING_ID"}}' --query "Item.{Status:status.S,Summary:summary.S,ActionCount:actionItems.L[0]}" --output json
```

**What to check:**
- `status` should be "DONE" (not "FAILED")
- `summary` should be specific to your meeting (not generic)
- `actionItems` should have real tasks (not template tasks)
- `transcript` should have real words (not "[Audio transcription pending]")

---

## Method 4: Test Failure Scenarios

### Test 1: Upload Invalid File
1. Create a text file: `echo "not audio" > test.txt`
2. Rename to `test.mp3`
3. Upload via UI
4. **Expected:** Status should be "FAILED" with clear error message

### Test 2: Upload Corrupted Audio
1. Create corrupted file: `dd if=/dev/urandom of=corrupt.mp3 bs=1024 count=100`
2. Upload via UI
3. **Expected:** Status should be "FAILED" with transcription error

### Test 3: Check Error Email
- You should receive email: "❌ Meeting Processing Failed"
- Error message should be clear
- No fake data should be shown

---

## Method 5: Verify No Mock Code

### Check Lambda Code
```bash
aws lambda get-function --function-name meetingmind-process-meeting --region ap-south-1 --query "Configuration.CodeSha256"
```

**Expected:** CodeSha256 should match your latest deployment

### Search for Mock References
```bash
# Download current Lambda code
aws lambda get-function --function-name meetingmind-process-meeting --region ap-south-1 --query "Code.Location" --output text

# This will give you a presigned URL - download and unzip it
# Then search for mock references:
grep -r "mock" .
grep -r "_mock_analysis" .
```

**Expected:** No results (mock code removed)

---

## Quick Verification Checklist

Run this after uploading a test meeting:

- [ ] Meeting status shows "DONE" (not "FAILED")
- [ ] Transcript contains real words from audio
- [ ] Summary is specific to your meeting content
- [ ] Action items make sense for your meeting
- [ ] Decisions match what was discussed
- [ ] Email notification received
- [ ] No generic names like "Ashhar", "Priya" in action items (unless real)
- [ ] No placeholder text like "[Audio transcription pending]"

---

## What Real Output Looks Like

### Example: Real Transcribe Output
```
"transcript": "Okay everyone, let's start the planning meeting. 
We need to discuss the Q1 roadmap and prioritize features. 
John, can you give us an update on the API work? 
Sure, we're about 80% done with the authentication endpoints..."
```

### Example: Real Nova Output
```json
{
  "summary": "Team discussed Q1 roadmap prioritization and API development progress. Authentication endpoints are 80% complete. Decision made to launch beta by March 15.",
  "decisions": [
    "Launch beta on March 15, 2026",
    "Prioritize authentication over mobile features"
  ],
  "action_items": [
    {
      "id": "action-1",
      "task": "Complete authentication endpoints",
      "owner": "John",
      "deadline": "2026-03-01",
      "completed": false
    }
  ],
  "follow_ups": [
    "Review API documentation before launch",
    "Schedule beta testing with pilot users"
  ]
}
```

---

## What Fake Output Looks Like (Should NOT See)

### Example: Mock Transcript (OLD - REMOVED)
```
"transcript": "[Audio transcription pending activation]

Meeting: Test Planning Meeting

Key topics discussed included project planning, resource allocation, and timeline review."
```

### Example: Mock Analysis (OLD - REMOVED)
```json
{
  "summary": "The team reviewed the Test Planning Meeting agenda and aligned on priorities...",
  "decisions": [
    "Launch beta on March 21, 2026",
    "Defer mobile app to v2 — focus on web MVP"
  ],
  "action_items": [
    {
      "task": "Finalize API documentation and share with frontend team",
      "owner": "Ashhar",
      "deadline": "2026-02-24"
    }
  ]
}
```

**Red Flags:**
- Generic summaries
- Names that weren't in your audio
- Dates calculated from today (not from meeting content)
- Template-like language

---

## Troubleshooting

### Issue: Meeting stuck in "TRANSCRIBING"
**Check:**
```bash
aws logs tail /aws/lambda/meetingmind-process-meeting --since 10m --region ap-south-1
```
**Possible causes:**
- Audio file too long (>60 minutes on free tier)
- Invalid audio format
- Transcribe service issue

### Issue: Meeting shows "FAILED"
**Check CloudWatch logs for error:**
```bash
aws logs filter-log-events --log-group-name /aws/lambda/meetingmind-process-meeting --filter-pattern "FAILED" --region ap-south-1 --max-items 5
```

**Common errors:**
- "Transcription failed" - Audio file issue
- "AI analysis failed" - Bedrock throttling or access issue

### Issue: No email received
**Check SES:**
```bash
aws ses get-send-quota --region ap-south-1
```
**Verify email is verified:**
```bash
aws ses list-verified-email-addresses --region ap-south-1
```

---

## Recommended Test Audio

### Option 1: Record Your Own (Best)
- Open voice recorder on phone
- Talk for 2-3 minutes about a project
- Mention specific action items and decisions
- Transfer to computer and upload

### Option 2: Use Sample Audio
Download a short podcast or interview:
```bash
# Example: Download a short YouTube video as audio
youtube-dl -x --audio-format mp3 --audio-quality 0 "https://www.youtube.com/watch?v=XXXXX"
```

### Option 3: Generate Test Audio (Quick)
Use text-to-speech:
```bash
# macOS
say "This is a test meeting. We need to complete the API documentation by Friday. John will handle the authentication. Sarah will review the design." -o test-meeting.aiff

# Convert to mp3
ffmpeg -i test-meeting.aiff test-meeting.mp3
```

---

## Success Criteria

Your system is working correctly if:

1. ✅ Transcribe produces accurate transcripts
2. ✅ Nova extracts relevant action items
3. ✅ Summaries match meeting content
4. ✅ No generic/template data appears
5. ✅ Failures are transparent (not hidden)
6. ✅ Email notifications work
7. ✅ CloudWatch logs show "Bedrock success"

---

## Next Steps After Verification

Once you confirm everything works:

1. **Upload 5-6 diverse meetings:**
   - Planning meeting
   - Daily standup
   - Retrospective
   - Client call
   - Strategy session

2. **Populate your demo:**
   - Graveyard dashboard
   - Meeting debt metrics
   - Pattern detection
   - Kanban board

3. **Record demo video:**
   - Show real AI output
   - Highlight graveyard
   - Demonstrate debt calculation

4. **Write competition article:**
   - Lead with graveyard angle
   - Show real screenshots
   - Include demo video

---

**Ready to test? Start with Method 1 (Web UI) - it's the easiest!**
