import boto3
import json
import time
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

def test_model(model_id, model_name, num_requests=10):
    """Test a model with rapid requests to check throttling"""
    print(f"\n{'='*60}")
    print(f"Testing {model_name} ({model_id})")
    print(f"Making {num_requests} rapid requests...")
    print(f"{'='*60}")
    
    success_count = 0
    throttle_count = 0
    error_count = 0
    
    start_time = time.time()
    
    for i in range(num_requests):
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
            print(f"  ✅ Request {i+1}: SUCCESS")
            
        except Exception as e:
            error_str = str(e)
            if 'ThrottlingException' in error_str or 'TooManyRequestsException' in error_str:
                throttle_count += 1
                print(f"  ⚠️  Request {i+1}: THROTTLED")
            else:
                error_count += 1
                print(f"  ❌ Request {i+1}: ERROR - {error_str[:100]}")
        
        # Small delay to avoid overwhelming
        time.sleep(0.1)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"RESULTS for {model_name}:")
    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {success_count}")
    print(f"  Throttled: {throttle_count}")
    print(f"  Errors: {error_count}")
    print(f"  Time elapsed: {elapsed:.2f}s")
    print(f"  Requests/second: {num_requests/elapsed:.2f}")
    print(f"{'='*60}")
    
    return {
        'success': success_count,
        'throttled': throttle_count,
        'errors': error_count,
        'rps': num_requests/elapsed
    }

# Test Nova Lite
print("\n🔍 THROTTLE TESTING - Nova Models")
print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

nova_lite_results = test_model('amazon.nova-lite-v1:0', 'Nova Lite', 15)
time.sleep(2)  # Cool down between models
nova_micro_results = test_model('amazon.nova-micro-v1:0', 'Nova Micro', 15)

print("\n" + "="*60)
print("FINAL SUMMARY")
print("="*60)
print(f"\nNova Lite:")
print(f"  Success rate: {nova_lite_results['success']}/15 ({nova_lite_results['success']/15*100:.1f}%)")
print(f"  Throttle rate: {nova_lite_results['throttled']}/15 ({nova_lite_results['throttled']/15*100:.1f}%)")

print(f"\nNova Micro:")
print(f"  Success rate: {nova_micro_results['success']}/15 ({nova_micro_results['success']/15*100:.1f}%)")
print(f"  Throttle rate: {nova_micro_results['throttled']}/15 ({nova_micro_results['throttled']/15*100:.1f}%)")

if nova_lite_results['throttled'] > 0 or nova_micro_results['throttled'] > 0:
    print("\n⚠️  THROTTLING DETECTED - Quotas are limited")
else:
    print("\n✅ NO THROTTLING - Quotas appear sufficient for testing")
