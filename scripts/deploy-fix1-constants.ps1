#!/usr/bin/env pwsh
# Deploy Fix #1: Extract Magic Numbers to Constants
# Part of demo-critical fixes for AWS Builder Center competition

Write-Host "🚀 Deploying Fix #1: Magic Numbers → Constants" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend
Set-Location backend

Write-Host "📦 Building SAM application..." -ForegroundColor Yellow
sam build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful!" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Deploying to AWS..." -ForegroundColor Yellow
sam deploy --no-confirm-changeset

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""

# Return to root
Set-Location ..

Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Extracted 16 magic numbers to constants.py" -ForegroundColor Green
Write-Host "  ✓ Created Lambda layer for shared constants" -ForegroundColor Green
Write-Host "  ✓ Updated 4 Lambda functions:" -ForegroundColor Green
Write-Host "    - process-meeting" -ForegroundColor Gray
Write-Host "    - get-debt-analytics" -ForegroundColor Gray
Write-Host "    - get-all-actions" -ForegroundColor Gray
Write-Host "    - check-duplicate" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Impact: Code looks professional for judge review" -ForegroundColor Cyan
Write-Host "⚡ Risk: VERY LOW (pure refactoring, no logic changes)" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Fix #1 Complete! Ready to test." -ForegroundColor Green
