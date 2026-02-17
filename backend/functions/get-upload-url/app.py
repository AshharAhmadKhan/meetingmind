import json
import boto3
from botocore.config import Config
import uuid
import os
from datetime import datetime, timezone

REGION = os.environ.get('REGION', 'ap-south-1')

# Force regional endpoint — prevents CORS/signature issues
s3 = boto3.client(
    's3',
    region_name=REGION,
    config=Config(
        signature_version='s3v4',
        s3={'addressing_style': 'path'}
    )
)
dynamodb = boto3.resource('dynamodb', region_name=REGION)

ALLOWED_TYPES = {
    'audio/mpeg': 'mp3', 'audio/mp3': 'mp3',
    'audio/wav': 'wav', 'audio/wave': 'wav',
    'audio/mp4': 'mp4', 'video/mp4': 'mp4',
    'audio/x-m4a': 'mp4', 'audio/m4a': 'mp4',
    'audio/webm': 'webm', 'video/webm': 'webm',
    'audio/ogg': 'ogg', 'application/octet-stream': 'mp3',
}
MAX_SIZE = 500 * 1024 * 1024

CORS_HEADERS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Content-Type': 'application/json'
}

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        claims   = event['requestContext']['authorizer']['claims']
        user_id  = claims['sub']
        body     = json.loads(event.get('body') or '{}')
        title    = body.get('title', 'Untitled Meeting').strip()
        content_type = body.get('contentType', 'audio/mpeg')
        file_size    = int(body.get('fileSize', 0))
        team_id  = body.get('teamId')  # Optional team context

        ext = ALLOWED_TYPES.get(content_type)
        if not ext:
            return {'statusCode': 400, 'headers': CORS_HEADERS,
                    'body': json.dumps({'error': f'Unsupported file type: {content_type}'})}
        if file_size > MAX_SIZE:
            return {'statusCode': 400, 'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'File too large. Max 500MB.'})}

        meeting_id = str(uuid.uuid4())
        safe_title = title.replace(' ', '-').replace('/', '-')[:60]
        s3_key     = f"audio/{user_id}__{meeting_id}__{safe_title}.{ext}"
        bucket     = os.environ['AUDIO_BUCKET']

        # Generate presigned URL with NO extra signed headers
        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key':    s3_key,
            },
            ExpiresIn=3600,
        )

        # Force regional URL (replace global endpoint if present)
        upload_url = upload_url.replace(
            f'{bucket}.s3.amazonaws.com',
            f'{bucket}.s3.{REGION}.amazonaws.com'
        ).replace(
            f's3.amazonaws.com/{bucket}',
            f's3.{REGION}.amazonaws.com/{bucket}'
        )

        # Save to DynamoDB
        table = dynamodb.Table(os.environ['MEETINGS_TABLE'])
        item = {
            'userId':    user_id,
            'meetingId': meeting_id,
            'title':     title,
            'status':    'PENDING',
            's3Key':     s3_key,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'email':     claims.get('email', ''),
        }
        if team_id:
            item['teamId'] = team_id
        
        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'meetingId': meeting_id,
                'uploadUrl': upload_url,
                's3Key':     s3_key,
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
        return {'statusCode': 500, 'headers': CORS_HEADERS,
                'body': json.dumps({'error': str(e)})}
