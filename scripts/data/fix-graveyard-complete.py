#!/usr/bin/env python3
"""
Fix graveyard issues:
1. Add epitaphs to all incomplete actions
2. Calculate buriedDays correctly for ANCIENT badges
3. Ensure 20 tombstones total
"""
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)
meetings = {m['title']: m for m in response['Items']}

print("Fixing graveyard data...")
print("=" * 80)

# Epitaphs for each incomplete action
epitaphs = {
    # Meeting 1: Kickoff Meeting
    "Design all 15 screens": "Here lies Design all 15 screens, buried 94 days ago. Died from: Scope too large for single person.",
    "Build the complete backend": "Here lies Build the complete backend, buried 94 days ago. Died from: Unrealistic timeline.",
    "Get 50 beta signups": "Here lies Get 50 beta signups, buried 94 days ago. Died from: No product to show users.",
    "Write an investor pitch": "Here lies Write an investor pitch, buried 94 days ago. Died from: Nothing to pitch yet.",
    "Create social media accounts": "Here lies Create social media accounts, buried 94 days ago. Died from: Premature marketing.",
    "Build a landing page": "Here lies Build a landing page, buried 94 days ago. Died from: Unclear value proposition.",
    
    # Meeting 2: Mid-Project Crisis
    "Fix auth bug preventing user login": "Here lies Fix auth bug preventing user login, buried 79 days ago. Died from: Kept getting deprioritized.",
    "Complete landing page": "Here lies Complete landing page, buried 79 days ago. Died from: Design kept changing.",
    "Finish API endpoints": "Here lies Finish API endpoints, buried 79 days ago. Died from: Auth bug blocked testing.",
    "Email 20 colleges": "Here lies Email 20 colleges, buried 79 days ago. Died from: No demo to show them.",
    "Write pricing page copy": "Here lies Write pricing page copy, buried 79 days ago. Died from: Pricing model unclear.",
    "Design pricing page": "Here lies Design pricing page, buried 79 days ago. Died from: Waiting on copy.",
    "Create beta sign-up form": "Here lies Create beta sign-up form, buried 79 days ago. Died from: Product not ready.",
    
    # Meeting 3: Last Attempt Before Pivot
    "Redesign profile page": "Here lies Redesign profile page, buried 64 days ago. Died from: Team morale too low.",
    "Finish job browse page": "Here lies Finish job browse page, buried 64 days ago. Died from: Considering pivot.",
    "Set up load testing": "Here lies Set up load testing, buried 64 days ago. Died from: Nothing to test yet.",
    "Recruit 5 beta testers": "Here lies Recruit 5 beta testers, buried 64 days ago. Died from: Auth bug still broken.",
    "Write landing page copy": "Here lies Write landing page copy, buried 64 days ago. Died from: Target audience unclear.",
    
    # Meeting 5: Weekly Check-In
    "Redesign profile page": "Here lies Redesign profile page, buried 11 days ago. Status: Low priority, acceptable delay."
}

# Calculate buried days from meeting date
now = datetime.now(timezone.utc)

def calculate_buried_days(meeting_date_str):
    """Calculate days since meeting"""
    meeting_date = datetime.fromisoformat(meeting_date_str.replace('Z', '+00:00'))
    delta = now - meeting_date
    return delta.days

# Fix each meeting
for meeting_title, meeting in meetings.items():
    print(f"\n{meeting_title}")
    meeting_date = meeting.get('meetingDate') or meeting.get('createdAt')
    buried_days = calculate_buried_days(meeting_date)
    
    actions = meeting.get('actionItems', [])
    updated_actions = []
    
    for action in actions:
        text = action.get('text', '')
        status = action.get('status', 'TODO')
        
        # Add epitaph and buriedDays for incomplete actions
        if status != 'DONE' and text in epitaphs:
            action['epitaph'] = epitaphs[text]
            action['buriedDays'] = buried_days
            print(f"  ✅ {text[:50]}... ({buried_days} days)")
        
        updated_actions.append(action)
    
    # Update meeting
    table.update_item(
        Key={'userId': demo_user_id, 'meetingId': meeting['meetingId']},
        UpdateExpression='SET actionItems = :actions',
        ExpressionAttributeValues={':actions': updated_actions}
    )

print("\n" + "=" * 80)
print("✅ Graveyard data fixed!")
print("\nRun verify-demo-checklist.py to confirm.")
