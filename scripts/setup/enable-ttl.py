#!/usr/bin/env python3
"""
Enable TTL (Time To Live) on MeetingMind DynamoDB tables
This allows demo meetings to auto-delete after 30 minutes
"""

import boto3
import sys

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'

def enable_ttl():
    """Enable TTL on the meetings table"""
    print("=" * 80)
    print("Enable DynamoDB TTL for Demo Meetings")
    print("=" * 80)
    
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        # Check current TTL status
        print(f"\n📊 Checking TTL status for table: {MEETINGS_TABLE}")
        response = dynamodb.describe_time_to_live(TableName=MEETINGS_TABLE)
        current_status = response['TimeToLiveDescription']['TimeToLiveStatus']
        
        print(f"Current TTL Status: {current_status}")
        
        if current_status == 'ENABLED':
            print("\n✅ TTL is already enabled!")
            print(f"   Attribute: {response['TimeToLiveDescription'].get('AttributeName', 'N/A')}")
            return
        
        # Enable TTL
        print(f"\n🔧 Enabling TTL on attribute 'ttl'...")
        dynamodb.update_time_to_live(
            TableName=MEETINGS_TABLE,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'ttl'
            }
        )
        
        print("\n✅ TTL enabled successfully!")
        print("\nHow it works:")
        print("  - Demo user meetings get a 'ttl' attribute (Unix timestamp)")
        print("  - DynamoDB automatically deletes items when ttl expires")
        print("  - Demo meetings expire 30 minutes after creation")
        print("  - Regular user meetings have no ttl (never expire)")
        
        print("\n⚠️  Note: TTL deletion can take up to 48 hours to process")
        print("   (but typically happens within minutes)")
        
    except Exception as e:
        print(f"\n❌ Error enabling TTL: {e}")
        sys.exit(1)

if __name__ == '__main__':
    enable_ttl()
