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
    
    subject = "Welcome to MeetingMind — Your Account is Active"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {{ 
                font-family: 'DM Mono', 'Courier New', monospace; 
                background-color: #0c0c09; 
                margin: 0; 
                padding: 0; 
                -webkit-font-smoothing: antialiased;
            }}
            .email-container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: #0c0c09;
            }}
            .email-wrapper {{ 
                background-color: #141410; 
                border: 2px solid #2a2a20;
                border-radius: 8px;
                overflow: hidden;
                margin: 40px 20px;
            }}
            .header {{ 
                background: linear-gradient(135deg, #0f0f0c 0%, #141410 100%);
                padding: 40px 40px 36px 40px;
                border-bottom: 2px solid #c8f04a;
                position: relative;
                text-align: center;
            }}
            .header::after {{
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, #c8f04a 0%, transparent 100%);
            }}
            .logo-container {{
                display: flex;
                align-items: baseline;
                gap: 2px;
                justify-content: center;
                margin-bottom: 12px;
            }}
            .logo-meeting {{ 
                font-family: 'Playfair Display', serif;
                color: #c8f04a; 
                font-size: 32px; 
                font-weight: 900; 
                margin: 0;
                letter-spacing: -0.5px;
            }}
            .logo-mind {{
                font-family: 'Playfair Display', serif;
                color: #f0ece0;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: -0.3px;
            }}
            .header-title {{
                font-family: 'Playfair Display', serif;
                color: #f0ece0;
                font-size: 22px;
                font-weight: 700;
                margin: 0;
                letter-spacing: -0.3px;
            }}
            .content {{ 
                padding: 40px; 
                background-color: #141410;
            }}
            .greeting {{ 
                color: #f0ece0; 
                font-size: 14px; 
                font-weight: 400; 
                margin: 0 0 24px 0;
                line-height: 1.6;
                letter-spacing: 0.02em;
            }}
            .section-label {{ 
                color: #8a8a74; 
                font-size: 9px; 
                font-weight: 500;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                margin: 32px 0 16px 0;
            }}
            .success-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #1a1a0e 0%, #141410 100%);
                border: 1px solid #3a3a2e;
                border-left: 3px solid #c8f04a;
                border-radius: 6px;
                padding: 16px 20px;
                margin: 20px 0;
                text-align: center;
            }}
            .success-text {{
                color: #c8f04a;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }}
            .features-list {{
                background-color: #0f0f0c;
                border: 1px solid #2a2a20;
                border-radius: 6px;
                padding: 24px;
                margin: 24px 0;
            }}
            .feature-item {{
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 12px 0;
                border-bottom: 1px solid #1a1a14;
            }}
            .feature-item:last-child {{
                border-bottom: none;
            }}
            .feature-icon {{
                width: 6px;
                height: 6px;
                background-color: #c8f04a;
                border-radius: 50%;
                margin-top: 6px;
                flex-shrink: 0;
            }}
            .feature-text {{
                color: #a8a894;
                font-size: 13px;
                line-height: 1.6;
            }}
            .cta-section {{
                text-align: center;
                margin: 32px 0;
            }}
            .cta-button {{
                display: inline-block;
                background-color: #c8f04a;
                color: #0c0c09;
                padding: 16px 32px;
                text-decoration: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                transition: opacity 0.2s;
            }}
            .cta-button:hover {{
                opacity: 0.9;
            }}
            .cta-hint {{
                color: #6b7260;
                font-size: 11px;
                margin-top: 12px;
                letter-spacing: 0.03em;
            }}
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, #2a2a20 50%, transparent 100%);
                margin: 32px 0;
            }}
            .footer {{ 
                background-color: #0f0f0c; 
                padding: 28px 40px;
                border-top: 1px solid #2a2a20;
                text-align: center;
            }}
            .footer-brand {{ 
                color: #f0ece0; 
                font-size: 13px; 
                font-weight: 500;
                margin: 0 0 8px 0;
                letter-spacing: 0.05em;
            }}
            .footer-tagline {{
                color: #6b7260;
                font-size: 10px;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 0 0 16px 0;
            }}
            .footer-meta {{ 
                color: #555548; 
                font-size: 10px; 
                line-height: 1.6;
                margin: 4px 0;
                letter-spacing: 0.03em;
            }}
            .accent-dot {{
                display: inline-block;
                width: 4px;
                height: 4px;
                background-color: #c8f04a;
                border-radius: 50%;
                margin: 0 8px;
                vertical-align: middle;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-wrapper">
                <div class="header">
                    <div class="logo-container">
                        <span class="logo-meeting">Meeting</span>
                        <span class="logo-mind">Mind</span>
                    </div>
                    <h1 class="header-title">Your Account is Active</h1>
                </div>
                
                <div class="content">
                    <p class="greeting">Welcome to MeetingMind,</p>
                    <p class="greeting">Your account has been approved and you now have full access to the platform.</p>
                    
                    <div class="success-badge">
                        <div class="success-text">Account Status: Active</div>
                    </div>
                    
                    <div class="section-label">What You Can Do Now</div>
                    <div class="features-list">
                        <div class="feature-item">
                            <div class="feature-icon"></div>
                            <div class="feature-text">Upload meeting recordings and receive instant AI-powered summaries with speaker diarization</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon"></div>
                            <div class="feature-text">Track action items automatically with intelligent risk scoring and deadline monitoring</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon"></div>
                            <div class="feature-text">Monitor your team's Meeting Debt and identify patterns that impact productivity</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon"></div>
                            <div class="feature-text">Receive daily digests of pending tasks and overdue action items</div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon"></div>
                            <div class="feature-text">Collaborate with your team using shared workspaces and real-time updates</div>
                        </div>
                    </div>
                    
                    <div class="cta-section">
                        <a href="{FRONTEND_URL}" class="cta-button">Access Your Dashboard</a>
                        <p class="cta-hint">Sign in with your registered email address</p>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <p style="color: #6b7260; font-size: 11px; line-height: 1.6; margin: 0; text-align: center;">
                        Need help getting started?<span class="accent-dot"></span>Visit our documentation or contact support
                    </p>
                </div>
                
                <div class="footer">
                    <p class="footer-brand">MeetingMind</p>
                    <p class="footer-tagline">Transform Meetings Into Action</p>
                    <p class="footer-meta">Powered by AWS<span class="accent-dot"></span>Region: ap-south-1</p>
                    <p class="footer-meta" style="margin-top: 12px;">© 2026 MeetingMind. All rights reserved.</p>
                </div>
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
