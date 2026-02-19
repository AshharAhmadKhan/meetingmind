#!/usr/bin/env python3
"""
Comprehensive Bedrock Throttling Test
Tests Nova Lite and Nova Micro with 50+ rapid requests to verify no throttling occurs.
"""

import boto3
import json
import time
from datetime import datetime
from botocore.config import Config

# Configure Bedrock client with minimal retries to catch throttling immediately
bedrock_config = Config(
    retries={
        'max_attempts': 1,  # No retries - we want to see throttling immediately
        'mode': 'standard'
    }
)

bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1', config=bedrock_config)

def test_model(model_id, model_name, num_requests=50):
    """Test a model with rapid requests."""
    print(f"\n{'='*70}")
    print(f"Testing {model_name} ({model_id})")
    print(f"Making {num_requests} rapid requests...")
    print(f"{'='*70}\n")
    
    results = {
        'success': 0,
        'throttled': 0,
        'errors': 0,
        'response_times': [],
        'error_details': []
    }
    
    start_time = time.time()
    
    for i in range(num_requests):
        request_start = time.time()
        
        try:
            # Simple prompt for fast response
            prompt = f"Say 'Test {i+1}' in one word."
            
            body = json.dumps({
                'messages': [{'role': 'user', 'content': [{'text': prompt}]}],
                'inferenceConfig': {'maxTokens': 10, 'temperature': 0.1}
            })
            
            response = bedrock.invoke_model(modelId=model_id, body=body)
            result = json.loads(response['body'].read())
            
            request_time = time.time() - request_start
            results['response_times'].append(request_time)
            results['success'] += 1
            
            # Print progress every 10 requests
            if (i + 1) % 10 == 0:
                print(f"✓ Completed {i+1}/{num_requests} requests (avg: {sum(results['response_times'])/len(results['response_times']):.2f}s)")
            
        except Exception as e:
            error_str = str(e)
            request_time = time.time() - request_start
            
            if 'ThrottlingException' in error_str or 'TooManyRequestsException' in error_str:
                results['throttled'] += 1
                print(f"✗ Request {i+1}: THROTTLED after {request_time:.2f}s")
                results['error_details'].append({
                    'request': i+1,
                    'type': 'throttled',
                    'error': error_str,
                    'time': request_time
                })
            else:
                results['errors'] += 1
                print(f"✗ Request {i+1}: ERROR - {error_str[:100]}")
                results['error_details'].append({
                    'request': i+1,
                    'type': 'error',
                    'error': error_str,
                    'time': request_time
                })
    
    total_time = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"RESULTS FOR {model_name}")
    print(f"{'='*70}")
    print(f"Total Requests:     {num_requests}")
    print(f"✓ Successful:       {results['success']} ({results['success']/num_requests*100:.1f}%)")
    print(f"⚠ Throttled:        {results['throttled']} ({results['throttled']/num_requests*100:.1f}%)")
    print(f"✗ Errors:           {results['errors']} ({results['errors']/num_requests*100:.1f}%)")
    print(f"\nTiming:")
    print(f"Total Time:         {total_time:.2f}s")
    print(f"Requests/Second:    {num_requests/total_time:.2f}")
    
    if results['response_times']:
        avg_time = sum(results['response_times']) / len(results['response_times'])
        min_time = min(results['response_times'])
        max_time = max(results['response_times'])
        print(f"Avg Response Time:  {avg_time:.2f}s")
        print(f"Min Response Time:  {min_time:.2f}s")
        print(f"Max Response Time:  {max_time:.2f}s")
    
    if results['error_details']:
        print(f"\nError Details:")
        for error in results['error_details'][:5]:  # Show first 5 errors
            print(f"  Request {error['request']}: {error['type']} - {error['error'][:80]}")
        if len(results['error_details']) > 5:
            print(f"  ... and {len(results['error_details']) - 5} more errors")
    
    print(f"{'='*70}\n")
    
    return results

def main():
    print(f"\n{'#'*70}")
    print(f"# COMPREHENSIVE BEDROCK THROTTLING TEST")
    print(f"# Testing Nova models with 50+ rapid requests")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}\n")
    
    models = [
        ('apac.amazon.nova-lite-v1:0', 'Nova Lite (APAC Profile)'),
        ('apac.amazon.nova-micro-v1:0', 'Nova Micro (APAC Profile)'),
    ]
    
    all_results = {}
    
    for model_id, model_name in models:
        results = test_model(model_id, model_name, num_requests=50)
        all_results[model_name] = results
        
        # Small delay between model tests
        if model_id != models[-1][0]:
            print("Waiting 5 seconds before next model test...\n")
            time.sleep(5)
    
    # Final summary
    print(f"\n{'#'*70}")
    print(f"# FINAL SUMMARY")
    print(f"{'#'*70}\n")
    
    for model_name, results in all_results.items():
        total = results['success'] + results['throttled'] + results['errors']
        print(f"{model_name}:")
        print(f"  Success Rate: {results['success']}/{total} ({results['success']/total*100:.1f}%)")
        print(f"  Throttle Rate: {results['throttled']}/{total} ({results['throttled']/total*100:.1f}%)")
        print(f"  Error Rate: {results['errors']}/{total} ({results['errors']/total*100:.1f}%)")
        
        if results['throttled'] == 0:
            print(f"  ✅ NO THROTTLING DETECTED")
        else:
            print(f"  ⚠️  THROTTLING DETECTED - {results['throttled']} requests throttled")
        print()
    
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}\n")
    
    # Return exit code based on throttling
    total_throttled = sum(r['throttled'] for r in all_results.values())
    if total_throttled > 0:
        print(f"⚠️  WARNING: {total_throttled} total requests were throttled")
        return 1
    else:
        print("✅ SUCCESS: No throttling detected across all models")
        return 0

if __name__ == '__main__':
    exit(main())
