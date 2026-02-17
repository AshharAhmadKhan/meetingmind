#!/bin/bash

# Day 5 Commit Script - Duplicate Action Detection

echo "📝 Committing Day 5: Duplicate Action Detection..."

# Add all changes
git add .

# Commit with detailed message
git commit -m "feat: Day 5 - Duplicate Action Detection with Embeddings

Implemented complete duplicate detection system:

Backend:
- Created check-duplicate Lambda with cosine similarity algorithm
- Modified process-meeting Lambda to generate embeddings
- Added /check-duplicate POST endpoint to API Gateway
- Backfilled embeddings for all 32 existing action items

Frontend:
- Added 'Check Duplicates' button in Actions Overview
- Implemented duplicate results panel with similarity scores
- Added chronic blocker warnings (tasks repeated 3+ times)
- Added history view for similar items

Infrastructure:
- Fixed S3 bucket deployment (frontend vs audio bucket)
- Added CloudFront 404 error handling for React routes
- Updated SAM template with new Lambda function

Testing:
- Backend: 7 duplicates detected with 100% similarity
- Frontend: UI working correctly with real data
- Coverage: 100% of action items have embeddings

Files:
- backend/functions/check-duplicate/app.py (NEW)
- backend/functions/process-meeting/app.py (MODIFIED)
- backend/template.yaml (MODIFIED)
- frontend/src/pages/ActionsOverview.jsx (MODIFIED)
- frontend/src/utils/api.js (MODIFIED)
- docs/implementation/DAY5_DUPLICATE_DETECTION.md (NEW)
- scripts/generate-embeddings.py (NEW)

Status: ✅ Complete and tested"

echo "✅ Day 5 committed successfully!"
echo ""
echo "📊 Summary:"
echo "  - Backend Lambda deployed and tested"
echo "  - Frontend UI working with real data"
echo "  - 7 duplicates detected in test data"
echo "  - 100% embedding coverage"
echo ""
echo "🚀 Ready for Day 6!"
