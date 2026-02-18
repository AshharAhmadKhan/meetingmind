#!/usr/bin/env python3
"""
Check Bedrock Model Access Configuration
"""
import boto3
import json
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

def check_model_access_grants():
    """Check which models have access granted"""
    print("\n🔓 Checking Model Access Grants...")
    print("=" * 60)
    
    try:
        bedrock = boto3.client('bedrock', region_name=REGION)
        
        # Try to list model access grants (if API exists)
        # This might not be available via API
        print("⚠️  Model access grants cannot be checked via API")
        print("   You must check manually in AWS Console")
        print("\n   Steps:")
        print("   1. Go to: https://console.aws.amazon.com/bedrock/")
        print("   2. Click 'Model access' in left sidebar")
        print("   3. Check if these models show 'Access granted':")
        print("      - Claude 3 Haiku")
        print("      - Claude 3.5 Sonnet")
        print("      - Titan Embeddings v2")
        print("\n   If they show 'Request access' or 'Pending':")
        print("   - Click 'Manage model access'")
        print("   - Enable the models")
        print("   - Click 'Save changes'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def check_payment_status():
    """Provide guidance on checking payment status"""
    print("\n💳 Payment Status Check")
    print("=" * 60)
    print("To verify your payment card status:")
    print("\n1. Go to: https://console.aws.amazon.com/billing/")
    print("2. Click 'Payment methods' in left sidebar")
    print("3. Verify:")
    print("   ✓ Card is listed")
    print("   ✓ Card shows as 'Active' or 'Valid'")
    print("   ✓ No error messages")
    print("\n4. Check your email for:")
    print("   - Card verification link (click to verify)")
    print("   - Payment confirmation")
    print("   - Any error notifications")
    print("\n5. If card shows as invalid:")
    print("   - Remove and re-add the card")
    print("   - Try a different card")
    print("   - Contact AWS Support")

def check_marketplace_subscription():
    """Check if Bedrock marketplace subscription is needed"""
    print("\n🛒 Marketplace Subscription Check")
    print("=" * 60)
    print("Some Bedrock models require AWS Marketplace subscription")
    print("\nTo check:")
    print("1. Go to: https://aws.amazon.com/marketplace/")
    print("2. Search for 'Anthropic Claude'")
    print("3. Check if you need to subscribe")
    print("\nNote: Most Bedrock models don't require separate subscription")
    print("      The payment card should be sufficient")

if __name__ == '__main__':
    print("=" * 60)
    print("Bedrock Model Access Configuration Check")
    print("=" * 60)
    
    check_model_access_grants()
    check_payment_status()
    check_marketplace_subscription()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Verify payment card is active in AWS Console")
    print("2. Check email for card verification link")
    print("3. Enable model access in Bedrock Console")
    print("4. Wait 5-10 minutes after making changes")
    print("5. Run: python scripts/test-aws-services.py")
    print("\nIf still failing after 15 minutes:")
    print("  - Contact AWS Support")
    print("  - Or use AWS Credits to bypass payment requirement")
    print("=" * 60)
