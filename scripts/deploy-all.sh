#!/bin/bash
# Deploy Both Backend and Frontend
# Full deployment script for MeetingMind

set -e

SCRIPT_DIR="$(dirname "$0")"

echo "========================================="
echo "MeetingMind Full Deployment"
echo "========================================="
echo ""

# Deploy Backend
echo "🔧 Step 1/2: Deploying Backend..."
echo ""
bash "$SCRIPT_DIR/deploy-backend.sh"

echo ""
echo "========================================="
echo ""

# Deploy Frontend
echo "🎨 Step 2/2: Deploying Frontend..."
echo ""
bash "$SCRIPT_DIR/deploy-frontend.sh"

echo ""
echo "========================================="
echo "✅ Full Deployment Complete!"
echo "========================================="
echo ""
echo "🌐 Application URL: https://dcfx593ywvy92.cloudfront.net"
echo "🔌 API URL: https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
echo ""
echo "📝 Next steps:"
echo "  1. Wait 1-2 minutes for CloudFront invalidation"
echo "  2. Test the application"
echo "  3. Check CloudWatch logs if issues occur"
