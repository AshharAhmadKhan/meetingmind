# Deploy Both Backend and Frontend
# Full deployment script for MeetingMind

$ErrorActionPreference = "Stop"

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MeetingMind Full Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Deploy Backend
Write-Host "🔧 Step 1/2: Deploying Backend..." -ForegroundColor Yellow
Write-Host ""
& "$scriptPath\deploy-backend.ps1"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Deploy Frontend
Write-Host "🎨 Step 2/2: Deploying Frontend..." -ForegroundColor Yellow
Write-Host ""
& "$scriptPath\deploy-frontend.ps1"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Full Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Application URL: https://dcfx593ywvy92.cloudfront.net"
Write-Host "🔌 API URL: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
Write-Host ""
Write-Host "📝 Next steps:"
Write-Host "  1. Wait 1-2 minutes for CloudFront invalidation"
Write-Host "  2. Test the application"
Write-Host "  3. Check CloudWatch logs if issues occur"
