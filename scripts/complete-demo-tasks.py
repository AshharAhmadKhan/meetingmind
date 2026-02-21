#!/usr/bin/env python3
"""
Mark specific tasks as completed in demo meetings to make it look authentic.

Strategy:
- Graveyard meetings: Complete some tasks (they tried but gave up)
- Should We Pivot: Complete the one task (discussion happened)
- Weekly Check-In: Complete 2-3 tasks (some progress made)
- Demo Prep Sync: Leave mostly incomplete (only 3 days old)
"""

import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

def complete_task(meeting_id, task_indices):
    """Mark specific tasks as completed in a meeting."""
    response = table.get_item(Key={'userId': user_id, 'meetingId': meeting_id})
    meeting = response['Item']
    
    action_items = meeting.get('actionItems', [])
    completed_count = 0
    
    for idx in task_indices:
        if idx < len(action_items):
            action_items[idx]['completed'] = True
            action_items[idx]['completedAt'] = datetime.now(timezone.utc).isoformat()
            completed_count += 1
    
    table.update_item(
        Key={'userId': user_id, 'meetingId': meeting_id},
        UpdateExpression='SET actionItems = :ai',
        ExpressionAttributeValues={':ai': action_items}
    )
    
    print(f"✅ {meeting['title']}: Marked {completed_count} tasks as completed")
    return completed_count

print("Completing tasks to make demo look authentic...")
print("=" * 80)

# GRAVEYARD MEETINGS (old project that died)
# Kickoff Meeting: Complete 2 out of 7 (they started but gave up)
complete_task('8aea38ac-d337-4ae0-92c7-297c871cb107', [0, 3])  # Designs, landing page

# Last Week Of The Project: Complete 3 out of 7 (made some progress before dying)
complete_task('ee766a31-6610-4408-8e0b-01fe54635b96', [0, 2, 4])  # API endpoints, logo, beta form

print()
print("RECENT MEETINGS (current attempt)")
print("-" * 80)

# Should We Pivot: Complete the 1 task (discussion in group chat)
complete_task('4a7c7a8d-b9ba-4668-b1da-3b5cd8bf1ac8', [0])  # Discuss in chat

# Weekly Check-In: Complete 3 out of 5 (showing progress)
complete_task('23fa629a-1250-4b94-94d6-2ada2ca19e8e', [0, 2, 3])  # Auth bug, profile page, email check

# Demo Prep Sync: Complete 1 out of 6 (just started, demo in 7 days)
complete_task('f9299610-dc59-406d-9729-790cfc9dde81', [5])  # Recruit testers (easiest task)

print()
print("=" * 80)
print("✅ Task completion updated!")
print()
print("Summary:")
print("  Graveyard meetings: Some tasks done (project died)")
print("  Should We Pivot: Discussion completed")
print("  Weekly Check-In: Good progress (3/5 done)")
print("  Demo Prep Sync: Just started (1/6 done, demo in 7 days)")
