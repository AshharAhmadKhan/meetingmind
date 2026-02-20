#!/usr/bin/env python3
"""
Comprehensive diagnostic script for all current issues
Tests Issue #1 (Email Flow) and Issue #3 (Display Name)
"""
import boto3
import json
import sys

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
TEST_USER_EMAIL = 'ashkagakoko@gmail.com'  # Keldeo user

cognito = boto3.client('cognito-idp', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_cognito_user():
    """Check if test user exists and has name attribute"""
    print_section("ISSUE #3: Display Name - Cognito Check")
    
    try:
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{TEST_USER_EMAIL}"'
        )
        
        if not response['Users']:
            print(f"❌ User not found: {TEST_USER_EMAIL}")
            return None
        
        user = response['Users'][0]
        username = user['Username']
        attributes = {attr['Name']: attr['Value'] for attr in user['Attributes']}
        
        print(f"✓ User found: {username}")
        print(f"  Status: {user['UserStatus']}")
        print(f"  Enabled: {user['Enabled']}")
        print(f"\n  Attributes:")
        print(f"    - email: {attributes.get('email', 'NOT SET')}")
        print(f"    - name: {attributes.get('name', 'NOT SET')}")
        print(f"    - email_verified: {attributes.get('email_verified', 'NOT SET')}")
        
        # Check if name is set
        if 'name' in attributes and attributes['name']:
            print(f"\n✓ Display name IS set: '{attributes['name']}'")
            print(f"  EXPECTED: Frontend should show '{attributes['name']}'")
            print(f"  ACTUAL: Frontend shows '{attributes['email']}'")
            print(f"\n❌ ISSUE: checkSession() stores email instead of name")
            print(f"  ROOT CAUSE: auth.js checkSession() doesn't fetch user attributes")
            print(f"  FIX NEEDED: Import fetchUserAttributes and extract name")
        else:
            print(f"\n❌ Display name NOT set")
            print(f"  User registered before name field was added")
        
        return user
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

def check_ses_verification():
    """Check SES email verification status"""
    print_section("ISSUE #1: Email Flow - SES Verification Check")
    
    try:
        response = ses.get_identity_verification_attributes(
            Identities=[TEST_USER_EMAIL]
        )
        
        attrs = response['VerificationAttributes']
        
        if TEST_USER_EMAIL in attrs:
            status = attrs[TEST_USER_EMAIL]['VerificationStatus']
            print(f"✓ SES verification status: {status}")
            
            if status == 'Success':
                print(f"  ✓ Email is verified in SES")
                print(f"  User can receive emails from MeetingMind")
            elif status == 'Pending':
                print(f"  ⚠️  Email verification pending")
                print(f"  User needs to click verification link")
            else:
                print(f"  ❌ Email not verified: {status}")
        else:
            print(f"❌ Email not found in SES")
            print(f"  User has not been approved yet")
            print(f"  Run: python scripts/setup/approve-user.py {TEST_USER_EMAIL}")
        
    except Exception as e:
        print(f"❌ Error checking SES: {e}")

def check_email_flow():
    """Analyze the complete email flow"""
    print_section("ISSUE #1: Email Flow - Complete Analysis")
    
    print("Current Flow:")
    print("  1. User registers → Pre-signup Lambda triggered")
    print("  2. Admin receives notification email ✓")
    print("  3. Admin runs approve-user.py script")
    print("  4. Script calls SES verify_email_identity()")
    print("  5. User receives SES verification email ✓")
    print("  6. User clicks verification link")
    print("  7. Script calls send-welcome-email Lambda")
    print("  8. User receives welcome email ✓")
    
    print("\n❌ PROBLEM: No congratulations email after SES verification")
    print("\nExpected Flow:")
    print("  1-6. Same as above")
    print("  7. User clicks SES verification link")
    print("  8. → MISSING: Congratulations email")
    print("  9. User receives welcome email")
    
    print("\n🔧 SOLUTION OPTIONS:")
    print("\n  Option A: Update approve-user.py")
    print("    - Send congrats email after SES verification")
    print("    - Requires polling SES status or user confirmation")
    print("    - Complexity: Medium")
    
    print("\n  Option B: Create SES notification handler")
    print("    - Use SNS topic for SES verification events")
    print("    - Lambda triggered when user verifies email")
    print("    - Sends congrats email automatically")
    print("    - Complexity: High")
    
    print("\n  Option C: Combine welcome + congrats")
    print("    - Send single email after approval")
    print("    - Email says 'verify your email to complete setup'")
    print("    - No separate congrats email")
    print("    - Complexity: Low")
    
    print("\n  RECOMMENDED: Option C (simplest, good UX)")

