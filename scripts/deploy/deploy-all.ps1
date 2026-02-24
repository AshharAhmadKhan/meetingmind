# COMPLETE FULL DEPLOYMENT SCRIPT
# Deploys EVERYTHING: Backend (SAM) + All Lambda Functions + Frontend
# Use this for complete deployments after code changes

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MEETINGMIND COMPLETE DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Configuration
$STACK_NAME = "meetingmind-stack"
$REGION = "ap-south-1"
$S3_BUCKET = "aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2"
$CLOUDFRONT_DIST_ID = "E3CAAI97MXY83V"
$FRONTEND_S3_BUCKET = "meetingmind-frontend-707411439284"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Stack: $STACK_NAME"
Write-Host "  Region: $REGION"
Write-Host "  S3 Bucket: $S3_BUCKET"
Write-Host ""

# ============================================================================
# STEP 1: BUILD BACKEND
# ============================================================================
Write-Host "STEP 1: Building Backend (SAM)" -ForegroundColor Cyan
Write-Host "-" * 80

try {
    Set-Location backend
    
    Write-Host "Running sam build..." -ForegroundColor Yellow
    sam build
    
    if ($LASTEXITCODE -ne 0) {
        throw "SAM build failed"
    }
    
    Write-Host "✓ Backend build successful" -ForegroundColor Green
    Set-Location ..
} catch {
    Write-Host "✗ Backend build failed: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 2: DEPLOY BACKEND (SAM)
# ============================================================================
Write-Host "STEP 2: Deploying Backend (SAM)" -ForegroundColor Cyan
Write-Host "-" * 80

try {
    Set-Location backend
    
    Write-Host "Running sam deploy..." -ForegroundColor Yellow
    sam deploy `
        --stack-name $STACK_NAME `
        --region $REGION `
        --capabilities CAPABILITY_IAM `
        --s3-bucket $S3_BUCKET `
        --no-confirm-changeset `
        --no-fail-on-empty-changeset
    
    if ($LASTEXITCODE -ne 0) {
        throw "SAM deploy failed"
    }
    
    Write-Host "✓ Backend deployment successful" -ForegroundColor Green
    Set-Location ..
} catch {
    Write-Host "✗ Backend deployment failed: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 3: BUILD FRONTEND
# ============================================================================
Write-Host "STEP 3: Building Frontend (React)" -ForegroundColor Cyan
Write-Host "-" * 80

try {
    Set-Location frontend
    
    Write-Host "Running npm run build..." -ForegroundColor Yellow
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    
    Write-Host "✓ Frontend build successful" -ForegroundColor Green
    Set-Location ..
} catch {
    Write-Host "✗ Frontend build failed: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 4: DEPLOY FRONTEND
# ============================================================================
Write-Host "STEP 4: Deploying Frontend (S3 + CloudFront)" -ForegroundColor Cyan
Write-Host "-" * 80

try {
    Set-Location frontend
    
    Write-Host "Uploading to S3..." -ForegroundColor Yellow
    aws s3 sync dist/ s3://$FRONTEND_S3_BUCKET --delete --region $REGION
    
    if ($LASTEXITCODE -ne 0) {
        throw "S3 upload failed"
    }
    
    Write-Host "✓ S3 upload successful" -ForegroundColor Green
    
    Write-Host "Invalidating CloudFront cache..." -ForegroundColor Yellow
    $invalidation = aws cloudfront create-invalidation `
        --distribution-id $CLOUDFRONT_DIST_ID `
        --paths "/*" `
        --query 'Invalidation.Id' `
        --output text
    
    if ($LASTEXITCODE -ne 0) {
        throw "CloudFront invalidation failed"
    }
    
    Write-Host "✓ CloudFront invalidation created: $invalidation" -ForegroundColor Green
    Set-Location ..
} catch {
    Write-Host "✗ Frontend deployment failed: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "=" * 80 -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  ✓ Backend (SAM) deployed" -ForegroundColor Green
Write-Host "  ✓ All Lambda functions updated" -ForegroundColor Green
Write-Host "  ✓ Frontend built and deployed" -ForegroundColor Green
Write-Host "  ✓ CloudFront cache invalidated" -ForegroundColor Green
Write-Host ""
Write-Host "Deployment Time: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: https://dcfx593ywvy92.cloudfront.net" -ForegroundColor Cyan
Write-Host "  API: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Wait 1-2 minutes for CloudFront cache to clear"
Write-Host "  2. Test the application at the frontend URL"
Write-Host "  3. Upload test audio to verify AI extraction fix"
Write-Host "  4. Run: python scripts/test/comprehensive-feature-test.py"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
