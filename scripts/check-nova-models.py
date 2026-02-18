#!/usr/bin/env python3
"""Check available Nova models and inference profiles in ap-south-1"""
import boto3
import json

REGION = 'ap-south-1'

bedrock = boto3.client('bedrock', region_name=REGION)

print("="*60)
print("CHECKING AVAILABLE NOVA MODELS")
print("="*60)
print(f"Region: {REGION}\n")

# List all foundation models
try:
    response = bedrock.list_foundation_models()
    nova_models = [m for m in response['modelSummaries'] if 'nova' in m['modelId'].lower()]
    
    if nova_models:
        print(f"Found {len(nova_models)} Nova models:\n")
        for model in nova_models:
            print(f"Model ID: {model['modelId']}")
            print(f"  Name: {model.get('modelName', 'N/A')}")
            print(f"  Provider: {model.get('providerName', 'N/A')}")
            print(f"  Input Modalities: {model.get('inputModalities', [])}")
            print(f"  Output Modalities: {model.get('outputModalities', [])}")
            print()
    else:
        print("❌ No Nova models found in ap-south-1")
        print("\nTrying to list ALL models to see what's available:")
        all_models = response['modelSummaries']
        print(f"\nTotal models available: {len(all_models)}")
        print("\nAmazon models:")
        for model in all_models:
            if model['providerName'] == 'Amazon':
                print(f"  - {model['modelId']}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Try to list inference profiles
print("\n" + "="*60)
print("CHECKING INFERENCE PROFILES")
print("="*60)

try:
    # This API might not exist or might require different permissions
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)
    
    # Try to invoke with cross-region profile
    test_profiles = [
        'us.amazon.nova-lite-v1:0',
        'us.amazon.nova-micro-v1:0',
        'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0',
        'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0',
    ]
    
    for profile in test_profiles:
        print(f"\nTesting: {profile}")
        try:
            body = json.dumps({
                'messages': [{'role': 'user', 'content': [{'text': 'Hi'}]}],
                'inferenceConfig': {'maxTokens': 10, 'temperature': 0.1}
            })
            response = bedrock_runtime.invoke_model(
                modelId=profile,
                body=body
            )
            print(f"  ✅ WORKS!")
        except Exception as e:
            error_msg = str(e)
            if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
                print(f"  ⚠️  Payment validation pending")
            elif 'AccessDeniedException' in error_msg:
                print(f"  ❌ Access denied")
            elif 'ValidationException' in error_msg:
                print(f"  ❌ Validation error: {error_msg[:100]}")
            else:
                print(f"  ❌ Error: {error_msg[:100]}")
                
except Exception as e:
    print(f"❌ Error checking inference profiles: {e}")

print("\n" + "="*60)
