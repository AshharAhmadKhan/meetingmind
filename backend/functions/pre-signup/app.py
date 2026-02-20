import json
import boto3
import os
from decimal import Decimal

ses = boto3.client('ses')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'thecyberprinciples@gmail.com')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'noreply@meetingmind.app')

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


def send_admin_notification(user_email, user_name=None):
    """Send notification to admin about new user signup"""
    try:
        subject = "New User Registration — MeetingMind"
        
        display_name = user_name if user_name else user_email
        
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
                    padding: 32px 40px;
                    border-bottom: 2px solid #c8f04a;
                    position: relative;
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
                }}
                .logo-meeting {{ 
                    font-family: 'Playfair Display', serif;
                    color: #c8f04a; 
                    font-size: 28px; 
                    font-weight: 900; 
                    margin: 0;
                    letter-spacing: -0.5px;
                }}
                .logo-mind {{
                    font-family: 'Playfair Display', serif;
                    color: #f0ece0;
                    font-size: 24px;
                    font-weight: 700;
                    letter-spacing: -0.3px;
                }}
                .header-subtitle {{
                    color: #8a8a74;
                    font-size: 10px;
                    letter-spacing: 0.15em;
                    text-transform: uppercase;
                    margin-top: 8px;
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
                .info-card {{ 
                    background-color: #0f0f0c; 
                    border: 1px solid #2a2a20;
                    border-left: 3px solid #c8f04a;
                    border-radius: 6px;
                    padding: 24px;
                    margin: 16px 0;
                }}
                .info-row {{ 
                    display: flex;
                    padding: 10px 0;
                    border-bottom: 1px solid #1a1a14;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{ 
                    color: #6b7260; 
                    font-size: 12px; 
                    font-weight: 500;
                    width: 140px;
                    flex-shrink: 0;
                    letter-spacing: 0.03em;
                }}
                .info-value {{ 
                    color: #f0ece0; 
                    font-size: 12px;
                    font-weight: 400;
                    word-break: break-word;
                }}
                .status-badge {{
                    display: inline-block;
                    background-color: #1a1a0e;
                    border: 1px solid #3a3a1e;
                    border-radius: 4px;
                    padding: 4px 10px;
                    color: #c8f04a;
                    font-size: 11px;
                    font-weight: 500;
                    letter-spacing: 0.05em;
                }}
                .action-box {{
                    background: linear-gradient(135deg, #1a1a0e 0%, #141410 100%);
                    border: 1px solid #3a3a2e;
                    border-radius: 6px;
                    padding: 24px;
                    margin: 28px 0;
                }}
                .action-title {{
                    color: #c8f04a;
                    font-size: 11px;
                    font-weight: 500;
                    letter-spacing: 0.12em;
                    text-transform: uppercase;
                    margin: 0 0 16px 0;
                }}
                .action-text {{
                    color: #a8a894;
                    font-size: 13px;
                    line-height: 1.6;
                    margin: 0 0 16px 0;
                }}
                .code-block {{ 
                    background-color: #0c0c09; 
                    color: #c8f04a;
                    padding: 16px 18px;
                    border-radius: 4px;
                    border: 1px solid #2a2a20;
                    font-family: 'DM Mono', 'Courier New', monospace;
                    font-size: 12px;
                    margin: 16px 0;
                    overflow-x: auto;
                    letter-spacing: 0.02em;
                }}
                .note {{
                    color: #6b7260;
                    font-size: 11px;
                    line-height: 1.6;
                    margin: 12px 0 0 0;
                    font-style: italic;
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
                        <div class="header-subtitle">Meeting Intelligence Platform</div>
                    </div>
                    
                    <div class="content">
                        <p class="greeting">Administrator,</p>
                        <p class="greeting">A new user has registered and is awaiting approval to access the platform.</p>
                        
                        <div class="section-label">User Information</div>
                        <div class="info-card">
                            <div class="info-row">
                                <div class="info-label">Email Address</div>
                                <div class="info-value">{user_email}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Display Name</div>
                                <div class="info-value">{display_name}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Account Status</div>
                                <div class="info-value">
                                    <span class="status-badge">Pending Approval</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="action-box">
                            <div class="action-title">Action Required</div>
                            <p class="action-text">To grant this user access to MeetingMind, execute the approval command:</p>
                            <div class="code-block">python scripts/setup/approve-user.py {user_email}</div>
                            <p class="note">Alternative: Manually enable the user via AWS Cognito console (ap-south-1 region)</p>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p style="color: #6b7260; font-size: 11px; line-height: 1.6; margin: 0; text-align: center;">
                            Automated notification from MeetingMind<span class="accent-dot"></span>Users are verified but remain inactive until approved
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
        
        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [ADMIN_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        print(f"Admin notification sent to {ADMIN_EMAIL} for new user: {user_email}")
        return True
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
        # Don't fail the signup if notification fails
        return False


def lambda_handler(event, context):
    """
    Cognito Pre-Signup trigger
    Auto-confirms user but they remain disabled until manually approved
    Also sends notification to admin
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    # Extract user info
    user_email = event['request']['userAttributes'].get('email', 'Unknown')
    user_name = event['request']['userAttributes'].get('name')
    
    # Send admin notification
    send_admin_notification(user_email, user_name)
    
    # Auto-confirm the user (skip email verification code)
    event['response']['autoConfirmUser'] = True
    event['response']['autoVerifyEmail'] = True
    
    return event
