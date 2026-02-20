# Meeting Recording Script - Issue #9 Test

**Team:** V2 - Active  
**Team ID:** df29c543-a4d0-4c80-a086-6c11712d66f3  
**Duration:** 3-5 minutes  
**Participants:** Ashhar (you), Keldeo (you with different voice/tone)

---

## Recording Instructions

1. Use your phone or computer to record audio
2. Speak clearly and mention names explicitly
3. Use different tones/pitches for Ashhar vs Keldeo
4. Pause 2-3 seconds between speakers

---

## Script

**Ashhar:** "Alright, let's start our sprint planning meeting. This is Ashhar speaking."

*[Pause 2 seconds]*

**Ashhar:** "We have several tasks to complete this week. Let me assign them."

*[Pause 2 seconds]*

**Ashhar:** "First task - Keldeo, can you handle the database migration to the new schema?"

*[Pause 2 seconds - Change voice/tone]*

**Keldeo:** "Yes, this is Keldeo. I'll complete the database migration by February 28th."

*[Pause 2 seconds - Back to normal voice]*

**Ashhar:** "Great. Ashhar will review and update the API documentation."

*[Pause 2 seconds]*

**Ashhar:** "I'll have the API docs updated by February 26th."

*[Pause 2 seconds - Change voice]*

**Keldeo:** "Keldeo here. I'll also test the staging environment after the migration is complete."

*[Pause 2 seconds]*

**Keldeo:** "I can have the test results ready by March 1st."

*[Pause 2 seconds - Normal voice]*

**Ashhar:** "Perfect. Ashhar will schedule the demo presentation for next week."

*[Pause 2 seconds]*

**Ashhar:** "I'll send the calendar invite by February 25th."

*[Pause 2 seconds - Change voice]*

**Keldeo:** "Keldeo will prepare the demo slides and talking points."

*[Pause 2 seconds]*

**Keldeo:** "I'll share the draft by February 27th."

*[Pause 2 seconds - Normal voice]*

**Ashhar:** "Excellent. One more thing - Ashhar will review the security audit findings."

*[Pause 2 seconds]*

**Ashhar:** "I'll complete the security review by March 2nd."

*[Pause 2 seconds - Change voice]*

**Keldeo:** "And Keldeo will implement the security fixes based on Ashhar's review."

*[Pause 2 seconds]*

**Keldeo:** "I'll have the fixes deployed by March 5th."

*[Pause 2 seconds - Normal voice]*

**Ashhar:** "Perfect. That's all for today. Thanks everyone. Meeting adjourned."

---

## Expected Results

After uploading and processing, you should see:

**Action Items:**
1. Database migration → Keldeo (Feb 28)
2. API documentation update → Ashhar (Feb 26)
3. Test staging environment → Keldeo (Mar 1)
4. Schedule demo → Ashhar (Feb 25)
5. Prepare demo slides → Keldeo (Feb 27)
6. Security audit review → Ashhar (Mar 2)
7. Implement security fixes → Keldeo (Mar 5)

**Success Criteria:**
- 0 "Unassigned" items
- All tasks assigned to either "Ashhar" or "Keldeo"
- Fuzzy matching may convert names (check logs)
- Health score > 60
- Leaderboard shows both members

---

## Upload Instructions

1. Save audio file as: `meeting-sprint-planning.mp3` (or .wav, .m4a)
2. Login to MeetingMind as thecyberprinciples@gmail.com
3. Select "V2 - Active" team
4. Click "Upload Meeting"
5. Title: "Sprint Planning - Feb 21"
6. Upload the audio file
7. Wait 5-10 minutes for processing
8. Check meeting details page

---

## Troubleshooting

If you still see "Unassigned":
- Check CloudWatch logs for `meetingmind-process-meeting`
- Look for "Fuzzy matched" messages
- Verify Transcribe extracted speaker labels
- Check Bedrock AI extraction output

---

**Ready to record? Let's fix Issue #9!**
