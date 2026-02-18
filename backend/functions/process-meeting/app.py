import json
import boto3
from botocore.config import Config
import os
import re
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# X-Ray instrumentation
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()  # Auto-instrument boto3, requests, etc.

REGION     = os.environ.get('REGION', 'ap-south-1')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://dcfx593ywvy92.cloudfront.net')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'thecyberprinciples@gmail.com')

# CRITICAL: Configure Bedrock with exponential backoff for throttling
# Retries are now safe since Nova models are working
bedrock_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'  # Adaptive mode handles throttling intelligently
    }
)

dynamodb   = boto3.resource('dynamodb', region_name=REGION)
bedrock    = boto3.client('bedrock-runtime', region_name=REGION, config=bedrock_config)
transcribe = boto3.client('transcribe', region_name=REGION)
ses        = boto3.client('ses', region_name=REGION)

def _update(table, user_id, meeting_id, status, extra=None):
    # Check if meeting exists to determine if it's new
    try:
        existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        is_new = 'Item' not in existing
    except:
        is_new = True
    
    now = datetime.now(timezone.utc).isoformat()
    
    item = {
        'userId': user_id,
        'meetingId': meeting_id,
        'status': status,
        'updatedAt': now
    }
    
    # Add createdAt only for new meetings
    if is_new:
        item['createdAt'] = now
    
    item.update(extra or {})
    table.put_item(Item=item)

def _get_format(s3_key):
    ext = s3_key.rsplit('.', 1)[-1].lower()
    return {'mp3':'mp3','wav':'wav','m4a':'mp4','mp4':'mp4','webm':'webm'}.get(ext,'mp3')

def _send_email_notification(email, meeting_id, title, status, summary='', action_count=0, error_message=''):
    """Send email notification via Amazon SES when meeting processing completes."""
    if not email:
        print("No email address provided, skipping notification")
        return
    
    meeting_url = f"{FRONTEND_URL}/meeting/{meeting_id}"
    
    try:
        if status == 'DONE':
            subject = f"✅ Meeting Analysis Complete: {title}"
            body_text = f"""Your meeting "{title}" has been processed successfully!

View your analysis: {meeting_url}

Summary: {summary if summary else 'Analysis complete'}

Action Items: {action_count}

Thank you for using MeetingMind!

---
MeetingMind - AI Meeting Intelligence Assistant
"""
            body_html = f"""<html>
<head></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4CAF50;">✅ Meeting Analysis Complete</h2>
        <h3 style="color: #555;">{title}</h3>
        
        <p>Your meeting has been processed successfully!</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Summary:</strong></p>
            <p>{summary if summary else 'Analysis complete'}</p>
        </div>
        
        <p><strong>Action Items Extracted:</strong> {action_count}</p>
        
        <a href="{meeting_url}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0;">View Full Analysis</a>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #888; font-size: 12px;">MeetingMind - AI Meeting Intelligence Assistant</p>
    </div>
</body>
</html>"""
        else:  # FAILED
            subject = f"❌ Meeting Processing Failed: {title}"
            body_text = f"""Unfortunately, we couldn't process your meeting "{title}".

Error: {error_message if error_message else 'Unknown error occurred'}

Please try uploading the audio file again. If the problem persists, contact support.

---
MeetingMind - AI Meeting Intelligence Assistant
"""
            body_html = f"""<html>
<head></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #f44336;">❌ Meeting Processing Failed</h2>
        <h3 style="color: #555;">{title}</h3>
        
        <p>Unfortunately, we couldn't process your meeting.</p>
        
        <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f44336;">
            <p><strong>Error:</strong></p>
            <p>{error_message if error_message else 'Unknown error occurred'}</p>
        </div>
        
        <p>Please try uploading the audio file again. If the problem persists, contact support.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #888; font-size: 12px;">MeetingMind - AI Meeting Intelligence Assistant</p>
    </div>
</body>
</html>"""
        
        # Send email via SES
        response = ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )
        print(f"Email sent successfully to {email}. MessageId: {response['MessageId']}")
        
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        # Don't raise - email failure shouldn't break the pipeline

