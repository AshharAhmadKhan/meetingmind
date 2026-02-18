#!/usr/bin/env python3
"""
Enable S3 Versioning for MeetingMind Buckets
Protects against accidental deletions
"""
import boto3

REGION = 'ap-south-1'

BUCKETS = [
    'meetingmind-audio-707411439284',
    'meetingmind-frontend-707411439284'
]

def enable_versioning(bucket_name):
    """Enable versioning for a bucket"""
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Verify versioning is enabled
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'Disabled')
        
        if status == 'Enabled':
            print(f"✅ {bucket_name}: Versioning ENABLED")
            return True
        else:
            print(f"⚠️  {bucket_name}: Versioning status = {status}")
            return False
            
    except Exception as e:
        print(f"❌ {bucket_name}: Error - {str(e)}")
        return False

def check_versioning_status():
    """Check current versioning status"""
    s3 = boto3.client('s3', region_name=REGION)
    
    print("\nCurrent Versioning Status:")
    print("-" * 60)
    
    for bucket in BUCKETS:
        try:
            response = s3.get_bucket_versioning(Bucket=bucket)
            status = response.get('Status', 'Disabled')
            
            icon = "✅" if status == 'Enabled' else "❌"
            print(f"{icon} {bucket}: {status}")
            
        except Exception as e:
            print(f"❌ {bucket}: Error - {str(e)}")

if __name__ == '__main__':
    print("="*60)
    print("ENABLE S3 VERSIONING")
    print("="*60)
    print(f"Region: {REGION}")
    print(f"Buckets: {len(BUCKETS)}")
    print("="*60)
    
    # Check current status
    check_versioning_status()
    
    # Enable versioning
    print("\nEnabling Versioning:")
    print("-" * 60)
    
    results = []
    for bucket in BUCKETS:
        result = enable_versioning(bucket)
        results.append(result)
    
    # Final status
    print("\n" + "="*60)
    if all(results):
        print("✅ SUCCESS: All buckets have versioning enabled")
        print("\n💡 Benefits:")
        print("   - Protection against accidental deletions")
        print("   - Ability to restore previous versions")
        print("   - Compliance with backup requirements")
    else:
        print("⚠️  PARTIAL: Some buckets failed to enable versioning")
    print("="*60)
