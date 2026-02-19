# MeetingMind Frontend Deployment Script (PowerShell)
# Deploys the React frontend to S3 and invalidates CloudFront cache

Write-Host "🚀 Starting MeetingMind Frontend Deployment..." -ForegroundColor Cyan

# Configuration
$CLOUDFRONT_DIST_ID = "E3CAAI97MXY83V"
$S3_BUCKET = "meetingmind-frontend-707411439284"
$REGION = "ap-south-1"

# Step 1: Build the frontend
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Sync to S3
Write-Host "☁️  Uploading to S3..." -ForegroundColor Yellow
aws s3 sync dist/ s3://$S3_BUCKET --delete --region $REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ S3 upload failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Invalidate CloudFront cache
Write-Host "🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
$invalidation = aws cloudfront create-invalidation `
    --distribution-id $CLOUDFRONT_DIST_ID `
    --paths "/*" `
    --query 'Invalidation.Id' `
    --output text

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CloudFront invalidation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Frontend URL: https://dcfx593ywvy92.cloudfront.net" -ForegroundColor Cyan
Write-Host "💰 Debt Dashboard: https://dcfx593ywvy92.cloudfront.net/debt" -ForegroundColor Cyan
Write-Host "🔄 CloudFront Invalidation ID: $invalidation" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Note: CloudFront cache invalidation may take 1-2 minutes to complete." -ForegroundColor Yellow

# Return to root directory
Set-Location ..
