#!/usr/bin/env python3
"""
Check pattern recognition for all users in the meeting
"""

import boto3
import json
from decimal import Decimal
from collections import Counter

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

print("="*70)
print("PATTERN RECOGNITION CHECK - ALL USERS")
print("="*70)

# Get the New Test meeting
response = meetings_table.scan(
    FilterExpression='contains(title, :title)',
    ExpressionAttributeValues={':title': 'New Test'}
)

meetings = response.get('Items', [])

if not meetings:
    print("\n❌ No 'New Test' meeting found!")
else:
    meeting = meetings[0]
    action_items = meeting.get('actionItems', [])
    
    # Analyze patterns by owner
    owner_patterns = {}
    
    for action in action_items:
        owner = action.get('owner', 'Unassigned')
        task = action.get('task', '')
        deadline = action.get('deadline')
        risk_level = action.get('riskLevel', 'UNKNOWN')
        
        if owner not in owner_patterns:
            owner_patterns[owner] = {
                'tasks': [],
                'total_tasks': 0,
                'has_deadlines': 0,
                'no_deadlines': 0,
                'risk_levels': []
            }
        
        owner_patterns[owner]['tasks'].append(task[:50])
        owner_patterns[owner]['total_tasks'] += 1
        owner_patterns[owner]['risk_levels'].append(risk_level)
        
        if deadline:
            owner_patterns[owner]['has_deadlines'] += 1
        else:
            owner_patterns[owner]['no_deadlines'] += 1
    
    print(f"\nPattern Analysis by Owner:\n")
    
    for owner, patterns in owner_patterns.items():
        print(f"{'='*70}")
        print(f"Owner: {owner}")
        print(f"{'='*70}")
        print(f"  Total Tasks: {patterns['total_tasks']}")
        print(f"  With Deadlines: {patterns['has_deadlines']}")
        print(f"  Without Deadlines: {patterns['no_deadlines']}")
        
        # Risk distribution
        risk_counter = Counter(patterns['risk_levels'])
        print(f"  Risk Distribution:")
        for risk, count in risk_counter.items():
            print(f"    - {risk}: {count}")
        
        print(f"  Tasks:")
        for i, task in enumerate(patterns['tasks'], 1):
            print(f"    {i}. {task}...")
        
        # Pattern detection
        print(f"\n  Detected Patterns:")
        
        # Check for overload
        if patterns['total_tasks'] >= 4:
            print(f"    ⚠️  OVERLOAD: {owner} has {patterns['total_tasks']} tasks (high workload)")
        elif patterns['total_tasks'] >= 3:
            print(f"    ⚠️  BUSY: {owner} has {patterns['total_tasks']} tasks")
        else:
            print(f"    ✓ BALANCED: {owner} has {patterns['total_tasks']} tasks")
        
        # Check for missing deadlines
        if patterns['no_deadlines'] > 0:
            pct = (patterns['no_deadlines'] / patterns['total_tasks']) * 100
            print(f"    ⚠️  VAGUE: {patterns['no_deadlines']}/{patterns['total_tasks']} tasks ({pct:.0f}%) lack deadlines")
        else:
            print(f"    ✓ CLEAR: All tasks have deadlines")
        
        # Check for high risk
        high_risk_count = sum(1 for r in patterns['risk_levels'] if r in ['HIGH', 'CRITICAL'])
        if high_risk_count > 0:
            print(f"    ⚠️  AT RISK: {high_risk_count} high-risk tasks")
        else:
            print(f"    ✓ LOW RISK: No high-risk tasks")
        
        print()
    
    # Overall patterns
    print(f"{'='*70}")
    print(f"OVERALL MEETING PATTERNS")
    print(f"{'='*70}")
    
    total_owners = len(owner_patterns)
    total_tasks = len(action_items)
    avg_tasks = total_tasks / total_owners if total_owners > 0 else 0
    
    print(f"  Total Owners: {total_owners}")
    print(f"  Total Tasks: {total_tasks}")
    print(f"  Average Tasks per Owner: {avg_tasks:.1f}")
    
    # Check for imbalance
    task_counts = [p['total_tasks'] for p in owner_patterns.values()]
    max_tasks = max(task_counts) if task_counts else 0
    min_tasks = min(task_counts) if task_counts else 0
    
    if max_tasks - min_tasks > 2:
        print(f"\n  ⚠️  IMBALANCE DETECTED:")
        print(f"     Max: {max_tasks} tasks, Min: {min_tasks} tasks")
        print(f"     Difference: {max_tasks - min_tasks} tasks")
        print(f"     Recommendation: Redistribute workload")
    else:
        print(f"\n  ✓ BALANCED WORKLOAD:")
        print(f"     Max: {max_tasks} tasks, Min: {min_tasks} tasks")
        print(f"     Difference: {max_tasks - min_tasks} tasks")
    
    # Check for deadline coverage
    total_with_deadlines = sum(p['has_deadlines'] for p in owner_patterns.values())
    deadline_coverage = (total_with_deadlines / total_tasks) * 100 if total_tasks > 0 else 0
    
    print(f"\n  Deadline Coverage: {total_with_deadlines}/{total_tasks} ({deadline_coverage:.0f}%)")
    if deadline_coverage < 80:
        print(f"     ⚠️  LOW: Many tasks lack deadlines")
    else:
        print(f"     ✓ GOOD: Most tasks have deadlines")

print("\n" + "="*70)
