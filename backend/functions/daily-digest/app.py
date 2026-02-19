import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

MEETINGS_TABLE = os.environ['MEETINGS_TABLE']
SES_FROM_EMAIL = os.environ['SES_FROM_EMAIL']
FRONTEND_URL = os.environ['FRONTEND_URL']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Daily digest email sent to all users with incomplete action items
    Triggered by EventBridge at 9 AM daily
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    print("Running daily digest...")
    
    # Get all users with incomplete actions
    table = dynamodb.Table(MEETINGS_TABLE)
    
    # Scan for all meetings (we'll group by user)
    response = table.scan()
    meetings = response.get('Items', [])
    
    # Group by user
    users = {}
    for meeting in meetings:
        user_id = meeting.get('userId')
        email = meeting.get('email')
        
        if not user_id or not email:
            continue
            
        if user_id not in users:
            users[user_id] = {
                'email': email,
                'meetings': []
            }
        
        users[user_id]['meetings'].append(meeting)
    
    # Send digest to each user
    sent_count = 0
    for user_id, user_data in users.items():
        try:
            digest_data = calculate_digest(user_data['meetings'])
            
            # Only send if user has incomplete items
            if digest_data['total_incomplete'] > 0:
                send_digest_email(user_data['email'], digest_data)
                sent_count += 1
        except Exception as e:
            print(f"Failed to send digest to {user_data['email']}: {e}")
    
    print(f"✅ Sent {sent_count} daily digests")
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': f'Sent {sent_count} digests'}, default=decimal_to_float)
    }


def calculate_digest(meetings):
    """Calculate digest data for a user"""
    now = datetime.now(timezone.utc)
    today = now.date()
    tomorrow = today + timedelta(days=1)
    week_from_now = today + timedelta(days=7)
    
    critical = []  # Due today or tomorrow
    overdue = []   # Past deadline
    upcoming = []  # Due this week
    
    total_actions = 0
    completed_actions = 0
    incomplete_actions = 0
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        meeting_title = meeting.get('title', 'Untitled Meeting')
        meeting_id = meeting.get('meetingId')
        
        for action in action_items:
            total_actions += 1
            
            if action.get('completed'):
                completed_actions += 1
                continue
            
            incomplete_actions += 1
            
            deadline_str = action.get('deadline')
            if not deadline_str:
                continue
            
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                
                action_with_context = {
                    'task': action.get('task'),
                    'owner': action.get('owner', 'Unassigned'),
                    'deadline': deadline_str,
                    'riskLevel': action.get('riskLevel', 'LOW'),
                    'meetingTitle': meeting_title,
                    'meetingId': meeting_id
                }
                
                if deadline < today:
                    overdue.append(action_with_context)
                elif deadline <= tomorrow:
                    critical.append(action_with_context)
                elif deadline <= week_from_now:
                    upcoming.append(action_with_context)
            except ValueError:
                continue
    
    # Calculate completion rate
    completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
    
    return {
        'critical': critical,
        'overdue': overdue,
        'upcoming': upcoming,
        'total_incomplete': incomplete_actions,
        'completion_rate': round(completion_rate, 1),
        'total_actions': total_actions,
        'completed_actions': completed_actions
    }


def send_digest_email(to_email, digest_data):
    """Send HTML email digest"""
    
    subject = f"🔔 MeetingMind Daily Digest — {digest_data['total_incomplete']} items need attention"
    
    # Build HTML email
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: #0c0c09; color: #c8f04a; padding: 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .stats {{ background: #f9f9f9; padding: 20px; border-bottom: 1px solid #e0e0e0; }}
            .stat-row {{ display: flex; justify-content: space-around; }}
            .stat {{ text-align: center; }}
            .stat-num {{ font-size: 32px; font-weight: bold; color: #333; }}
            .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
            .section {{ padding: 20px; }}
            .section-title {{ font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #333; }}
            .action-item {{ background: #f9f9f9; padding: 12px; margin-bottom: 8px; border-radius: 4px; border-left: 4px solid #ccc; }}
            .action-item.critical {{ border-left-color: #e87a6a; }}
            .action-item.overdue {{ border-left-color: #e87a6a; }}
            .action-item.upcoming {{ border-left-color: #e8c06a; }}
            .action-task {{ font-size: 14px; color: #333; margin-bottom: 4px; }}
            .action-meta {{ font-size: 12px; color: #666; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            .btn {{ display: inline-block; background: #c8f04a; color: #0c0c09; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Your Daily Digest</h1>
                <p style="margin: 8px 0 0 0; opacity: 0.9;">MeetingMind</p>
            </div>
            
            <div class="stats">
                <div class="stat-row">
                    <div class="stat">
                        <div class="stat-num">{digest_data['completion_rate']}%</div>
                        <div class="stat-label">Completion Rate</div>
                    </div>
                    <div class="stat">
                        <div class="stat-num">{digest_data['completed_actions']}</div>
                        <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-num">{digest_data['total_incomplete']}</div>
                        <div class="stat-label">Pending</div>
                    </div>
                </div>
            </div>
    """
    
    # Critical items
    if digest_data['critical']:
        html_body += f"""
            <div class="section">
                <div class="section-title">🔴 CRITICAL — Due Today/Tomorrow ({len(digest_data['critical'])})</div>
        """
        for action in digest_data['critical'][:5]:  # Limit to 5
            html_body += f"""
                <div class="action-item critical">
                    <div class="action-task">{action['task']}</div>
                    <div class="action-meta">
                        👤 {action['owner']} • 📅 {action['deadline']} • 📋 {action['meetingTitle']}
                    </div>
                </div>
            """
        html_body += "</div>"
    
    # Overdue items
    if digest_data['overdue']:
        html_body += f"""
            <div class="section">
                <div class="section-title">🔴 OVERDUE — Past Deadline ({len(digest_data['overdue'])})</div>
        """
        for action in digest_data['overdue'][:5]:  # Limit to 5
            html_body += f"""
                <div class="action-item overdue">
                    <div class="action-task">{action['task']}</div>
                    <div class="action-meta">
                        👤 {action['owner']} • 📅 {action['deadline']} • 📋 {action['meetingTitle']}
                    </div>
                </div>
            """
        html_body += "</div>"
    
    # Upcoming items
    if digest_data['upcoming']:
        html_body += f"""
            <div class="section">
                <div class="section-title">🟡 UPCOMING — Due This Week ({len(digest_data['upcoming'])})</div>
        """
        for action in digest_data['upcoming'][:5]:  # Limit to 5
            html_body += f"""
                <div class="action-item upcoming">
                    <div class="action-task">{action['task']}</div>
                    <div class="action-meta">
                        👤 {action['owner']} • 📅 {action['deadline']} • 📋 {action['meetingTitle']}
                    </div>
                </div>
            """
        html_body += "</div>"
    
    html_body += f"""
            <div class="footer">
                <a href="{FRONTEND_URL}" class="btn">View All Actions →</a>
                <p style="margin-top: 16px;">
                    You're receiving this because you have incomplete action items in MeetingMind.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send email
    ses.send_email(
        Source=SES_FROM_EMAIL,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': html_body}
            }
        }
    )
    
    print(f"Sent digest to {to_email}")
