#!/bin/bash
# Deploy Backend to AWS
# Stack: meetingmind-stack
# Region: ap-south-1

set -e

echo "========================================="
echo "MeetingMind Backend Deployment"
echo "========================================="
echo ""

# Configuration
STACK_NAME="meetingmind-stack"
REGION="ap-south-1"
S3_BUCKET="aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2"

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

echo "📦 Building SAM application..."
sam build

echo ""
echo "🚀 Deploying to AWS..."
sam deploy \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --capabilities CAPABILITY_IAM \
  --s3-bucket "$S3_BUCKET" \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

echo ""
echo "✅ Backend deployed successfully!"
echo ""
echo "API URL: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
echo "Stack: $STACK_NAME"
echo "Region: $REGION"
