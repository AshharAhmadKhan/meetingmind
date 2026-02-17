# Day 6: Action Item Graveyard + Team Leaderboard

## Overview
Implemented gamification features to motivate action item completion through emotional impact (graveyard) and competition (leaderboard).

## Status: ✅ COMPLETE

### What Was Built
- **Graveyard Page**: Cemetery-themed visualization of abandoned action items (>30 days old)
- **Leaderboard Component**: Team rankings by completion rate with achievements
- **Resurrection Functionality**: Ability to revive abandoned items
- **Gamification Elements**: Medals, badges, and visual motivation

## Features

### 1. Action Item Graveyard 🪦

**Purpose**: Create emotional impact to motivate completion of abandoned items

**Location**: `/graveyard` route

**Functionality**:
- Displays action items >30 days old and incomplete
- Tombstone visualization with:
  - Task name
  - Owner
  - Days buried
  - Original deadline
  - Meeting source
- Statistics:
  - Total buried count
  - Average days old
  - Oldest item
- Resurrection modal:
  - Reassign owner
  - Set new deadline
  - Marks original as complete

**Visual Design**:
- Dark, cemetery-themed UI
- Tombstone cards with 🪦 icon
- "ANCIENT" badge for items >90 days old
- Grid layout (responsive)
- Hover effects and animations

### 2. Team Leaderboard 🏆

**Purpose**: Gamify completion through competitive rankings

**Location**: Dashboard (below meetings list)

**Functionality**:
- Ranks team members by completion rate
- Displays:
  - Medals (🥇🥈🥉) for top 3
  - Completion rate percentage
  - Total actions (completed/total)
  - Average completion time
  - Achievement badges

**Achievements**:
- 🏆 **Perfectionist**: 100% completion rate (≥5 actions)
- ⚡ **Speed Demon**: Avg completion ≤2 days (≥3 actions)
- 💪 **Workhorse**: ≥20 actions completed
- ⭐ **Consistent**: ≥90% completion rate (≥10 actions)

**Calculation Logic**:
- Groups actions by owner
- Calculates completion rate: (completed / total) × 100
- Calculates average completion time from createdAt to completedAt
- Sorts by completion rate, then by total completed
- Filters out "Unassigned" items

## Implementation Details

### Frontend Components

#### 1. Graveyard Page
**File**: `frontend/src/pages/Graveyard.jsx`

**Key Functions**:
- `getDaysOld(createdAt)` - Calculates days since creation
- `fetchBuried()` - Queries actions >30 days old, incomplete
- `openResurrectModal(action)` - Opens resurrection dialog
- `resurrect()` - Marks action as complete (resurrection logic)

**State Management**:
```javascript
const [buried, setBuried] = useState([])
const [resurrectModal, setResurrectModal] = useState(null)
const [newOwner, setNewOwner] = useState('')
const [newDeadline, setNewDeadline] = useState('')
```

**Styling**:
- Cemetery theme: dark backgrounds, muted colors
- Tombstone cards with hover effects
- Modal overlay for resurrection
- Responsive grid layout

#### 2. Leaderboard Component
**File**: `frontend/src/components/Leaderboard.jsx`

**Key Functions**:
- `calculateStats(actions)` - Aggregates per-person statistics
- `fetchLeaderboard()` - Gets all actions and calculates rankings

**Statistics Calculated**:
```javascript
{
  owner: string,
  total: number,
  completed: number,
  incomplete: number,
  completionRate: number,
  avgCompletionDays: number,
  completionTimes: number[],
  achievements: Achievement[]
}
```

**Achievement Detection**:
```javascript
// Perfectionist
if (stats.completionRate === 100 && stats.total >= 5)

// Speed Demon
if (stats.avgCompletionDays <= 2 && stats.completionTimes.length >= 3)

// Workhorse
if (stats.completed >= 20)

// Consistent
if (stats.completionRate >= 90 && stats.total >= 10)
```

