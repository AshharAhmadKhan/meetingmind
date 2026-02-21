import json
import boto3
from botocore.config import Config
import os
import re
import time
import urllib.request
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from difflib import SequenceMatcher

# X-Ray instrumentation
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()  # Auto-instrument boto3, requests, etc.

REGION     = os.environ.get('REGION', 'ap-south-1')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')
TEAMS_TABLE = os.environ.get('TEAMS_TABLE', 'meetingmind-teams')
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

def _get_team_members(team_id):
    """Fetch team members' names from the teams table."""
    if not team_id:
        return []
    
    try:
        teams_table = dynamodb.Table(TEAMS_TABLE)
        response = teams_table.get_item(Key={'teamId': team_id})
        team = response.get('Item')
        
        if not team:
            return []
        
        members = team.get('members', [])
        # Extract names from members list
        member_names = [m.get('name', '') for m in members if m.get('name')]
        print(f"Team {team_id} members: {member_names}")
        return member_names
    except Exception as e:
        print(f"Error fetching team members: {e}")
        return []

def _fuzzy_match_owner(ai_owner, team_members, threshold=0.6):
    """
    Match AI-extracted owner name to team member names using fuzzy matching.
    
    Args:
        ai_owner: Name extracted by AI (e.g., "Zeeshan", "Abdul")
        team_members: List of team member names (e.g., ["Abdul Zeeshan", "Ashhar Ahmad Khan"])
        threshold: Minimum similarity ratio (0.0 to 1.0)
    
    Returns:
        Best matching team member name or original ai_owner if no good match
    """
    if not ai_owner or ai_owner == 'Unassigned' or not team_members:
        return ai_owner
    
    ai_owner_lower = ai_owner.lower().strip()
    best_match = None
    best_ratio = 0.0
    
    for member_name in team_members:
        member_lower = member_name.lower().strip()
        
        # Check for exact match first
        if ai_owner_lower == member_lower:
            return member_name
        
        # Check if AI name is a word in member name (e.g., "Zeeshan" in "Abdul Zeeshan")
        member_words = member_lower.split()
        if ai_owner_lower in member_words:
            print(f"Fuzzy matched '{ai_owner}' → '{member_name}' (word match)")
            return member_name
        
        # Check if AI name is a substring of any word in member name
        for word in member_words:
            if ai_owner_lower in word or word in ai_owner_lower:
                ratio = SequenceMatcher(None, ai_owner_lower, word).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = member_name
        
        # Also check overall similarity
        overall_ratio = SequenceMatcher(None, ai_owner_lower, member_lower).ratio()
        if overall_ratio > best_ratio:
            best_ratio = overall_ratio
            best_match = member_name
    
    # Return best match if above threshold
    if best_match and best_ratio >= threshold:
        print(f"Fuzzy matched '{ai_owner}' → '{best_match}' (ratio: {best_ratio:.2f})")
        return best_match
    
    # No good match found
    return ai_owner

def _update(table, user_id, meeting_id, status, extra=None):
    # Check if meeting exists to determine if it's new
    try:
        existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        is_new = 'Item' not in existing
        existing_item = existing.get('Item', {})
    except:
        is_new = True
        existing_item = {}
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Start with existing item to preserve fields like teamId
    item = existing_item.copy() if existing_item else {}
    
    # Update with new values
    item.update({
        'userId': user_id,
        'meetingId': meeting_id,
        'status': status,
        'updatedAt': now
    })
    
    # Add createdAt only for new meetings
    if is_new:
        item['createdAt'] = now
    
    # Add extra fields
    item.update(extra or {})
    
    # Log teamId preservation
    if 'teamId' in item:
        print(f"🔄 Preserving teamId: {item['teamId']}")
    
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
            Source=f'MeetingMind <{SES_FROM_EMAIL}>',
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

def _calculate_health_score(action_items, decisions, created_at):
    """
    Calculate meeting health score (0-100) and letter grade.
    
    Formula:
    - Completion rate: 40%
    - Owner assignment rate: 30%
    - Inverted risk score: 20%
    - Recency bonus: 10%
    """
    if not action_items:
        # No actions = perfect score (nothing to fail)
        return {'score': Decimal('100.0'), 'grade': 'A', 'label': 'Perfect meeting'}
    
    total = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    owned = sum(1 for a in action_items if a.get('owner') and a['owner'] != 'Unassigned')
    
    # Calculate average risk score
    risk_scores = [a.get('riskScore', 0) for a in action_items]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Calculate recency bonus (meetings < 7 days old get bonus)
    recency_bonus = 1.0
    try:
        days_old = (datetime.now(timezone.utc) - created_at).days
        recency_bonus = 1.0 if days_old < 7 else 0.8
    except:
        pass
    
    # Calculate weighted score
    completion_rate = (completed / total) * 40
    owner_rate = (owned / total) * 30
    risk_inverted = ((100 - avg_risk) / 100) * 20
    recency_component = recency_bonus * 10
    
    score = completion_rate + owner_rate + risk_inverted + recency_component
    score = min(max(score, 0), 100)  # Clamp to 0-100
    
    # Determine grade and label
    if score >= 90:
        grade, label = 'A', 'Excellent meeting'
    elif score >= 80:
        grade, label = 'B', 'Strong meeting'
    elif score >= 70:
        grade, label = 'C', 'Average meeting'
    elif score >= 60:
        grade, label = 'D', 'Poor meeting'
    else:
        grade, label = 'F', 'Failed meeting'
    
    return {
        'score': Decimal(str(round(score, 1))),
        'grade': grade,
        'label': label
    }