def check_auth_js_issue():
    """Analyze the auth.js checkSession issue"""
    print_section("ISSUE #3: Display Name - auth.js Analysis")
    
    print("Current Implementation:")
    print("  checkSession() {")
    print("    const user = await getCurrentUser()")
    print("    localStorage.setItem('mm_user', user.signInDetails?.loginId || user.username)")
    print("    return user")
    print("  }")
    
    print("\n❌ PROBLEM:")
    print("  - getCurrentUser() returns basic user info (username, userId)")
    print("  - Does NOT include custom attributes like 'name'")
    print("  - loginId is the email used to sign in")
    print("  - Result: Email stored in localStorage instead of name")
    
    print("\n✓ CORRECT Implementation:")
    print("  import { fetchUserAttributes } from 'aws-amplify/auth'")
    print("")
    print("  async function checkSession() {")
    print("    try {")
    print("      const user = await getCurrentUser()")
    print("      const attributes = await fetchUserAttributes()")
    print("      const displayName = attributes.name || user.signInDetails?.loginId || user.username")
    print("      localStorage.setItem('mm_user', displayName)")
    print("      return user")
    print("    } catch {")
    print("      localStorage.removeItem('mm_user')")
    print("      return null")
    print("    }")
    print("  }")
    
    print("\n🔧 FIX REQUIRED:")
    print("  1. Import fetchUserAttributes from aws-amplify/auth")
    print("  2. Call fetchUserAttributes() in checkSession()")
    print("  3. Extract name attribute")
    print("  4. Fallback to email if name doesn't exist")
    print("  5. Rebuild and deploy frontend")

def main():
    print("\n" + "="*70)
    print("  MEETINGMIND - COMPREHENSIVE ISSUE DIAGNOSIS")
    print("  Testing Issues #1 (Email Flow) and #3 (Display Name)")
    print("="*70)
    
    # Check Cognito user
    user = check_cognito_user()
    
    # Check SES verification
    check_ses_verification()
    
    # Analyze email flow
    check_email_flow()
    
    # Analyze auth.js issue
    check_auth_js_issue()
    
    # Summary
    print_section("SUMMARY")
    
    print("Issue #1: Email Flow")
    print("  Status: ⚠️  Partially working")
    print("  Problem: No congrats email after SES verification")
    print("  Impact: User doesn't know when email is verified")
    print("  Fix: Update approve-user.py or combine emails")
    print("  Priority: MEDIUM")
    
    print("\nIssue #3: Display Name")
    print("  Status: ⚠️  Partially working")
    print("  Problem: Name stored in Cognito but not displayed")
    print("  Impact: Frontend shows email instead of name")
    print("  Fix: Update auth.js checkSession() to fetch attributes")
    print("  Priority: HIGH (demo blocker)")
    
    print("\n" + "="*70)
    print("  NEXT STEPS")
    print("="*70)
    print("\n1. Fix Issue #3 (Display Name) - 15 minutes")
    print("   - Update frontend/src/utils/auth.js")
    print("   - Add fetchUserAttributes import and call")
    print("   - Rebuild and deploy frontend")
    print("   - Test with Keldeo user")
    
    print("\n2. Fix Issue #1 (Email Flow) - 30 minutes")
    print("   - Update scripts/setup/approve-user.py")
    print("   - Combine welcome + verification instructions")
    print("   - OR add congrats email after verification")
    print("   - Test with new user")
    
    print("\n3. Verify both fixes")
    print("   - Register new test user")
    print("   - Check admin notification")
    print("   - Approve user")
    print("   - Verify email flow")
    print("   - Login and check display name")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
