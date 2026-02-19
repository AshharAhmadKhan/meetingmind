import boto3
import os
import json
from decimal import Decimal

ses = boto3.client('ses')
SES_FROM_EMAIL = os.environ['SES_FROM_EMAIL']
FRONTEND_URL = os.environ['FRONTEND_URL']

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
    Send welcome email when user is approved
    Triggered manually via CLI or API
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    email = event.get('email')
    
    if not email:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Email required'}, default=decimal_to_float)
        }
    
    subject = "🎉 Your MeetingMind account is approved!"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: #0c0c09; color: #c8f04a; padding: 32px 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ padding: 32px 24px; }}
            .content h2 {{ color: #333; font-size: 20px; margin-bottom: 16px; }}
            .content p {{ color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 16px; }}
            .btn {{ display: inline-block; background: #c8f04a; color: #0c0c09; padding: 14px 28px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 16px; }}
            .footer {{ background: #f9f9f9; padding: 20px 24px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to MeetingMind!</h1>
            </div>
            
            <div class="content">
                <h2>Your account is approved</h2>
                <p>Great news! Your MeetingMind account has been approved and is now active.</p>
                
                <p>You can now:</p>
                <ul style="color: #666; font-size: 14px; line-height: 1.8;">
                    <li>Upload meeting recordings and get instant AI summaries</li>
                    <li>Track action items with automatic risk scoring</li>
                    <li>Monitor your team's Meeting Debt</li>
                    <li>Receive daily digests of pending tasks</li>
                </ul>
                
                <p>Click below to sign in and start using MeetingMind:</p>
                
                <a href="{FRONTEND_URL}" class="btn">Sign In Now →</a>
            </div>
            
            <div class="footer">
                <p>You're receiving this because you registered for MeetingMind.</p>
                <p>Powered by AWS Bedrock · Running on ap-south-1</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        print(f"Welcome email sent to {email}")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': f'Welcome email sent to {email}'}, default=decimal_to_float)
        }
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)}, default=decimal_to_float)
        }
