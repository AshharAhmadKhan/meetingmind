#!/usr/bin/env python3
"""
Comprehensive AWS Service Access Checker
Tests all services used by MeetingMind to verify account permissions
"""
import boto3
import json
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime

REGION = 'ap-south-1'
ACCOUNT_ID = '707411439284'

# Disable retries for Bedrock to prevent marketplace triggers
bedrock_config = Config(retries={'max_attempts': 0, 'mode': 'standard'})

def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_service(name, status, details=""):
    """Print service status"""
    icon = "✅" if status == "ACCESSIBLE" else "⚠️" if status == "PARTIAL" else "❌"
    print(f"{icon} {name:30} {status:15} {details}")

def check_sts():
    """Check AWS STS (Security Token Service) - validates credentials"""
    print_header("1. AWS CREDENTIALS & IDENTITY")
    try:
        sts = boto3.client('sts', region_name=REGION)
        identity = sts.get_caller_identity()
        print(f"✅ Account ID: {identity['Account']}")
        print(f"✅ User ARN: {identity['Arn']}")
        print(f"✅ User ID: {identity['UserId']}")
        return True
    except Exception as e:
        print(f"❌ STS Error: {str(e)}")
        return False

def check_s3():
    """Check S3 access"""
    print_header("2. S3 (STORAGE)")
    s3 = boto3.client('s3', region_name=REGION)
    
    buckets_to_check = [
        'meetingmind-audio-707411439284',
        'meetingmind-frontend-707411439284'
    ]
    
    results = []
    for bucket in buckets_to_check:
        try:
            # Check if bucket exists and is accessible
            s3.head_bucket(Bucket=bucket)
            
            # Check bucket location
            location = s3.get_bucket_location(Bucket=bucket)
            region = location['LocationConstraint'] or 'us-east-1'
            
            # Check encryption
            try:
                encryption = s3.get_bucket_encryption(Bucket=bucket)
                enc_status = "Encrypted"
            except ClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    enc_status = "⚠️ Not Encrypted"
                else:
                    enc_status = "Unknown"
            
            # Check versioning
            versioning = s3.get_bucket_versioning(Bucket=bucket)
            ver_status = versioning.get('Status', 'Disabled')
            
            print_service(bucket, "ACCESSIBLE", f"Region: {region}, {enc_status}, Versioning: {ver_status}")
            results.append(True)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print_service(bucket, "ERROR", f"{error_code}")
            results.append(False)
    
    return all(results)

def check_dynamodb():
    """Check DynamoDB access"""
    print_header("3. DYNAMODB (DATABASE)")
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    tables_to_check = [
        'meetingmind-meetings',
        'meetingmind-teams'
    ]
    
    results = []
    for table_name in tables_to_check:
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table = response['Table']
            
            status = table['TableStatus']
            item_count = table['ItemCount']
            billing = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
            
            # Check GSIs
            gsi_count = len(table.get('GlobalSecondaryIndexes', []))
            
            print_service(
                table_name, 
                "ACCESSIBLE", 
                f"Status: {status}, Items: {item_count}, Billing: {billing}, GSIs: {gsi_count}"
            )
            results.append(True)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print_service(table_name, "ERROR", f"{error_code}")
            results.append(False)
    
    return all(results)

