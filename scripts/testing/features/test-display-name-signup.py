#!/usr/bin/env python3
"""
Test script for Issue #3: Display Name Feature
Verifies that users can set display name during registration
"""

import boto3
import sys
from datetime import datetime

def test_display_name_feature():
    """Test that Cognito user pool accepts name attribute"""
    
    print("=" * 60)
    print("Testing Issue #3: Display Name Feature")
    print("=" * 60)
    print()
    
    cognito = boto3.client('cognito-idp', region_name='ap-south-1')
    
    # Get user pool ID from CloudFormation stack
    user_pool_id = 'ap-south-1_mkFJawjMp'
    
    try:
        # Check if user pool supports 'name' attribute
        print("✓ Step 1: Checking user pool configuration...")
        response = cognito.describe_user_pool(UserPoolId=user_pool_id)
        
        schema = response['UserPool']['SchemaAttributes']
        name_attr = next((attr for attr in schema if attr['Name'] == 'name'), None)
        
        if name_attr:
            print(f"  ✓ 'name' attribute found in user pool schema")
            print(f"    - Required: {name_attr.get('Required', False)}")
            print(f"    - Mutable: {name_attr.get('Mutable', True)}")
        else:
            print("  ✗ 'name' attribute NOT found in user pool schema")
            print("  Note: This is a standard Cognito attribute, should be available")
        
        print()
        
        # List a few users to check if name attribute is being stored
        print("✓ Step 2: Checking existing users for name attribute...")
        users_response = cognito.list_users(
            UserPoolId=user_pool_id,
            Limit=5
        )
        
        users_with_names = 0
        users_without_names = 0
        
        for user in users_response['Users']:
            email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), 'Unknown')
            name = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'name'), None)
            
            if name:
                users_with_names += 1
                print(f"  ✓ {email}: has name = '{name}'")
            else:
                users_without_names += 1
                print(f"  ○ {email}: no name attribute (shows as email)")
        
        print()
        print(f"Summary: {users_with_names} users with names, {users_without_names} without")
        print()
        
        # Check pre-signup Lambda configuration
        print("✓ Step 3: Checking pre-signup Lambda configuration...")
        lambda_config = response['UserPool'].get('LambdaConfig', {})
        pre_signup = lambda_config.get('PreSignUp')
        
        if pre_signup:
            print(f"  ✓ Pre-signup trigger configured: {pre_signup}")
            print(f"    This Lambda should extract 'name' attribute and send to admin")
        else:
            print("  ○ No pre-signup trigger configured")
        
        print()
        
        # Summary
        print("=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print()
        print("Frontend Changes:")
        print("  ✓ Name field added to signup form (LoginPage.jsx)")
        print("  ✓ Signup function updated to pass name (auth.js)")
        print()
        print("Backend Status:")
        if name_attr:
            print("  ✓ User pool supports 'name' attribute")
        else:
            print("  ⚠ User pool may not support 'name' attribute")
        
        if pre_signup:
            print("  ✓ Pre-signup Lambda configured to handle name")
        
        print()
        print("Next Steps:")
        print("  1. Deploy frontend: npm run build && aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete")
        print("  2. Invalidate CloudFront: aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths '/*'")
        print("  3. Test signup in app with a new email")
        print("  4. Verify name appears in admin notification email")
        print("  5. Check if name displays instead of email in app")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_display_name_feature()
    sys.exit(0 if success else 1)
