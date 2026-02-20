import boto3

sqs = boto3.client('sqs', region_name='ap-south-1')
queue_url = 'https://sqs.ap-south-1.amazonaws.com/707411439284/meetingmind-processing-queue'

attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])['Attributes']
print(f'Messages Available: {attrs.get("ApproximateNumberOfMessages", "0")}')
print(f'Messages In Flight: {attrs.get("ApproximateNumberOfMessagesNotVisible", "0")}')
