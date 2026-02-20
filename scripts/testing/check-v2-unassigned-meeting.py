#!/usr/bin/env python3
"""
Check if there are any V2 meetings with all unassigned tasks
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

response = meetings_table.scan()
meetings = response.get('Items', [])

print("Looking for meetings with all unassigned tasks...\n")

for meeting in meetings:
    title = meeting.get('title', 'Untitled')
    action_items = meeting.get('actionItems', [])
    
    if not action_items:
        continue
    
    total = len(action_items)
    unassigned = sum(1 for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned')
    
    if unassigned == total:
        health_score = meeting.get('healthScore', {})
        roi_data = meeting.get('roi', {})
        
        print(f"Meeting: {title}")
        print(f"  All {total} actions are unassigned")
        print(f"  Health Score: {health_score}")
        print(f"  ROI: {roi_data}")
        print()
