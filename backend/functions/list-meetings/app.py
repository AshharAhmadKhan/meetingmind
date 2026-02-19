import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

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


def calculate_health_score(meeting):
    """
    Calculate meeting health score (0-100) and letter grade.
    
    Formula:
    - Completion rate: 40%
    - Owner assignment rate: 30%
    - Inverted risk score: 20%
    - Recency bonus: 10%
    """
    action_items = meeting.get('actionItems', [])
    
    if not action_items:
        # No actions = perfect score (nothing to fail)
        return {'score': 100, 'grade': 'A', 'label': 'Perfect meeting'}
    
    total = len(action_items)
    completed = sum(1 for a in action_items if a.get('completed', False))
    owned = sum(1 for a in action_items if a.get('owner') and a['owner'] != 'Unassigned')
    
    # Calculate average risk score - convert Decimal to float
    risk_scores = [float(a.get('riskScore', 0)) for a in action_items]
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    # Calculate recency bonus (meetings < 7 days old get bonus)
    created_at = meeting.get('createdAt')
    recency_bonus = 1.0
    if created_at:
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.now(timezone.utc) - created_dt).days
            recency_bonus = 1.0 if days_old < 7 else 0.8
        except:
            pass
    
    # Calculate weighted score
    completion_rate = (completed / total) * 40
    owner_rate = (owned / total) * 30
    risk_inverted = ((100 - avg_risk) / 100) * 20
    recency_component = recency_bonus * 10
    
    score = completion_rate + owner_rate + risk_inverted + recency_component
    score = min(max(score, 0), 100)  # Clamp to 0-100
    
    # Determine grade and label
    if score >= 90:
        grade, label = 'A', 'Excellent meeting'
    elif score >= 80:
        grade, label = 'B', 'Strong meeting'
    elif score >= 70:
        grade, label = 'C', 'Average meeting'
    elif score >= 60:
        grade, label = 'D', 'Poor meeting'
    else:
        grade, label = 'F', 'Failed meeting'
    
    return {
        'score': round(score, 1),
        'grade': grade,
        'label': label
    }


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    user_id = event['requestContext']['authorizer']['claims']['sub']
    table   = dynamodb.Table(TABLE_NAME)
    
    # Get query parameters for team filtering
    params = event.get('queryStringParameters') or {}
    team_id = params.get('teamId')

    # Query by teamId if provided, otherwise by userId
    if team_id:
        # Validate user is member of the team
        teams_table = dynamodb.Table(os.environ['TEAMS_TABLE'])
        team_response = teams_table.get_item(Key={'teamId': team_id})
        
        if 'Item' not in team_response:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Team not found'})
            }
        
        team = team_response['Item']
        members = team.get('members', [])
        
        # Check if user is a member of the team
        # Members can be either strings (old format) or dicts (new format)
        member_ids = []
        for member in members:
            if isinstance(member, dict):
                member_ids.append(member.get('userId'))
            else:
                member_ids.append(member)
        
        if user_id not in member_ids:
            return {
                'statusCode': 403,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'You are not a member of this team'})
            }
        
        # Query by teamId using GSI
        response = table.query(
            IndexName='teamId-createdAt-index',
            KeyConditionExpression='teamId = :tid',
            ExpressionAttributeValues={':tid': team_id},
            ScanIndexForward=False,   # newest first
        )
    else:
        # Query by userId (personal meetings)
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,   # newest first
        )

    meetings = response.get('Items', [])
    
    # Calculate health score and ghost status for each meeting
    for meeting in meetings:
        if meeting.get('status') == 'DONE':
            health = calculate_health_score(meeting)
            meeting['healthScore'] = health['score']
            meeting['healthGrade'] = health['grade']
            meeting['healthLabel'] = health['label']
            
            # Check if ghost meeting (zero decisions AND zero actions)
            decisions = meeting.get('decisions', [])
            action_items = meeting.get('actionItems', [])
            meeting['isGhost'] = len(decisions) == 0 and len(action_items) == 0
        
        # Remove large fields from list view
        meeting.pop('transcript', None)
        meeting.pop('actionItems', None)  # Don't send full action items in list
        meeting.pop('embedding', None)
    
    # Sort newest first by createdAt (fallback to updatedAt for old meetings)
    meetings.sort(key=lambda x: x.get('createdAt') or x.get('updatedAt', ''), reverse=True)

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'meetings': meetings}, default=decimal_to_float)
    }
