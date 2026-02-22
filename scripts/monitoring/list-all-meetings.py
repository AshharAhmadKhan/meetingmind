import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

# Scan all meetings
response = table.scan()
meetings = response.get('Items', [])

# Sort by createdAt (most recent first)
meetings.sort(key=lambda x: x.get('createdAt', ''), reverse=True)

print(f"\n{'='*80}")
print(f"Total Meetings: {len(meetings)}")
print(f"{'='*80}\n")

for i, meeting in enumerate(meetings[:10], 1):  # Show last 10
    print(f"{i}. Meeting ID: {meeting.get('meetingId', 'N/A')}")
    print(f"   Title: {meeting.get('title', 'N/A')}")
    print(f"   Status: {meeting.get('status', 'N/A')}")
    print(f"   Owner: {meeting.get('userId', 'N/A')}")
    print(f"   Created: {meeting.get('createdAt', 'N/A')}")
    print(f"   Updated: {meeting.get('updatedAt', 'N/A')}")
    
    if meeting.get('status') == 'PENDING':
        print(f"   S3 Key: {meeting.get('s3Key', 'N/A')}")
        print(f"   Audio URL: {meeting.get('audioUrl', 'N/A')}")
    
    print()
