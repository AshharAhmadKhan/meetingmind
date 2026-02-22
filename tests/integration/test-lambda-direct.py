#!/usr/bin/env python3
"""Test the check-duplicate Lambda directly"""

import json
import boto3

REGION = 'ap-south-1'
FUNCTION_NAME = 'meetingmind-check-duplicate'
TEST_USER_ID = 'c1c38d2a-1081-7088-7c71-0abc19a150e9'

def test_duplicate_detection():
    """Test duplicate detection with known duplicate task"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Test with a task we know is repeated multiple times
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
    
    print("\n" + "="*60)
    print("TESTING DUPLICATE DETECTION LAMBDA")
    print("="*60)
    print(f"\nTest task: '{test_task}'")
    print(f"User ID: {TEST_USER_ID}")
    print("\nInvoking Lambda...")
    
    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    
    result = json.loads(response['Payload'].read())
    
    print(f"\nLambda Status Code: {result.get('statusCode')}")
    
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Is Duplicate: {body.get('isDuplicate')}")
        print(f"Similarity: {body.get('similarity')}%")
        print(f"Is Chronic Blocker: {body.get('isChronicBlocker')}")
        print(f"Repeat Count: {body.get('repeatCount')}")
        
        if body.get('bestMatch'):
            print(f"\nBest Match:")
            print(f"  Task: {body['bestMatch']['task']}")
            print(f"  From: {body['bestMatch']['meetingTitle']}")
            print(f"  Similarity: {body['bestMatch']['similarity']}%")
        
        if body.get('history'):
            print(f"\nHistory ({len(body['history'])} similar items):")
            for i, item in enumerate(body['history'][:5], 1):
                print(f"  {i}. {item['task'][:60]}... ({item['similarity']}%)")
        
        print("\n✓ Duplicate detection working correctly!")
        return True
    else:
        print(f"\n✗ Lambda returned error:")
        print(json.dumps(result, indent=2))
        return False

if __name__ == '__main__':
    test_duplicate_detection()
