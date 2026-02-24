#!/usr/bin/env python3
"""Diagnose Yatra meeting health score issue."""

import boto3
from decimal import Decimal

REGION = 'ap-south-1'
TABLE_NAME = 'meetingmind-meetings'
MEETING_ID = '6f1f9423-a000-436e-a862-c96edb9f356d'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# Scan for the meeting
response = table.scan(
    FilterExpression='meetingId = :mid',
    ExpressionAttributeValues={':mid': MEETING_ID}
)

if not response['Items']:
    print('Meeting not found')
    exit(1)

meeting = response['Items'][0]
actions = meeting.get('actionItems', [])

total = len(actions)
completed = sum(1 for a in actions if a.get('completed'))

print('MEETING DIAGNOSIS')
print('=' * 80)
print(f'Meeting ID: {meeting["meetingId"]}')
print(f'User ID: {meeting["userId"]}')
print(f'Title: {meeting.get("title", "N/A")}')
print()
print('HEALTH METRICS IN DYNAMODB:')
print(f'  Health Score: {meeting.get("healthScore", "N/A")}/100')
print(f'  Health Grade: {meeting.get("healthGrade", "N/A")}')
print(f'  Health Label: {meeting.get("healthLabel", "N/A")}')
print()
print('ACTION ITEMS:')
print(f'  Total: {total}')
print(f'  Completed: {completed}')
print(f'  Completion Rate: {(completed/total*100):.1f}%')
print()
print('EXPECTED HEALTH SCORE:')
owned = sum(1 for a in actions if a.get('owner') and a['owner'] != 'Unassigned')
risk_scores = [float(a.get('riskScore', 0)) for a in actions]
avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

completion_rate = (completed / total) * 40
owner_rate = (owned / total) * 30
risk_inverted = ((100 - avg_risk) / 100) * 20
recency = 10

expected_score = completion_rate + owner_rate + risk_inverted + recency

if expected_score >= 90:
    expected_grade = 'A'
elif expected_score >= 80:
    expected_grade = 'B'
elif expected_score >= 70:
    expected_grade = 'C'
elif expected_score >= 60:
    expected_grade = 'D'
else:
    expected_grade = 'F'

print(f'  Expected Score: {expected_score:.1f}/100')
print(f'  Expected Grade: {expected_grade}')
print()
print('DIAGNOSIS:')
stored_score = float(meeting.get('healthScore', 0))
stored_grade = meeting.get('healthGrade', 'N/A')

if abs(expected_score - stored_score) > 5:
    print(f'  ❌ MISMATCH: Score difference of {abs(expected_score - stored_score):.1f} points')
    print(f'  ❌ Grade stored: {stored_grade}, expected: {expected_grade}')
    print()
    print('POSSIBLE CAUSES:')
    print('  1. Health score not recalculating after action updates')
    print('  2. Lambda function error during update')
    print('  3. Layer not properly attached')
else:
    print(f'  ✅ Score matches (difference: {abs(expected_score - stored_score):.1f} points)')
    print(f'  ✅ Grade: {stored_grade}')

print()
print('CHECKING CLOUDWATCH LOGS...')
print('(Check update-action Lambda logs for errors)')
