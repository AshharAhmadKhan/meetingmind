import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

response = table.get_item(
    Key={
        'userId': 'a1a3cd5a-00e1-701f-a07b-b12a35f16664',
        'meetingId': '0a292ff3-973f-42aa-84b9-b56928f2a4d3'
    }
)

meeting = response.get('Item')
if meeting:
    print(f'Status: {meeting.get("status")}')
    print(f'Title: {meeting.get("title")}')
    print(f'S3 Key: {meeting.get("s3Key", "MISSING")}')
else:
    print('Meeting not found')
