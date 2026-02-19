# MeetingMind 7-Day Transformation - Tasks

## Day 1: Meeting Debt Dashboard
- [ ] 1.1 Create backend Lambda function (get-debt-analytics)
  - [ ] 1.1.1 Create app.py with debt calculation logic
  - [ ] 1.1.2 Create requirements.txt
  - [ ] 1.1.3 Add function to SAM template
- [ ] 1.2 Create frontend API client
  - [ ] 1.2.1 Add getDebtAnalytics() to api.js
- [ ] 1.3 Create DebtDashboard page
  - [ ] 1.3.1 Create DebtDashboard.jsx component
  - [ ] 1.3.2 Add route to App.jsx
  - [ ] 1.3.3 Add navigation button to Dashboard
- [ ] 1.4 Deploy and test
  - [ ] 1.4.1 Deploy backend (sam build && sam deploy)
  - [ ] 1.4.2 Deploy frontend (npm run build && sync to S3)
  - [ ] 1.4.3 Test debt dashboard loads
  - [ ] 1.4.4 Verify calculations are accurate
  - [ ] 1.4.5 Test mobile responsive

## Day 2: Enhanced Meeting Summary (Autopsy Report)
- [ ] 2.1 Create ROI calculation Lambda
  - [ ] 2.1.1 Create calculate-meeting-roi function
  - [ ] 2.1.2 Add to SAM template
- [ ] 2.2 Modify process-meeting Lambda
  - [ ] 2.2.1 Calculate ROI on meeting completion
  - [ ] 2.2.2 Store ROI data in DynamoDB
- [ ] 2.3 Update MeetingDetail page
  - [ ] 2.3.1 Add MeetingROI component
  - [ ] 2.3.2 Add QualityScore component
  - [ ] 2.3.3 Add Recommendations section
- [ ] 2.4 Deploy and test
  - [ ] 2.4.1 Deploy backend
  - [ ] 2.4.2 Deploy frontend
  - [ ] 2.4.3 Upload test meeting
  - [ ] 2.4.4 Verify ROI calculation
  - [ ] 2.4.5 Verify recommendations display

## Day 3: Cross-Meeting Action Item View
- [ ] 3.1 Create get-all-actions Lambda
  - [ ] 3.1.1 Create function with filtering logic
  - [ ] 3.1.2 Add to SAM template
- [ ] 3.2 Create DynamoDB GSI
  - [ ] 3.2.1 Add ActionItemsByUser index
  - [ ] 3.2.2 Update SAM template
- [ ] 3.3 Create ActionsOverview page
  - [ ] 3.3.1 Create Kanban board component
  - [ ] 3.3.2 Add filter bar
  - [ ] 3.3.3 Add bulk actions
  - [ ] 3.3.4 Add drag-and-drop
- [ ] 3.4 Deploy and test
  - [ ] 3.4.1 Deploy backend
  - [ ] 3.4.2 Deploy frontend
  - [ ] 3.4.3 Test filtering
  - [ ] 3.4.4 Test drag-and-drop
  - [ ] 3.4.5 Test bulk operations

## Day 4: Action Item Decay Prediction
- [ ] 4.1 Create calculate-decay-risk Lambda
  - [ ] 4.1.1 Implement risk calculation algorithm
  - [ ] 4.1.2 Add to SAM template
- [ ] 4.2 Create EventBridge rule
  - [ ] 4.2.1 Schedule daily risk recalculation
  - [ ] 4.2.2 Add to SAM template
- [ ] 4.3 Update action item display
  - [ ] 4.3.1 Add risk badges to action cards
  - [ ] 4.3.2 Add risk explanation tooltips
  - [ ] 4.3.3 Add intervention suggestions
- [ ] 4.4 Deploy and test
  - [ ] 4.4.1 Deploy backend
  - [ ] 4.4.2 Deploy frontend
  - [ ] 4.4.3 Verify risk scores
  - [ ] 4.4.4 Test EventBridge trigger
  - [ ] 4.4.5 Verify risk badges display

## Day 5: Duplicate Action Detection (Bedrock Embeddings)
- [x] 5.1 Modify process-meeting Lambda
  - [x] 5.1.1 Generate embeddings for action items
  - [x] 5.1.2 Store embeddings in DynamoDB
- [x] 5.2 Create check-duplicate Lambda
  - [x] 5.2.1 Implement cosine similarity
  - [x] 5.2.2 Add duplicate detection logic
  - [x] 5.2.3 Add to SAM template
- [x] 5.3 Update frontend validation
  - [x] 5.3.1 Add duplicate check button in Actions Overview
  - [x] 5.3.2 Show duplicate results panel
  - [ ] 5.3.3 Add smart breakdown suggestions (future enhancement)
