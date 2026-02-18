#!/usr/bin/env python3
"""
Safe Bedrock Status Checker
Checks if Bedrock models are accessible without triggering marketplace subscriptions
"""
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError

REGION = 'ap-south-1'

# Disable retries to prevent multiple marketplace triggers
bedrock_config = Config(
    retries={'max_attempts': 0, 'mode': 'standard'}
)

def check_bedrock_access():
    """Check Bedrock access for different models"""
    bedrock = boto3.client('bedrock-runtime', region_name=REGION, config=bedrock_config)
    
    models_to_test = [
        ('anthropic.claude-3-haiku-20240307-v1:0', 'Claude Haiku'),
        ('amazon.nova-lite-v1:0', 'Nova Lite'),
        ('amazon.nova-micro-v1:0', 'Nova Micro'),
        ('amazon.titan-embed-text-v2:0', 'Titan Embeddings v2'),
    ]
    
    results = []
    
    for model_id, model_name in models_to_test:
        print(f"\n🔍 Testing {model_name} ({model_id})...")
        
        try:
            if 'titan-embed' in model_id:
                # Test embeddings model
                body = json.dumps({"inputText": "test"})
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=body
                )
                result = json.loads(response['body'].read())
                
                if 'embedding' in result:
                    print(f"   ✅ {model_name}: ACCESSIBLE (embedding generated)")
                    results.append((model_name, 'ACCESSIBLE', None))
                else:
                    print(f"   ⚠️  {model_name}: UNEXPECTED RESPONSE")
                    results.append((model_name, 'UNEXPECTED', 'No embedding in response'))
            
            elif 'anthropic' in model_id:
                # Test Claude model
                body = json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'Hi'}]
                })
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=body
                )
                result = json.loads(response['body'].read())
                
                if 'content' in result:
                    print(f"   ✅ {model_name}: ACCESSIBLE (response generated)")
                    results.append((model_name, 'ACCESSIBLE', None))
                else:
                    print(f"   ⚠️  {model_name}: UNEXPECTED RESPONSE")
                    results.append((model_name, 'UNEXPECTED', 'No content in response'))
            
            else:
                # Test Nova models
                body = json.dumps({
                    'messages': [{'role': 'user', 'content': [{'text': 'Hi'}]}],
                    'inferenceConfig': {'maxTokens': 10, 'temperature': 0.1}
                })
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=body
                )
                result = json.loads(response['body'].read())
                
                if 'output' in result:
                    print(f"   ✅ {model_name}: ACCESSIBLE (response generated)")
                    results.append((model_name, 'ACCESSIBLE', None))
                else:
                    print(f"   ⚠️  {model_name}: UNEXPECTED RESPONSE")
                    results.append((model_name, 'UNEXPECTED', 'No output in response'))
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
                print(f"   ❌ {model_name}: PAYMENT ISSUE (credit card not validated)")
                results.append((model_name, 'PAYMENT_ISSUE', 'Credit card validation pending'))
            
            elif 'AccessDeniedException' in error_code:
                print(f"   ❌ {model_name}: ACCESS DENIED (model not enabled)")
                results.append((model_name, 'ACCESS_DENIED', 'Model access not enabled'))
            
            elif 'ThrottlingException' in error_code:
                print(f"   ⚠️  {model_name}: THROTTLED (but accessible)")
                results.append((model_name, 'THROTTLED', 'Rate limited but accessible'))
            
            elif 'ValidationException' in error_code:
                print(f"   ⚠️  {model_name}: VALIDATION ERROR")
                results.append((model_name, 'VALIDATION_ERROR', error_msg))
            
            else:
                print(f"   ❌ {model_name}: ERROR - {error_code}: {error_msg}")
                results.append((model_name, 'ERROR', f"{error_code}: {error_msg}"))
        
        except Exception as e:
            print(f"   ❌ {model_name}: UNEXPECTED ERROR - {str(e)}")
            results.append((model_name, 'UNEXPECTED_ERROR', str(e)))
    
    return results


def check_transcribe_access():
    """Check Transcribe access"""
    print(f"\n🔍 Testing Amazon Transcribe...")
    
    transcribe = boto3.client('transcribe', region_name=REGION)
    
    try:
        # List transcription jobs (safe operation, doesn't create anything)
        response = transcribe.list_transcription_jobs(MaxResults=1)
        print(f"   ✅ Amazon Transcribe: ACCESSIBLE")
        return ('Amazon Transcribe', 'ACCESSIBLE', None)
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"   ❌ Amazon Transcribe: ERROR - {error_code}: {error_msg}")
        return ('Amazon Transcribe', 'ERROR', f"{error_code}: {error_msg}")
    
    except Exception as e:
        print(f"   ❌ Amazon Transcribe: UNEXPECTED ERROR - {str(e)}")
        return ('Amazon Transcribe', 'UNEXPECTED_ERROR', str(e))


def print_summary(bedrock_results, transcribe_result):
    """Print summary of all tests"""
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    accessible = []
    issues = []
    
    # Check Bedrock results
    for model_name, status, error in bedrock_results:
        if status == 'ACCESSIBLE' or status == 'THROTTLED':
            accessible.append(model_name)
        else:
            issues.append((model_name, status, error))
    
    # Check Transcribe result
    if transcribe_result[1] == 'ACCESSIBLE':
        accessible.append(transcribe_result[0])
    else:
        issues.append(transcribe_result)
    
    print(f"\n✅ ACCESSIBLE ({len(accessible)}):")
    for model in accessible:
        print(f"   - {model}")
    
    if issues:
        print(f"\n❌ ISSUES ({len(issues)}):")
        for model, status, error in issues:
            print(f"   - {model}: {status}")
            if error:
                print(f"     {error}")
    
    print("\n" + "="*60)
    
    if len(accessible) == 5:  # All 4 Bedrock models + Transcribe
        print("🎉 ALL SERVICES ACCESSIBLE!")
        print("✅ Credit card validation has propagated")
        print("✅ Ready for production use")
    elif len(accessible) > 0:
        print("⚠️  PARTIAL ACCESS")
        print(f"✅ {len(accessible)}/5 services accessible")
        print("⏳ Some services may still be propagating")
    else:
        print("❌ NO ACCESS")
        print("⏳ Credit card validation still pending")
        print("💡 Wait 24-48 hours for propagation")


if __name__ == '__main__':
    print("="*60)
    print("BEDROCK & TRANSCRIBE STATUS CHECK")
    print("="*60)
    print(f"Region: {REGION}")
    print(f"Account: {boto3.client('sts').get_caller_identity()['Account']}")
    
    # Check Bedrock
    bedrock_results = check_bedrock_access()
    
    # Check Transcribe
    transcribe_result = check_transcribe_access()
    
    # Print summary
    print_summary(bedrock_results, transcribe_result)
