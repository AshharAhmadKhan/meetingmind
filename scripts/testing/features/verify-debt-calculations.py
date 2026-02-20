#!/usr/bin/env python3
"""
Issue #7: Verify Debt Dashboard Calculations
Comprehensive verification of debt calculation formulas
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import boto3
import json
from decimal import Decimal
from datetime import datetime, timezone

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

USER_ID = "c1c38d2a-1081-7088-7c71-0abc19a150e9"
TEAM_ID = "95febcb2-97e2-4395-bdde-da8475dbae0d"

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

print("="*70)
print("ISSUE #7: DEBT DASHBOARD CALCULATION VERIFICATION")
print("="*70)
print()

# Step 1: Get raw data from DynamoDB
print("Step 1: Fetching raw data from DynamoDB...")
print("-"*70)

response = meetings_table.query(
    KeyConditionExpression='userId = :uid',
    FilterExpression='teamId = :tid',
    ExpressionAttributeValues={
        ':uid': USER_ID,
        ':tid': TEAM_ID
    }
)

meetings = response['Items']
print(f"✅ Found {len(meetings)} meetings for team")
print()

# Step 2: Manual calculation
print("Step 2: Manual debt calculation...")
print("-"*70)

total_actions = 0
completed_actions = 0
incomplete_actions = 0

overdue_count = 0
unassigned_count = 0
at_risk_count = 0

now = datetime.now(timezone.utc)

for meeting in meetings:
    action_items = meeting.get('actionItems', [])
    
    for action in action_items:
        total_actions += 1
        
        # Check if completed
        completed = action.get('completed', False) or action.get('status') == 'done'
        
        if completed:
            completed_actions += 1
        else:
            incomplete_actions += 1
            
            # Categorize incomplete actions
            owner = action.get('owner', 'Unassigned')
            deadline = action.get('deadline')
            risk_score = float(action.get('riskScore', 0))
            
            # Overdue
            if deadline:
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    if deadline_dt < now:
                        overdue_count += 1
                        continue
                except:
                    pass
            
            # Unassigned
            if owner == 'Unassigned' or not owner:
                unassigned_count += 1
                continue
            
            # At-risk (high risk score)
            if risk_score >= 70:
                at_risk_count += 1

# Calculate debt
COST_PER_ACTION = 240  # $240 per incomplete action
total_debt = incomplete_actions * COST_PER_ACTION
overdue_debt = overdue_count * COST_PER_ACTION
unassigned_debt = unassigned_count * COST_PER_ACTION
at_risk_debt = at_risk_count * COST_PER_ACTION

completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0

print(f"Total Actions: {total_actions}")
print(f"Completed: {completed_actions}")
print(f"Incomplete: {incomplete_actions}")
print()
print(f"Debt Breakdown:")
print(f"  Overdue: {overdue_count} actions × $240 = ${overdue_debt:,}")
print(f"  Unassigned: {unassigned_count} actions × $240 = ${unassigned_debt:,}")
print(f"  At-Risk: {at_risk_count} actions × $240 = ${at_risk_debt:,}")
print(f"  Total Debt: ${total_debt:,}")
print()
print(f"Completion Rate: {completion_rate:.1f}%")
print()

# Step 3: Call Lambda function
print("Step 3: Calling get-debt-analytics Lambda...")
print("-"*70)

event = {
    'httpMethod': 'GET',
    'requestContext': {
        'authorizer': {
            'claims': {
                'sub': USER_ID
            }
        }
    },
    'queryStringParameters': {
        'teamId': TEAM_ID
    }
}

try:
    response = lambda_client.invoke(
        FunctionName='meetingmind-get-debt-analytics',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    
    result = json.loads(response['Payload'].read())
    
    if response['StatusCode'] == 200:
        print("✅ Lambda invoked successfully")
        print()
        
        # Debug: print raw response
        print("Raw Lambda response:")
        print(json.dumps(result, indent=2, default=decimal_default))
        print()
        
        body = json.loads(result['body'])
        
        print("Lambda Response:")
        print(f"  Total Debt: ${body.get('totalDebt', 'N/A'):,}")
        print(f"  Total Actions: {body.get('totalActions', 'N/A')}")
        print(f"  Completed: {body.get('completedActions', 'N/A')}")
        print(f"  Incomplete: {body.get('incompleteActions', 'N/A')}")
        
        # Lambda returns completion rate as decimal (0.22), convert to percentage
        lambda_completion_rate = body.get('completionRate', 0) * 100
        print(f"  Completion Rate: {lambda_completion_rate:.1f}%")
        print()
        
        if 'debtBreakdown' in body:
            print(f"  Debt Breakdown:")
            print(f"    Overdue: ${body['debtBreakdown'].get('overdue', 0):,}")
            print(f"    Unassigned: ${body['debtBreakdown'].get('unassigned', 0):,}")
            print(f"    At-Risk: ${body['debtBreakdown'].get('atRisk', 0):,}")
            print()
        
        # Check if we have the required fields
        if 'totalDebt' not in body:
            print("❌ Lambda response missing 'totalDebt' field")
            print("Available fields:", list(body.keys()))
            sys.exit(1)
        
        # Step 4: Verify calculations match
        print("Step 4: Verifying calculations...")
        print("-"*70)
        
        errors = []
        
        if body['totalActions'] != total_actions:
            errors.append(f"Total actions mismatch: Lambda={body['totalActions']}, Manual={total_actions}")
        
        if body['completedActions'] != completed_actions:
            errors.append(f"Completed actions mismatch: Lambda={body['completedActions']}, Manual={completed_actions}")
        
        if body['incompleteActions'] != incomplete_actions:
            errors.append(f"Incomplete actions mismatch: Lambda={body['incompleteActions']}, Manual={incomplete_actions}")
        
        if body['totalDebt'] != total_debt:
            errors.append(f"Total debt mismatch: Lambda=${body['totalDebt']}, Manual=${total_debt}")
        
        # Lambda returns completion rate as decimal (0.22), convert to percentage for comparison
        lambda_completion_rate = body['completionRate'] * 100
        if abs(lambda_completion_rate - completion_rate) > 1.0:  # Allow 1% tolerance for rounding
            errors.append(f"Completion rate mismatch: Lambda={lambda_completion_rate:.1f}%, Manual={completion_rate:.1f}%")
        
        if errors:
            print("❌ CALCULATION ERRORS FOUND:")
            for error in errors:
                print(f"  • {error}")
            print()
            sys.exit(1)
        else:
            print("✅ All calculations match!")
            print()
            print("="*70)
            print("✅ ISSUE #7 VERIFIED: Debt calculations are correct")
            print("="*70)
            print()
            print("Summary:")
            print(f"  • Manual calculation: ${total_debt:,}")
            print(f"  • Lambda calculation: ${body['totalDebt']:,}")
            print(f"  • Match: ✅")
            print()
            print("Formula verified:")
            print(f"  • Cost per action: $240")
            print(f"  • Incomplete actions: {incomplete_actions}")
            print(f"  • Total debt: {incomplete_actions} × $240 = ${total_debt:,}")
            print()
            sys.exit(0)
    else:
        print(f"❌ Lambda returned error: {result}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error calling Lambda: {e}")
    sys.exit(1)
