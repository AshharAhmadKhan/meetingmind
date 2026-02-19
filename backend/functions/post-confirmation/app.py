import boto3
import os
import json
from decimal import Decimal

cognito = boto3.client('cognito-idp')
ses = boto3.client('ses')
USER_POOL_ID = os.environ['USER_POOL_ID']
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'itzashhar@gmail.com')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'thecyberprinciples@gmail.com')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Cognito Post-Confirmation trigger
    Disables user immediately after signup - they must be manually approved
    Sends notification email to admin
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    username = event['userName']
    user_email = event['request']['userAttributes'].get('email', 'unknown')
    
    # Disable the user immediately after signup
    cognito.admin_disable_user(
        UserPoolId=USER_POOL_ID,
        Username=username
    )
    
    print(f"User {username} ({user_email}) created and disabled - awaiting manual approval")
    
    # Send notification email to admin
    try:
        send_admin_notification(user_email)
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    return event


def send_admin_notification(user_email):
    """Send email to admin when new user signs up"""
    
    subject = f"🔔 New MeetingMind Signup: {user_email}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: #0c0c09; color: #c8f04a; padding: 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 24px; }}
            .content h2 {{ color: #333; font-size: 18px; margin-bottom: 16px; }}
            .content p {{ color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 16px; }}
            .email-box {{ background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 4px; padding: 12px; font-family: monospace; font-size: 14px; color: #333; margin: 16px 0; }}
            .command-box {{ background: #0c0c09; color: #c8f04a; border-radius: 4px; padding: 12px; font-family: monospace; font-size: 13px; margin: 16px 0; overflow-x: auto; }}
            .steps {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; }}
            .steps ol {{ margin: 8px 0; padding-left: 20px; }}
            .steps li {{ color: #1e40af; margin: 8px 0; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 New User Signup</h1>
            </div>
            
            <div class="content">
                <h2>Someone just signed up for MeetingMind!</h2>
                
                <p><strong>Email:</strong></p>
                <div class="email-box">{user_email}</div>
                
                <div class="steps">
                    <strong>To approve this user:</strong>
                    <ol>
                        <li>Open your terminal</li>
                        <li>Run the approval command below</li>
                        <li>User will receive verification email from SES</li>
                        <li>User clicks verification link</li>
                        <li>User receives welcome email and can log in</li>
                    </ol>
                </div>
                
                <p><strong>Approval Command:</strong></p>
                <div class="command-box">python scripts/approve-user.py {user_email}</div>
                
                <p style="margin-top: 24px; font-size: 12px; color: #999;">
                    This usually takes 2-3 minutes. The user is expecting an email notification when their account is ready.
                </p>
            </div>
            
            <div class="footer">
                <p>MeetingMind Admin Notification</p>
                <p>User is waiting for approval</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    ses.send_email(
        Source=SES_FROM_EMAIL,
        Destination={'ToAddresses': [ADMIN_EMAIL]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': html_body}}
        }
    )
    
    print(f"Admin notification sent to {ADMIN_EMAIL}")
