#!/usr/bin/env python3
"""
Test list-meetings Lambda directly by simulating the exact API Gateway event
"""
import boto3
import json

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
LAMBDA_NAME = 'meetingmind-list-meetings'

# Test users
TEST_USERS = [
    {
        'name': 'Uploader (thecyberprinciples)',
        'email': 'thecyberprinciples@gmail.com',
        'userId': 'c1c38d2a-1081-7088-7c71-0abc19a150e9'
    },
    {
        'name': 'Member 1 (thehiddenif)',
        'email': 'thehiddenif@gmail.com',
        'userId': 'e153cd2a-70b1-7019-4a1b-fabfc31d3134'
    },
    {
        'name': 'Member 2 (ashkagakoko/Keldeo)',
        'email': 'ashkagakoko@gmail.com',
        'userId': 'a1a3cd5a-00e1-701f-a07b-b12a35f16664'
    }
]

V1_TEAM_ID = '95febcb2-97e2-4395-bdde-da8475dbae0d'

lambda_client = boto3.client('lambda', region_name=REGION)

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_user(user_info, team_id):
    """Test list-meetings for a specific user"""
    print(f"\n{'─'*80}")
    print(f"Testing: {user_info['name']}")
    print(f"Email: {user_info['email']}")
    print(f"UserId: {user_info['userId']}")
    print(f"{'─'*80}")
    
    # Create API Gateway event
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': {
            'teamId': team_id
        },
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': user_info['userId'],
                    'email': user_info['email']
                }
            }
        }
    }
    
    print(f"\nInvoking Lambda with teamId={team_id}")
    
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        print(f"Lambda Response:")
        print(f"  StatusCode: {payload.get('statusCode')}")
        
        if payload.get('statusCode') == 200:
            body = json.loads(payload.get('body', '{}'))
            meetings = body.get('meetings', [])
            
            print(f"  ✅ SUCCESS: Got {len(meetings)} meetings")
            
            for i, meeting in enumerate(meetings, 1):
                print(f"    {i}. {meeting.get('title', 'Untitled')}")
                print(f"       Status: {meeting.get('status', 'Unknown')}")
                print(f"       MeetingId: {meeting.get('meetingId', 'Unknown')}")
            
            return True
        else:
            body = json.loads(payload.get('body', '{}'))
            print(f"  ❌ FAILED: {body.get('error', 'Unknown error')}")
            print(f"  Full response: {json.dumps(payload, indent=2)}")
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("  TEST LIST-MEETINGS LAMBDA DIRECTLY")
    print("  Simulating exact API Gateway events")
    print("="*80)
    
    print_section(f"Testing V1 Team: {V1_TEAM_ID}")
    
    results = {}
    
    for user_info in TEST_USERS:
        results[user_info['email']] = test_user(user_info, V1_TEAM_ID)
    
    # Summary
    print_section("SUMMARY")
    
    for email, success in results.items():
        status = "✅ CAN see meetings" if success else "❌ CANNOT see meetings"
        print(f"{email}: {status}")
    
    if all(results.values()):
        print(f"\n✅ ALL USERS CAN SEE MEETINGS")
        print(f"   Lambda is working correctly")
        print(f"   Issue is likely:")
        print(f"     1. Frontend not sending teamId correctly")
        print(f"     2. Frontend not sending auth token correctly")
        print(f"     3. CloudFront caching old responses")
    else:
        print(f"\n❌ SOME USERS CANNOT SEE MEETINGS")
        print(f"   Lambda has a bug")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
