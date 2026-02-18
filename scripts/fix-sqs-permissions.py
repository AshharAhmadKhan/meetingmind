#!/usr/bin/env python3
"""
Fix SQS Permissions for meetingmind-dev IAM user
Adds necessary SQS permissions to access processing queues
"""
import boto3
import json

REGION = 'ap-south-1'
IAM_USER = 'meetingmind-dev'
ACCOUNT_ID = '707411439284'

def get_current_policies():
    """Get current inline policies for the user"""
    iam = boto3.client('iam')
    
    try:
        response = iam.list_user_policies(UserName=IAM_USER)
        return response.get('PolicyNames', [])
    except Exception as e:
        print(f"❌ Error listing policies: {str(e)}")
        return []

def add_sqs_policy():
    """Add SQS permissions to IAM user"""
    iam = boto3.client('iam')
    
    policy_name = 'MeetingMindSQSAccess'
    
    # SQS policy document
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "SQSQueueAccess",
                "Effect": "Allow",
                "Action": [
                    "sqs:GetQueueUrl",
                    "sqs:GetQueueAttributes",
                    "sqs:SetQueueAttributes",
                    "sqs:ListQueues",
                    "sqs:ListQueueTags",
                    "sqs:SendMessage",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:ChangeMessageVisibility",
                    "sqs:PurgeQueue"
                ],
                "Resource": [
                    f"arn:aws:sqs:{REGION}:{ACCOUNT_ID}:meetingmind-*"
                ]
            },
            {
                "Sid": "SQSListAll",
                "Effect": "Allow",
                "Action": [
                    "sqs:ListQueues"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Check if policy already exists
        existing_policies = get_current_policies()
        
        if policy_name in existing_policies:
            print(f"⚠️  Policy '{policy_name}' already exists. Updating...")
            # Delete old policy
            iam.delete_user_policy(UserName=IAM_USER, PolicyName=policy_name)
        
        # Add new policy
        iam.put_user_policy(
            UserName=IAM_USER,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"✅ Successfully added SQS permissions to user '{IAM_USER}'")
        print(f"   Policy Name: {policy_name}")
        print(f"   Permissions: SQS queue operations for meetingmind-* queues")
        return True
        
    except Exception as e:
        print(f"❌ Error adding SQS policy: {str(e)}")
        return False

def verify_sqs_access():
    """Verify SQS access works"""
    sqs = boto3.client('sqs', region_name=REGION)
    
    try:
        response = sqs.list_queues(QueueNamePrefix='meetingmind')
        
        if 'QueueUrls' in response:
            print(f"\n✅ SQS Access Verified!")
            print(f"   Found {len(response['QueueUrls'])} queue(s):")
            for url in response['QueueUrls']:
                queue_name = url.split('/')[-1]
                print(f"   - {queue_name}")
            return True
        else:
            print(f"\n⚠️  No queues found (but access works)")
            return True
            
    except Exception as e:
        print(f"\n❌ SQS access still blocked: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("FIX SQS PERMISSIONS")
    print("="*60)
    print(f"IAM User: {IAM_USER}")
    print(f"Region: {REGION}")
    print(f"Account: {ACCOUNT_ID}")
    print("="*60)
    
    # Add SQS policy
    if add_sqs_policy():
        # Wait a moment for IAM to propagate
        import time
        print("\n⏳ Waiting 3 seconds for IAM propagation...")
        time.sleep(3)
        
        # Verify access
        verify_sqs_access()
    
    print("\n" + "="*60)
