#!/usr/bin/env python3
"""Check demo user in Cognito"""
import boto3

cognito = boto3.client('cognito-idp', region_name='ap-south-1')
user_pool_id = 'ap-south-1_mkFJawjMp'

try:
    response = cognito.list_users(
        UserPoolId=user_pool_id,
        Filter='email = "demo@meetingmind.com"'
    )
    
    if response['Users']:
        user = response['Users'][0]
        print(f"Username: {user['Username']}")
        print(f"Status: {user['UserStatus']}")
        print(f"Enabled: {user['Enabled']}")
        print("\nAttributes:")
        for attr in user['Attributes']:
            print(f"  {attr['Name']}: {attr['Value']}")
    else:
        print("Demo user not found in Cognito")
except Exception as e:
    print(f"Error: {e}")
