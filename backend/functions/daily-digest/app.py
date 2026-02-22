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
    """Send HTML email digest with professional Gmail-style formatting"""
    
    subject = f"Daily Action Items Summary — {digest_data['total_incomplete']} items need attention"
    
    # Build professional HTML email (matching other templates)
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {{ 
                font-family: 'DM Mono', 'Courier New', monospace; 
                background-color: #0c0c09; 
                margin: 0; 
                padding: 0; 
                -webkit-font-smoothing: antialiased;
            }}
            .email-container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: #0c0c09;
            }}
            .email-wrapper {{ 
                background-color: #141410; 
                border: 2px solid #2a2a20;
                border-radius: 8px;
                overflow: hidden;
                margin: 40px 20px;
            }}
            .header {{ 
                background: linear-gradient(135deg, #0f0f0c 0%, #141410 100%);
                padding: 32px 40px;
                border-bottom: 2px solid #c8f04a;
                position: relative;
            }}
            .header::after {{
                content: '';
                position: absolute;
                bottom: -2px;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, #c8f04a 0%, transparent 100%);
            }}
            .logo-container {{
                display: flex;
                align-items: baseline;
                gap: 2px;
            }}
            .logo-meeting {{ 
                font-family: 'Playfair Display', serif;
                color: #c8f04a; 
                font-size: 28px; 
                font-weight: 900; 
                margin: 0;
                letter-spacing: -0.5px;
            }}
            .logo-mind {{
                font-family: 'Playfair Display', serif;
                color: #f0ece0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.3px;
            }}
            .header-subtitle {{
                color: #8a8a74;
                font-size: 10px;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                margin-top: 8px;
            }}
            .content {{ 
                padding: 40px; 
                background-color: #141410;
            }}
            .greeting {{ 
                color: #f0ece0; 
                font-size: 14px; 
                font-weight: 400; 
                margin: 0 0 24px 0;
                line-height: 1.6;
                letter-spacing: 0.02em;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin: 24px 0;
            }}
            .stat-card {{
                background-color: #0f0f0c;
                border: 1px solid #2a2a20;
                border-radius: 6px;
                padding: 20px;
                text-align: center;
            }}
            .stat-number {{
                font-family: 'Playfair Display', serif;
                font-size: 32px;
                font-weight: 700;
                color: #c8f04a;
                margin: 0 0 8px 0;
            }}
            .stat-label {{
                color: #6b7260;
                font-size: 10px;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            }}
            .section-label {{ 
                color: #8a8a74; 
                font-size: 9px; 
                font-weight: 500;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                margin: 32px 0 16px 0;
            }}
            .action-list {{
                background-color: #0f0f0c;
                border: 1px solid #2a2a20;
                border-radius: 6px;
                padding: 16px;
                margin: 16px 0;
            }}
            .action-item {{
                padding: 16px;
                border-bottom: 1px solid #1a1a14;
            }}
            .action-item:last-child {{
                border-bottom: none;
            }}
            .action-item.critical {{
                border-left: 3px solid #e87a6a;
                padding-left: 13px;
            }}
            .action-item.overdue {{
                border-left: 3px solid #d93025;
                padding-left: 13px;
            }}
            .action-item.upcoming {{
                border-left: 3px solid #e8c06a;
                padding-left: 13px;
            }}
            .action-task {{
                color: #f0ece0;
                font-size: 13px;
                line-height: 1.6;
                margin: 0 0 8px 0;
            }}
            .action-meta {{
                color: #6b7260;
                font-size: 11px;
                line-height: 1.4;
            }}
            .meta-row {{
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }}
            .meta-item {{
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .cta-section {{
                text-align: center;
                margin: 32px 0;
            }}
            .cta-button {{
                display: inline-block;
                background-color: #c8f04a;
                color: #0c0c09;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
                letter-spacing: 0.1em;
                text-transform: uppercase;
            }}
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, #2a2a20 50%, transparent 100%);
                margin: 32px 0;
            }}
            .footer {{ 
                background-color: #0f0f0c; 
                padding: 28px 40px;
                border-top: 1px solid #2a2a20;
                text-align: center;
            }}
            .footer-brand {{ 
                color: #f0ece0; 
                font-size: 13px; 
                font-weight: 500;
                margin: 0 0 8px 0;
                letter-spacing: 0.05em;
            }}
            .footer-tagline {{
                color: #6b7260;
                font-size: 10px;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin: 0 0 16px 0;
            }}
            .footer-meta {{ 
                color: #555548; 
                font-size: 10px; 
                line-height: 1.6;
                margin: 4px 0;
                letter-spacing: 0.03em;
            }}
            .accent-dot {{
                display: inline-block;
                width: 4px;
                height: 4px;
                background-color: #c8f04a;
                border-radius: 50%;
                margin: 0 8px;
                vertical-align: middle;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-wrapper">
                <div class="header">
                    <div class="logo-container">
                        <span class="logo-meeting">Meeting</span>
                        <span class="logo-mind">Mind</span>
                    </div>
                    <div class="header-subtitle">Daily Action Items Summary</div>
                </div>
                
                <div class="content">
                    <p class="greeting">Good morning,</p>
                    <p class="greeting">Here is your daily summary of pending action items and upcoming deadlines.</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{digest_data['completion_rate']}%</div>
                            <div class="stat-label">Completion</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{digest_data['completed_actions']}</div>
                            <div class="stat-label">Completed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{digest_data['total_incomplete']}</div>
                            <div class="stat-label">Pending</div>
                        </div>
                    </div>
    """
    
    # Critical items
    if digest_data['critical']:
        html_body += f"""
                    <div class="section-label">Critical — Due Today or Tomorrow</div>
                    <div class="action-list">
        """
        for action in digest_data['critical'][:5]:  # Limit to 5
            html_body += f"""
                        <div class="action-item critical">
                            <div class="action-task">{action['task']}</div>
                            <div class="action-meta">
                                <div class="meta-row">
                                    <div class="meta-item">Owner: {action['owner']}</div>
                                    <div class="meta-item">Due: {action['deadline']}</div>
                                    <div class="meta-item">Meeting: {action['meetingTitle']}</div>
                                </div>
                            </div>
                        </div>
            """
        html_body += """
                    </div>
        """
    
    # Overdue items
    if digest_data['overdue']:
        html_body += f"""
                    <div class="section-label">Overdue — Past Deadline</div>
                    <div class="action-list">
        """
        for action in digest_data['overdue'][:5]:  # Limit to 5
            html_body += f"""
                        <div class="action-item overdue">
                            <div class="action-task">{action['task']}</div>
                            <div class="action-meta">
                                <div class="meta-row">
                                    <div class="meta-item">Owner: {action['owner']}</div>
                                    <div class="meta-item">Due: {action['deadline']}</div>
                                    <div class="meta-item">Meeting: {action['meetingTitle']}</div>
                                </div>
                            </div>
                        </div>
            """
        html_body += """
                    </div>
        """
    
    # Upcoming items
    if digest_data['upcoming']:
        html_body += f"""
                    <div class="section-label">Upcoming — Due This Week</div>
                    <div class="action-list">
        """
        for action in digest_data['upcoming'][:5]:  # Limit to 5
            html_body += f"""
                        <div class="action-item upcoming">
                            <div class="action-task">{action['task']}</div>
                            <div class="action-meta">
                                <div class="meta-row">
                                    <div class="meta-item">Owner: {action['owner']}</div>
                                    <div class="meta-item">Due: {action['deadline']}</div>
                                    <div class="meta-item">Meeting: {action['meetingTitle']}</div>
                                </div>
                            </div>
                        </div>
            """
        html_body += """
                    </div>
        """
    
    html_body += f"""
                    <div class="cta-section">
                        <a href="{FRONTEND_URL}" class="cta-button">View All Actions</a>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <p style="color: #6b7260; font-size: 11px; line-height: 1.6; margin: 0; text-align: center;">
                        Automated daily summary from MeetingMind<span class="accent-dot"></span>Sent at 9:00 AM IST
                    </p>
                </div>
                
                <div class="footer">
                    <p class="footer-brand">MeetingMind</p>
                    <p class="footer-tagline">Transform Meetings Into Action</p>
                    <p class="footer-meta">Powered by AWS<span class="accent-dot"></span>Region: ap-south-1</p>
                    <p class="footer-meta" style="margin-top: 12px;">© 2026 MeetingMind. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send email
    ses.send_email(
        Source=f'MeetingMind <{SES_FROM_EMAIL}>',
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': html_body}
            }
        }
    )
    
    print(f"Sent digest to {to_email}")
