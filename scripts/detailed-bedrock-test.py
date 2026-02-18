#!/usr/bin/env python3
"""
Detailed Bedrock Access Test
Tests different Bedrock models and provides specific diagnostics
"""
import boto3
import json
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

def test_bedrock_model_access():
    """Check which Bedrock models have access enabled"""
    print("\n🔐 Checking Bedrock Model Access...")
    print("=" * 60)
    
    try:
        bedrock = boto3.client('bedrock', region_name=REGION)
        
        # Get list of models
        response = bedrock.list_foundation_models()
        models = response.get('modelSummaries', [])
        
        # Check access for key models
        key_models = {
            'Claude 3 Haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
            'Claude 3.5 Sonnet': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
            'Titan Embeddings v2': 'amazon.titan-embed-text-v2:0',
            'Nova Lite': 'amazon.nova-lite-v1:0',
        }
        
        print("\nModel Access Status:")
        for name, model_id in key_models.items():
            # Find model in list
            model_info = next((m for m in models if m['modelId'] == model_id), None)
            if model_info:
                status = model_info.get('modelLifecycle', {}).get('status', 'UNKNOWN')
                print(f"  {name}: {status}")
            else:
                print(f"  {name}: NOT FOUND")
        
        # Try to get model access
        print("\n📋 Requesting Model Access Status...")
        try:
            # This API might not be available
            access_response = bedrock.get_model_invocation_logging_configuration()
            print("  Logging Config: Available")
        except Exception as e:
            print(f"  Cannot check logging config: {e.response['Error']['Code']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_bedrock_inference_profiles():
    """Check inference profiles"""
    print("\n🎯 Checking Bedrock Inference Profiles...")
    print("=" * 60)
    
    try:
        bedrock = boto3.client('bedrock', region_name=REGION)
        
        # List inference profiles
        response = bedrock.list_inference_profiles()
        profiles = response.get('inferenceProfileSummaries', [])
        
        if profiles:
            print(f"Found {len(profiles)} inference profiles:")
            for profile in profiles[:5]:  # Show first 5
                print(f"  - {profile.get('inferenceProfileName', 'Unknown')}")
        else:
            print("No inference profiles found")
            print("This might indicate model access is not enabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_specific_model_invoke(model_id, model_name):
    """Test invoking a specific model"""
    print(f"\n🧪 Testing {model_name}...")
    print("=" * 60)
    
    try:
        runtime = boto3.client('bedrock-runtime', region_name=REGION)
        
        # Prepare request based on model type
        if 'claude' in model_id:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })
        elif 'titan-embed' in model_id:
            body = json.dumps({"inputText": "test"})
        elif 'nova' in model_id:
            body = json.dumps({
                "messages": [{"role": "user", "content": "Hi"}],
                "inferenceConfig": {"max_new_tokens": 10}
            })
        else:
            print(f"⚠️  Unknown model type")
            return False
        
        response = runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        
        print(f"✅ {model_name} is ACCESSIBLE")
        print(f"   Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        print(f"❌ {model_name} is BLOCKED")
        print(f"   Error: {error_code}")
        
        # Provide specific guidance based on error
        if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
            print(f"   Issue: Payment card not valid or not propagated yet")
            print(f"   Action: Wait 2-5 minutes and try again")
        elif 'AccessDeniedException' in error_code:
            print(f"   Issue: Model access not enabled")
            print(f"   Action: Go to Bedrock Console → Model Access → Enable models")
        elif 'ValidationException' in error_code:
            print(f"   Issue: Invalid model ID or configuration")
            print(f"   Action: Check model ID is correct")
        else:
            print(f"   Message: {error_msg}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_payment_propagation():
    """Check if payment method has propagated"""
    print("\n⏱️  Payment Propagation Check...")
    print("=" * 60)
    print("AWS typically takes 2-5 minutes to propagate payment changes")
    print("\nIf you just added a payment card:")
    print("  1. Wait 5 minutes")
    print("  2. Run this test again")
    print("  3. If still failing, check AWS Console → Bedrock → Model Access")
    print("\nIf payment was added >5 minutes ago:")
    print("  1. Verify card is valid in AWS Console → Account → Payment Methods")
    print("  2. Enable model access in AWS Console → Bedrock → Model Access")
    print("  3. Request access to: Claude, Titan, Nova models")

if __name__ == '__main__':
    print("=" * 60)
    print("Detailed Bedrock Access Diagnostic")
    print("=" * 60)
    
    test_bedrock_model_access()
    test_bedrock_inference_profiles()
    
    # Test specific models
    models_to_test = [
        ('anthropic.claude-3-haiku-20240307-v1:0', 'Claude 3 Haiku'),
        ('amazon.titan-embed-text-v2:0', 'Titan Embeddings v2'),
        ('amazon.nova-lite-v1:0', 'Nova Lite'),
    ]
    
    results = {}
    for model_id, model_name in models_to_test:
        results[model_name] = test_specific_model_invoke(model_id, model_name)
    
    check_payment_propagation()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for model_name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {model_name}: {'PASS' if status else 'FAIL'}")
    
    if all(results.values()):
        print("\n🎉 All models accessible - Ready for production!")
    else:
        print("\n⚠️  Some models still blocked - See guidance above")
    
    print("=" * 60)
