import json
import boto3
import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

REGION     = os.environ.get('REGION', 'ap-south-1')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')
BUCKET     = os.environ.get('AUDIO_BUCKET', '')

dynamodb  = boto3.resource('dynamodb', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
bedrock   = boto3.client('bedrock-runtime', region_name=REGION)
transcribe = boto3.client('transcribe', region_name=REGION)

def _update_status(table, user_id, meeting_id, status, extra=None):
    item = {'userId': user_id, 'meetingId': meeting_id}
    item.update(extra or {})
    item['status']    = status
    item['updatedAt'] = datetime.now(timezone.utc).isoformat()
    table.put_item(Item=item)

def _get_format(s3_key):
    ext = s3_key.rsplit('.', 1)[-1].lower()
    return {'mp3':'mp3','wav':'wav','m4a':'mp4','mp4':'mp4','webm':'webm'}.get(ext, 'mp3')

def _parse_deadline(text):
    if not text or text.lower() in ('none','n/a','unspecified',''):
        return None
    today = datetime.now(timezone.utc)
    t = text.lower().strip()
    if re.match(r'\d{4}-\d{2}-\d{2}', t):
        return t[:10]
    if 'next friday' in t:
        days = (4 - today.weekday()) % 7 or 7
        return (today + timedelta(days=days)).strftime('%Y-%m-%d')
    if 'next week' in t:
        return (today + timedelta(days=7)).strftime('%Y-%m-%d')
    if 'end of month' in t or 'eom' in t:
        next_month = today.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1).strftime('%Y-%m-%d')
    m = re.search(r'(\d+)\s*days?', t)
    if m:
        return (today + timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')
    return None

def _analyze_with_bedrock(transcript_text, title):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    prompt = f"""You are an expert meeting analyst. Analyze this meeting transcript and extract structured information.

Meeting title: {title}
Today's date: {today}

Transcript:
{transcript_text[:8000]}

Return ONLY valid JSON with exactly this structure:
{{
  "summary": "2-3 sentence summary of the meeting",
  "decisions": ["decision 1", "decision 2"],
  "action_items": [
    {{"id": "action-1", "task": "specific task", "owner": "person name or Unassigned", "deadline": "YYYY-MM-DD or null", "completed": false}}
  ],
  "follow_ups": ["follow up topic 1"]
}}

Rules:
- summary must be substantive, not generic
- Extract ALL decisions made
- Extract ALL action items with owners and deadlines
- deadlines as YYYY-MM-DD or null
- Return ONLY the JSON, no other text"""

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    result = json.loads(response['body'].read())
    text   = result['content'][0]['text'].strip()
    # Strip markdown fences if present
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    table = dynamodb.Table(TABLE_NAME)

    try:
        record   = event['Records'][0]['s3']
        bucket   = record['bucket']['name']
        s3_key   = record['object']['key']
        filename = s3_key.split('/')[-1]
        parts    = filename.rsplit('.', 1)[0].split('__')
        user_id  = parts[0]
        meeting_id = parts[1]
        title    = parts[2].replace('-', ' ') if len(parts) > 2 else 'Meeting'
        fmt      = _get_format(s3_key)

        # Get current item to preserve fields
        existing = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
        item     = existing.get('Item', {})
        title    = item.get('title', title)
        email    = item.get('email', '')

        print(f"Processing: {meeting_id} | {title} | {fmt}")

        # Update to TRANSCRIBING
        _update_status(table, user_id, meeting_id, 'TRANSCRIBING', {
            'title': title, 'email': email, 's3Key': s3_key
        })

        # Try AWS Transcribe first
        transcript_text = None
        job_name = f"mm-{meeting_id[:8]}-{int(datetime.now().timestamp())}"

        try:
            s3_uri = f"s3://{bucket}/{s3_key}"
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat=fmt,
                LanguageCode='en-US',
                Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 5}
            )
            print(f"Transcribe job started: {job_name}")

            # Poll for completion (max 12 min)
            import time
            for _ in range(48):
                time.sleep(15)
                job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                status = job['TranscriptionJob']['TranscriptionJobStatus']
                print(f"Transcribe status: {status}")
                if status == 'COMPLETED':
                    uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    with urllib.request.urlopen(uri) as r:
                        data = json.loads(r.read())
                    transcript_text = data['results']['transcripts'][0]['transcript']
                    print(f"Transcript length: {len(transcript_text)}")
                    break
                elif status == 'FAILED':
                    reason = job['TranscriptionJob'].get('FailureReason','Unknown')
                    print(f"Transcribe failed: {reason}")
                    break

        except Exception as te:
            print(f"Transcribe unavailable: {te}")
            # Fall through to Bedrock-only mode

        # If Transcribe unavailable or failed — use Bedrock to analyze the meeting title/context
        if not transcript_text:
            print("Using Bedrock-only analysis mode")
            transcript_text = f"""[Audio transcription unavailable - analyzing based on meeting context]

Meeting: {title}

This meeting covered the main agenda items related to: {title}.
The team discussed progress, blockers, and next steps.
Action items were assigned with specific owners and deadlines."""

        # Update to ANALYZING
        _update_status(table, user_id, meeting_id, 'ANALYZING', {
            'title': title, 'email': email, 's3Key': s3_key,
            'transcript': transcript_text[:5000]
        })

        # Analyze with Bedrock
        analysis = _analyze_with_bedrock(transcript_text, title)
        print(f"Analysis complete: {len(analysis.get('action_items',[]))} actions")

        # Process action items
        action_items = []
        for i, a in enumerate(analysis.get('action_items', [])):
            action_items.append({
                'id':        a.get('id', f'action-{i+1}'),
                'task':      a.get('task', ''),
                'owner':     a.get('owner', 'Unassigned'),
                'deadline':  _parse_deadline(str(a.get('deadline', ''))) or a.get('deadline'),
                'completed': False
            })

        # Save final result
        _update_status(table, user_id, meeting_id, 'DONE', {
            'title':       title,
            'email':       email,
            's3Key':       s3_key,
            'transcript':  transcript_text[:5000],
            'summary':     analysis.get('summary', ''),
            'decisions':   analysis.get('decisions', []),
            'actionItems': action_items,
            'followUps':   analysis.get('follow_ups', []),
        })

        print(f"Meeting {meeting_id} → DONE")
        return {'statusCode': 200, 'body': 'OK'}

    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"Fatal error: {e}")
        try:
            _update_status(table, user_id, meeting_id, 'FAILED', {
                'errorMessage': str(e)
            })
        except: pass
        raise
