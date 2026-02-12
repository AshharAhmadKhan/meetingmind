import json
import boto3
import time
import uuid
import urllib.request
from datetime import datetime, timezone

transcribe = boto3.client('transcribe')
bedrock    = boto3.client('bedrock-runtime')
dynamodb   = boto3.resource('dynamodb')
s3         = boto3.client('s3')

import os
TABLE_NAME = os.environ['MEETINGS_TABLE']
REGION     = os.environ['REGION']


# ── ENTRY POINT ───────────────────────────────────────────────
def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Get the uploaded file details from the S3 event
    record     = event['Records'][0]
    bucket     = record['s3']['bucket']['name']
    key        = record['s3']['object']['key']   # e.g. audio/userId__meetingId__title.mp3
    
    print(f"Processing: s3://{bucket}/{key}")

    # Parse userId, meetingId, title from the key
    # Key format: audio/{userId}__{meetingId}__{title}.{ext}
    filename   = key.split('/')[-1]              # userId__meetingId__title.mp3
    parts      = filename.rsplit('.', 1)[0].split('__')  # ['userId','meetingId','title']
    
    if len(parts) < 3:
        print(f"ERROR: unexpected key format: {key}")
        return {'statusCode': 400, 'body': 'Bad key format'}

    user_id    = parts[0]
    meeting_id = parts[1]
    title      = parts[2].replace('-', ' ')

    table = dynamodb.Table(TABLE_NAME)

    # ── STEP 1: Update status to TRANSCRIBING ─────────────────
    _update_status(table, user_id, meeting_id, 'TRANSCRIBING')

    # ── STEP 2: Start Transcribe job ──────────────────────────
    job_name = f"mm-{meeting_id}"
    media_uri = f"s3://{bucket}/{key}"

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat=_get_format(key),
            LanguageCode='en-US',
            Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 10}
        )
    except transcribe.exceptions.ConflictException:
        # Job already exists (retry scenario) - proceed to poll
        print(f"Job {job_name} already exists, polling...")

    # ── STEP 3: Poll until Transcribe finishes ─────────────────
    transcript_text = _poll_transcribe(job_name)
    if not transcript_text:
        _update_status(table, user_id, meeting_id, 'FAILED', 
                       error='Transcription failed or timed out')
        return {'statusCode': 500, 'body': 'Transcription failed'}

    # ── STEP 4: Update status to ANALYZING ────────────────────
    _update_status(table, user_id, meeting_id, 'ANALYZING')

    # ── STEP 5: Call Bedrock to extract insights ───────────────
    insights = _extract_insights(transcript_text, title)
    if not insights:
        _update_status(table, user_id, meeting_id, 'FAILED',
                       error='AI analysis failed')
        return {'statusCode': 500, 'body': 'AI analysis failed'}

    # ── STEP 6: Save full meeting record to DynamoDB ───────────
    now = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression="""
            SET #st = :status,
                transcript = :transcript,
                summary = :summary,
                decisions = :decisions,
                actionItems = :actions,
                followUps = :followups,
                updatedAt = :updated
        """,
        ExpressionAttributeNames={'#st': 'status'},
        ExpressionAttributeValues={
            ':status':    'DONE',
            ':transcript': transcript_text[:50000],  # DynamoDB 400KB limit safety
            ':summary':   insights['summary'],
            ':decisions': insights['decisions'],
            ':actions':   insights['action_items'],
            ':followups': insights['follow_ups'],
            ':updated':   now,
        }
    )

    print(f"✅ Meeting {meeting_id} processed successfully")
    return {'statusCode': 200, 'body': 'OK'}


# ── HELPERS ───────────────────────────────────────────────────

def _update_status(table, user_id, meeting_id, status, error=None):
    expr = "SET #st = :s, updatedAt = :t"
    vals = {':s': status, ':t': datetime.now(timezone.utc).isoformat()}
    names = {'#st': 'status'}
    if error:
        expr += ", errorMessage = :e"
        vals[':e'] = error
    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression=expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=vals
    )
    print(f"Status updated → {status}")


def _get_format(key):
    ext = key.rsplit('.', 1)[-1].lower()
    mapping = {'mp3': 'mp3', 'mp4': 'mp4', 'wav': 'wav',
               'm4a': 'mp4', 'webm': 'webm', 'ogg': 'ogg'}
    return mapping.get(ext, 'mp3')


def _poll_transcribe(job_name, max_wait_seconds=600):
    """Poll Transcribe every 15s, max 10 minutes."""
    waited = 0
    while waited < max_wait_seconds:
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job      = response['TranscriptionJob']
        status   = job['TranscriptionJobStatus']
        print(f"Transcribe status: {status} ({waited}s elapsed)")

        if status == 'COMPLETED':
            uri = job['Transcript']['TranscriptFileUri']
            return _fetch_transcript(uri)
        elif status == 'FAILED':
            print("Transcribe FAILED:", job.get('FailureReason'))
            return None

        time.sleep(15)
        waited += 15

    print("Transcribe timed out")
    return None


def _fetch_transcript(uri):
    """Download the transcript JSON from S3 presigned URL."""
    try:
        with urllib.request.urlopen(uri) as response:
            data = json.loads(response.read().decode('utf-8'))
        # Extract plain text from Transcribe result
        return data['results']['transcripts'][0]['transcript']
    except Exception as e:
        print(f"Failed to fetch transcript: {e}")
        return None


def _extract_insights(transcript, meeting_title):
    """Call Bedrock Claude to extract structured insights from transcript."""
    
    # Truncate transcript to avoid token limits (Claude has large context but let's be safe)
    truncated = transcript[:15000] if len(transcript) > 15000 else transcript

    prompt = f"""You are an expert meeting analyst. Analyze this meeting transcript and extract structured insights.

Meeting Title: {meeting_title}

Transcript:
{truncated}

Extract and return a JSON object with EXACTLY this structure:
{{
  "summary": "2-3 sentence plain English summary of what the meeting was about and what was accomplished",
  "decisions": [
    "Decision 1 that was made",
    "Decision 2 that was made"
  ],
  "action_items": [
    {{
      "id": "action-1",
      "task": "Clear description of what needs to be done",
      "owner": "Person's name or 'Unassigned' if not mentioned",
      "deadline": "YYYY-MM-DD format if mentioned, or null if not mentioned",
      "completed": false
    }}
  ],
  "follow_ups": [
    "Topic or question that needs follow-up in next meeting"
  ]
}}

Rules:
- If no decisions were made, return empty array for decisions
- If no action items, return empty array for action_items  
- If no follow-ups, return empty array for follow_ups
- For deadlines: convert natural language like "next Friday" or "end of month" to YYYY-MM-DD based on today being {datetime.now().strftime('%Y-%m-%d')}
- Return ONLY valid JSON, no explanation, no markdown code blocks"""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        body    = json.loads(response['body'].read())
        content = body['content'][0]['text'].strip()
        
        # Clean up in case Claude adds markdown code fences
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()
        
        insights = json.loads(content)
        print(f"✅ Insights extracted: {len(insights.get('action_items',[]))} actions, "
              f"{len(insights.get('decisions',[]))} decisions")
        return insights

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {content}")
        return None
    except Exception as e:
        print(f"Bedrock error: {e}")
        return None
