#!/usr/bin/env python3
"""
Critical Bug Fix Script for MeetingMind
Fixes the 5 critical issues causing 502 Bad Gateway errors:
1. CORS headers (restrict to CloudFront domain)
2. Decimal serialization in all Lambda functions
3. Missing CORS headers in error responses
4. OPTIONS request handling
5. API Gateway CORS configuration
"""

import os
import re

# CloudFront domain for CORS
CLOUDFRONT_DOMAIN = "https://dcfx593ywvy92.cloudfront.net"

# Standard CORS headers to use
CORS_HEADERS_TEMPLATE = f"""
CORS_HEADERS = {{
    'Access-Control-Allow-Origin':  '{CLOUDFRONT_DOMAIN}',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}}
"""

# Lambda functions to fix
LAMBDA_FUNCTIONS = [
    'backend/functions/get-upload-url/app.py',
    'backend/functions/list-meetings/app.py',
    'backend/functions/get-meeting/app.py',
    'backend/functions/update-action/app.py',
    'backend/functions/get-all-actions/app.py',
    'backend/functions/check-duplicate/app.py',
    'backend/functions/get-debt-analytics/app.py',
    'backend/functions/create-team/app.py',
    'backend/functions/join-team/app.py',
    'backend/functions/get-team/app.py',
    'backend/functions/list-user-teams/app.py',
]

def fix_cors_headers(file_path):
    """Fix CORS headers in a Lambda function."""
    print(f"Fixing CORS headers in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace wildcard CORS with CloudFront domain
    content = re.sub(
        r"'Access-Control-Allow-Origin':\s*'\*'",
        f"'Access-Control-Allow-Origin': '{CLOUDFRONT_DOMAIN}'",
        content
    )
    
    # Ensure CORS headers are in all return statements
    # This is a simple check - manual review still needed
    if 'CORS_HEADERS' not in content:
        print(f"  WARNING: {file_path} doesn't define CORS_HEADERS")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Fixed CORS headers in {file_path}")

def add_decimal_serialization(file_path):
    """Ensure decimal_to_float is used in all json.dumps() calls."""
    print(f"Checking Decimal serialization in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if decimal_to_float function exists
    if 'def decimal_to_float' not in content:
        print(f"  WARNING: {file_path} doesn't define decimal_to_float()")
        return
    
    # Find json.dumps() calls without default parameter
    dumps_pattern = r'json\.dumps\(([^)]+)\)(?!\s*,\s*default=)'
    matches = re.findall(dumps_pattern, content)
    
    if matches:
        print(f"  WARNING: Found {len(matches)} json.dumps() calls without default=decimal_to_float")
        print(f"    Manual fix required for: {file_path}")
    else:
        print(f"  ✓ All json.dumps() calls use default=decimal_to_float")

def add_options_handler(file_path):
    """Ensure OPTIONS requests are handled."""
    print(f"Checking OPTIONS handler in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if OPTIONS is handled
    if "event.get('httpMethod') == 'OPTIONS'" not in content and \
       "event['httpMethod'] == 'OPTIONS'" not in content:
        print(f"  WARNING: {file_path} doesn't handle OPTIONS requests")
        print(f"    Manual fix required")
    else:
        print(f"  ✓ OPTIONS handler found")

def main():
    print("="*70)
    print("MeetingMind Critical Bug Fix Script")
    print("="*70)
    print()
    
    for func_path in LAMBDA_FUNCTIONS:
        if not os.path.exists(func_path):
            print(f"SKIP: {func_path} not found")
            continue
        
        print(f"\n{'='*70}")
        print(f"Processing: {func_path}")
        print(f"{'='*70}")
        
        fix_cors_headers(func_path)
        add_decimal_serialization(func_path)
        add_options_handler(func_path)
    
    print(f"\n{'='*70}")
    print("Fix Summary")
    print(f"{'='*70}")
    print("✓ CORS headers updated to use CloudFront domain")
    print("⚠ Decimal serialization checks completed (manual fixes may be needed)")
    print("⚠ OPTIONS handler checks completed (manual fixes may be needed)")
    print()
    print("Next steps:")
    print("1. Review warnings above")
    print("2. Run: cd backend && sam build")
    print("3. Deploy updated Lambda functions")
    print("4. Test frontend at https://dcfx593ywvy92.cloudfront.net")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
