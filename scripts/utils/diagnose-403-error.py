#!/usr/bin/env python3
"""
Diagnose 403 Forbidden errors on meetings endpoint
"""

import boto3
import json
from datetime import datetime

def check_cognito_users():
    """Check Cognito user pool status"""
    print("=" * 60)
    print("🔍 DIAGNOSING 403 FORBIDDEN ERROR")
    print("=" * 60)
    
    cognito = boto3.client('cognito-idp', region_name='ap-south-1')
    user_pool_id = 'ap-south-1_mkFJawjMp'
    
    print(f"\n1️⃣ Checking Cognito User Pool: {user_pool_id}")
    
    try:
        # List users
        response = cognito.list_users(UserPoolId=user_pool_id)
        users = response.get('Users', [])
        
        print(f"   Total users: {len(users)}")
        
        for user in users:
            username = user['Username']
            status = user['UserStatus']
            enabled = user['Enabled']
            created = user['UserCreateDate']
            
            print(f"\n   User: {username}")
            print(f"   Status: {status}")
            print(f"   Enabled: {enabled}")
            print(f"   Created: {created}")
            
            # Check attributes
            attrs = {attr['Name']: attr['Value'] for attr in user.get('Attributes', [])}
            print(f"   Email: {attrs.get('email', 'N/A')}")
            print(f"   Email Verified: {attrs.get('email_verified', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n2️⃣ Checking DynamoDB Meetings")
    
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('meetingmind-meetings')
    
    try:
        response = table.scan(Limit=5)
        items = response.get('Items', [])
        
        print(f"   Total meetings (sample): {len(items)}")
        
        for item in items[:3]:
            print(f"\n   Meeting: {item.get('title', 'Unknown')}")
            print(f"   User ID: {item.get('userId', 'N/A')}")
            print(f"   Meeting ID: {item.get('meetingId', 'N/A')}")
            print(f"   Status: {item.get('status', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n3️⃣ Common 403 Causes:")
    print("   • Token expired (Cognito tokens expire after 1 hour)")
    print("   • User not confirmed in Cognito")
    print("   • API Gateway authorizer misconfigured")
    print("   • User trying to access another user's meetings")
    
    print(f"\n4️⃣ Quick Fixes:")
    print("   • Logout and login again (refresh token)")
    print("   • Clear browser cache/localStorage")
    print("   • Check browser console for auth errors")
    print("   • Verify Cognito user is CONFIRMED status")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_cognito_users()