def _calculate_meeting_roi(actions, decisions, meeting_duration_minutes=30):
    """
    Calculate meeting ROI based on cost vs value created.
    
    Cost = attendees × duration × hourly_rate
    Value = (decisions × decision_value) + (clear_actions × action_value)
    ROI = (value - cost) / cost × 100
    """
    try:
        # Assumptions for MVP
        avg_attendees = 4  # Typical meeting size
        hourly_rate = 75   # Average knowledge worker rate
        decision_value = 500  # Value of each decision made
        action_value = 200    # Value of each clear action item
        
        # Calculate cost
        cost = avg_attendees * (meeting_duration_minutes / 60) * hourly_rate
        
        # Calculate value
        decision_count = len(decisions) if decisions else 0
        clear_actions = len([a for a in actions if a.get('owner') and a.get('owner') != 'Unassigned' and a.get('deadline')]) if actions else 0
        value = (decision_count * decision_value) + (clear_actions * action_value)
        
        # Calculate ROI
        if cost == 0:
            roi = 0
        else:
            roi = ((value - cost) / cost) * 100
        
        # Convert to Decimal for DynamoDB
        return {
            'cost': Decimal(str(round(cost, 2))),
            'value': Decimal(str(round(value, 2))),
            'roi': Decimal(str(round(roi, 1))),
            'decision_count': decision_count,
            'clear_action_count': clear_actions,
            'meeting_duration_minutes': meeting_duration_minutes
        }
    except Exception as e:
        print(f"Error calculating ROI: {e}")
        # Return safe defaults as Decimal for DynamoDB
        return {
            'cost': Decimal('150.0'),
            'value': Decimal('0.0'),
            'roi': Decimal('-100.0'),
            'decision_count': 0,
            'clear_action_count': 0,
            'meeting_duration_minutes': 30
        }

def _days_from_now(n):
    return (datetime.now(timezone.utc) + timedelta(days=n)).strftime('%Y-%m-%d')

def _calculate_risk_score(action, created_at):
    """
    Calculate intelligent risk score (0-100) for action item.
    
    Uses smooth curves instead of cliffs for more accurate prediction.
    
    Risk Factors:
    - Deadline urgency (smooth curve, not cliff)
    - Owner assignment
    - Task vagueness (word count)
    - Staleness (days since created)
    """
    risk = 0
    
    # Factor 1: Deadline urgency (smooth curve)
    deadline = action.get('deadline')
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            days_left = (deadline_dt - datetime.now(timezone.utc)).days
            
            if days_left <= 0:
                risk += 45  # overdue
            elif days_left <= 2:
                risk += 40  # critical
            elif days_left <= 5:
                risk += 30  # urgent
            elif days_left <= 10:
                risk += 15  # approaching
            elif days_left <= 20:
                risk += 5   # watch
        except:
            pass  # Invalid deadline format, skip
    else:
        # No deadline at all
        risk += 20
    
    # Factor 2: Owner missing
    if not action.get('owner') or action['owner'] == 'Unassigned':
        risk += 25
    
    # Factor 3: Task vagueness (word count, not character count)
    task_text = action.get('task', '')
    word_count = len(task_text.split())
    
    if word_count < 3:
        risk += 20  # "do the thing"
    elif word_count < 6:
        risk += 10  # still vague
    
    # Factor 4: Staleness (how long it's been sitting unstarted)
    try:
        days_since_created = (datetime.now(timezone.utc) - created_at).days
        
        if days_since_created > 14:
            risk += 10
        elif days_since_created > 7:
            risk += 5
    except:
        pass
    
    # Cap at 100
    return min(risk, 100)

def _get_risk_level(score):
    """Convert numeric risk score to level."""
    if score >= 75:
        return 'CRITICAL'
    if score >= 50:
        return 'HIGH'
    if score >= 25:
        return 'MEDIUM'
    return 'LOW'