- [x] 5.4 Deploy and test
  - [x] 5.4.1 Deploy backend
  - [x] 5.4.2 Deploy frontend (to correct S3 bucket)
  - [x] 5.4.3 Test duplicate detection (7 duplicates found)
  - [x] 5.4.4 Verify similarity scores (100% for exact matches)
  - [x] 5.4.5 Fix CloudFront routing for React (404 → index.html)

## Day 6: Action Item Graveyard + Team Leaderboard
- [x] 6.1 Create Graveyard page
  - [x] 6.1.1 Create Graveyard.jsx component
  - [x] 6.1.2 Add tombstone visualization
  - [x] 6.1.3 Add resurrection functionality
  - [x] 6.1.4 Add route to App.jsx
- [x] 6.2 Create Leaderboard component
  - [x] 6.2.1 Calculate per-person stats
  - [x] 6.2.2 Add ranking logic
  - [x] 6.2.3 Add achievements
  - [x] 6.2.4 Add to Dashboard
- [x] 6.3 Deploy and test
  - [x] 6.3.1 Deploy frontend
  - [ ] 6.3.2 Test graveyard display
  - [ ] 6.3.3 Test resurrection
  - [ ] 6.3.4 Test leaderboard rankings
  - [ ] 6.3.5 Verify achievements

## Day 7: Pattern Detection + Article Rewrite
- [ ] 7.1 Create detect-patterns Lambda
  - [ ] 7.1.1 Implement pattern detection algorithms
  - [ ] 7.1.2 Use Bedrock for pattern analysis
  - [ ] 7.1.3 Add to SAM template
- [ ] 7.2 Create Pattern cards component
  - [ ] 7.2.1 Display detected patterns
  - [ ] 7.2.2 Show symptoms and prescriptions
  - [ ] 7.2.3 Add to Dashboard
- [ ] 7.3 Rewrite competition article
  - [ ] 7.3.1 Add personal story hook
  - [ ] 7.3.2 Add research citations
  - [ ] 7.3.3 Add social proof (testimonials)
  - [ ] 7.3.4 Update COMPETITION_ARTICLE.md
- [ ] 7.4 Create demo video
  - [ ] 7.4.1 Record screen walkthrough
  - [ ] 7.4.2 Add voiceover
  - [ ] 7.4.3 Upload to YouTube
- [ ] 7.5 Deploy and test
  - [ ] 7.5.1 Deploy backend
  - [ ] 7.5.2 Deploy frontend
  - [ ] 7.5.3 Test pattern detection
  - [ ] 7.5.4 Verify pattern cards display
  - [ ] 7.5.5 Final end-to-end test

## Day 8: Team Meeting Visibility Fix (CRITICAL)
- [ ] 8.1 Investigate frontend filtering
  - [ ] 8.1.1 Check Dashboard.jsx for userId filtering
  - [ ] 8.1.2 Check if meetings array is being filtered client-side
  - [ ] 8.1.3 Verify API response contains all team meetings
- [ ] 8.2 Fix frontend display
  - [ ] 8.2.1 Remove any client-side userId filtering
  - [ ] 8.2.2 Add "Uploaded by" indicator on meeting cards
  - [ ] 8.2.3 Add visual distinction for V1 vs V2 teams
- [ ] 8.3 Test team visibility
  - [ ] 8.3.1 Login as thehidden account
  - [ ] 8.3.2 Select "Project V1 - Legacy" team
  - [ ] 8.3.3 Verify 3 V1 meetings appear
  - [ ] 8.3.4 Select "Project V2 - Active" team
  - [ ] 8.3.5 Verify 3 V2 meetings appear
  - [ ] 8.3.6 Select "Personal" - verify 0 meetings
- [ ] 8.4 Deploy and verify
  - [ ] 8.4.1 Deploy frontend changes
  - [ ] 8.4.2 Clear CloudFront cache
  - [ ] 8.4.3 Test with all 3 accounts

## Final Review
- [ ] 9.1 Complete testing
  - [ ] 8.1.1 Test all features work together
  - [ ] 8.1.2 Test mobile responsive
  - [ ] 8.1.3 Test accessibility (keyboard navigation)
  - [ ] 8.1.4 Check console for errors
- [ ] 8.2 Performance optimization
  - [ ] 8.2.1 Verify API response times <500ms
  - [ ] 8.2.2 Verify dashboard loads <2s
  - [ ] 8.2.3 Optimize large queries
- [ ] 8.3 Documentation
  - [ ] 8.3.1 Update README with new features
  - [ ] 8.3.2 Add architecture diagram
  - [ ] 8.3.3 Document API endpoints
- [ ] 8.4 Competition submission
  - [ ] 8.4.1 Final article review
  - [ ] 8.4.2 Demo video ready
  - [ ] 8.4.3 Screenshots prepared
  - [ ] 8.4.4 Submit to competition
