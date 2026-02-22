#!/usr/bin/env python3
"""
Check CloudFront cache invalidation status
"""

import boto3
from datetime import datetime, timezone

cloudfront = boto3.client('cloudfront', region_name='us-east-1')  # CloudFront is always us-east-1

# CloudFront distribution ID
DISTRIBUTION_ID = 'E3CAAI97MXY83V'

print("=" * 100)
print("CLOUDFRONT CACHE STATUS")
print("=" * 100)
print()

try:
    # List recent invalidations
    response = cloudfront.list_invalidations(
        DistributionId=DISTRIBUTION_ID,
        MaxItems='10'
    )
    
    invalidations = response.get('InvalidationList', {}).get('Items', [])
    
    if not invalidations:
        print("No recent invalidations found")
        print()
        print("⚠️  Frontend may not have been deployed recently")
        print("⚠️  Or cache invalidation was not triggered")
    else:
        print(f"Found {len(invalidations)} recent invalidations:")
        print()
        
        for inv in invalidations:
            inv_id = inv['Id']
            status = inv['Status']
            create_time = inv['CreateTime']
            
            # Calculate time since creation
            now = datetime.now(timezone.utc)
            time_diff = now - create_time
            minutes_ago = int(time_diff.total_seconds() / 60)
            
            print(f"Invalidation ID: {inv_id}")
            print(f"Status: {status}")
            print(f"Created: {create_time} ({minutes_ago} minutes ago)")
            
            if status == 'Completed':
                print("✅ Cache cleared successfully")
            elif status == 'InProgress':
                print("⏳ Cache clearing in progress...")
            
            print()
        
        # Get the most recent invalidation details
        latest = invalidations[0]
        if latest['Status'] == 'Completed':
            print("=" * 100)
            print("CONCLUSION:")
            print("=" * 100)
            print("✅ Latest cache invalidation completed")
            print("✅ Users should see new frontend code")
            print()
            print("If users still see old code:")
            print("  1. Hard refresh browser (Ctrl+Shift+R)")
            print("  2. Clear browser cache")
            print("  3. Try incognito/private mode")
        else:
            print("=" * 100)
            print("CONCLUSION:")
            print("=" * 100)
            print("⏳ Cache invalidation still in progress")
            print("⏳ Wait 1-2 minutes and try again")

except Exception as e:
    print(f"Error checking CloudFront: {e}")
    print()
    print("This might mean:")
    print("  1. AWS credentials not configured")
    print("  2. No permission to access CloudFront")
    print("  3. Distribution ID is wrong")
