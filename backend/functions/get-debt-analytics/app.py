import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['MEETINGS_TABLE']

# Constants based on research
AVG_HOURLY_RATE = 75  # $75/hour average developer salary
AVG_BLOCKED_TIME_HOURS = 3.2  # Research-backed: time blocked per incomplete action


def lambda_handler(event, context):
    """
    Get meeting debt analytics for authenticated user
    """
    try:
        # Extract user ID from Cognito authorizer (same pattern as list-meetings)
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Get query parameters for team filtering
        params = event.get('queryStringParameters') or {}
        team_id = params.get('teamId')  # optional team filter
        
        # Get all meetings for user or team
        table = dynamodb.Table(TABLE_NAME)
        
        if team_id:
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
        
        # Calculate debt analytics
        analytics = calculate_debt_analytics(meetings)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(analytics, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error calculating debt analytics: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }


def calculate_debt_analytics(meetings):
    """
    Calculate comprehensive debt analytics from all meetings
    """
    total_actions = 0
    completed_actions = 0
    incomplete_actions = 0
    
    debt_breakdown = {
        'forgotten': 0,   # >30 days old, incomplete
        'overdue': 0,     # Past deadline
        'unassigned': 0,  # No owner
        'atRisk': 0       # Other incomplete items
    }
    
    # For trend calculation (last 8 weeks)
    weekly_debt = {}
    now = datetime.now(timezone.utc)
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        
        for action in action_items:
            total_actions += 1
            
            if action.get('completed'):
                completed_actions += 1
                continue
            
            incomplete_actions += 1
            
            # Calculate cost per incomplete action
            cost = AVG_BLOCKED_TIME_HOURS * AVG_HOURLY_RATE
            
            # Determine age of action item
            created_at_str = action.get('createdAt') or meeting.get('createdAt')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    age_days = (now - created_at).days
                except:
                    age_days = 0
            else:
                age_days = 0
            
            # Categorize debt (priority order matters)
            if age_days > 30:
                debt_breakdown['forgotten'] += cost
            elif action.get('deadline'):
                try:
                    deadline = datetime.fromisoformat(action['deadline'] + 'T00:00:00+00:00')
                    if deadline < now:
                        debt_breakdown['overdue'] += cost
                    else:
                        debt_breakdown['atRisk'] += cost
                except:
                    debt_breakdown['atRisk'] += cost
            elif not action.get('owner') or action['owner'] == 'Unassigned':
                debt_breakdown['unassigned'] += cost
            else:
                debt_breakdown['atRisk'] += cost
            
            # Track weekly debt for trend
            if created_at_str:
                try:
                    week_key = created_at.strftime('%Y-W%U')
                    weekly_debt[week_key] = weekly_debt.get(week_key, 0) + cost
                except:
                    pass
    
    # Calculate total debt
    total_debt = sum(debt_breakdown.values())
    
    # Calculate completion rate
    completion_rate = completed_actions / total_actions if total_actions > 0 else 0
    
    # Generate trend data (last 8 weeks)
    trend = generate_trend_data(weekly_debt, now)
    
    # Industry benchmark (research-backed: 67% average completion rate)
    industry_benchmark = 0.67
    
    return {
        'totalDebt': round(total_debt, 2),
        'breakdown': {
            'forgotten': round(debt_breakdown['forgotten'], 2),
            'overdue': round(debt_breakdown['overdue'], 2),
            'unassigned': round(debt_breakdown['unassigned'], 2),
            'atRisk': round(debt_breakdown['atRisk'], 2)
        },
        'trend': trend,
        'completionRate': round(completion_rate, 2),
        'industryBenchmark': industry_benchmark,
        'totalActions': total_actions,
        'completedActions': completed_actions,
        'incompleteActions': incomplete_actions,
        'debtVelocity': calculate_debt_velocity(trend)
    }


def generate_trend_data(weekly_debt, now):
    """
    Generate trend data for last 8 weeks
    """
    trend = []
    
    for i in range(7, -1, -1):
        week_date = now - timedelta(weeks=i)
        week_key = week_date.strftime('%Y-W%U')
        debt = weekly_debt.get(week_key, 0)
        
        trend.append({
            'date': week_date.strftime('%Y-%m-%d'),
            'debt': round(debt, 2)
        })
    
    return trend


def calculate_debt_velocity(trend):
    """
    Calculate debt velocity (change per week)
    """
    if len(trend) < 2:
        return 0
    
    recent_debt = trend[-1]['debt']
    previous_debt = trend[-2]['debt']
    
    velocity = recent_debt - previous_debt
    return round(velocity, 2)


def decimal_default(obj):
    """JSON serializer for Decimal objects from DynamoDB"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
