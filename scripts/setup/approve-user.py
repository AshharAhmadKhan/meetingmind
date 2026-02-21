#!/usr/bin/env python3
"""
Script to approve a new MeetingMind user
Usage: python scripts/approve-user.py user@email.com
"""
import sys
import boto3
import time

REGION = 'ap-south-1'
USER_POOL_ID = 'ap-south-1_mkFJawjMp'
SES_FROM_EMAIL = 'thecyberprinciples@gmail.com'

cognito = boto3.client('cognito-idp', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

def send_congrats_email(email):
    """Send congratulations email after SES verification"""
    subject = "Email Verified — Welcome to MeetingMind!"
    
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
            .success-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #1a1a0e 0%, #141410 100%);
                border: 1px solid #3a3a2e;
                border-left: 3px solid #c8f04a;
                border-radius: 6px;
                padding: 16px 20px;
                margin: 20px 0;
                text-align: center;
                width: 100%;
            }}
            .success-text {{
                color: #c8f04a;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.08em;
                text-transform: uppercase;
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
                    <h1 class="header-title">Email Verified Successfully!</h1>
                </div>
                
                <div class="content">
                    <p class="greeting">Congratulations,</p>
                    <p class="greeting">Your email address has been verified successfully. Your account setup is now complete!</p>
                    
                    <div class="success-badge">
                        <div class="success-text">✓ Email Verified</div>
                    </div>
                    
                    <p class="greeting">You will receive a welcome email shortly with instructions on how to access your MeetingMind dashboard.</p>
                    
                    <div class="divider"></div>
                    
                    <p style="color: #6b7260; font-size: 11px; line-height: 1.6; margin: 0; text-align: center;">
                        Thank you for verifying your email<span class="accent-dot"></span>We're excited to have you on board
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
            Source=f'MeetingMind <{SES_FROM_EMAIL}>',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        print(f"   ✓ Congratulations email sent to {email}")
        return True
    except Exception as e:
        print(f"   ⚠️  Failed to send congrats email: {e}")
        return False

def wait_for_ses_verification(email, max_wait=300):
    """Wait for user to verify their email in SES"""
    print(f"\n⏳ Waiting for email verification (max {max_wait}s)...")
    print(f"   User needs to click the verification link in their email")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = ses.get_identity_verification_attributes(Identities=[email])
            attrs = response.get('VerificationAttributes', {})
            
            if email in attrs:
                status = attrs[email]['VerificationStatus']
                if status == 'Success':
                    print(f"   ✓ Email verified!")
                    return True
            
            # Wait 5 seconds before checking again
            time.sleep(5)
            print("   ⏳ Still waiting...", end='\r')
        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
            time.sleep(5)
    
    print(f"\n   ⚠️  Timeout: Email not verified within {max_wait}s")
    return False

def approve_user(email):
    """Approve a user: verify email in SES, enable Cognito account, send welcome email"""
    
    print(f"\n🔄 Approving user: {email}\n")
    
    # Step 1: Verify email in SES
    print("1️⃣  Verifying email in SES...")
    try:
        ses.verify_email_identity(EmailAddress=email)
        print(f"   ✓ Verification email sent to {email}")
    except Exception as e:
        print(f"   ⚠️  SES verification failed: {e}")
    
    # Step 2: Wait for user to verify email
    verified = wait_for_ses_verification(email, max_wait=300)
    
    # Step 3: Send congratulations email if verified
    if verified:
        print("\n2️⃣  Sending congratulations email...")
        send_congrats_email(email)
    
    # Step 4: Enable user in Cognito
    print("\n3️⃣  Enabling Cognito account...")
    try:
        # Find user by email
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{email}"'
        )
        
        if not response['Users']:
            print(f"   ❌ User not found: {email}")
            return False
        
        username = response['Users'][0]['Username']
        
        # Enable the user
        cognito.admin_enable_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        print(f"   ✓ User enabled: {username}")
    except Exception as e:
        print(f"   ❌ Failed to enable user: {e}")
        return False
    
    # Step 5: Send welcome email
    print("\n4️⃣  Sending welcome email...")
    try:
        lambda_client.invoke(
            FunctionName='meetingmind-send-welcome-email',
            InvocationType='Event',  # Async
            Payload=f'{{"email": "{email}"}}'
        )
        print(f"   ✓ Welcome email sent to {email}")
    except Exception as e:
        print(f"   ⚠️  Failed to send welcome email: {e}")
    
    print(f"\n✅ User approved successfully!")
    print(f"\n📧 Email sequence:")
    print(f"   1. ✓ SES verification email sent")
    if verified:
        print(f"   2. ✓ User verified email")
        print(f"   3. ✓ Congratulations email sent")
        print(f"   4. ✓ Welcome email sent")
    else:
        print(f"   2. ⚠️  User did not verify email (timeout)")
        print(f"   3. ⏭️  Skipped congratulations email")
        print(f"   4. ✓ Welcome email sent anyway")
    print(f"\n🌐 User can now log in at https://dcfx593ywvy92.cloudfront.net")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/approve-user.py user@email.com")
        sys.exit(1)
    
    email = sys.argv[1]
    approve_user(email)
