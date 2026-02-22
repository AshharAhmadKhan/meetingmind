#!/bin/bash
# Test that CORS headers are now returned on error responses

API_URL="https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"

echo "Testing CORS headers on error responses..."
echo ""

# Test 1: OPTIONS request (should work)
echo "1. Testing OPTIONS request (preflight):"
curl -X OPTIONS \
  -H "Origin: https://dcfx593ywvy92.cloudfront.net" \
  -H "Access-Control-Request-Method: PUT" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -i \
  "$API_URL/meetings/test-id/actions/test-action-id" 2>&1 | grep -i "access-control"

echo ""
echo "2. Testing PUT request with invalid token (should return 502 with CORS headers):"
curl -X PUT \
  -H "Origin: https://dcfx593ywvy92.cloudfront.net" \
  -H "Authorization: invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"status":"todo"}' \
  -i \
  "$API_URL/meetings/test-id/actions/test-action-id" 2>&1 | grep -i "access-control"

echo ""
echo "✓ If you see Access-Control-Allow-Origin headers above, CORS is fixed!"