def check_cognito():
    """Check Cognito access"""
    print_header("4. COGNITO (AUTHENTICATION)")
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    user_pool_id = 'ap-south-1_mkFJawjMp'
    
    try:
        response = cognito.describe_user_pool(UserPoolId=user_pool_id)
        pool = response['UserPool']
        
        status = pool.get('Status', 'Active')
        print_service(
            "User Pool", 
            "ACCESSIBLE", 
            f"Name: {pool['Name']}, ID: {pool['Id']}"
        )
        
        # Check user pool client
        client_id = '150n899gkc651g6e0p7hacguac'
        try:
            client_response = cognito.describe_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id
            )
            print_service("User Pool Client", "ACCESSIBLE", f"Client ID: {client_id}")
        except Exception as e:
            print_service("User Pool Client", "ERROR", str(e))
        
        # Get user count
        try:
            users = cognito.list_users(UserPoolId=user_pool_id, Limit=1)
            print(f"   Users can be listed (sample check passed)")
        except Exception as e:
            print(f"   ⚠️ Cannot list users: {str(e)}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("User Pool", "ERROR", f"{error_code}")
        return False

def check_lambda():
    """Check Lambda access"""
    print_header("5. LAMBDA (SERVERLESS FUNCTIONS)")
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Key functions to check
    functions_to_check = [
        'meetingmind-process-meeting',
        'meetingmind-get-upload-url',
        'meetingmind-list-meetings',
        'meetingmind-get-all-actions'
    ]
    
    results = []
    for func_name in functions_to_check:
        try:
            response = lambda_client.get_function(FunctionName=func_name)
            config = response['Configuration']
            
            runtime = config['Runtime']
            memory = config['MemorySize']
            timeout = config['Timeout']
            
            print_service(
                func_name.replace('meetingmind-', ''), 
                "ACCESSIBLE", 
                f"{runtime}, {memory}MB, {timeout}s timeout"
            )
            results.append(True)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print_service(func_name.replace('meetingmind-', ''), "ERROR", f"{error_code}")
            results.append(False)
    
    return all(results)

def check_api_gateway():
    """Check API Gateway access"""
    print_header("6. API GATEWAY (REST API)")
    apigw = boto3.client('apigateway', region_name=REGION)
    
    api_id = '25g9jf8sqa'
    
    try:
        response = apigw.get_rest_api(restApiId=api_id)
        
        print_service(
            "REST API", 
            "ACCESSIBLE", 
            f"Name: {response['name']}, Endpoint: {response.get('endpointConfiguration', {}).get('types', ['EDGE'])[0]}"
        )
        
        # Check stages
        try:
            stages = apigw.get_stages(restApiId=api_id)
            stage_names = [s['stageName'] for s in stages['item']]
            print(f"   Stages: {', '.join(stage_names)}")
        except Exception as e:
            print(f"   ⚠️ Cannot list stages: {str(e)}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("REST API", "ERROR", f"{error_code}")
        return False

def check_transcribe():
    """Check Amazon Transcribe access"""
    print_header("7. AMAZON TRANSCRIBE (SPEECH-TO-TEXT)")
    transcribe = boto3.client('transcribe', region_name=REGION)
    
    try:
        # List transcription jobs (safe operation)
        response = transcribe.list_transcription_jobs(MaxResults=5)
        
        job_count = len(response.get('TranscriptionJobSummaries', []))
        
        print_service(
            "Transcribe Service", 
            "ACCESSIBLE", 
            f"Recent jobs: {job_count}"
        )
        
        # Check if we can get vocabulary lists (another safe operation)
        try:
            vocabs = transcribe.list_vocabularies(MaxResults=1)
            print(f"   ✅ Can list vocabularies")
        except Exception as e:
            print(f"   ⚠️ Cannot list vocabularies: {str(e)}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print_service("Transcribe Service", "ERROR", f"{error_code}: {error_msg}")
        return False

def check_bedrock():
    """Check Amazon Bedrock access"""
    print_header("8. AMAZON BEDROCK (AI MODELS)")
    bedrock = boto3.client('bedrock-runtime', region_name=REGION, config=bedrock_config)
    
    models_to_test = [
        ('anthropic.claude-3-haiku-20240307-v1:0', 'Claude 3 Haiku', 'text'),
        ('amazon.nova-lite-v1:0', 'Nova Lite', 'text'),
        ('amazon.nova-micro-v1:0', 'Nova Micro', 'text'),
        ('amazon.titan-embed-text-v2:0', 'Titan Embeddings v2', 'embedding'),
    ]
    
    accessible_count = 0
    total_count = len(models_to_test)
    
    for model_id, model_name, model_type in models_to_test:
        try:
            if model_type == 'embedding':
                body = json.dumps({"inputText": "test"})
                response = bedrock.invoke_model(modelId=model_id, body=body)
                result = json.loads(response['body'].read())
                
                if 'embedding' in result:
                    print_service(model_name, "ACCESSIBLE", f"Embedding dimension: {len(result['embedding'])}")
                    accessible_count += 1
                else:
                    print_service(model_name, "PARTIAL", "Unexpected response format")
            
            elif 'anthropic' in model_id:
                body = json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'Hi'}]
                })
                response = bedrock.invoke_model(modelId=model_id, body=body)
                result = json.loads(response['body'].read())
                
                if 'content' in result:
                    print_service(model_name, "ACCESSIBLE", "Text generation working")
                    accessible_count += 1
                else:
                    print_service(model_name, "PARTIAL", "Unexpected response format")
            
            else:  # Nova models
                body = json.dumps({
                    'messages': [{'role': 'user', 'content': [{'text': 'Hi'}]}],
                    'inferenceConfig': {'maxTokens': 10, 'temperature': 0.1}
                })
                response = bedrock.invoke_model(modelId=model_id, body=body)
                result = json.loads(response['body'].read())
                
                if 'output' in result:
                    print_service(model_name, "ACCESSIBLE", "Text generation working")
                    accessible_count += 1
                else:
                    print_service(model_name, "PARTIAL", "Unexpected response format")
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if 'INVALID_PAYMENT_INSTRUMENT' in error_msg:
                print_service(model_name, "BLOCKED", "Payment validation pending")
            elif 'AccessDeniedException' in error_code:
                print_service(model_name, "BLOCKED", "Model access not enabled")
            elif 'ThrottlingException' in error_code:
                print_service(model_name, "ACCESSIBLE", "⚠️ Rate limited (but accessible)")
                accessible_count += 1
            elif 'ValidationException' in error_code:
                if 'inference profile' in error_msg.lower():
                    print_service(model_name, "BLOCKED", "Needs inference profile")
                else:
                    print_service(model_name, "ERROR", f"Validation: {error_msg[:50]}")
            else:
                print_service(model_name, "ERROR", f"{error_code}")
        
        except Exception as e:
            print_service(model_name, "ERROR", f"Unexpected: {str(e)[:50]}")
    
    print(f"\n   Bedrock Status: {accessible_count}/{total_count} models accessible")
    return accessible_count > 0

