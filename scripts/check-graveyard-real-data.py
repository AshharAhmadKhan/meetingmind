#!/usr/bin/env python3
"""Check real graveyard data and epitaphs"""

import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

print("=" * 70)
print("CHECKING REAL GRAVEYARD DATA")
print("=" * 70)
print()

# Scan meetings
response = table.scan(Limit=50)
meetings = response.get('Items', [])

print(f"✓ Scanned {len(meetings)} meetings")
print()

# Find graveyard items (>30 days old, incomplete)
graveyard = []
now = datetime.now(timezone.utc)

for meeting in meetings:
    action_items = meeting.get('actionItems', [])
    
    for action in action_items:
        if action.get('completed'):
            continue
        
        created_at = action.get('createdAt')
        if not created_at:
            continue
        
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (now - created_dt).days
            
            if days_old > 30:
                graveyard.append({
                    'task': action.get('task') or action.get('text', 'Unknown'),
                    'owner': action.get('owner', 'Unassigned'),
                    'daysOld': days_old,
                    'epitaph': action.get('epitaph'),
                    'epitaphGeneratedAt': action.get('epitaphGeneratedAt'),
                    'meetingTitle': meeting.get('title', 'Unknown')
                })
        except:
            pass

print(f"Found {len(graveyard)} graveyard items (>30 days old)")
print()

if len(graveyard) == 0:
    print("ℹ️  No graveyard items found. Your action items are all fresh!")
    print()
    print("To test the graveyard feature:")
    print("1. Upload an old meeting (or wait 30 days)")
    print("2. The nightly job will generate epitaphs automatically")
    print("3. Visit /graveyard to see them")
else:
    print("=" * 70)
    print("GRAVEYARD ITEMS WITH EPITAPHS:")
    print("=" * 70)
    print()
    
    with_epitaph = [g for g in graveyard if g['epitaph']]
    without_epitaph = [g for g in graveyard if not g['epitaph']]
    
    print(f"✓ {len(with_epitaph)} items have epitaphs")
    print(f"⚠ {len(without_epitaph)} items need epitaphs (will be generated tonight)")
    print()
    
    # Show first 5 with epitaphs
    for i, item in enumerate(with_epitaph[:5], 1):
        print(f"{i}. Task: {item['task'][:60]}...")
        print(f"   Owner: {item['owner']}")
        print(f"   Age: {item['daysOld']} days old")
        print(f"   Epitaph: \"{item['epitaph']}\"")
        if item['epitaphGeneratedAt']:
            gen_date = datetime.fromisoformat(item['epitaphGeneratedAt'].replace('Z', '+00:00'))
            print(f"   Generated: {gen_date.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"   From meeting: {item['meetingTitle'][:50]}")
        print()

print("=" * 70)
print("HOW TO SEE THIS IN YOUR APP:")
print("=" * 70)
print()
print("1. Open browser: https://dcfx593ywvy92.cloudfront.net")
print("2. Login with your account")
print("3. Click 'Graveyard' button (🪦)")
print("4. You'll see tombstones with AI-generated epitaphs")
print("5. Page loads INSTANTLY (<500ms) - epitaphs are pre-generated!")
print()
