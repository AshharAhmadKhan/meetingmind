import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Scan all meetings
response = table.scan()
meetings = response.get('Items', [])

print(f"Found {len(meetings)} meetings")

# Update email for each meeting
updated = 0
for meeting in meetings:
    meeting_id = meeting.get('meetingId')
    user_id = meeting.get('userId')
    old_email = meeting.get('email')
    
    if not user_id or not meeting_id:
        continue
    
    if old_email == 'ashhar@meetingmind.com':
        print(f"Updating {meeting_id}...")
        table.update_item(
            Key={
                'userId': user_id,
                'meetingId': meeting_id
            },
            UpdateExpression='SET email = :new_email',
            ExpressionAttributeValues={
                ':new_email': 'thecyberprinciples@gmail.com'
            }
        )
        updated += 1

print(f"✅ Updated {updated} meetings")
