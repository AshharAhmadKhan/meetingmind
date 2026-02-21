import json
import boto3
import os
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from botocore.config import Config
import sys
sys.path.append('/opt/python')  # Lambda layer path
from constants import GRAVEYARD_THRESHOLD_DAYS, EPITAPH_TTL_DAYS, EPITAPH_TASK_TRUNCATION

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://dcfx593ywvy92.cloudfront.net',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Content-Type': 'application/json'
}

# Configure Bedrock with retry logic for throttling
bedrock_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'ap-south-1'), config=bedrock_config)


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    Get all action items from all meetings for authenticated user
    Returns action items with meeting context
    """
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    
    try:
        # Extract user ID from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Get query parameters for filtering
        params = event.get('queryStringParameters') or {}
        status_filter = params.get('status', 'all')  # all, incomplete, complete
        owner_filter = params.get('owner')  # filter by owner name
        team_id = params.get('teamId')  # optional team filter
        
        # Get all meetings for user or team
        table = dynamodb.Table(TABLE_NAME)
        
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
                ExpressionAttributeValues={':tid': team_id}
            )
        else:
            # Query by userId (personal meetings)
            response = table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
        
        meetings = response.get('Items', [])
        
        # Extract all action items with meeting context
        all_actions = []
        
        for meeting in meetings:
            meeting_id = meeting.get('meetingId')
            meeting_title = meeting.get('title', 'Untitled Meeting')
            meeting_date = meeting.get('createdAt') or meeting.get('updatedAt')
            action_items = meeting.get('actionItems', [])
            
            for action in action_items:
                # Apply status filter
                is_complete = action.get('completed', False)
                if status_filter == 'incomplete' and is_complete:
                    continue
                if status_filter == 'complete' and not is_complete:
                    continue
                
                # Apply owner filter
                if owner_filter and action.get('owner') != owner_filter:
                    continue
                
                # Add meeting context to action
                action_with_context = {
                    'id': action.get('id'),
                    'task': action.get('task') or action.get('text'),  # V1 uses 'text', V2 uses 'task'
                    'owner': action.get('owner', 'Unassigned'),
                    'deadline': action.get('deadline'),
                    'completed': is_complete,
                    'completedAt': action.get('completedAt'),
                    'status': action.get('status', 'done' if is_complete else 'todo'),
                    'riskScore': action.get('riskScore', 0),
                    'riskLevel': action.get('riskLevel', 'LOW'),
                    'createdAt': action.get('createdAt'),
                    'epitaph': action.get('epitaph'),  # Include cached epitaph if exists
                    'epitaphGeneratedAt': action.get('epitaphGeneratedAt'),
                    # Meeting context (ALWAYS included)
                    'meetingId': meeting_id,
                    'meetingTitle': meeting_title,
                    'meetingDate': meeting_date
                }
                
                all_actions.append(action_with_context)
        
        # Sort by deadline (soonest first), then by risk score (highest first)
        all_actions.sort(key=lambda x: (
            x.get('deadline') or '9999-12-31',  # No deadline goes to end
            -x.get('riskScore', 0)  # Higher risk first
        ))
        
        # Add fallback message for graveyard items without cached epitaphs
        # Epitaphs are pre-generated nightly by generate-epitaphs Lambda
        now = datetime.now(timezone.utc)
        
        for action in all_actions:
            if action['completed']:
                continue
                
            # Calculate days old
            created_at = action.get('createdAt')
            if not created_at:
                continue
                
            try:
                # Parse created_at - handle both timezone-aware and naive formats
                created_at_str = created_at.replace('Z', '+00:00')
                try:
                    created_dt = datetime.fromisoformat(created_at_str)
                except ValueError:
                    # Try parsing without timezone
                    created_dt = datetime.fromisoformat(created_at)
                    # Make it timezone-aware (assume UTC)
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                
                days_old = (now - created_dt).days
                
                # Only add fallback for graveyard items without epitaph
                if days_old > GRAVEYARD_THRESHOLD_DAYS and not action.get('epitaph'):
                    # Fallback message (epitaph will be generated tonight)
                    action['epitaph'] = "Awaiting final words... (epitaph generating nightly)"
                            
            except Exception as e:
                print(f"Error processing action: {e}")
                continue
        
        # Calculate stats
        total = len(all_actions)
        completed = len([a for a in all_actions if a['completed']])
        incomplete = total - completed
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'actions': all_actions,
                'stats': {
                    'total': total,
                    'completed': completed,
                    'incomplete': incomplete,
                    'completionRate': round(completed / total, 2) if total > 0 else 0
                }
            }, default=decimal_to_float)
        }
        
    except Exception as e:
        print(f"Error getting all actions: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)}, default=decimal_to_float)
        }
