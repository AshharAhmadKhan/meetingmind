# Deploy Backend to AWS
# Stack: meetingmind-stack
# Region: ap-south-1

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MeetingMind Backend Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$STACK_NAME = "meetingmind-stack"
$REGION = "ap-south-1"
$S3_BUCKET = "aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2"

# Navigate to backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\..\backend"

Write-Host "📦 Building SAM application..." -ForegroundColor Yellow
sam build

Write-Host ""
Write-Host "🚀 Deploying to AWS..." -ForegroundColor Yellow
sam deploy `
  --stack-name $STACK_NAME `
  --region $REGION `
  --capabilities CAPABILITY_IAM `
  --s3-bucket $S3_BUCKET `
  --no-confirm-changeset `
  --no-fail-on-empty-changeset

Write-Host ""
Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
Write-Host "Stack: $STACK_NAME"
Write-Host "Region: $REGION"
