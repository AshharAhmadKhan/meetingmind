#!/usr/bin/env python3
"""
Final Verification - Test all scenarios after IAM fix
"""
import boto3
import json

REGION = 'ap-south-1'
LAMBDA_NAME = 'meetingmind-list-meetings'

TEST_SCENARIOS = [
    {
        'name': 'V1 Team - Uploader',
        'email': 'thecyberprinciples@gmail.com',
        'userId': 'c1c38d2a-1081-7088-7c71-0abc19a150e9',
        'teamId': '95febcb2-97e2-4395-bdde-da8475dbae0d',
        'expected_meetings': 5
    },
    {
        'name': 'V1 Team - Member 1',
        'email': 'thehiddenif@gmail.com',
        'userId': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134',
        'teamId': '95febcb2-97e2-4395-bdde-da8475dbae0d',
        'expected_meetings': 5
    },
    {
        'name': 'V1 Team - Member 2',
        'email': 'ashkagakoko@gmail.com',
        'userId': 'a1a3cd5a-00e1-701f-a07b-b12a35f16664',
        'teamId': '95febcb2-97e2-4395-bdde-da8475dbae0d',
        'expected_meetings': 5
    },
    {
        'name': 'V2 Team - Uploader',
        'email': 'thecyberprinciples@gmail.com',
        'userId': 'c1c38d2a-1081-7088-7c71-0abc19a150e9',
        'teamId': 'df29c543-a4d0-4c80-a086-6c11712d66f3',
        'expected_meetings': 3
    },
    {
        'name': 'V2 Team - Member 1',
        'email': 'thehiddenif@gmail.com',
        'userId': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134',
        'teamId': 'df29c543-a4d0-4c80-a086-6c11712d66f3',
        'expected_meetings': 3
    },
    {
        'name': 'V2 Team - Member 2',
        'email': 'whispersbehindthecode@gmail.com',
        'userId': 'f1d33d1a-9041-7006-5af8-d18269b15a92',
        'teamId': 'df29c543-a4d0-4c80-a086-6c11712d66f3',
        'expected_meetings': 3
    }
]

lambda_client = boto3.client('lambda', region_name=REGION)

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_scenario(scenario):
    """Test a specific scenario"""
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': {
            'teamId': scenario['teamId']
        },
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': scenario['userId'],
                    'email': scenario['email']
                }
            }
        }
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if payload.get('statusCode') == 200:
            body = json.loads(payload.get('body', '{}'))
            meetings = body.get('meetings', [])
            
            if len(meetings) == scenario['expected_meetings']:
                return True, len(meetings), None
            else:
                return False, len(meetings), f"Expected {scenario['expected_meetings']}, got {len(meetings)}"
        else:
            body = json.loads(payload.get('body', '{}'))
            return False, 0, body.get('error', 'Unknown error')
    except Exception as e:
        return False, 0, str(e)

def main():
    print("\n" + "="*80)
    print("  FINAL VERIFICATION - ALL SCENARIOS")
    print("  Testing after IAM permission fix")
    print("="*80)
    
    results = []
    
    for scenario in TEST_SCENARIOS:
        print(f"\nTesting: {scenario['name']}")
        print(f"  User: {scenario['email']}")
        print(f"  Team: {scenario['teamId'][:8]}...")
        
        success, count, error = test_scenario(scenario)
        
        if success:
            print(f"  ✅ PASS: Got {count} meetings")
        else:
            print(f"  ❌ FAIL: {error}")
        
        results.append({
            'scenario': scenario['name'],
            'success': success,
            'count': count,
            'error': error
        })
    
    # Summary
    print_section("SUMMARY")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Passed: {passed}/{total}\n")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {result['scenario']}")
        if not result['success']:
            print(f"       Error: {result['error']}")
    
    if passed == total:
        print(f"\n{'='*80}")
        print(f"  ✅ ALL TESTS PASSED")
        print(f"{'='*80}")
        print(f"\nBackend is working perfectly!")
        print(f"\nNext steps:")
        print(f"  1. Invalidate CloudFront cache:")
        print(f"     aws cloudfront create-invalidation \\")
        print(f"       --distribution-id E3CAAI97MXY83V \\")
        print(f"       --paths \"/*\"")
        print(f"  2. Wait 5-10 minutes for cache invalidation")
        print(f"  3. Clear browser cache completely")
        print(f"  4. Test in browser with all 3 accounts")
        print(f"\n{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"  ❌ SOME TESTS FAILED")
        print(f"{'='*80}")
        print(f"\nCheck errors above and investigate further.\n")

if __name__ == '__main__':
    main()
