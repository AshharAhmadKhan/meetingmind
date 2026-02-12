import json
import boto3
import uuid
import os
from datetime import datetime, timezone

s3         = boto3.client('s3')
dynamodb   = boto3.resource('dynamodb')

BUCKET     = os.environ['AUDIO_BUCKET']
TABLE_NAME = os.environ['MEETINGS_TABLE']

ALLOWED_TYPES = {
    'audio/mpeg': 'mp3',
    'audio/mp4': 'mp4',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/m4a': 'm4a',
    'audio/x-m4a': 'm4a',
    'video/mp4': 'mp4',
    'audio/webm': 'webm',
    'audio/ogg': 'ogg',
}


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Get userId from Cognito JWT (injected by API Gateway authorizer)
    user_id = event['requestContext']['authorizer']['claims']['sub']

    body = json.loads(event.get('body') or '{}')
    title        = body.get('title', 'Untitled Meeting').strip()[:100]
    content_type = body.get('contentType', 'audio/mpeg')
    file_size    = body.get('fileSize', 0)

    # Validate content type
    if content_type not in ALLOWED_TYPES:
        return _response(400, {'error': f'Unsupported file type: {content_type}. Allowed: mp3, mp4, wav, m4a, webm, ogg'})

    # Validate file size (max 500MB)
    if file_size > 500 * 1024 * 1024:
        return _response(400, {'error': 'File too large. Maximum size is 500MB.'})

    ext        = ALLOWED_TYPES[content_type]
    meeting_id = str(uuid.uuid4())
    safe_title = title.replace(' ', '-').replace('/', '-')[:50]

    # S3 key format: audio/{userId}__{meetingId}__{title}.{ext}
    s3_key = f"audio/{user_id}__{meeting_id}__{safe_title}.{ext}"

    # Generate presigned URL (valid for 1 hour)
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET,
            'Key': s3_key,
            'ContentType': content_type,
        },
        ExpiresIn=3600
    )

    # Create meeting record in DynamoDB (status: PENDING)
    now = datetime.now(timezone.utc).isoformat()
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'userId':    user_id,
        'meetingId': meeting_id,
        'title':     title,
        'status':    'PENDING',
        's3Key':     s3_key,
        'createdAt': now,
        'updatedAt': now,
        'actionItems': [],
        'decisions':   [],
        'followUps':   [],
        'summary':     '',
    })

    print(f"✅ Created meeting {meeting_id} for user {user_id}")

    return _response(200, {
        'meetingId':   meeting_id,
        'uploadUrl':   presigned_url,
        's3Key':       s3_key,
    })


def _response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body)
    }
