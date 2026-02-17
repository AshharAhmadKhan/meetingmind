#!/usr/bin/env python3
"""
Comprehensive test suite for Day 5 Duplicate Detection feature.
Tests backend Lambda, API Gateway, and provides frontend verification steps.
"""

import json
import boto3
import requests
from decimal import Decimal

# Configuration
REGION = 'ap-south-1'
STACK_NAME = 'meetingmind-stack'
TABLE_NAME = 'meetingmind-meetings'

# Test user (from your actual data)
TEST_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

def test_1_check_lambda_exists():
    """Test 1: Verify check-duplicate Lambda exists"""
    print("\n" + "="*60)
    print("TEST 1: Check Lambda Function Exists")
    print("="*60)
    
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        response = lambda_client.get_function(
            FunctionName=f'{STACK_NAME}-CheckDuplicateFunction'
        )
        print("✓ Lambda function exists")
        print(f"  Function ARN: {response['Configuration']['FunctionArn']}")
        print(f"  Runtime: {response['Configuration']['Runtime']}")
        print(f"  Memory: {response['Configuration']['MemorySize']} MB")
        return True
    except Exception as e:
        print(f"✗ Lambda function not found: {e}")
        return False

def test_2_check_api_endpoint():
    """Test 2: Verify API Gateway endpoint exists"""
    print("\n" + "="*60)
    print("TEST 2: Check API Gateway Endpoint")
    print("="*60)
    
    try:
        cf_client = boto3.client('cloudformation', region_name=REGION)
        response = cf_client.describe_stacks(StackName=STACK_NAME)
        
        outputs = response['Stacks'][0]['Outputs']
        api_url = None
        for output in outputs:
            if output['OutputKey'] == 'ApiUrl':
                api_url = output['OutputValue']
                break
        
        if api_url:
            print(f"✓ API Gateway URL found: {api_url}")
            print(f"  Duplicate endpoint: {api_url}/check-duplicate")
            return api_url
        else:
            print("✗ API Gateway URL not found in stack outputs")
            return None
    except Exception as e:
        print(f"✗ Failed to get API endpoint: {e}")
        return None

def test_3_check_dynamodb_data():
    """Test 3: Verify DynamoDB has action items with embeddings"""
    print("\n" + "="*60)
    print("TEST 3: Check DynamoDB Data")
    print("="*60)
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)
        
        # Query user's meetings
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': TEST_USER_ID},
            Limit=5
        )
        
        meetings = response.get('Items', [])
        print(f"✓ Found {len(meetings)} meetings for test user")
        
        total_actions = 0
        actions_with_embeddings = 0
        sample_actions = []
        
        for meeting in meetings:
            actions = meeting.get('actionItems', [])
            total_actions += len(actions)
            
            for action in actions:
                if action.get('embedding'):
                    actions_with_embeddings += 1
                
                # Collect sample actions for testing
                if len(sample_actions) < 3 and not action.get('completed'):
                    sample_actions.append({
                        'task': action.get('task'),
                        'meetingTitle': meeting.get('title'),
                        'hasEmbedding': bool(action.get('embedding'))
                    })
        
        print(f"  Total action items: {total_actions}")
        print(f"  Actions with embeddings: {actions_with_embeddings}")
        print(f"  Coverage: {(actions_with_embeddings/total_actions*100):.1f}%")
        
        print("\n  Sample actions for testing:")
        for i, action in enumerate(sample_actions, 1):
            print(f"    {i}. {action['task'][:60]}...")
            print(f"       From: {action['meetingTitle']}")
            print(f"       Has embedding: {action['hasEmbedding']}")
        
        return sample_actions
    except Exception as e:
        print(f"✗ Failed to check DynamoDB: {e}")
        return []

