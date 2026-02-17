#!/bin/bash

# Day 6 Commit Script - Graveyard + Team Leaderboard

echo "📝 Committing Day 6: Graveyard + Team Leaderboard..."

# Add all changes
git add .

# Commit with detailed message
git commit -m "feat: Day 6 - Action Item Graveyard + Team Leaderboard

Implemented gamification features for motivation:

Frontend:
- Created Graveyard page (/graveyard) with tombstone visualization
- Shows action items >30 days old and incomplete
- Resurrection functionality to revive abandoned items
- Created Leaderboard component with team rankings
- Displays completion rates, medals (🥇🥈🥉), and achievements
- Added to Dashboard below meetings list

Features:
- Graveyard: Cemetery-themed UI with tombstones
- Resurrection modal: Reassign owner and set new deadline
- Leaderboard: Ranked by completion rate
- Achievements: 🏆 Perfectionist, ⚡ Speed Demon, 💪 Workhorse, ⭐ Consistent
- Stats: Total/completed actions, avg completion time per person

UI/UX:
- Added Graveyard button (🪦) to Dashboard navigation
- Responsive grid layout for tombstones
- Animated rankings with medals for top 3
- Visual badges for achievements

Files:
- frontend/src/pages/Graveyard.jsx (NEW)
- frontend/src/components/Leaderboard.jsx (NEW)
- frontend/src/App.jsx (MODIFIED - added /graveyard route)
- frontend/src/pages/Dashboard.jsx (MODIFIED - added Leaderboard + button)

Status: ✅ Complete and tested
- Graveyard displays correctly (empty = good!)
- Leaderboard shows team rankings
- No backend changes needed (uses existing APIs)"

echo "✅ Day 6 committed successfully!"
echo ""
echo "📊 Summary:"
echo "  - Graveyard page with tombstone visualization"
echo "  - Team Leaderboard with rankings and achievements"
echo "  - Resurrection functionality for abandoned items"
echo "  - Gamification to motivate completion"
echo ""
echo "🚀 Ready for Day 7!"
