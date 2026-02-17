import boto3
import os

cognito = boto3.client('cognito-idp')
USER_POOL_ID = os.environ['USER_POOL_ID']

def lambda_handler(event, context):
    """
    Cognito Post-Confirmation trigger
    Disables user immediately after signup - they must be manually approved
    """
    username = event['userName']
    
    # Disable the user immediately after signup
    cognito.admin_disable_user(
        UserPoolId=USER_POOL_ID,
        Username=username
    )
    
    print(f"User {username} created and disabled - awaiting manual approval")
    
    return event
