#!/usr/bin/env python3
"""
Check what healthScore values are actually stored in the database
"""
import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

response = meetings_table.scan()
meetings = response.get('Items', [])

print("Stored healthScore values in database:\n")

for meeting in meetings:
    title = meeting.get('title', 'Untitled')
    health_score = meeting.get('healthScore')
    
    print(f"{title}:")
    print(f"  healthScore field: {health_score}")
    print(f"  Type: {type(health_score)}")
    if isinstance(health_score, dict):
        print(f"  Score: {health_score.get('score')}")
        print(f"  Grade: {health_score.get('grade')}")
    print()