def check_ses():
    """Check SES (Simple Email Service) access"""
    print_header("9. SES (EMAIL SERVICE)")
    ses = boto3.client('ses', region_name=REGION)
    
    from_email = 'thecyberprinciples@gmail.com'
    
    try:
        # Check email verification status
        response = ses.get_identity_verification_attributes(Identities=[from_email])
        
        if from_email in response['VerificationAttributes']:
            status = response['VerificationAttributes'][from_email]['VerificationStatus']
            print_service("Email Identity", "ACCESSIBLE", f"{from_email} - Status: {status}")
        else:
            print_service("Email Identity", "ERROR", f"{from_email} not found")
        
        # Check sending quota
        try:
            quota = ses.get_send_quota()
            print(f"   Daily Quota: {quota['Max24HourSend']:.0f}, Sent: {quota['SentLast24Hours']:.0f}, Rate: {quota['MaxSendRate']:.0f}/sec")
        except Exception as e:
            print(f"   ⚠️ Cannot get quota: {str(e)}")
        
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("SES Service", "ERROR", f"{error_code}")
        return False

def check_sns():
    """Check SNS (Simple Notification Service) access"""
    print_header("10. SNS (NOTIFICATIONS)")
    sns = boto3.client('sns', region_name=REGION)
    
    topic_arn = f'arn:aws:sns:{REGION}:{ACCOUNT_ID}:meetingmind-reminders'
    
    try:
        response = sns.get_topic_attributes(TopicArn=topic_arn)
        attrs = response['Attributes']
        
        sub_count = attrs.get('SubscriptionsConfirmed', '0')
        
        print_service(
            "SNS Topic", 
            "ACCESSIBLE", 
            f"Subscriptions: {sub_count}"
        )
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("SNS Topic", "ERROR", f"{error_code}")
        return False

def check_sqs():
    """Check SQS (Simple Queue Service) access"""
    print_header("11. SQS (MESSAGE QUEUES)")
    sqs = boto3.client('sqs', region_name=REGION)
    
    try:
        # List queues
        response = sqs.list_queues(QueueNamePrefix='meetingmind')
        
        if 'QueueUrls' in response:
            for queue_url in response['QueueUrls']:
                queue_name = queue_url.split('/')[-1]
                
                # Get queue attributes
                attrs = sqs.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
                )
                
                msg_count = attrs['Attributes'].get('ApproximateNumberOfMessages', '0')
                in_flight = attrs['Attributes'].get('ApproximateNumberOfMessagesNotVisible', '0')
                
                print_service(
                    queue_name, 
                    "ACCESSIBLE", 
                    f"Messages: {msg_count}, In-flight: {in_flight}"
                )
            return True
        else:
            print_service("SQS Queues", "ERROR", "No queues found")
            return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("SQS Service", "ERROR", f"{error_code}")
        return False

