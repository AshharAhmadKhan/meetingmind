import boto3
import json
import time

bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

print("="*60)
print("TESTING NOVA WITH INFERENCE PROFILES")
print("="*60)

models = [
    ('apac.amazon.nova-lite-v1:0', 'Nova Lite (APAC Profile)'),
    ('apac.amazon.nova-micro-v1:0', 'Nova Micro (APAC Profile)'),
]

for model_id, model_name in models:
    print(f"\n🔍 Testing {model_name}...")
    print(f"   Model ID: {model_id}")
    
    success_count = 0
    throttle_count = 0
    
    # Test 5 rapid requests
    for i in range(5):
        try:
            body = json.dumps({
                'messages': [{'role': 'user', 'content': [{'text': f'Test {i+1}'}]}],
                'inferenceConfig': {'maxTokens': 50, 'temperature': 0.1}
            })
            
            response = bedrock.invoke_model(
                modelId=model_id,
                body=body
            )
            
            result = json.loads(response['body'].read())
            success_count += 1
            print(f"   ✅ Request {i+1}: SUCCESS")
            
        except Exception as e:
            error_str = str(e)
            if 'ThrottlingException' in error_str or 'TooManyRequestsException' in error_str:
                throttle_count += 1
                print(f"   ⚠️  Request {i+1}: THROTTLED")
            else:
                print(f"   ❌ Request {i+1}: ERROR - {error_str[:150]}")
        
        time.sleep(0.2)  # 200ms between requests
    
    print(f"\n   Results: {success_count}/5 successful, {throttle_count}/5 throttled")
    
    if success_count == 5:
        print(f"   ✅ {model_name} is FULLY ACCESSIBLE")
    elif success_count > 0:
        print(f"   ⚠️  {model_name} is PARTIALLY ACCESSIBLE (some throttling)")
    else:
        print(f"   ❌ {model_name} is NOT ACCESSIBLE")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("\nIf both models show 5/5 successful:")
print("  ✅ You can upload meetings - they will process fine")
print("\nIf throttling occurs:")
print("  ⚠️  You can still upload, but may hit rate limits")
print("  💡 Your code has exponential backoff to handle this")
