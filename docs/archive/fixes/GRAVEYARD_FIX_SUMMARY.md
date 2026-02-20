# Graveyard Page Fix - Team Member Access

## Issue
Non-uploader team members saw empty graveyard page even when switching to V1 or V2 teams.

## Root Cause
The Graveyard page (`frontend/src/pages/Graveyard.jsx`) was missing:
1. TeamSelector component
2. `selectedTeamId` state
3. `teamId` parameter in API call

Without the teamId parameter, the `get-all-actions` Lambda queried by the current user's userId, which returned NO meetings for non-uploaders (they don't upload meetings, they only access team meetings).

## Fix Applied

### Changes to `frontend/src/pages/Graveyard.jsx`:

1. **Added TeamSelector import**:
```javascript
import TeamSelector from '../components/TeamSelector.jsx'
```

2. **Added selectedTeamId state**:
```javascript
const [selectedTeamId, setSelectedTeamId] = useState(null)
```

3. **Updated useEffect dependency**:
```javascript
useEffect(() => {
  // ...
}, [selectedTeamId])  // Re-fetch when team changes
```

4. **Updated API call to pass teamId**:
```javascript
const data = await getAllActions(null, null, selectedTeamId)
```

5. **Added TeamSelector component to JSX**:
```jsx
<main style={s.main}>
  {/* Team Selector */}
  <div style={{marginBottom: 24}}>
    <TeamSelector 
      selectedTeamId={selectedTeamId}
      onTeamChange={setSelectedTeamId}
    />
  </div>
  {/* Rest of content */}
</main>
```

## Verification

### Database Check:
- Total meetings: 6
- Total actions: 20
- Completed (graveyard) items: 5
  - 2 from V1 team
  - 3 from V2 team

### Expected Behavior After Fix:
1. Non-uploader visits `/graveyard`
2. Initially shows "Personal (Just Me)" - empty (correct, they have no personal meetings)
3. User switches to "Project V1" team → Shows 2 graveyard items
4. User switches to "Project V2" team → Shows 3 graveyard items

## Deployment
- Frontend built and deployed to S3
- CloudFront cache cleared (invalidation: I8AJVP3B1NM3NW921B8EGEKWRF)
- Changes live at: https://dcfx593ywvy92.cloudfront.net/graveyard

## Related Issues
This is the same pattern that was already working correctly on:
- Dashboard page (team meetings visibility)
- Actions Overview page (action items by team)
- Debt Dashboard page (debt analytics by team)

The Graveyard page was the only page missing the TeamSelector integration.
