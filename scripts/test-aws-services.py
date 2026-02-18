#!/usr/bin/env python3
"""
Test AWS Services Availability
Checks if Transcribe and Bedrock are accessible
"""
import boto3
import json
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

def test_transcribe():
    """Test AWS Transcribe access"""
    print("\n🎤 Testing AWS Transcribe...")
    try:
        client = boto3.client('transcribe', region_name=REGION)
        # Try to list transcription jobs (should work even if empty)
        response = client.list_transcription_jobs(MaxResults=1)
        print("✅ Transcribe is ACCESSIBLE")
        print(f"   Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Transcribe is BLOCKED")
        print(f"   Error: {error_code}")
        print(f"   Message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Transcribe ERROR: {str(e)}")
        return False

def test_bedrock_runtime():
    """Test Bedrock Runtime (for inference)"""
    print("\n🤖 Testing Bedrock Runtime (Claude)...")
    try:
        client = boto3.client('bedrock-runtime', region_name=REGION)
        # Try to invoke Claude with minimal prompt
        response = client.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })
        )
        print("✅ Bedrock Claude is ACCESSIBLE")
        print(f"   Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Bedrock Claude is BLOCKED")
        print(f"   Error: {error_code}")
        print(f"   Message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Bedrock Claude ERROR: {str(e)}")
        return False

def test_bedrock_embeddings():
    """Test Bedrock Titan Embeddings"""
    print("\n🧠 Testing Bedrock Titan Embeddings...")
    try:
        client = boto3.client('bedrock-runtime', region_name=REGION)
        # Try to generate embeddings
        response = client.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=json.dumps({"inputText": "test"})
        )
        print("✅ Bedrock Titan Embeddings is ACCESSIBLE")
        print(f"   Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Bedrock Titan Embeddings is BLOCKED")
        print(f"   Error: {error_code}")
        print(f"   Message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Bedrock Titan Embeddings ERROR: {str(e)}")
        return False

def test_bedrock_models():
    """List available Bedrock models"""
    print("\n📋 Listing Bedrock Models...")
    try:
        client = boto3.client('bedrock', region_name=REGION)
        response = client.list_foundation_models()
        models = response.get('modelSummaries', [])
        print(f"✅ Found {len(models)} Bedrock models")
        
        # Show relevant models
        relevant = ['claude', 'titan', 'nova']
        for model in models:
            model_id = model.get('modelId', '')
            if any(r in model_id.lower() for r in relevant):
                print(f"   - {model_id}")
        return True
    except ClientError as e:
        print(f"❌ Cannot list models: {e.response['Error']['Code']}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_aws_credentials():
    """Verify AWS credentials are configured"""
    print("\n🔑 Checking AWS Credentials...")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS Credentials are valid")
        print(f"   Account: {identity['Account']}")
        print(f"   User: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"❌ AWS Credentials ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("AWS Services Availability Test")
    print("=" * 60)
    
    results = {
        'credentials': check_aws_credentials(),
        'transcribe': test_transcribe(),
        'bedrock_claude': test_bedrock_runtime(),
        'bedrock_embeddings': test_bedrock_embeddings(),
        'bedrock_models': test_bedrock_models()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    all_pass = all(results.values())
    print("\n" + "=" * 60)
    if all_pass:
        print("🎉 ALL SERVICES ACCESSIBLE - Ready for production!")
    else:
        print("⚠️  SOME SERVICES BLOCKED - Check errors above")
    print("=" * 60)
