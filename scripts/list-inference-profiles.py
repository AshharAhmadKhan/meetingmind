#!/usr/bin/env python3
"""List available inference profiles for Nova models"""
import boto3
import json

REGION = 'ap-south-1'

bedrock = boto3.client('bedrock', region_name=REGION)

print("="*60)
print("LISTING INFERENCE PROFILES")
print("="*60)
print(f"Region: {REGION}\n")

try:
    response = bedrock.list_inference_profiles()
    
    if 'inferenceProfileSummaries' in response:
        profiles = response['inferenceProfileSummaries']
        print(f"Found {len(profiles)} inference profiles:\n")
        
        for profile in profiles:
            print(f"Profile ID: {profile.get('inferenceProfileId', 'N/A')}")
            print(f"  Name: {profile.get('inferenceProfileName', 'N/A')}")
            print(f"  Type: {profile.get('type', 'N/A')}")
            print(f"  Status: {profile.get('status', 'N/A')}")
            if 'models' in profile:
                print(f"  Models: {profile['models']}")
            print()
        
        # Filter for Nova profiles
        nova_profiles = [p for p in profiles if 'nova' in p.get('inferenceProfileId', '').lower()]
        if nova_profiles:
            print("\n" + "="*60)
            print("NOVA INFERENCE PROFILES")
            print("="*60)
            for profile in nova_profiles:
                print(f"\n✅ {profile.get('inferenceProfileId')}")
                print(f"   Name: {profile.get('inferenceProfileName')}")
                print(f"   Type: {profile.get('type')}")
                print(f"   Status: {profile.get('status')}")
        else:
            print("\n❌ No Nova inference profiles found")
            print("\n💡 You may need to:")
            print("   1. Create an inference profile in the Bedrock console")
            print("   2. Or use a different region (us-east-1, us-west-2)")
    else:
        print("❌ No inference profiles found")
        print(f"\nFull response: {json.dumps(response, indent=2, default=str)}")
        
except Exception as e:
    print(f"❌ Error listing inference profiles: {e}")
    print("\n💡 This might mean:")
    print("   - Inference profiles not supported in this region")
    print("   - API permissions issue")
    print("   - Feature not available for your account")

print("\n" + "="*60)
