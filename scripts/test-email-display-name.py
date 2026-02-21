#!/usr/bin/env python3
"""
Test script to verify SES display name shows as "MeetingMind"
"""
import boto3
import json
from datetime import datetime

REGION = 'ap-south-1'
SES_FROM_EMAIL = 'thecyberprinciples@gmail.com'
TEST_EMAIL = 'itzashhar@gmail.com'

ses = boto3.client('ses', region_name=REGION)

def send_test_email():
    """Send a test email to verify display name"""
    
    subject = "✅ MeetingMind Display Name Test"
    
    body_text = f"""This is a test email to verify the display name.

If you see "MeetingMind" as the sender (not just the email address), then the display name is working correctly!

Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
MeetingMind - AI Meeting Intelligence Assistant
"""
    
    body_html = f"""<html>
<head></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4CAF50;">✅ Display Name Test</h2>
        
        <p>This is a test email to verify the display name.</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>What to check:</strong></p>
            <ul>
                <li>In your inbox, does the sender show as <strong>"MeetingMind"</strong>?</li>
                <li>Or does it show as <strong>"thecyberprinciples@gmail.com"</strong>?</li>
            </ul>
        </div>
        
        <p style="color: #666; font-size: 14px;">Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #888; font-size: 12px;">MeetingMind - AI Meeting Intelligence Assistant</p>
    </div>
</body>
</html>"""
    
    try:
        response = ses.send_email(
            Source=f'MeetingMind <{SES_FROM_EMAIL}>',
            Destination={'ToAddresses': [TEST_EMAIL]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"✅ Test email sent successfully!")
        print(f"   To: {TEST_EMAIL}")
        print(f"   From: MeetingMind <{SES_FROM_EMAIL}>")
        print(f"   MessageId: {response['MessageId']}")
        print(f"\n📧 Check your inbox at {TEST_EMAIL}")
        print(f"   Look for sender name: 'MeetingMind'")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        raise

if __name__ == '__main__':
    send_test_email()
