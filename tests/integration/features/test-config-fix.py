#!/usr/bin/env python3
"""
Test that config.js is deployed and accessible
"""

import requests
import sys

def test_config_deployed():
    """Test that config.js is accessible from CloudFront"""
    
    print("=" * 60)
    print("Testing Config File Deployment")
    print("=" * 60)
    print()
    
    cloudfront_url = "https://dcfx593ywvy92.cloudfront.net"
    config_url = f"{cloudfront_url}/config.js"
    
    print(f"✓ Checking: {config_url}")
    print()
    
    try:
        response = requests.get(config_url, timeout=10)
        
        if response.status_code == 200:
            print("✓ Config file is accessible")
            print()
            print("Content:")
            print("-" * 60)
            print(response.text)
            print("-" * 60)
            print()
            
            # Check if it contains expected values
            content = response.text
            checks = [
                ('apiUrl' in content, "API URL configured"),
                ('userPoolId' in content, "User Pool ID configured"),
                ('userPoolClientId' in content, "User Pool Client ID configured"),
                ('25g9jf8sqa.execute-api' in content, "Correct API Gateway URL"),
                ('ap-south-1_mkFJawjMp' in content, "Correct User Pool ID"),
            ]
            
            all_passed = True
            for passed, desc in checks:
                if passed:
                    print(f"  ✓ {desc}")
                else:
                    print(f"  ✗ {desc}")
                    all_passed = False
            
            print()
            if all_passed:
                print("✅ All checks passed - Config is correct!")
                print()
                print("Next: Refresh app and check if meetings load")
                return True
            else:
                print("⚠ Some checks failed")
                return False
        else:
            print(f"✗ Config file not accessible: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_config_deployed()
    sys.exit(0 if success else 1)
