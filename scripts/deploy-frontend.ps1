# Deploy Frontend to S3 + CloudFront
# Bucket: meetingmind-frontend-707411439284
# Distribution: E3CAAI97MXY83V
# URL: https://dcfx593ywvy92.cloudfront.net

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MeetingMind Frontend Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$S3_BUCKET = "meetingmind-frontend-707411439284"
$CLOUDFRONT_ID = "E3CAAI97MXY83V"
$REGION = "ap-south-1"

# Navigate to frontend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\..\frontend"

Write-Host "📦 Building frontend..." -ForegroundColor Yellow
npm run build

Write-Host ""
Write-Host "📤 Uploading to S3..." -ForegroundColor Yellow
aws s3 sync dist/ s3://$S3_BUCKET/ `
  --region $REGION `
  --delete `
  --cache-control "public, max-age=31536000, immutable" `
  --exclude "index.html"

# Upload index.html separately with no-cache
aws s3 cp dist/index.html s3://${S3_BUCKET}/index.html `
  --region $REGION `
  --cache-control "no-cache, no-store, must-revalidate"

Write-Host ""
Write-Host "🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
aws cloudfront create-invalidation `
  --distribution-id $CLOUDFRONT_ID `
  --paths "/*" `
  --query 'Invalidation.Id' `
  --output text

Write-Host ""
Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "URL: https://dcfx593ywvy92.cloudfront.net"
Write-Host "S3 Bucket: $S3_BUCKET"
Write-Host "CloudFront: $CLOUDFRONT_ID"
Write-Host ""
Write-Host "⏳ CloudFront invalidation in progress (takes 1-2 minutes)" -ForegroundColor Yellow