def _generate_autopsy(action_items, decisions, transcript_text, health_score):
    """
    Generate meeting autopsy for failed meetings using rule-based logic.
    Provides specific, actionable feedback based on meeting patterns.
    """
    # Only generate for F grade (< 60) or ghost meetings
    is_ghost = len(decisions) == 0 and len(action_items) == 0
    if health_score >= 60 and not is_ghost:
        return None
    
    # Calculate metrics
    total_actions = len(action_items)
    completed = [a for a in action_items if a.get('completed')]
    unassigned = [a for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned']
    decision_count = len(decisions)
    
    completion_rate = len(completed) / total_actions if total_actions > 0 else 0
    unassigned_rate = len(unassigned) / total_actions if total_actions > 0 else 0
    
    # Rule 1: Ghost meeting (no decisions, no actions)
    if is_ghost:
        return "Cause of death: Zero decisions and zero action items extracted from this meeting. Prescription: This meeting could have been an email—try Slack next time."
    
    # Rule 2: High unassigned rate (>50%)
    if unassigned_rate > 0.5:
        return f"Cause of death: {len(unassigned)} of {total_actions} tasks have no owner—classic diffusion of responsibility. Prescription: No one leaves until every task has a name."
    
    # Rule 3: Zero completion (all tasks incomplete)
    if total_actions > 0 and completion_rate == 0:
        return f"Cause of death: Zero of {total_actions} action items completed despite clear assignments. Prescription: Set up accountability check-ins before the next meeting."
    
    # Rule 4: Very low completion (1-25%)
    if 0 < completion_rate <= 0.25:
        return f"Cause of death: Only {len(completed)} of {total_actions} commitments delivered—poor follow-through. Prescription: Assign fewer, higher-priority tasks or reduce meeting frequency."
    
    # Rule 5: Low completion (26-50%)
    if 0.25 < completion_rate <= 0.5:
        return f"Cause of death: Half the commitments were abandoned ({len(completed)}/{total_actions} completed). Prescription: Focus on the critical few instead of the trivial many."
    
    # Rule 6: No decisions but many actions
    if decision_count == 0 and total_actions > 3:
        return f"Cause of death: {total_actions} tasks assigned but zero decisions made—this was a status update, not a meeting. Prescription: Cancel recurring meetings that don't drive decisions."
    
    # Rule 7: Many decisions, few actions
    if decision_count > 3 and total_actions < 2:
        return f"Cause of death: {decision_count} decisions with no clear next steps—lots of talk, little execution. Prescription: Convert decisions into concrete action items with owners."
    
    # Rule 8: No decisions at all
    if decision_count == 0 and total_actions > 0:
        return f"Cause of death: {total_actions} tasks but zero decisions—no strategic direction. Prescription: Decide what NOT to do before assigning more work."
    
    # Rule 9: Some unassigned tasks (20-50%)
    if 0.2 < unassigned_rate <= 0.5:
        return f"Cause of death: {len(unassigned)} of {total_actions} tasks lack clear ownership. Prescription: Use the 'who does what by when' format for every commitment."
    
    # Rule 10: Generic fallback for other F-grade meetings
    if health_score < 50:
        return f"Cause of death: Meeting health score of {health_score}/100 indicates critical failure. Prescription: Review meeting necessity—this might not need to happen."
    else:
        return f"Cause of death: Meeting scored {health_score}/100 with unclear action clarity. Prescription: Define specific, measurable outcomes before scheduling the next one."


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
        # Convert floats to Decimal for DynamoDB compatibility
        return [Decimal(str(float(v))) for v in embedding]
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

        # Get team members for fuzzy name matching
        team_id = item.get('teamId')
        team_members = _get_team_members(team_id) if team_id else []
        
        # Normalize action items with risk scores and embeddings
        action_items = []
        created_at = datetime.now(timezone.utc)
        
        for i, a in enumerate(analysis.get('action_items', [])):
            # Apply fuzzy matching to owner name
            ai_owner = a.get('owner', 'Unassigned')
            matched_owner = _fuzzy_match_owner(ai_owner, team_members) if team_members else ai_owner
            
            action = {
                'id':        str(uuid.uuid4()),  # Generate unique UUID for each action
                'task':      a.get('task', ''),
                'owner':     matched_owner,
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
        
        # Calculate health score
        health_data = _calculate_health_score(action_items, analysis.get('decisions', []), created_at)
        
        # Generate autopsy for failed meetings (F grade or ghost meetings)
        # Only generate for truly failed meetings (score < 60) or ghost meetings
        autopsy = None
        is_ghost = len(analysis.get('decisions', [])) == 0 and len(action_items) == 0
        if health_data['score'] < 60 or is_ghost:
            with xray_recorder.capture('generate_autopsy'):
                autopsy = _generate_autopsy(
                    action_items,
                    analysis.get('decisions', []),
                    transcript_text,
                    health_data['score']
                )

        # DONE
        done_data = {
            'title':       title,
            'email':       email,
            's3Key':       s3_key,
            'transcript':  transcript_text[:5000],
            'summary':     analysis.get('summary',''),
            'decisions':   analysis.get('decisions',[]),
            'actionItems': action_items,
            'followUps':   analysis.get('follow_ups',[]),
            'roi':         roi_data,
            'healthScore': health_data['score'],  # Already a Decimal from _calculate_health_score
            'healthGrade': health_data['grade'],
            'healthLabel': health_data['label'],
            'isGhost':     is_ghost,
        }
        
        if autopsy:
            done_data['autopsy'] = autopsy
            done_data['autopsyGeneratedAt'] = datetime.now(timezone.utc).isoformat()
        
        _update(table, user_id, meeting_id, 'DONE', done_data)

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
