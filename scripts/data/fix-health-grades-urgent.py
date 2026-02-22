#!/usr/bin/env python3
"""
URGENT FIX: Correct healthGrade field for all meetings
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

demo_user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

def get_grade_letter(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def get_health_label(grade):
    """Get health label for grade"""
    labels = {
        'A': 'Excellent meeting',
        'B': 'Strong meeting',
        'C': 'Average meeting',
        'D': 'Poor meeting',
        'F': 'Failed meeting'
    }
    return labels.get(grade, 'Unknown')

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': demo_user_id},
    ScanIndexForward=False
)

print("URGENT: Fixing healthGrade fields")
print("="*80)

for meeting in response['Items']:
    title = meeting.get('title')
    health_score = meeting.get('healthScore', 0)
    current_grade = meeting.get('healthGrade')
    
    # Calculate correct grade
    correct_grade = get_grade_letter(health_score)
    correct_label = get_health_label(correct_grade)
    
    print(f"\n{title}")
    print(f"  healthScore: {health_score}")
    print(f"  Current healthGrade: {current_grade}")
    print(f"  Correct healthGrade: {correct_grade}")
    
    if current_grade != correct_grade:
        print(f"  ❌ WRONG! Fixing...")
        
        # Update the meeting
        table.update_item(
            Key={
                'userId': demo_user_id,
                'meetingId': meeting['meetingId']
            },
            UpdateExpression='SET healthGrade = :grade, healthLabel = :label',
            ExpressionAttributeValues={
                ':grade': correct_grade,
                ':label': correct_label
            }
        )
        print(f"  ✅ Fixed: {current_grade} → {correct_grade}")
    else:
        print(f"  ✅ Already correct")

print("\n" + "="*80)
print("✅ All healthGrade fields fixed!")
print("\nExpected results:")
print("  Kickoff Meeting: F (55)")
print("  Mid-Project Crisis: F (50)")
print("  Last Attempt Before Pivot: F (48)")
print("  Should We Pivot: A (95)")
print("  Weekly Check-In: B (85)")
