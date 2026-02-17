import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb')
sns        = boto3.client('sns')
TABLE_NAME = os.environ['MEETINGS_TABLE']
TOPIC_ARN  = os.environ['SNS_TOPIC_ARN']


def lambda_handler(event, context):
    print("Running daily reminder check...")
    table   = dynamodb.Table(TABLE_NAME)
    today   = datetime.now(timezone.utc).date()
    soon    = today + timedelta(days=2)   # Remind 2 days before deadline

    # Query using GSI instead of scan (efficient!)
    response = table.query(
        IndexName='status-createdAt-index',
        KeyConditionExpression='#st = :done',
        ExpressionAttributeNames={'#st': 'status'},
        ExpressionAttributeValues={':done': 'DONE'}
    )

    reminders_sent = 0
    for meeting in response.get('Items', []):
        actions = meeting.get('actionItems', [])
        overdue_or_soon = []

        for action in actions:
            if action.get('completed'):
                continue
            deadline_str = action.get('deadline')
            if not deadline_str:
                continue
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                if deadline <= soon:
                    status = 'OVERDUE' if deadline < today else 'DUE SOON'
                    overdue_or_soon.append({**action, 'deadline_status': status})
            except ValueError:
                continue

        if overdue_or_soon:
            _send_reminder(meeting, overdue_or_soon)
            reminders_sent += 1

    print(f"✅ Sent {reminders_sent} reminders")
    return {'statusCode': 200, 'body': f'Sent {reminders_sent} reminders'}


def _send_reminder(meeting, actions):
    title   = meeting.get('title', 'Unknown Meeting')
    lines   = [f"📋 Action Item Reminder — {title}\n"]
    for a in actions:
        status = a.get('deadline_status', '')
        lines.append(f"  [{status}] {a.get('task','?')}")
        lines.append(f"     Owner: {a.get('owner','Unassigned')}")
        lines.append(f"     Due:   {a.get('deadline','?')}\n")

    message = '\n'.join(lines)
    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=f"MeetingMind Reminder: {len(actions)} action item(s) need attention",
        Message=message
    )
    print(f"Reminder sent for meeting: {title}")
