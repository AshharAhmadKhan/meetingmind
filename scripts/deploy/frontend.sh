#!/bin/bash

# MeetingMind Frontend Deployment Script (Bash/Linux/Mac)
# Deploys the React frontend to S3 and invalidates CloudFront cache
# 
# For Windows PowerShell, use: deploy-frontend.ps1

set -e

echo "🚀 Starting MeetingMind Frontend Deployment..."

# Configuration
CLOUDFRONT_DIST_ID="E3CAAI97MXY83V"
S3_BUCKET="meetingmind-frontend-707411439284"
REGION="ap-south-1"

# Navigate to project root
cd "$(dirname "$0")"

# Step 1: Build the frontend
echo "📦 Building frontend..."
cd frontend
npm run build

# Step 2: Sync to S3
echo "☁️  Uploading to S3..."
aws s3 sync dist/ s3://${S3_BUCKET} --delete --region ${REGION}

# Step 3: Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DIST_ID} \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "✅ Deployment complete!"
echo "🌐 Frontend URL: https://dcfx593ywvy92.cloudfront.net"
echo "💰 Debt Dashboard: https://dcfx593ywvy92.cloudfront.net/debt"
echo "🔄 CloudFront Invalidation ID: ${INVALIDATION_ID}"
echo ""
echo "⏳ Note: CloudFront cache invalidation may take 1-2 minutes to complete."
