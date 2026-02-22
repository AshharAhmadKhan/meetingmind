#!/usr/bin/env python3
"""
Test Rate Limiting Implementation
Tests API behavior before and after rate limiting deployment
"""

import requests
import time
import json
from datetime import datetime

# Configuration
API_BASE = "https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod"
TOKEN = None  # Will be set from auth

def get_auth_token():
    """Get authentication token (you'll need to login first)"""
    # For now, return None - user needs to provide token
    print("⚠️  You need to provide an auth token")
    print("   1. Login to https://dcfx593ywvy92.cloudfront.net")
    print("   2. Open DevTools → Application → Local Storage")
    print("   3. Copy the token value")
    return None

def test_single_request():
    """Test a single API request works"""
    print("\n" + "="*60)
    print("TEST 1: Single Request (Should Always Work)")
    print("="*60)
    
    headers = {}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    
    try:
        response = requests.get(f"{API_BASE}/meetings", headers=headers, timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Meetings returned: {len(data.get('meetings', []))}")
            return True
        elif response.status_code == 401:
            print("   ⚠️  Unauthorized - need valid token")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_burst_requests(count=10):
    """Test burst of requests (should work with generous limits)"""
    print("\n" + "="*60)
    print(f"TEST 2: Burst of {count} Requests (Should Work)")
    print("="*60)
    
    headers = {}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    
    success_count = 0
    throttled_count = 0
    error_count = 0
    
    start_time = time.time()
    
    for i in range(count):
        try:
            response = requests.get(f"{API_BASE}/meetings", headers=headers, timeout=10)
            
            if response.status_code == 200:
                success_count += 1
                print(f"  Request {i+1}: ✅ 200 OK")
            elif response.status_code == 429:
                throttled_count += 1
                print(f"  Request {i+1}: ⚠️  429 THROTTLED")
            else:
                error_count += 1
                print(f"  Request {i+1}: ❌ {response.status_code}")
                
        except Exception as e:
            error_count += 1
            print(f"  Request {i+1}: ❌ Error: {e}")
    
    elapsed = time.time() - start_time
    
    print(f"\n📊 Results:")
    print(f"   Success: {success_count}/{count}")
    print(f"   Throttled: {throttled_count}/{count}")
    print(f"   Errors: {error_count}/{count}")
    print(f"   Time: {elapsed:.2f}s ({count/elapsed:.1f} req/s)")
    
    return success_count, throttled_count, error_count

def test_sustained_load(duration_seconds=10, rate_per_second=5):
    """Test sustained load over time"""
    print("\n" + "="*60)
    print(f"TEST 3: Sustained Load ({rate_per_second} req/s for {duration_seconds}s)")
    print("="*60)
    
    headers = {}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    
    success_count = 0
    throttled_count = 0
    error_count = 0
    
    start_time = time.time()
    request_count = 0
    
    while time.time() - start_time < duration_seconds:
        try:
            response = requests.get(f"{API_BASE}/meetings", headers=headers, timeout=10)
            request_count += 1
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                throttled_count += 1
            else:
                error_count += 1
            
            # Sleep to maintain rate
            time.sleep(1.0 / rate_per_second)
            
        except Exception as e:
            error_count += 1
            time.sleep(1.0 / rate_per_second)
    
    elapsed = time.time() - start_time
    
    print(f"\n📊 Results:")
    print(f"   Total requests: {request_count}")
    print(f"   Success: {success_count}")
    print(f"   Throttled: {throttled_count}")
    print(f"   Errors: {error_count}")
    print(f"   Actual rate: {request_count/elapsed:.1f} req/s")
    
    return success_count, throttled_count, error_count

def main():
    print("="*60)
    print("MeetingMind API - Rate Limiting Test")
    print("="*60)
    print(f"API: {API_BASE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    global TOKEN
    TOKEN = get_auth_token()
    
    if not TOKEN:
        print("\n⚠️  Running tests without authentication")
        print("   Some tests may fail with 401 Unauthorized")
        print("   This is expected - we're testing the API is reachable")
    
    # Test 1: Single request
    single_works = test_single_request()
    
    if not single_works and TOKEN is None:
        print("\n⚠️  Skipping load tests - need authentication")
        print("   But API is reachable, which is good!")
        return
    
    # Test 2: Burst
    time.sleep(2)
    success, throttled, errors = test_burst_requests(10)
    
    # Test 3: Sustained
    time.sleep(2)
    success, throttled, errors = test_sustained_load(10, 5)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if throttled > 0:
        print("✅ Rate limiting is ACTIVE")
        print(f"   {throttled} requests were throttled (429 status)")
    else:
        print("⚠️  No throttling detected")
        print("   Either limits are very generous OR not yet deployed")
    
    print("\n💡 Expected behavior AFTER deployment:")
    print("   - Normal usage (10 req/burst): All succeed")
    print("   - Sustained load (50 req/s): All succeed")
    print("   - Spam (>100 burst): Some throttled (429)")
    print("   - Daily quota (>10,000): Throttled (429)")

if __name__ == "__main__":
    main()