def _generate_embedding(text):
    """
    Generate embedding vector for text using Bedrock Titan Embeddings.
    Falls back to mock embedding if Bedrock unavailable.
    """
    try:
        # Try Bedrock Titan Embeddings
        body = json.dumps({"inputText": text})
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=body
        )
        result = json.loads(response['body'].read())
        embedding = result['embedding']
        print(f"Generated Bedrock embedding: {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        print(f"Bedrock embedding failed: {e} — using mock embedding")
        # Mock embedding: simple hash-based vector (1536 dimensions like Titan)
        # This allows the system to work without Bedrock
        import hashlib
        from decimal import Decimal
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Expand to 1536 dimensions by repeating and normalizing
        mock_embedding = []
        for i in range(1536):
            byte_val = hash_bytes[i % len(hash_bytes)]
            # Convert to Decimal for DynamoDB compatibility
            mock_embedding.append(Decimal(str((byte_val / 255.0) - 0.5)))
        return mock_embedding

def _try_bedrock(transcript_text, title):
    """Attempt real Bedrock analysis with retry logic for throttling."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    prompt = f"""Analyze this meeting and return ONLY valid JSON:
{{
  "summary": "2-3 sentence summary",
  "decisions": ["decision 1"],
  "action_items": [{{"id":"action-1","task":"task","owner":"person","deadline":"YYYY-MM-DD or null","completed":false}}],
  "follow_ups": ["follow up"]
}}

Meeting: {title}
Date: {today}
Transcript: {transcript_text[:6000]}

Return ONLY JSON."""

    models = [
        ('anthropic.claude-3-haiku-20240307-v1:0', 'anthropic'),  # Use Haiku (stable, works with on-demand)
        ('apac.amazon.nova-lite-v1:0', 'nova'),  # APAC inference profile
        ('apac.amazon.nova-micro-v1:0', 'nova'),  # APAC inference profile
    ]

    for model_id, model_type in models:
        # Try each model with exponential backoff for throttling
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if model_type == 'anthropic':
                    body = json.dumps({'anthropic_version':'bedrock-2023-05-31',
                        'max_tokens':2000,'messages':[{'role':'user','content':prompt}]})
                else:
                    body = json.dumps({'messages':[{'role':'user','content':[{'text':prompt}]}],
                        'inferenceConfig':{'maxTokens':2000,'temperature':0.1}})

                resp = bedrock.invoke_model(modelId=model_id, body=body)
                result = json.loads(resp['body'].read())

                if model_type == 'anthropic':
                    text = result['content'][0]['text'].strip()
                else:
                    text = result['output']['message']['content'][0]['text'].strip()

                text = re.sub(r'^```json\s*|^```\s*|\s*```$','',text).strip()
                parsed = json.loads(text)
                print(f"Bedrock success with {model_id} (attempt {attempt + 1})")
                return parsed
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a throttling error
                if 'ThrottlingException' in error_str or 'TooManyRequestsException' in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                        print(f"Model {model_id} throttled, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Model {model_id} throttled after {max_retries} attempts, moving to next model")
                        break
                else:
                    # Non-throttling error, move to next model immediately
                    print(f"Model {model_id} failed: {e}")
                    break

    print("❌ All Bedrock models failed - returning None")
    return None

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    table = dynamodb.Table(TABLE_NAME)
    user_id = meeting_id = None

    try:
        # Parse event - handle both SQS (new) and direct S3 (legacy)
        with xray_recorder.capture('parse_event'):
            # Check if event is from SQS
            if 'Records' in event and event['Records'][0].get('eventSource') == 'aws:sqs':
                # SQS event - extract S3 event from message body
                sqs_record = event['Records'][0]
                s3_event = json.loads(sqs_record['body'])
                record = s3_event['Records'][0]['s3']
                print("Processing from SQS queue")
            else:
                # Direct S3 event (legacy path)
                record = event['Records'][0]['s3']
                print("Processing from direct S3 event")
            
            bucket     = record['bucket']['name']
            s3_key     = record['object']['key']
            filename   = s3_key.split('/')[-1]
            parts      = filename.rsplit('.', 1)[0].split('__')
            user_id    = parts[0]
            meeting_id = parts[1]
            fmt        = _get_format(s3_key)

            existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
            item     = existing.get('Item', {})
            title    = item.get('title', parts[2].replace('-',' ') if len(parts)>2 else 'Meeting')
            email    = item.get('email', '')

            print(f"Processing: {meeting_id} | {title}")

        # TRANSCRIBING phase
        _update(table, user_id, meeting_id, 'TRANSCRIBING',
            {'title':title,'email':email,'s3Key':s3_key})

        transcript_text = None

        # Try AWS Transcribe
        with xray_recorder.capture('transcribe_audio'):
            try:
                job_name = f"mm-{meeting_id[:8]}-{int(datetime.now().timestamp())}"
                transcribe.start_transcription_job(
                    TranscriptionJobName=job_name,
                    Media={'MediaFileUri': f"s3://{bucket}/{s3_key}"},
                    MediaFormat=fmt, LanguageCode='en-US',
                    Settings={'ShowSpeakerLabels':True,'MaxSpeakerLabels':5}
                )
                for _ in range(48):
                    time.sleep(15)
                    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                    status = job['TranscriptionJob']['TranscriptionJobStatus']
                    print(f"Transcribe: {status}")
                    if status == 'COMPLETED':
                        uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        with urllib.request.urlopen(uri) as r:
                            data = json.loads(r.read())
                        transcript_text = data['results']['transcripts'][0]['transcript']
                        print(f"Transcript: {len(transcript_text)} chars")
                        break
                    elif status == 'FAILED':
                        print(f"Transcribe failed: {job['TranscriptionJob'].get('FailureReason')}")
                        break
            except Exception as te:
                print(f"Transcribe unavailable: {te}")

        if not transcript_text:
            error_msg = "Transcription failed - no audio transcript available. Please ensure the audio file is valid and try again."
            print(f"❌ TRANSCRIPTION FAILED: {error_msg}")
            _update(table, user_id, meeting_id, 'FAILED', {'errorMessage': error_msg})
            _send_email_notification(
                email=email,
                meeting_id=meeting_id,
                title=title,
                status='FAILED',
                error_message=error_msg
            )
            raise Exception(error_msg)

        # ANALYZING phase
        _update(table, user_id, meeting_id, 'ANALYZING',
            {'title':title,'email':email,'s3Key':s3_key,
             'transcript': transcript_text[:5000]})

        # Try Bedrock with multi-model fallback
        with xray_recorder.capture('bedrock_analysis'):
            analysis = _try_bedrock(transcript_text, title)
            
            if not analysis:
                error_msg = "AI analysis failed - all Bedrock models unavailable. Please try again later."
                print(f"❌ BEDROCK ANALYSIS FAILED: {error_msg}")
                _update(table, user_id, meeting_id, 'FAILED', {'errorMessage': error_msg, 'transcript': transcript_text[:5000]})
                _send_email_notification(
                    email=email,
                    meeting_id=meeting_id,
                    title=title,
                    status='FAILED',
                    error_message=error_msg
                )
                raise Exception(error_msg)

        # Normalize action items with risk scores and embeddings
        action_items = []
        created_at = datetime.now(timezone.utc)
        
        for i, a in enumerate(analysis.get('action_items', [])):
            action = {
                'id':        a.get('id', f'action-{i+1}'),
                'task':      a.get('task', ''),
                'owner':     a.get('owner', 'Unassigned'),
                'deadline':  a.get('deadline') if a.get('deadline') not in (None,'null','None','') else None,
                'completed': False,
                'status':    'todo',  # Initialize with todo status
                'createdAt': created_at.isoformat()
            }
            
            # Calculate risk score
            risk_score = _calculate_risk_score(action, created_at)
            action['riskScore'] = risk_score
            action['riskLevel'] = _get_risk_level(risk_score)
            
            # Generate embedding for duplicate detection (Day 5)
            task_text = action['task']
            if task_text:
                embedding = _generate_embedding(task_text)
                action['embedding'] = embedding
            
            action_items.append(action)

        # Calculate meeting ROI
        roi_data = _calculate_meeting_roi(action_items, analysis.get('decisions', []))

        # DONE
        _update(table, user_id, meeting_id, 'DONE', {
            'title':       title,
            'email':       email,
            's3Key':       s3_key,
            'transcript':  transcript_text[:5000],
            'summary':     analysis.get('summary',''),
            'decisions':   analysis.get('decisions',[]),
            'actionItems': action_items,
            'followUps':   analysis.get('follow_ups',[]),
            'roi':         roi_data,
        })

        # Send success email notification
        with xray_recorder.capture('send_email_notification'):
            _send_email_notification(
                email=email,
                meeting_id=meeting_id,
                title=title,
                status='DONE',
                summary=analysis.get('summary', ''),
                action_count=len(action_items)
            )

        print(f"✅ Meeting {meeting_id} → DONE")
        return {'statusCode': 200, 'body': 'OK'}

    except Exception as e:
        import traceback; traceback.print_exc()
        error_msg = str(e)
        try:
            if user_id and meeting_id:
                _update(table, user_id, meeting_id, 'FAILED', {'errorMessage': error_msg})
                
                # Send failure email notification
                # Try to get email and title from DynamoDB if available
                try:
                    existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
                    item = existing.get('Item', {})
                    email = item.get('email', '')
                    title = item.get('title', 'Meeting')
                    
                    _send_email_notification(
                        email=email,
                        meeting_id=meeting_id,
                        title=title,
                        status='FAILED',
                        error_message=error_msg
                    )
                except Exception as email_error:
                    print(f"Failed to send error notification email: {email_error}")
        except: pass
        raise
# redeployed Sun Feb 15 10:18:18 IST 2026
# force Sun Feb 15 17:30:02 IST 2026
# fix Sun Feb 15 17:49:31 IST 2026
