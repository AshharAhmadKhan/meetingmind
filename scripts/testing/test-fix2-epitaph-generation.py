#!/usr/bin/env python3
"""
Test script for Fix #2: Epitaph Pre-Generation
Manually invokes the generate-epitaphs Lambda and verifies results
"""

import boto3
import json
import sys
import time

def test_epitaph_generation():
    """Test the epitaph generation Lambda"""
    print("=" * 60)
    print("FIX #2: EPITAPH PRE-GENERATION TEST")
    print("=" * 60)
    print()
    
    lambda_client = boto3.client('lambda', region_name='ap-south-1')
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Step 1: Invoke Lambda
    print("Step 1: Invoking generate-epitaphs Lambda...")
    try:
        response = lambda_client.invoke(
            FunctionName='meetingmind-generate-epitaphs',
            InvocationType='RequestResponse',
            LogType='Tail'
        )
        
        payload = json.loads(response['Payload'].read())
        print(f"✓ Lambda invoked successfully")
        print(f"  Status Code: {response['StatusCode']}")
        print()
        
        if 'body' in payload:
            result = json.loads(payload['body'])
            print("Results:")
            print(f"  Total meetings scanned: {result.get('totalMeetings', 0)}")
            print(f"  Actions processed: {result.get('actionsProcessed', 0)}")
            print(f"  Success count: {result.get('successCount', 0)}")
            print(f"  Failure count: {result.get('failureCount', 0)}")
            print()
            
            if result.get('actionsProcessed', 0) == 0:
                print("ℹ️  No epitaphs needed generation (all up to date)")
                return True
                
        else:
            print("⚠️  No body in response")
            print(f"  Full payload: {payload}")
            
    except Exception as e:
        print(f"✗ Lambda invocation failed: {e}")
        return False
    
    # Step 2: Verify DynamoDB updates
    print("Step 2: Verifying DynamoDB updates...")
    try:
        table = dynamodb.Table('meetingmind-meetings')
        
        # Scan for meetings with graveyard items
        response = table.scan(
            Limit=10  # Check first 10 meetings
        )
        
        epitaph_count = 0
        graveyard_count = 0
        
        for meeting in response.get('Items', []):
            action_items = meeting.get('actionItems', [])
            
            for action in action_items:
                if action.get('completed'):
                    continue
                
                # Check if it's a graveyard item (>30 days old)
                created_at = action.get('createdAt')
                if created_at:
                    from datetime import datetime, timezone
                    try:
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_old = (datetime.now(timezone.utc) - created_dt).days
                        
                        if days_old > 30:
                            graveyard_count += 1
                            if action.get('epitaph'):
                                epitaph_count += 1
                                print(f"✓ Found epitaph: {action['epitaph'][:60]}...")
                                if action.get('epitaphGeneratedAt'):
                                    print(f"  Generated: {action['epitaphGeneratedAt']}")
                    except:
                        pass
        
        print()
        print(f"Graveyard items found: {graveyard_count}")
        print(f"Epitaphs found: {epitaph_count}")
        
        if graveyard_count > 0 and epitaph_count > 0:
            print(f"✓ {epitaph_count}/{graveyard_count} graveyard items have epitaphs")
            return True
        elif graveyard_count == 0:
            print("ℹ️  No graveyard items found (no actions >30 days old)")
            return True
        else:
            print(f"⚠️  Some graveyard items missing epitaphs")
            return False
            
    except Exception as e:
        print(f"✗ DynamoDB verification failed: {e}")
        return False

def main():
    print()
    success = test_epitaph_generation()
    print()
    print("=" * 60)
    if success:
        print("✅ FIX #2 TEST PASSED")
        print()
        print("Next steps:")
        print("1. Check CloudWatch logs for detailed output")
        print("2. Visit /graveyard page - should load instantly")
        print("3. Verify epitaphs display correctly")
        return 0
    else:
        print("❌ FIX #2 TEST FAILED")
        print()
        print("Check CloudWatch logs for errors:")
        print("  aws logs tail /aws/lambda/meetingmind-generate-epitaphs --region ap-south-1 --follow")
        return 1

if __name__ == '__main__':
    sys.exit(main())
