#!/bin/bash

# Commit Day 1: Meeting Debt Dashboard

set -e

echo "📝 Committing Day 1: Meeting Debt Dashboard..."

# Add all changes
git add .

# Commit with detailed message
git commit -m "feat: Day 1 - Meeting Debt Dashboard

Implemented Meeting Debt Dashboard with research-backed cost calculations:

Backend:
- New Lambda function: get-debt-analytics
- Calculates debt using $75/hr × 3.2 hours blocked per incomplete action
- Categorizes debt: forgotten (>30 days), overdue, unassigned, at-risk
- Generates 8-week trend data and debt velocity
- API endpoint: GET /debt-analytics

Frontend:
- New page: DebtDashboard.jsx with animated visualizations
- Animated debt counter (CountUp component)
- Pie chart breakdown of debt categories
- 8-week trend line chart
- Completion rate comparison (team vs industry 67% benchmark)
- Action items summary
- Quick wins recommendations
- New route: /debt
- View Debt button on main dashboard

Features:
- Real-time debt calculation from DynamoDB meetings
- Animated charts and counters for visual impact
- Research-backed metrics for credibility
- Actionable insights (Quick Wins section)
- Responsive design matching existing UI

Deployment:
- Backend deployed to meetingmind-stack
- Frontend deployed to CloudFront
- Lambda execution time: ~100-160ms
- X-Ray tracing enabled

Competition Impact:
- Unique innovation not seen in competitors
- Quantifies hidden cost of incomplete meetings
- High visual impact for non-technical judges
- Demonstrates business value and ROI

Tested and verified working in production.
"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin master

echo "✅ Day 1 committed and pushed successfully!"
echo "🌐 GitHub: https://github.com/AshharAhmadKhan/meetingmind"
