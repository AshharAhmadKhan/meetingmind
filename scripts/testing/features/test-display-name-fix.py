#!/usr/bin/env python3
"""
Test that display name fix is working
"""
import boto3

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
KELDEO_EMAIL = 'ashkagakoko@gmail.com'

cognito = boto3.client('cognito-idp', region_name=REGION)

def test_display_name():
    print("\n" + "="*70)
    print("  TEST: Display Name Fix")
    print("="*70 + "\n")
    
    # Get Keldeo user
    response = cognito.list_users(
        UserPoolId=USER_POOL_ID,
        Filter=f'email = "{KELDEO_EMAIL}"'
    )
    
    if not response['Users']:
        print(f"❌ User not found: {KELDEO_EMAIL}")
        return False
    
    user = response['Users'][0]
    attributes = {attr['Name']: attr['Value'] for attr in user['Attributes']}
    
    print("✓ User found:")
    print(f"  Email: {attributes.get('email')}")
    print(f"  Name: {attributes.get('name', 'NOT SET')}")
    
    if 'name' in attributes and attributes['name']:
        print(f"\n✓ Display name is set: '{attributes['name']}'")
        print(f"\n📋 MANUAL TEST REQUIRED:")
        print(f"  1. Open https://dcfx593ywvy92.cloudfront.net")
        print(f"  2. Login as Keldeo:")
        print(f"     Email: {KELDEO_EMAIL}")
        print(f"     Password: (your password)")
        print(f"  3. Check top navigation bar")
        print(f"  4. Verify it shows: '{attributes['name']}'")
        print(f"  5. NOT: '{attributes['email']}'")
        print(f"\n✓ If name shows correctly, fix is working!")
        print(f"❌ If email still shows, clear browser cache and try again")
        return True
    else:
        print(f"\n❌ Display name NOT set")
        return False

if __name__ == '__main__':
    test_display_name()
