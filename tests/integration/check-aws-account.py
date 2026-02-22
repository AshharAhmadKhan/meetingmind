#!/usr/bin/env python3
"""
Check AWS Account Information
Shows account type, billing info, and service limits
"""
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

def get_account_info():
    """Get basic account information"""
    print("\n📋 Account Information")
    print("=" * 60)
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        print(f"User ID: {identity['UserId']}")
        
        # Try to get account alias
        try:
            iam = boto3.client('iam')
            aliases = iam.list_account_aliases()
            if aliases['AccountAliases']:
                print(f"Account Alias: {aliases['AccountAliases'][0]}")
        except:
            pass
            
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_billing_info():
    """Check billing and payment information"""
    print("\n💳 Billing Information")
    print("=" * 60)
    try:
        # Try to get billing info (requires billing permissions)
        ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
        
        # Get current month costs
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1)
        
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        
        if response['ResultsByTime']:
            cost = response['ResultsByTime'][0]['Total']['UnblendedCost']
            amount = float(cost['Amount'])
            print(f"Current Month Spend: ${amount:.2f} USD")
            print(f"Currency: {cost['Unit']}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("⚠️  No permission to view billing information")
            print("   (This is normal for IAM users)")
        else:
            print(f"❌ Error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_free_tier():
    """Check free tier usage"""
    print("\n🆓 Free Tier Status")
    print("=" * 60)
    try:
        # Try to get free tier info
        ce = boto3.client('ce', region_name='us-east-1')
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # This might not work without proper permissions
        print("⚠️  Free tier details require root account access")
        print("   Check AWS Console → Billing → Free Tier")
        
        return True
    except Exception as e:
        print(f"⚠️  Cannot check free tier programmatically")
        print("   Check AWS Console → Billing → Free Tier")
        return False

def check_service_quotas():
    """Check service quotas/limits"""
    print("\n📊 Service Quotas (Key Services)")
    print("=" * 60)
    try:
        quotas = boto3.client('service-quotas', region_name='ap-south-1')
        
        # Check Lambda quotas
        try:
            lambda_quota = quotas.get_service_quota(
                ServiceCode='lambda',
                QuotaCode='L-B99A9384'  # Concurrent executions
            )
            print(f"Lambda Concurrent Executions: {lambda_quota['Quota']['Value']:.0f}")
        except:
            print("Lambda: Cannot retrieve quota")
        
        # Check DynamoDB quotas
        try:
            dynamo_quota = quotas.get_service_quota(
                ServiceCode='dynamodb',
                QuotaCode='L-F98FE922'  # Account-level read capacity
            )
            print(f"DynamoDB Read Capacity: {dynamo_quota['Quota']['Value']:.0f}")
        except:
            print("DynamoDB: Cannot retrieve quota")
            
        return True
    except Exception as e:
        print(f"⚠️  Cannot check service quotas: {str(e)}")
        return False

def check_payment_methods():
    """Check if payment methods are configured"""
    print("\n💰 Payment Method Status")
    print("=" * 60)
    print("⚠️  Payment method details require root account access")
    print("   Check: AWS Console → Account → Payment Methods")
    print("\n   Based on Bedrock error, payment method is:")
    print("   ❌ INVALID or MISSING")
    print("\n   To fix:")
    print("   1. Go to AWS Console → Account → Payment Methods")
    print("   2. Add a valid credit/debit card")
    print("   3. Wait 2 minutes for propagation")
    print("   4. Re-run test-aws-services.py")

def check_support_plan():
    """Check AWS Support plan"""
    print("\n🎫 AWS Support Plan")
    print("=" * 60)
    try:
        support = boto3.client('support', region_name='us-east-1')
        # This requires support API access
        print("⚠️  Support plan details require specific permissions")
        print("   Most likely: Basic (Free) or Developer ($29/month)")
    except Exception as e:
        print("⚠️  Cannot check support plan programmatically")
        print("   Check: AWS Console → Support → Support Center")

def check_credits():
    """Check for AWS credits"""
    print("\n🎁 AWS Credits")
    print("=" * 60)
    print("⚠️  Credit information requires root account access")
    print("   Check: AWS Console → Billing → Credits")
    print("\n   You mentioned credit code: PC18KC9IDKOFDW8")
    print("   To redeem:")
    print("   1. Go to AWS Console → Billing → Credits")
    print("   2. Enter code: PC18KC9IDKOFDW8")
    print("   3. Click 'Redeem'")

if __name__ == '__main__':
    print("=" * 60)
    print("AWS Account Status Check")
    print("=" * 60)
    
    get_account_info()
    check_billing_info()
    check_free_tier()
    check_service_quotas()
    check_payment_methods()
    check_support_plan()
    check_credits()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("\n1. Add Payment Method (CRITICAL)")
    print("   → AWS Console → Account → Payment Methods")
    print("   → This will unlock Bedrock")
    print("\n2. Redeem Credit Code")
    print("   → AWS Console → Billing → Credits")
    print("   → Code: PC18KC9IDKOFDW8")
    print("\n3. Add IAM Permissions for Transcribe")
    print("   → AWS Console → IAM → Users → meetingmind-dev")
    print("   → Add policy: AmazonTranscribeFullAccess")
    print("\n4. Request Bedrock Model Access")
    print("   → AWS Console → Bedrock → Model Access")
    print("   → Request access to Claude and Titan models")
    print("=" * 60)
