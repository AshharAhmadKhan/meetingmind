# Recording Best Practices - MeetingMind

**Last Updated:** February 20, 2026  
**Author:** Ashhar Ahmad Khan

---

## Overview

MeetingMind uses Amazon Transcribe for speaker diarization and AI-powered action item extraction. To get the best results, follow these recording guidelines.

---

## Critical Rule: Explicitly Mention Names

**Why:** Amazon Transcribe identifies speakers by voice characteristics, not by names. If everyone sounds the same (single person recording), all tasks will be assigned to "Unassigned".

### ❌ Bad Example (Ambiguous)
```
Person A: "Can you handle the database migration?"
Person B: "Yes, I'll do it by Friday."
```
**Result:** Task assigned to "Unassigned" or task description

### ✅ Good Example (Explicit Names)
```
Ashhar: "Alishba, can you handle the database migration?"
Alishba: "Yes, Alishba here - I'll complete it by Friday."
```
**Result:** Task correctly assigned to Alishba with Friday deadline

---

## Recording Guidelines

### 1. Use Real Names in Every Assignment

Always mention the person's name when assigning a task:
- "Ashhar, you'll handle X"
- "Alishba, can you do Y?"
- "Aayush will take care of Z"

### 2. Self-Identify When Accepting Tasks

When accepting a task, state your name:
- "Yes, Ashhar here - I'll do it"
- "Alishba speaking - I can handle that"
- "Aayush - I'll take care of it"

### 3. Use Multiple Voices (Recommended)

**Best Practice:** Record with actual team members
- Each person has unique voice characteristics
- Transcribe can distinguish speakers automatically
- More natural conversation flow

**Alternative:** If recording alone, vary your voice significantly for each "speaker"

### 4. Speak Clearly and Naturally

- Normal conversation pace (not too fast)
- Clear pronunciation of names
- Avoid background noise
- Use good quality microphone

### 5. Include Deadlines Explicitly

Always mention specific dates or timeframes:
- "by Friday"
- "by January 23rd"
- "by end of week"
- "by next Monday"

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using Pronouns Instead of Names
```
"You'll handle the API, right?"
"Yes, I'll do it."
```
**Fix:** "Ashhar, you'll handle the API, right?" "Yes, Ashhar here - I'll do it."

### ❌ Mistake 2: Single Voice Recording Without Names
```
[One person recording all voices without mentioning names]
```
**Fix:** Either use multiple people OR explicitly mention names in every assignment

### ❌ Mistake 3: Vague Deadlines
```
"Can you do this soon?"
"Yeah, I'll get to it."
```
**Fix:** "Can you do this by Friday?" "Yes, I'll complete it by Friday."

### ❌ Mistake 4: Unclear Task Descriptions
```
"Handle that thing we discussed."
```
**Fix:** "Complete the database migration we discussed in the planning meeting."

---

## Recording Checklist

Before uploading your meeting recording, verify:

- [ ] All task assignments mention the assignee's name
- [ ] Assignees self-identify when accepting tasks
- [ ] Deadlines are explicitly stated
- [ ] Task descriptions are clear and specific
- [ ] Audio quality is good (no excessive background noise)
- [ ] Multiple voices used (or names mentioned if single voice)

---

## Example: Perfect Meeting Recording

```
Ashhar: "Alright team, let's review the action items from today's meeting."

Ashhar: "First, Alishba, can you handle the database schema design?"

Alishba: "Yes, Alishba here - I'll have the schema ready by January 23rd."

Ashhar: "Great. Aayush, you'll implement the API endpoints, correct?"

Aayush: "Aayush speaking - yes, I'll complete the API implementation by January 25th."

Ashhar: "Perfect. And I'll handle the frontend integration by January 27th."

Alishba: "Sounds good. Should we schedule a review meeting?"

Ashhar: "Yes, let's meet on January 28th to review everything."
```

**Result:**
- ✅ Alishba: Database schema design (Due: Jan 23)
- ✅ Aayush: API endpoints implementation (Due: Jan 25)
- ✅ Ashhar: Frontend integration (Due: Jan 27)
- ✅ Team: Review meeting (Due: Jan 28)

---

## Troubleshooting

### Problem: Tasks Assigned to "Unassigned"

**Cause:** Names not mentioned in recording OR single voice used

**Solution:**
1. Re-record with explicit name mentions
2. OR use multiple people to record
3. Check that team member names match registered names exactly

### Problem: Wrong Person Assigned

**Cause:** Name mentioned but doesn't match team member list

**Solution:**
1. Ensure names in recording match registered team member names
2. Use full names if multiple people have similar names
3. Check team member list before recording

### Problem: No Deadline Detected

**Cause:** Deadline not explicitly stated

**Solution:**
1. Always mention specific dates: "by January 23rd"
2. Use clear timeframes: "by end of week", "by Friday"
3. Avoid vague terms: "soon", "later", "eventually"

---

## Tips for Better Results

### 1. Start with Introductions
Begin meetings with: "This is [Name] speaking" for each participant

### 2. Use Natural Language
Don't over-formalize - speak naturally but clearly

### 3. Summarize at the End
Recap action items with names and deadlines at meeting end

### 4. Test First
Record a short test meeting and upload to verify names are detected correctly

### 5. Review Before Uploading
Listen to your recording to ensure:
- Names are clearly audible
- Deadlines are mentioned
- Audio quality is good

---

## Technical Details

### How Speaker Diarization Works

Amazon Transcribe analyzes:
- Voice pitch and tone
- Speaking patterns
- Acoustic characteristics
- Timing and pauses

**Important:** It does NOT recognize names automatically - you must mention them!

### Name Matching Algorithm

MeetingMind matches mentioned names against your team member list:
1. Exact match: "Ashhar" → Ashhar Ahmad Khan
2. Partial match: "Alishba" → Alishba Khan
3. No match: Task assigned to "Unassigned"

**Note:** Currently no fuzzy matching - names must match exactly

---

## Quick Reference Card

**Before Recording:**
- [ ] Know your team member names
- [ ] Plan to mention names explicitly
- [ ] Prepare clear task descriptions
- [ ] Have specific deadlines ready

**During Recording:**
- [ ] Mention assignee name for each task
- [ ] Self-identify when accepting tasks
- [ ] State deadlines explicitly
- [ ] Speak clearly and naturally

**After Recording:**
- [ ] Review audio quality
- [ ] Verify names are audible
- [ ] Check deadlines are mentioned
- [ ] Upload and verify results

---

## Need Help?

If you're still having issues with task assignment:

1. Check the team member list in your workspace
2. Verify names in recording match registered names
3. Review this guide for common mistakes
4. Contact support with your recording for analysis

---

**Remember:** The key to accurate task assignment is explicitly mentioning names in your recordings!

---

**Last Updated:** February 20, 2026  
**Version:** 1.0  
**Contact:** thecyberprinciples@gmail.com
