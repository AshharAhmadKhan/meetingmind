#!/usr/bin/env python3
"""
Comprehensive MeetingMind Test Suite
Tests all components: backend, frontend config, AWS services, data integrity
"""
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError
from datetime import datetime

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
TEAMS_TABLE = 'meetingmind-teams'
AUDIO_BUCKET = 'meetingmind-audio-707411439284'

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"  ❌ {test_name}")
        print(f"     Error: {error}")
    
    def add_warning(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"  ⚠️  {test_name}")
        print(f"     Warning: {message}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\n🔴 FAILED TESTS:")
            for test, error in self.failed:
                print(f"  - {test}: {error}")
        
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for test, msg in self.warnings:
                print(f"  - {test}: {msg}")
        
        return len(self.failed) == 0

results = TestResults()

# ============================================================
# 1. AWS CREDENTIALS & ACCOUNT
# ============================================================
def test_aws_credentials():
    print("\n🔑 Testing AWS Credentials...")
    print("=" * 60)
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        results.add_pass(f"AWS Credentials Valid (Account: {identity['Account']})")
        return True
    except Exception as e:
        results.add_fail("AWS Credentials", str(e))
        return False

# ============================================================
# 2. DYNAMODB TABLES
# ============================================================
def test_dynamodb_tables():
    print("\n📊 Testing DynamoDB Tables...")
    print("=" * 60)
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    # Test Meetings Table
    try:
        response = dynamodb.describe_table(TableName=MEETINGS_TABLE)
        table_status = response['Table']['TableStatus']
        if table_status == 'ACTIVE':
            results.add_pass(f"Meetings Table ({table_status})")
        else:
            results.add_warning("Meetings Table", f"Status: {table_status}")
        
        # Check GSIs
        gsis = response['Table'].get('GlobalSecondaryIndexes', [])
        gsi_names = [gsi['IndexName'] for gsi in gsis]
        
        expected_gsis = ['status-createdAt-index', 'teamId-createdAt-index']
        for gsi in expected_gsis:
            if gsi in gsi_names:
                results.add_pass(f"GSI: {gsi}")
            else:
                results.add_fail(f"GSI: {gsi}", "Not found")
                
    except ClientError as e:
        results.add_fail("Meetings Table", e.response['Error']['Code'])
    
    # Test Teams Table
    try:
        response = dynamodb.describe_table(TableName=TEAMS_TABLE)
        table_status = response['Table']['TableStatus']
        if table_status == 'ACTIVE':
            results.add_pass(f"Teams Table ({table_status})")
        else:
            results.add_warning("Teams Table", f"Status: {table_status}")
        
        # Check GSI
        gsis = response['Table'].get('GlobalSecondaryIndexes', [])
        gsi_names = [gsi['IndexName'] for gsi in gsis]
        
        if 'inviteCode-index' in gsi_names:
            results.add_pass("GSI: inviteCode-index")
        else:
            results.add_fail("GSI: inviteCode-index", "Not found")
            
    except ClientError as e:
        results.add_fail("Teams Table", e.response['Error']['Code'])

# ============================================================
# 3. S3 BUCKET
# ============================================================
def test_s3_bucket():
    print("\n🪣 Testing S3 Bucket...")
    print("=" * 60)
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        # Check bucket exists
        s3.head_bucket(Bucket=AUDIO_BUCKET)
        results.add_pass(f"Audio Bucket Exists ({AUDIO_BUCKET})")
        
        # Check CORS configuration
        try:
            cors = s3.get_bucket_cors(Bucket=AUDIO_BUCKET)
            results.add_pass("CORS Configuration Present")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                results.add_warning("CORS Configuration", "Not configured")
            else:
                results.add_fail("CORS Configuration", e.response['Error']['Code'])
        
        # Check lifecycle rules
        try:
            lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=AUDIO_BUCKET)
            results.add_pass("Lifecycle Rules Present")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                results.add_warning("Lifecycle Rules", "Not configured")
            else:
                results.add_fail("Lifecycle Rules", e.response['Error']['Code'])
                
    except ClientError as e:
        results.add_fail("Audio Bucket", e.response['Error']['Code'])

