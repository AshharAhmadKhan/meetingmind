#!/usr/bin/env python3
"""
Add Transcribe Permissions to IAM User
Creates an inline policy for the meetingmind-dev user
"""
import boto3
import json
from botocore.exceptions import ClientError

IAM_USER = 'meetingmind-dev'
POLICY_NAME = 'MeetingMindTranscribeAccess'

TRANSCRIBE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:ListTranscriptionJobs",
                "transcribe:DeleteTranscriptionJob"
            ],
            "Resource": "*"
        }
    ]
}

def add_transcribe_permissions():
    """Add Transcribe permissions to IAM user"""
    print(f"\n🔐 Adding Transcribe Permissions to {IAM_USER}...")
    print("=" * 60)
    
    try:
        iam = boto3.client('iam')
        
        # Put user policy
        iam.put_user_policy(
            UserName=IAM_USER,
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(TRANSCRIBE_POLICY)
        )
        
        print(f"✅ Successfully added policy: {POLICY_NAME}")
        print(f"   User: {IAM_USER}")
        print("\n   Permissions granted:")
        for action in TRANSCRIBE_POLICY['Statement'][0]['Action']:
            print(f"     - {action}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'AccessDenied':
            print("❌ Access Denied")
            print("\n   Your current IAM user doesn't have permission to")
            print("   modify IAM policies.")
            print("\n   Solutions:")
            print("   1. Log in as root user or admin")
            print("   2. Run this script with admin credentials")
            print("   3. Manually add policy in AWS Console:")
            print(f"      → IAM → Users → {IAM_USER} → Add permissions")
            print("      → Attach policy: AmazonTranscribeFullAccess")
        elif error_code == 'NoSuchEntity':
            print(f"❌ User '{IAM_USER}' not found")
            print("\n   Check if the user name is correct")
        else:
            print(f"❌ Error: {error_code}")
            print(f"   Message: {e.response['Error']['Message']}")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def verify_permissions():
    """Verify the permissions were added"""
    print("\n✓ Verifying Permissions...")
    print("=" * 60)
    
    try:
        iam = boto3.client('iam')
        
        # Get user policy
        response = iam.get_user_policy(
            UserName=IAM_USER,
            PolicyName=POLICY_NAME
        )
        
        print(f"✅ Policy '{POLICY_NAME}' is attached")
        print("\n   To test Transcribe access, run:")
        print("   python scripts/test-aws-services.py")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"⚠️  Policy not found (may not have been created)")
        else:
            print(f"⚠️  Cannot verify: {e.response['Error']['Code']}")
        return False

def show_manual_instructions():
    """Show manual instructions for adding permissions"""
    print("\n📋 Manual Instructions (if script fails)")
    print("=" * 60)
    print("\n1. Go to AWS Console: https://console.aws.amazon.com/iam/")
    print(f"2. Navigate to: Users → {IAM_USER}")
    print("3. Click 'Add permissions' → 'Attach policies directly'")
    print("4. Search for: AmazonTranscribeFullAccess")
    print("5. Check the box and click 'Next' → 'Add permissions'")
    print("\nOR create inline policy:")
    print("1. Click 'Add permissions' → 'Create inline policy'")
    print("2. Click 'JSON' tab")
    print("3. Paste this policy:")
    print("\n" + json.dumps(TRANSCRIBE_POLICY, indent=2))
    print(f"\n4. Name it: {POLICY_NAME}")
    print("5. Click 'Create policy'")

if __name__ == '__main__':
    print("=" * 60)
    print("Add Transcribe Permissions to IAM User")
    print("=" * 60)
    
    print(f"\nThis will add Transcribe permissions to: {IAM_USER}")
    print("Policy name: " + POLICY_NAME)
    
    confirm = input("\nContinue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = add_transcribe_permissions()
        
        if success:
            verify_permissions()
            print("\n" + "=" * 60)
            print("✅ COMPLETE - Transcribe permissions added!")
            print("=" * 60)
        else:
            show_manual_instructions()
    else:
        print("\n❌ Cancelled")
        show_manual_instructions()
