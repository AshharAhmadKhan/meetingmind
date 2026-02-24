#!/bin/bash

# COMPLETE FULL DEPLOYMENT SCRIPT
# Deploys EVERYTHING: Backend (SAM) + All Lambda Functions + Frontend
# Use this for complete deployments after code changes

set -e

echo ""
echo "================================================================================"
echo "MEETINGMIND COMPLETE DEPLOYMENT"
echo "================================================================================"
echo ""

START_TIME=$(date +%s)

# Configuration
STACK_NAME="meetingmind-stack"
REGION="ap-south-1"
S3_BUCKET="aws-sam-cli-managed-default-samclisourcebucket-ycgahiblhag2"
CLOUDFRONT_DIST_ID="E3CAAI97MXY83V"
FRONTEND_S3_BUCKET="meetingmind-frontend-707411439284"

echo "Configuration:"
echo "  Stack: $STACK_NAME"
echo "  Region: $REGION"
echo "  S3 Bucket: $S3_BUCKET"
echo ""

# ============================================================================
# STEP 1: BUILD BACKEND
# ============================================================================
echo "STEP 1: Building Backend (SAM)"
echo "--------------------------------------------------------------------------------"

cd backend
echo "Running sam build..."
sam build

if [ $? -ne 0 ]; then
    echo "✗ Backend build failed"
    exit 1
fi

echo "✓ Backend build successful"
cd ..
echo ""

# ============================================================================
# STEP 2: DEPLOY BACKEND (SAM)
# ============================================================================
echo "STEP 2: Deploying Backend (SAM)"
echo "--------------------------------------------------------------------------------"

cd backend
echo "Running sam deploy..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM \
    --s3-bucket $S3_BUCKET \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

if [ $? -ne 0 ]; then
    echo "✗ Backend deployment failed"
    exit 1
fi

echo "✓ Backend deployment successful"
cd ..
echo ""

# ============================================================================
# STEP 3: BUILD FRONTEND
# ============================================================================
echo "STEP 3: Building Frontend (React)"
echo "--------------------------------------------------------------------------------"

cd frontend
echo "Running npm run build..."
npm run build

if [ $? -ne 0 ]; then
    echo "✗ Frontend build failed"
    exit 1
fi

echo "✓ Frontend build successful"
cd ..
echo ""

# ============================================================================
# STEP 4: DEPLOY FRONTEND
# ============================================================================
echo "STEP 4: Deploying Frontend (S3 + CloudFront)"
echo "--------------------------------------------------------------------------------"

cd frontend
echo "Uploading to S3..."
aws s3 sync dist/ s3://$FRONTEND_S3_BUCKET --delete --region $REGION

if [ $? -ne 0 ]; then
    echo "✗ S3 upload failed"
    exit 1
fi

echo "✓ S3 upload successful"

echo "Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_DIST_ID \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

if [ $? -ne 0 ]; then
    echo "✗ CloudFront invalidation failed"
    exit 1
fi

echo "✓ CloudFront invalidation created: $INVALIDATION_ID"
cd ..
echo ""

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo "================================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  ✓ Backend (SAM) deployed"
echo "  ✓ All Lambda functions updated"
echo "  ✓ Frontend built and deployed"
echo "  ✓ CloudFront cache invalidated"
echo ""
echo "Deployment Time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "URLs:"
echo "  Frontend: https://dcfx593ywvy92.cloudfront.net"
echo "  API: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
echo ""
echo "Next Steps:"
echo "  1. Wait 1-2 minutes for CloudFront cache to clear"
echo "  2. Test the application at the frontend URL"
echo "  3. Upload test audio to verify AI extraction fix"
echo "  4. Run: python scripts/test/comprehensive-feature-test.py"
echo ""
echo "================================================================================"
