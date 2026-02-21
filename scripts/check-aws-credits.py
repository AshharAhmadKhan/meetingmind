#!/usr/bin/env python3
"""
Check AWS credits and current month spending
Note: Requires billing permissions which may not be available to IAM users
"""

import boto3
import json
from datetime import datetime

def check_credits():
    """Check AWS credits balance"""
    print("=" * 60)
    print("💰 AWS CREDITS & BILLING CHECK")
    print("=" * 60)
    
    # Try to get billing info
    try:
        ce_client = boto3.client('ce', region_name='us-east-1')
        
        # Get current month costs
        today = datetime.now()
        start = f"{today.year}-{today.month:02d}-01"
        end = today.strftime('%Y-%m-%d')
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['BlendedCost', 'UnblendedCost']
        )
        
        print(f"\n📊 Current Month Spending (Feb 2026):")
        for result in response['ResultsByTime']:
            amount = float(result['Total']['BlendedCost']['Amount'])
            print(f"   Total: ${amount:.2f}")
        
    except Exception as e:
        print(f"\n❌ Cannot access billing data: {e}")
        print("\n💡 To check billing:")
        print("   1. Login to AWS Console as root user")
        print("   2. Go to: Billing Dashboard")
        print("   3. Check 'Credits' section")
        print("   4. Check 'Month-to-Date Spend'")
    
    # Check Free Tier usage
    print(f"\n📈 Free Tier Status:")
    print("   Transcribe: 3600/3600 seconds (100% used)")
    print("   ⚠️  Any new transcriptions will be charged")
    
    # Estimate costs
    print(f"\n💵 Cost Estimates:")
    print("   Transcribe: $0.024/minute = $1.44/hour")
    print("   Lambda: Free Tier (1M requests/month)")
    print("   DynamoDB: Free Tier (25GB storage)")
    print("   S3: Free Tier (5GB storage)")
    print("   CloudFront: Free Tier (1TB transfer)")
    
    print(f"\n🎯 Recommendations:")
    print("   1. Stop uploading test meetings")
    print("   2. Use existing meetings for testing")
    print("   3. Keep audio files short (<2 min) if testing")
    print("   4. Delete old test meetings")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_credits()
