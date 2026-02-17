import json
import boto3
import os
from datetime import datetime, timezone

REGION = os.environ.get('REGION', 'ap-south-1')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'thecyberprinciples@gmail.com')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://dcfx593ywvy92.cloudfront.net')

dynamodb = boto3.resource('dynamodb', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)


def lambda_handler(event, context):
    """
    Handle failed meeting processing from Dead Letter Queue.
    Send notification email to user about the failure.
    """
    print("DLQ Event:", json.dumps(event))
    
    try:
        # Parse DLQ message
        sqs_record = event['Records'][0]
        s3_event = json.loads(sqs_record['body'])
        record = s3_event['Records'][0]['s3']
        
        s3_key = record['object']['key']
        filename = s3_key.split('/')[-1]
        parts = filename.rsplit('.', 1)[0].split('__')
        user_id = parts[0]
        meeting_id = parts[1]
        
        print(f"Processing DLQ for meeting: {meeting_id}")
        
        # Get meeting details from DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        item = response.get('Item', {})
        
        title = item.get('title', 'Unknown Meeting')
        email = item.get('email', '')
        
        # Update meeting status to FAILED
        table.update_item(
            Key={'userId': user_id, 'meetingId': meeting_id},
            UpdateExpression='SET #st = :failed, updatedAt = :now',
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={
                ':failed': 'FAILED',
                ':now': datetime.now(timezone.utc).isoformat()
            }
        )

        
        # Send failure notification email
        if email:
            _send_failure_email(email, title, meeting_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'DLQ processed', 'meetingId': meeting_id})
        }
        
    except Exception as e:
        print(f"Error processing DLQ: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def _send_failure_email(email, title, meeting_id):
    """Send email notification about processing failure."""
    try:
        subject = f"MeetingMind: Processing Failed - {title}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc2626;">⚠️ Meeting Processing Failed</h2>
            <p>We encountered an issue processing your meeting recording:</p>
            
            <div style="background: #fee2e2; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <strong>{title}</strong>
            </div>
            
            <p>We attempted to process this meeting 3 times but were unable to complete the analysis.</p>
            
            <h3>What happened?</h3>
            <p>This could be due to:</p>
            <ul>
                <li>Audio file format issues</li>
                <li>Temporary service unavailability</li>
                <li>File corruption during upload</li>
            </ul>
            
            <h3>What to do next?</h3>
            <p>Please try uploading the meeting again. If the issue persists, contact support.</p>
            
            <a href="{FRONTEND_URL}" style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                Return to Dashboard
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                Meeting ID: {meeting_id}
            </p>
        </body>
        </html>
        """
        
        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}}
            }
        )
        print(f"Failure notification sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