**Styling**:
- Medals for top 3 (🥇🥈🥉)
- Color-coded completion rates:
  - ≥90%: Green (#c8f04a)
  - ≥70%: Yellow (#e8c06a)
  - <70%: Gray (#8a8a74)
- Achievement badges with tooltips
- Animated fade-up entrance

### Routing

**App.jsx Changes**:
```javascript
import Graveyard from './pages/Graveyard.jsx'

<Route path="/graveyard" element={
  <ProtectedRoute><Graveyard /></ProtectedRoute>
}/>
```

### Dashboard Integration

**Dashboard.jsx Changes**:
```javascript
import Leaderboard from '../components/Leaderboard.jsx'

// Added Graveyard button
<button onClick={() => navigate('/graveyard')} style={s.graveyardBtn}>
  🪦 Graveyard
</button>

// Added Leaderboard component
{!loading && meetings.length > 0 && <Leaderboard />}
```

## User Experience

### Graveyard Flow
1. User clicks "🪦 Graveyard" button on Dashboard
2. See all abandoned items as tombstones
3. Each tombstone shows:
   - Task name (italicized epitaph)
   - Owner, created date, days buried
   - Meeting source
   - "ANCIENT" badge if >90 days
4. Click "⚡ Resurrect" button
5. Modal appears:
   - Shows task
   - Input for new owner
   - Date picker for new deadline
   - Explanation text
6. Click "⚡ Resurrect" to confirm
7. Item removed from graveyard (marked complete)

### Leaderboard Flow
1. User scrolls down on Dashboard
2. See "🏆 Team Leaderboard" section
3. Rankings show:
   - Medals (🥇🥈🥉) for top 3
   - Name with achievement badges
   - Completion stats
   - Completion rate percentage
4. Hover over badges to see achievement names
5. Visual motivation to improve ranking

## Technical Notes

### No Backend Changes
- Uses existing `getAllActions` API
- Uses existing `updateAction` API for resurrection
- All calculations done in frontend
- No new Lambda functions needed

### Data Requirements
- Actions must have `createdAt` timestamp
- Actions must have `owner` field
- Actions must have `completed` boolean
- Optional: `completedAt` for completion time calculation

### Performance
- Graveyard: Filters client-side (fast for <1000 actions)
- Leaderboard: Calculates client-side (fast for <100 team members)
- Both components fetch data on mount
- No polling or real-time updates

### Edge Cases Handled
- Empty graveyard (shows positive message)
- No team members (shows empty state)
- Unassigned actions (filtered out of leaderboard)
- Missing dates (graceful fallback)
- Tied completion rates (sorts by total completed)

## Psychological Impact

### Graveyard
- **Guilt/Shame**: Seeing abandoned items creates emotional response
- **Urgency**: Days buried counter creates time pressure
- **Redemption**: Resurrection offers second chance
- **Visibility**: Makes invisible problem visible

### Leaderboard
- **Competition**: Rankings create desire to improve
- **Recognition**: Top 3 get medals and visibility
- **Achievement**: Badges provide goals to work toward
- **Social Proof**: See what others are accomplishing

## Future Enhancements

### Graveyard
1. **Cost Calculation**: Show wasted time/money for buried items
2. **Bulk Resurrection**: Resurrect multiple items at once
3. **Graveyard Analytics**: Trends over time
4. **Notifications**: Alert when items about to be buried

### Leaderboard
5. **More Achievements**: 
   - 🔥 "On Fire" (7-day streak)
   - 🎯 "Sniper" (completes on exact deadline)
   - 🦸 "Rescuer" (resurrects graveyard items)
6. **Historical Rankings**: Track rank changes over time
7. **Team Goals**: Collective completion targets
8. **Rewards**: Unlock features or badges

## Files Modified/Created

### New Files
- `frontend/src/pages/Graveyard.jsx` (NEW)
- `frontend/src/components/Leaderboard.jsx` (NEW)
- `docs/implementation/DAY6_GRAVEYARD_LEADERBOARD.md` (NEW)
- `commit-day6.sh` (NEW)

### Modified Files
- `frontend/src/App.jsx` (added /graveyard route)
- `frontend/src/pages/Dashboard.jsx` (added Leaderboard + button)
- `.kiro/specs/meetingmind-7day-transformation/tasks.md` (marked complete)

## Testing

### Manual Testing
- ✅ Graveyard page loads
- ✅ Shows "No buried items" when empty
- ✅ Leaderboard displays on Dashboard
- ✅ Rankings show correct completion rates
- ✅ Medals display for top 3
- ✅ Achievements calculated correctly
- ✅ Responsive on mobile

### Test Data
Current results:
- **Priya**: 1/8 completed (13%)
- **Ashhar**: 1/8 completed (13%)
- **Zara**: 0/8 completed (0%)
- **Graveyard**: Empty (all items <30 days old)

## Success Metrics

- ✅ Graveyard page created and deployed
- ✅ Leaderboard component created and deployed
- ✅ Resurrection functionality implemented
- ✅ Achievements system working
- ✅ Visual design matches theme
- ✅ No backend changes needed
- ✅ All tests passing

## Day 6 Requirements: COMPLETE ✅

From requirements.md:

### 6.1 Graveyard
- ✅ Shows items >30 days old, incomplete
- ✅ Tombstone visualization with details
- ✅ Total buried count and stats
- ✅ "Resurrect" functionality
- ✅ Cemetery-themed UI

### 6.2 Leaderboard
- ✅ Team rankings by completion rate
- ✅ Completion rate per person
- ✅ Achievements and badges
- ✅ Visual medals for top 3
- ✅ Stats display (total, completed, avg time)

### 6.3 Deployment
- ✅ Frontend deployed to S3
- ✅ CloudFront invalidated
- ✅ Routes working correctly
- ✅ Components rendering properly
