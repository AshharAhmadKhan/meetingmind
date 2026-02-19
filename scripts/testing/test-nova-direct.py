#!/usr/bin/env python3
"""Direct test of Nova models with detailed error reporting"""
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

bedrock_config = Config(retries={'max_attempts': 0, 'mode': 'standard'})
bedrock = boto3.client('bedrock-runtime', region_name=REGION, config=bedrock_config)

print("="*60)
print("DIRECT NOVA MODEL TEST")
print("="*60)
print(f"Region: {REGION}\n")

# Test Nova Lite
print("Testing amazon.nova-lite-v1:0...")
try:
    body = json.dumps({
        'messages': [{'role': 'user', 'content': [{'text': 'Say hello'}]}],
        'inferenceConfig': {'maxTokens': 20, 'temperature': 0.1}
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=body
    )
    
    result = json.loads(response['body'].read())
    print(f"✅ SUCCESS!")
    print(f"Response: {json.dumps(result, indent=2)}")
    
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_msg = e.response['Error']['Message']
    print(f"❌ {error_code}")
    print(f"Message: {error_msg}")
    
    if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
        print("\n💡 Solution: Credit card validation pending (24-48 hours)")
    elif 'AccessDeniedException' in error_code:
        print("\n💡 Solution: Enable model access in Bedrock console")
        print("   1. Go to AWS Console > Bedrock > Model access")
        print("   2. Click 'Manage model access'")
        print("   3. Enable 'Amazon Nova Lite'")
        print("   4. Save changes")
    elif 'ValidationException' in error_code:
        print("\n💡 Possible causes:")
        print("   - Model not available in this region")
        print("   - Incorrect request format")
        print("   - Model access not enabled")
        
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "="*60)

# Test Nova Micro
print("\nTesting amazon.nova-micro-v1:0...")
try:
    body = json.dumps({
        'messages': [{'role': 'user', 'content': [{'text': 'Say hello'}]}],
        'inferenceConfig': {'maxTokens': 20, 'temperature': 0.1}
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.nova-micro-v1:0',
        body=body
    )
    
    result = json.loads(response['body'].read())
    print(f"✅ SUCCESS!")
    print(f"Response: {json.dumps(result, indent=2)}")
    
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_msg = e.response['Error']['Message']
    print(f"❌ {error_code}")
    print(f"Message: {error_msg}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "="*60)
