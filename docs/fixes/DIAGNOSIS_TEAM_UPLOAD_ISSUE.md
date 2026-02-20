# Team Upload Issue - Diagnosis

**Date:** February 20, 2026  
**Reporter:** User (thehiddenif account)  
**Issue:** Selected "V1 - Legacy" team, uploaded audio, but it went to "Personal (Just Me)" instead

---

## What Happened

1. User logged in as thehiddenif@gmail.com
2. Selected "V1 - Legacy" from team dropdown
3. Uploaded audio file
4. Meeting was created WITHOUT teamId (personal meeting)
5. Meeting processed successfully (status: DONE)
6. But only thehiddenif can see it (not visible to other V1 team members)

---

## Root Cause Analysis

### The Code is CORRECT ✅

**Frontend (Dashboard.jsx):**
```javascript
Line 127: const [selectedTeamId, setSelectedTeamId] = useState(null)

Line 147: async function handleFile(file) {
  ...
  const { uploadUrl } = await getUploadUrl(
    meetingTitle, 
    file.type || 'audio/mpeg', 
    file.size, 
    selectedTeamId  // ← Correctly passing teamId
  )
}
```

**API Utils (api.js):**
```javascript
export async function getUploadUrl(title, contentType, fileSize, teamId = null) {
  const headers = await authHeaders()
  const body = { title, contentType, fileSize }
  if (teamId) body.teamId = teamId  // ← Correctly adding teamId to request
  
  const res = await axios.post(`${BASE}/upload-url`, body, { headers })
  return res.data
}
```

**Backend (get-upload-url/app.py):**
```python
team_id = body.get('teamId')  # ← Correctly reading teamId

item = {
    'userId':    user_id,
    'meetingId': meeting_id,
    'title':     title,
    'status':    'PENDING',
    's3Key':     s3_key,
    'createdAt': datetime.now(timezone.utc).isoformat(),
    'email':     claims.get('email', ''),
}
if team_id:
    item['teamId'] = team_id  # ← Correctly storing teamId
```

### The Problem: Frontend State Issue 🐛

**Issue:** The `selectedTeamId` state is NOT being preserved correctly.

**Why this happens:**

1. **Page Refresh/Navigation:** If the page refreshed or user navigated, `selectedTeamId` resets to `null`
2. **State Not Persisted:** The team selection is stored in React state, not localStorage
3. **Race Condition:** The upload might happen before team selection fully updates

**Evidence:**
```
Latest upload by thehiddenif:
  Title: WhatsApp Audio 2026-02-17 at 19.24.27
  TeamId: NONE - Personal meeting  ← This proves selectedTeamId was null
  Status: DONE
```

---

## Current System Capabilities

### ✅ What Works (Backend)

1. **Team Creation:**
   - Any user can create a team
   - Gets unique teamId and invite code
   - Becomes team owner

2. **Team Joining:**
   - Any user can join with invite code
   - Added to team members list
   - Can see all team meetings

3. **Team Upload (when teamId is sent):**
   - Meeting stored with teamId
   - ALL team members can see it
   - Uploader info preserved

4. **Team Visibility:**
   - Query by teamId returns ALL meetings
   - Team membership validated
   - Works for all members

### ❌ What's Broken (Frontend)

1. **Team Selection Persistence:**
   - Team selection doesn't persist across page refresh
   - State resets to `null` on reload
   - Upload happens with `null` teamId → Personal meeting

2. **No Visual Confirmation:**
   - User doesn't see which team is selected during upload
   - No warning if team selection is lost
   - Silent failure (meeting goes to Personal)

---

## User Permissions (Current System)

### Any Team Member Can:
- ✅ See ALL team meetings
- ✅ Upload meetings to the team (if teamId is sent)
- ✅ View meeting details
- ✅ Update action items
- ✅ See who uploaded each meeting

### Team Owner Can:
- ✅ Everything a member can do
- ✅ See team invite code
- ❌ Cannot remove members (not implemented)
- ❌ Cannot delete team (not implemented)

### Uploader vs Non-Uploader:
- **No difference!** Both have equal permissions
- Both can upload to team
- Both can see all team meetings
- Both can update action items

---

## Why It Went to Personal

**Scenario:**
```
1. User selects "V1 - Legacy"
   → selectedTeamId = "95febcb2-97e2-4395-bdde-da8475dbae0d"

2. [SOMETHING HAPPENS - page refresh? navigation? state reset?]
   → selectedTeamId = null

3. User uploads file
   → getUploadUrl(..., null)  ← teamId is null!
   → Backend stores meeting WITHOUT teamId
   → Meeting becomes personal

4. Meeting processes successfully
   → Status: DONE
   → But only visible to uploader
```

---

## The Fix Needed

### Option 1: Persist Team Selection (Recommended)

Store `selectedTeamId` in localStorage so it survives page refresh:

```javascript
// When team changes
function handleTeamChange(teamId) {
  setSelectedTeamId(teamId)
  localStorage.setItem('selectedTeamId', teamId || '')
}

// On page load
useEffect(() => {
  const savedTeamId = localStorage.getItem('selectedTeamId')
  if (savedTeamId) setSelectedTeamId(savedTeamId)
}, [])
```

### Option 2: Show Team in Upload UI

Display which team the upload will go to:

```javascript
<div style={s.uploadTeamInfo}>
  {selectedTeamId ? (
    <p>📤 Uploading to: <strong>{teamName}</strong></p>
  ) : (
    <p>📤 Uploading to: <strong>Personal (Just Me)</strong></p>
  )}
</div>
```

### Option 3: Require Team Selection

Don't allow upload if team is selected but state is lost:

```javascript
async function handleFile(file) {
  // Check if we're on a team page but teamId is null
  const urlParams = new URLSearchParams(window.location.search)
  const expectedTeam = urlParams.get('team')
  
  if (expectedTeam && !selectedTeamId) {
    setError('Team selection lost. Please select team again.')
    return
  }
  
  // Continue with upload...
}
```

---

## Testing Needed

### Test 1: Team Upload (Happy Path)
1. Log in as thehiddenif
2. Select "V1 - Legacy"
3. Upload audio
4. **Verify:** Meeting has teamId in database
5. **Verify:** All 4 V1 members can see it

### Test 2: Team Upload After Refresh
1. Log in as thehiddenif
2. Select "V1 - Legacy"
3. **Refresh page** (Ctrl+R)
4. Upload audio
5. **Verify:** Meeting still has teamId

### Test 3: Personal Upload
1. Log in as thehiddenif
2. Select "Personal (Just Me)"
3. Upload audio
4. **Verify:** Meeting has NO teamId
5. **Verify:** Only thehiddenif can see it

### Test 4: Switch Teams
1. Log in as thehiddenif
2. Select "V1 - Legacy"
3. Upload audio → Should go to V1
4. Select "V2 - Active"
5. Upload audio → Should go to V2
6. **Verify:** Each meeting in correct team

---

## Summary

**The backend is working perfectly.** The issue is in the frontend:

1. ✅ Backend correctly stores teamId when provided
2. ✅ Backend correctly returns meetings by teamId
3. ✅ All team members can see team meetings
4. ❌ Frontend loses team selection (state resets to null)
5. ❌ Upload happens with null teamId → Personal meeting

**Fix:** Persist `selectedTeamId` in localStorage or add visual confirmation of which team the upload will go to.

---

## Next Steps

1. **Don't modify yet** - waiting for your approval
2. Implement Option 1 (localStorage persistence)
3. Add Option 2 (visual confirmation)
4. Test all 4 scenarios above
5. Verify with all 3 accounts

**Status:** Diagnosed, ready to fix
