#!/usr/bin/env python3
"""
Setup CloudWatch Alarms for MeetingMind
Monitors Lambda errors, API Gateway 5xx, and DynamoDB throttling
"""
import boto3

REGION = 'ap-south-1'
SNS_TOPIC_ARN = f'arn:aws:sns:{REGION}:707411439284:meetingmind-reminders'

# Critical Lambda functions to monitor
LAMBDA_FUNCTIONS = [
    'meetingmind-process-meeting',
    'meetingmind-get-upload-url',
    'meetingmind-list-meetings',
    'meetingmind-get-all-actions'
]

# DynamoDB tables to monitor
DYNAMODB_TABLES = [
    'meetingmind-meetings',
    'meetingmind-teams'
]

# API Gateway ID
API_GATEWAY_ID = '25g9jf8sqa'

def create_lambda_error_alarm(function_name):
    """Create alarm for Lambda function errors"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    alarm_name = f'meetingmind-{function_name.replace("meetingmind-", "")}-errors'
    
    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f'Alert when {function_name} has errors',
            ActionsEnabled=True,
            AlarmActions=[SNS_TOPIC_ARN],
            MetricName='Errors',
            Namespace='AWS/Lambda',
            Statistic='Sum',
            Dimensions=[
                {'Name': 'FunctionName', 'Value': function_name}
            ],
            Period=300,  # 5 minutes
            EvaluationPeriods=1,
            Threshold=5.0,  # Alert if 5+ errors in 5 minutes
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
        
        print(f"✅ Created alarm: {alarm_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alarm {alarm_name}: {str(e)}")
        return False

def create_lambda_throttle_alarm(function_name):
    """Create alarm for Lambda function throttles"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    alarm_name = f'meetingmind-{function_name.replace("meetingmind-", "")}-throttles'
    
    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f'Alert when {function_name} is throttled',
            ActionsEnabled=True,
            AlarmActions=[SNS_TOPIC_ARN],
            MetricName='Throttles',
            Namespace='AWS/Lambda',
            Statistic='Sum',
            Dimensions=[
                {'Name': 'FunctionName', 'Value': function_name}
            ],
            Period=300,  # 5 minutes
            EvaluationPeriods=1,
            Threshold=10.0,  # Alert if 10+ throttles in 5 minutes
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
        
        print(f"✅ Created alarm: {alarm_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alarm {alarm_name}: {str(e)}")
        return False

def create_api_gateway_5xx_alarm():
    """Create alarm for API Gateway 5xx errors"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    alarm_name = 'meetingmind-api-5xx-errors'
    
    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription='Alert when API Gateway has 5xx errors',
            ActionsEnabled=True,
            AlarmActions=[SNS_TOPIC_ARN],
            MetricName='5XXError',
            Namespace='AWS/ApiGateway',
            Statistic='Sum',
            Dimensions=[
                {'Name': 'ApiName', 'Value': 'meetingmind-stack'}
            ],
            Period=300,  # 5 minutes
            EvaluationPeriods=1,
            Threshold=10.0,  # Alert if 10+ 5xx errors in 5 minutes
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
        
        print(f"✅ Created alarm: {alarm_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alarm {alarm_name}: {str(e)}")
        return False

def create_api_gateway_latency_alarm():
    """Create alarm for API Gateway high latency"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    alarm_name = 'meetingmind-api-high-latency'
    
    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription='Alert when API Gateway latency is high',
            ActionsEnabled=True,
            AlarmActions=[SNS_TOPIC_ARN],
            MetricName='Latency',
            Namespace='AWS/ApiGateway',
            Statistic='Average',
            Dimensions=[
                {'Name': 'ApiName', 'Value': 'meetingmind-stack'}
            ],
            Period=300,  # 5 minutes
            EvaluationPeriods=2,
            Threshold=5000.0,  # Alert if avg latency > 5 seconds
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
        
        print(f"✅ Created alarm: {alarm_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alarm {alarm_name}: {str(e)}")
        return False

def create_dynamodb_throttle_alarm(table_name):
    """Create alarm for DynamoDB throttling"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    alarm_name = f'meetingmind-{table_name.replace("meetingmind-", "")}-throttles'
    
    try:
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f'Alert when {table_name} is throttled',
            ActionsEnabled=True,
            AlarmActions=[SNS_TOPIC_ARN],
            MetricName='UserErrors',
            Namespace='AWS/DynamoDB',
            Statistic='Sum',
            Dimensions=[
                {'Name': 'TableName', 'Value': table_name}
            ],
            Period=300,  # 5 minutes
            EvaluationPeriods=1,
            Threshold=10.0,  # Alert if 10+ throttles in 5 minutes
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
        
        print(f"✅ Created alarm: {alarm_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating alarm {alarm_name}: {str(e)}")
        return False

def list_existing_alarms():
    """List existing CloudWatch alarms"""
    cw = boto3.client('cloudwatch', region_name=REGION)
    
    try:
        response = cw.describe_alarms(AlarmNamePrefix='meetingmind')
        alarms = response.get('MetricAlarms', [])
        
        if alarms:
            print(f"\nExisting Alarms ({len(alarms)}):")
            print("-" * 60)
            for alarm in alarms:
                state = alarm['StateValue']
                icon = "✅" if state == 'OK' else "⚠️" if state == 'INSUFFICIENT_DATA' else "❌"
                print(f"{icon} {alarm['AlarmName']}: {state}")
        else:
            print("\n⚠️  No existing alarms found")
            
    except Exception as e:
        print(f"❌ Error listing alarms: {str(e)}")

if __name__ == '__main__':
    print("="*60)
    print("SETUP CLOUDWATCH ALARMS")
    print("="*60)
    print(f"Region: {REGION}")
    print(f"SNS Topic: {SNS_TOPIC_ARN}")
    print("="*60)
    
    # Check existing alarms
    list_existing_alarms()
    
    # Create alarms
    print("\nCreating Alarms:")
    print("-" * 60)
    
    results = []
    
    # Lambda error alarms
    print("\n1. Lambda Error Alarms:")
    for func in LAMBDA_FUNCTIONS:
        result = create_lambda_error_alarm(func)
        results.append(result)
    
    # Lambda throttle alarms
    print("\n2. Lambda Throttle Alarms:")
    for func in LAMBDA_FUNCTIONS:
        result = create_lambda_throttle_alarm(func)
        results.append(result)
    
    # API Gateway alarms
    print("\n3. API Gateway Alarms:")
    results.append(create_api_gateway_5xx_alarm())
    results.append(create_api_gateway_latency_alarm())
    
    # DynamoDB alarms
    print("\n4. DynamoDB Throttle Alarms:")
    for table in DYNAMODB_TABLES:
        result = create_dynamodb_throttle_alarm(table)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"✅ SUCCESS: Created {success_count}/{total_count} alarms")
        print("\n💡 Monitoring:")
        print("   - Lambda errors and throttles")
        print("   - API Gateway 5xx errors and latency")
        print("   - DynamoDB throttling")
        print(f"   - Notifications sent to: {SNS_TOPIC_ARN}")
    else:
        print(f"⚠️  PARTIAL: Created {success_count}/{total_count} alarms")
    
    print("="*60)
    
    # List final state
    list_existing_alarms()
