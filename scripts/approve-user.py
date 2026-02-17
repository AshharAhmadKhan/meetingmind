#!/usr/bin/env python3
"""
Script to approve a new MeetingMind user
Usage: python scripts/approve-user.py user@email.com
"""
import sys
import boto3

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'

cognito = boto3.client('cognito-idp', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

def approve_user(email):
    """Approve a user: verify email in SES, enable Cognito account, send welcome email"""
    
    print(f"\n🔄 Approving user: {email}\n")
    
    # Step 1: Verify email in SES
    print("1️⃣  Verifying email in SES...")
    try:
        ses.verify_email_identity(EmailAddress=email)
        print(f"   ✓ Verification email sent to {email}")
        print(f"   ⚠️  User must click the verification link in their email!")
    except Exception as e:
        print(f"   ⚠️  SES verification failed: {e}")
    
    # Step 2: Enable user in Cognito
    print("\n2️⃣  Enabling Cognito account...")
    try:
        # Find user by email
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{email}"'
        )
        
        if not response['Users']:
            print(f"   ❌ User not found: {email}")
            return False
        
        username = response['Users'][0]['Username']
        
        # Enable the user
        cognito.admin_enable_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        print(f"   ✓ User enabled: {username}")
    except Exception as e:
        print(f"   ❌ Failed to enable user: {e}")
        return False
    
    # Step 3: Send welcome email
    print("\n3️⃣  Sending welcome email...")
    try:
        lambda_client.invoke(
            FunctionName='meetingmind-send-welcome-email',
            InvocationType='Event',  # Async
            Payload=f'{{"email": "{email}"}}'
        )
        print(f"   ✓ Welcome email sent to {email}")
    except Exception as e:
        print(f"   ⚠️  Failed to send welcome email: {e}")
    
    print(f"\n✅ User approved successfully!")
    print(f"\n📧 Next steps:")
    print(f"   1. User must click SES verification link in their email")
    print(f"   2. User can then log in at https://dcfx593ywvy92.cloudfront.net")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/approve-user.py user@email.com")
        sys.exit(1)
    
    email = sys.argv[1]
    approve_user(email)
