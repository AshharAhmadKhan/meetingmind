#!/usr/bin/env python3
"""
Approve a Cognito user account by confirming their email.
This bypasses the email verification requirement.
"""

import boto3
import sys

# Configuration
USER_POOL_ID = 'ap-south-1_YourPoolId'  # Update this with your actual User Pool ID
REGION = 'ap-south-1'

def approve_user(email):
    """Approve a user by admin-confirming their account"""
    
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    try:
        # Admin confirm sign up (bypasses email verification)
        response = cognito.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=email
        )
        
        print(f"✅ Successfully approved user: {email}")
        print(f"Response: {response}")
        
        # Also set email as verified
        cognito.admin_update_user_attributes(
            UserPoolId=USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
        )
        
        print(f"✅ Email verified for: {email}")
        
        return True
        
    except cognito.exceptions.UserNotFoundException:
        print(f"❌ User not found: {email}")
        print("Make sure the user has completed signup first.")
        return False
        
    except cognito.exceptions.NotAuthorizedException:
        print(f"❌ Not authorized. Check your AWS credentials.")
        return False
        
    except Exception as e:
        print(f"❌ Error approving user: {str(e)}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python approve-user.py <email>")
        print("Example: python approve-user.py alishba@jamiahamdard.org.in")
        sys.exit(1)
    
    email = sys.argv[1]
    approve_user(email)