def check_cloudfront():
    """Check CloudFront access"""
    print_header("12. CLOUDFRONT (CDN)")
    cf = boto3.client('cloudfront')
    
    distribution_id = 'E3CAAI97MXY83V'
    
    try:
        response = cf.get_distribution(Id=distribution_id)
        dist = response['Distribution']
        
        status = dist['Status']
        domain = dist['DomainName']
        enabled = dist['DistributionConfig']['Enabled']
        
        print_service(
            "Distribution", 
            "ACCESSIBLE", 
            f"Status: {status}, Enabled: {enabled}"
        )
        print(f"   Domain: {domain}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("Distribution", "ERROR", f"{error_code}")
        return False

def check_eventbridge():
    """Check EventBridge access"""
    print_header("13. EVENTBRIDGE (SCHEDULED EVENTS)")
    events = boto3.client('events', region_name=REGION)
    
    try:
        # List rules with meetingmind prefix
        response = events.list_rules(NamePrefix='meetingmind')
        
        if 'Rules' in response and len(response['Rules']) > 0:
            for rule in response['Rules']:
                state = rule['State']
                schedule = rule.get('ScheduleExpression', 'N/A')
                
                print_service(
                    rule['Name'].replace('meetingmind-', ''), 
                    "ACCESSIBLE", 
                    f"State: {state}, Schedule: {schedule}"
                )
            return True
        else:
            print_service("EventBridge Rules", "ERROR", "No rules found")
            return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("EventBridge", "ERROR", f"{error_code}")
        return False

def check_cloudwatch():
    """Check CloudWatch Logs access"""
    print_header("14. CLOUDWATCH (LOGGING & MONITORING)")
    logs = boto3.client('logs', region_name=REGION)
    
    try:
        # List log groups for Lambda functions
        response = logs.describe_log_groups(logGroupNamePrefix='/aws/lambda/meetingmind', limit=5)
        
        if 'logGroups' in response:
            log_count = len(response['logGroups'])
            print_service(
                "CloudWatch Logs", 
                "ACCESSIBLE", 
                f"Log groups found: {log_count}"
            )
            
            # Check for alarms
            cw = boto3.client('cloudwatch', region_name=REGION)
            try:
                alarms = cw.describe_alarms(AlarmNamePrefix='meetingmind', MaxRecords=10)
                alarm_count = len(alarms['MetricAlarms'])
                if alarm_count > 0:
                    print(f"   ✅ CloudWatch Alarms: {alarm_count} configured")
                else:
                    print(f"   ⚠️ No CloudWatch Alarms configured (recommended)")
            except Exception as e:
                print(f"   ⚠️ Cannot check alarms: {str(e)}")
            
            return True
        else:
            print_service("CloudWatch Logs", "ERROR", "No log groups found")
            return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print_service("CloudWatch", "ERROR", f"{error_code}")
        return False

def generate_summary(results):
    """Generate final summary"""
    print_header("SUMMARY")
    
    total = len(results)
    accessible = sum(1 for r in results.values() if r)
    
    print(f"\n✅ Accessible Services: {accessible}/{total}")
    print(f"❌ Blocked/Error Services: {total - accessible}/{total}")
    
    print("\n📊 Service Status:")
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {service}")
    
    print("\n" + "="*70)
    
    if accessible == total:
        print("🎉 ALL SERVICES ACCESSIBLE!")
        print("✅ Your AWS account has full access to all MeetingMind services")
    elif accessible >= total * 0.7:
        print("⚠️  MOSTLY ACCESSIBLE")
        print(f"✅ {accessible}/{total} services working")
        print("⏳ Some services may need configuration or permissions")
    else:
        print("❌ LIMITED ACCESS")
        print(f"⚠️  Only {accessible}/{total} services accessible")
        print("💡 Check IAM permissions and service configurations")
    
    print("="*70)

if __name__ == '__main__':
    print("="*70)
    print("  MEETINGMIND - COMPREHENSIVE AWS ACCESS CHECK")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Region: {REGION}")
    print(f"  Account: {ACCOUNT_ID}")
    print("="*70)
    
    results = {}
    
    # Run all checks
    results['STS (Credentials)'] = check_sts()
    results['S3 (Storage)'] = check_s3()
    results['DynamoDB (Database)'] = check_dynamodb()
    results['Cognito (Auth)'] = check_cognito()
    results['Lambda (Functions)'] = check_lambda()
    results['API Gateway'] = check_api_gateway()
    results['Transcribe'] = check_transcribe()
    results['Bedrock (AI)'] = check_bedrock()
    results['SES (Email)'] = check_ses()
    results['SNS (Notifications)'] = check_sns()
    results['SQS (Queues)'] = check_sqs()
    results['CloudFront (CDN)'] = check_cloudfront()
    results['EventBridge (Cron)'] = check_eventbridge()
    results['CloudWatch (Logs)'] = check_cloudwatch()
    
    # Generate summary
    generate_summary(results)