def test_4_invoke_lambda_directly():
    """Test 4: Invoke Lambda function directly"""
    print("\n" + "="*60)
    print("TEST 4: Invoke Lambda Directly")
    print("="*60)
    
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        
        # Test with a known duplicate task
        test_task = "Update project tracker with new milestones"
        
        event = {
            'body': json.dumps({'task': test_task}),
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': TEST_USER_ID
                    }
                }
            }
        }
        
        print(f"  Testing task: '{test_task}'")
        
        response = lambda_client.invoke(
            FunctionName=f'{STACK_NAME}-CheckDuplicateFunction',
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"  Lambda response status: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result['body'])
            body = decimal_to_float(body)
            
            print(f"✓ Lambda executed successfully")
            print(f"  Is duplicate: {body.get('isDuplicate')}")
            print(f"  Similarity: {body.get('similarity')}%")
            print(f"  Is chronic blocker: {body.get('isChronicBlocker')}")
            print(f"  Repeat count: {body.get('repeatCount')}")
            
            if body.get('bestMatch'):
                print(f"  Best match: {body['bestMatch']['task'][:60]}...")
                print(f"    From: {body['bestMatch']['meetingTitle']}")
            
            return True
        else:
            print(f"✗ Lambda returned error: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to invoke Lambda: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_check_frontend_build():
    """Test 5: Verify frontend build has duplicate detection code"""
    print("\n" + "="*60)
    print("TEST 5: Check Frontend Build")
    print("="*60)
    
    try:
        import os
        
        # Check if dist folder exists
        if not os.path.exists('frontend/dist'):
            print("✗ frontend/dist folder not found")
            return False
        
        # Check index.html
        with open('frontend/dist/index.html', 'r') as f:
            html = f.read()
            if 'index-B3aTIndA.js' in html:
                print("✓ index.html references correct JavaScript file")
            else:
                print("✗ index.html references wrong JavaScript file")
                return False
        
        # Check if JavaScript file exists
        js_file = 'frontend/dist/assets/index-B3aTIndA.js'
        if os.path.exists(js_file):
            print(f"✓ JavaScript file exists: {js_file}")
            
            # Check if it contains duplicate detection code
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
                
                checks = [
                    ('checkDuplicate', 'checkDuplicate function'),
                    ('scanForDuplicates', 'scanForDuplicates function'),
                    ('Check Duplicates', 'Check Duplicates button text'),
                    ('duplicateResults', 'duplicateResults state'),
                ]
                
                all_found = True
                for search_term, description in checks:
                    if search_term in js_content:
                        print(f"  ✓ Found: {description}")
                    else:
                        print(f"  ✗ Missing: {description}")
                        all_found = False
                
                return all_found
        else:
            print(f"✗ JavaScript file not found: {js_file}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to check frontend build: {e}")
        return False

def test_6_check_s3_deployment():
    """Test 6: Verify S3 has correct files"""
    print("\n" + "="*60)
    print("TEST 6: Check S3 Deployment")
    print("="*60)
    
    try:
        s3_client = boto3.client('s3', region_name=REGION)
        bucket = 'meetingmind-audio-707411439284'
        
        # Check index.html
        response = s3_client.get_object(Bucket=bucket, Key='index.html')
        html = response['Body'].read().decode('utf-8')
        
        if 'index-B3aTIndA.js' in html:
            print("✓ S3 index.html references correct JavaScript file")
        else:
            print("✗ S3 index.html references wrong JavaScript file")
            print(f"  Content: {html[:200]}...")
            return False
        
        # Check if JavaScript file exists
        try:
            s3_client.head_object(Bucket=bucket, Key='assets/index-B3aTIndA.js')
            print("✓ JavaScript file exists in S3")
        except:
            print("✗ JavaScript file not found in S3")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to check S3: {e}")
        return False

def test_7_check_cloudfront():
    """Test 7: Check CloudFront distribution"""
    print("\n" + "="*60)
    print("TEST 7: Check CloudFront Distribution")
    print("="*60)
    
    try:
        cf_client = boto3.client('cloudfront', region_name=REGION)
        dist_id = 'E3CAAI97MXY83V'
        
        response = cf_client.get_distribution(Id=dist_id)
        config = response['Distribution']['DistributionConfig']
        
        print(f"✓ CloudFront distribution found")
        print(f"  Domain: {response['Distribution']['DomainName']}")
        print(f"  Status: {response['Distribution']['Status']}")
        print(f"  Origin path: {config['Origins']['Items'][0].get('OriginPath', '(root)')}")
        
        # Check for recent invalidations
        invalidations = cf_client.list_invalidations(DistributionId=dist_id)
        if invalidations['InvalidationList']['Items']:
            latest = invalidations['InvalidationList']['Items'][0]
            print(f"  Latest invalidation: {latest['Id']}")
            print(f"  Status: {latest['Status']}")
            print(f"  Created: {latest['CreateTime']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to check CloudFront: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MEETINGMIND DAY 5 - DUPLICATE DETECTION TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Lambda Exists", test_1_check_lambda_exists()))
    api_url = test_2_check_api_endpoint()
    results.append(("API Endpoint", api_url is not None))
    sample_actions = test_3_check_dynamodb_data()
    results.append(("DynamoDB Data", len(sample_actions) > 0))
    results.append(("Lambda Invocation", test_4_invoke_lambda_directly()))
    results.append(("Frontend Build", test_5_check_frontend_build()))
    results.append(("S3 Deployment", test_6_check_s3_deployment()))
    results.append(("CloudFront", test_7_check_cloudfront()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    # Frontend verification instructions
    print("\n" + "="*60)
    print("FRONTEND VERIFICATION STEPS")
    print("="*60)
    print("""
To verify the frontend is working:

1. CLEAR BROWSER CACHE COMPLETELY:
   - Edge: Ctrl+Shift+Delete → Clear all cached images and files
   - Close browser completely
   - Reopen browser

2. VISIT IN INCOGNITO/PRIVATE MODE:
   - This bypasses all cache
   - URL: https://dcfx593ywvy92.cloudfront.net

3. CHECK DEVELOPER TOOLS:
   - Press F12
   - Go to Network tab
   - Reload page (Ctrl+R)
   - Look for: index-B3aTIndA.js (should be 200 OK)
   - If you see: index-m55NV4Kl.js (OLD FILE - cache issue)

4. VERIFY BUTTON EXISTS:
   - Go to Actions Overview page
   - Look for "🔍 Check Duplicates" button in filter bar
   - If not visible, check Elements tab for "Check Duplicates" text

5. TEST DUPLICATE DETECTION:
   - Click "🔍 Check Duplicates" button
   - Should scan all incomplete actions
   - Should show results panel with duplicates found
   - You have perfect test data: "Update project tracker" repeated 6+ times

6. IF STILL NOT WORKING:
   - Try different browser
   - Try different device
   - Try mobile phone on cellular data (different network)
   - Wait 5-10 more minutes for CloudFront propagation
""")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED! Backend is working correctly.")
        print("  Issue is likely browser/CloudFront cache.")
    else:
        print("\n✗ SOME TESTS FAILED. Check errors above.")

if __name__ == '__main__':
    main()
