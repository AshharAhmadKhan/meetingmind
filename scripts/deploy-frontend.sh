#!/bin/bash
# Deploy Frontend to S3 + CloudFront
# Bucket: meetingmind-frontend-707411439284
# Distribution: E3CAAI97MXY83V
# URL: https://dcfx593ywvy92.cloudfront.net

set -e

echo "========================================="
echo "MeetingMind Frontend Deployment"
echo "========================================="
echo ""

# Configuration
S3_BUCKET="meetingmind-frontend-707411439284"
CLOUDFRONT_ID="E3CAAI97MXY83V"
REGION="ap-south-1"

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

echo "📦 Building frontend..."
npm run build

echo ""
echo "📤 Uploading to S3..."
aws s3 sync dist/ s3://$S3_BUCKET/ \
  --region $REGION \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html"

# Upload index.html separately with no-cache
aws s3 cp dist/index.html s3://$S3_BUCKET/index.html \
  --region $REGION \
  --cache-control "no-cache, no-store, must-revalidate"

echo ""
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text

echo ""
echo "✅ Frontend deployed successfully!"
echo ""
echo "URL: https://dcfx593ywvy92.cloudfront.net"
echo "S3 Bucket: $S3_BUCKET"
echo "CloudFront: $CLOUDFRONT_ID"
echo ""
echo "⏳ CloudFront invalidation in progress (takes 1-2 minutes)"