# ============================================================
# 4. LAMBDA FUNCTIONS
# ============================================================
def test_lambda_functions():
    print("\n⚡ Testing Lambda Functions...")
    print("=" * 60)
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    expected_functions = [
        'meetingmind-get-upload-url',
        'meetingmind-process-meeting',
        'meetingmind-list-meetings',
        'meetingmind-get-meeting',
        'meetingmind-update-action',
        'meetingmind-get-debt-analytics',
        'meetingmind-get-all-actions',
        'meetingmind-check-duplicate',
        'meetingmind-create-team',
        'meetingmind-join-team',
        'meetingmind-get-team',
        'meetingmind-list-user-teams',
        'meetingmind-send-reminders',
        'meetingmind-daily-digest',
        'meetingmind-dlq-handler',
    ]
    
    for func_name in expected_functions:
        try:
            response = lambda_client.get_function(FunctionName=func_name)
            state = response['Configuration']['State']
            if state == 'Active':
                results.add_pass(f"Lambda: {func_name}")
            else:
                results.add_warning(f"Lambda: {func_name}", f"State: {state}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                results.add_fail(f"Lambda: {func_name}", "Not found")
            else:
                results.add_fail(f"Lambda: {func_name}", e.response['Error']['Code'])

# ============================================================
# 5. API GATEWAY
# ============================================================
def test_api_gateway():
    print("\n🌐 Testing API Gateway...")
    print("=" * 60)
    apigw = boto3.client('apigateway', region_name=REGION)
    
    try:
        # List REST APIs
        response = apigw.get_rest_apis()
        apis = response.get('items', [])
        
        meetingmind_api = None
        for api in apis:
            if 'meetingmind' in api['name'].lower():
                meetingmind_api = api
                break
        
        if meetingmind_api:
            results.add_pass(f"API Gateway: {meetingmind_api['name']}")
            api_id = meetingmind_api['id']
            
            # Check if deployed
            try:
                stages = apigw.get_stages(restApiId=api_id)
                if stages['item']:
                    results.add_pass(f"API Deployed (Stage: {stages['item'][0]['stageName']})")
                else:
                    results.add_warning("API Deployment", "No stages found")
            except:
                results.add_warning("API Deployment", "Cannot check stages")
        else:
            results.add_fail("API Gateway", "MeetingMind API not found")
            
    except Exception as e:
        results.add_fail("API Gateway", str(e))

# ============================================================
# 6. COGNITO USER POOL
# ============================================================
def test_cognito():
    print("\n👤 Testing Cognito User Pool...")
    print("=" * 60)
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    try:
        # List user pools
        response = cognito.list_user_pools(MaxResults=10)
        pools = response.get('UserPools', [])
        
        meetingmind_pool = None
        for pool in pools:
            if 'meetingmind' in pool['Name'].lower():
                meetingmind_pool = pool
                break
        
        if meetingmind_pool:
            results.add_pass(f"User Pool: {meetingmind_pool['Name']}")
            
            # Check user pool client
            try:
                clients = cognito.list_user_pool_clients(
                    UserPoolId=meetingmind_pool['Id'],
                    MaxResults=10
                )
                if clients['UserPoolClients']:
                    results.add_pass("User Pool Client Configured")
                else:
                    results.add_warning("User Pool Client", "No clients found")
            except:
                results.add_warning("User Pool Client", "Cannot check clients")
        else:
            results.add_fail("Cognito User Pool", "MeetingMind pool not found")
            
    except Exception as e:
        results.add_fail("Cognito User Pool", str(e))

# ============================================================
# 7. AWS SERVICES ACCESS
# ============================================================
def test_aws_services():
    print("\n🔧 Testing AWS Services Access...")
    print("=" * 60)
    
    # Test Transcribe
    try:
        transcribe = boto3.client('transcribe', region_name=REGION)
        transcribe.list_transcription_jobs(MaxResults=1)
        results.add_pass("Transcribe Access")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            results.add_fail("Transcribe Access", "IAM permissions missing")
        else:
            results.add_fail("Transcribe Access", e.response['Error']['Code'])
    
    # Test Bedrock
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=REGION)
        bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })
        )
        results.add_pass("Bedrock Claude Access")
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
            results.add_fail("Bedrock Claude Access", "Payment card not valid/propagated")
        elif 'AccessDeniedException' in e.response['Error']['Code']:
            results.add_fail("Bedrock Claude Access", "Model access not enabled")
        else:
            results.add_fail("Bedrock Claude Access", e.response['Error']['Code'])
    
    # Test Bedrock Embeddings
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=REGION)
        bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=json.dumps({"inputText": "test"})
        )
        results.add_pass("Bedrock Titan Embeddings Access")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            results.add_pass("Bedrock Titan Embeddings Access (throttled but accessible)")
        else:
            results.add_fail("Bedrock Titan Embeddings Access", e.response['Error']['Code'])
    
    # Test SES
    try:
        ses = boto3.client('ses', region_name=REGION)
        ses.get_send_quota()
        results.add_pass("SES Access")
    except ClientError as e:
        results.add_fail("SES Access", e.response['Error']['Code'])

# ============================================================
# 8. DATA INTEGRITY
# ============================================================
def test_data_integrity():
    print("\n🔍 Testing Data Integrity...")
    print("=" * 60)
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    
    # Check meetings table structure
    try:
        table = dynamodb.Table(MEETINGS_TABLE)
        response = table.scan(Limit=1)
        
        if response['Count'] == 0:
            results.add_warning("Meetings Data", "No meetings in database (clean state)")
        else:
            item = response['Items'][0]
            required_fields = ['userId', 'meetingId', 'status', 'createdAt']
            missing = [f for f in required_fields if f not in item]
            
            if missing:
                results.add_fail("Meeting Schema", f"Missing fields: {missing}")
            else:
                results.add_pass("Meeting Schema Valid")
                
    except Exception as e:
        results.add_fail("Data Integrity Check", str(e))

# ============================================================
# 9. FRONTEND CONFIGURATION
# ============================================================
def test_frontend_config():
    print("\n🎨 Testing Frontend Configuration...")
    print("=" * 60)
    
    # Check if frontend files exist
    frontend_files = [
        'frontend/package.json',
        'frontend/src/App.jsx',
        'frontend/src/utils/api.js',
        'frontend/src/utils/auth.js',
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            results.add_pass(f"Frontend File: {file_path}")
        else:
            results.add_fail(f"Frontend File: {file_path}", "Not found")
    
    # Check CloudFront distribution
    try:
        cf = boto3.client('cloudfront')
        response = cf.list_distributions()
        distributions = response.get('DistributionList', {}).get('Items', [])
        
        if distributions:
            results.add_pass(f"CloudFront Distribution Found ({len(distributions)} total)")
        else:
            results.add_warning("CloudFront Distribution", "No distributions found")
    except Exception as e:
        results.add_warning("CloudFront Check", str(e))

# ============================================================
# MAIN TEST RUNNER
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("MEETINGMIND COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_aws_credentials()
    test_dynamodb_tables()
    test_s3_bucket()
    test_lambda_functions()
    test_api_gateway()
    test_cognito()
    test_aws_services()
    test_data_integrity()
    test_frontend_config()
    
    # Print summary
    all_passed = results.summary()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is healthy!")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)
