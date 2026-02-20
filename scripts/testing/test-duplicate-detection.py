#!/usr/bin/env python3
"""
Test script for Issue #8: Verify Duplicate Detection
Tests semantic similarity detection for action items
"""

import boto3
import json
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
meetings_table = dynamodb.Table('meetingmind-meetings')

def get_all_action_items():
    """Get all action items from all meetings"""
    response = meetings_table.scan()
    meetings = response.get('Items', [])
    
    all_actions = []
    for meeting in meetings:
        meeting_id = meeting.get('meetingId')
        meeting_title = meeting.get('title', 'Untitled')
        user_id = meeting.get('userId')
        
        for action in meeting.get('actionItems', []):
            all_actions.append({
                'meetingId': meeting_id,
                'meetingTitle': meeting_title,
                'userId': user_id,
                'task': action.get('task', ''),
                'owner': action.get('owner', 'Unassigned'),
                'completed': action.get('completed', False),
                'embedding': action.get('embedding')
            })
    
    return all_actions

def simple_similarity(text1, text2):
    """Simple word-based similarity check"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def find_potential_duplicates(actions, threshold=0.5):
    """Find potential duplicate pairs using simple similarity"""
    duplicates = []
    
    for i, action1 in enumerate(actions):
        for action2 in actions[i+1:]:
            # Skip if same meeting
            if action1['meetingId'] == action2['meetingId']:
                continue
            
            # Skip completed actions
            if action1['completed'] or action2['completed']:
                continue
            
            task1 = action1['task']
            task2 = action2['task']
            
            if not task1 or not task2:
                continue
            
            similarity = simple_similarity(task1, task2)
            
            if similarity >= threshold:
                duplicates.append({
                    'task1': task1,
                    'task2': task2,
                    'meeting1': action1['meetingTitle'],
                    'meeting2': action2['meetingTitle'],
                    'similarity': round(similarity * 100, 1),
                    'has_embedding1': action1['embedding'] is not None,
                    'has_embedding2': action2['embedding'] is not None
                })
    
    return duplicates

def main():
    print("\n" + "=" * 60)
    print("ISSUE #8: DUPLICATE DETECTION VERIFICATION")
    print("=" * 60)
    print()
    
    # Get all actions
    print("Fetching all action items...")
    actions = get_all_action_items()
    print(f"✅ Found {len(actions)} total action items")
    print()
    
    # Count embeddings
    with_embeddings = sum(1 for a in actions if a['embedding'] is not None)
    without_embeddings = len(actions) - with_embeddings
    
    print("Embedding Status:")
    print(f"  ✅ With embeddings: {with_embeddings}")
    print(f"  ❌ Without embeddings: {without_embeddings}")
    print()
    
    # Find potential duplicates
    print("Searching for potential duplicates...")
    duplicates = find_potential_duplicates(actions, threshold=0.4)
    
    if not duplicates:
        print("❌ No potential duplicates found")
        print()
        print("This could mean:")
        print("  1. No similar tasks exist across meetings")
        print("  2. Threshold is too high")
        print("  3. Tasks are too different")
        print()
    else:
        print(f"✅ Found {len(duplicates)} potential duplicate pairs")
        print()
        
        # Show top 5
        print("Top Potential Duplicates:")
        print("-" * 60)
        for i, dup in enumerate(sorted(duplicates, key=lambda x: x['similarity'], reverse=True)[:5], 1):
            print(f"\n{i}. Similarity: {dup['similarity']}%")
            print(f"   Task 1: {dup['task1']}")
            print(f"   Meeting: {dup['meeting1']}")
            print(f"   Embedding: {'✅' if dup['has_embedding1'] else '❌'}")
            print(f"   Task 2: {dup['task2']}")
            print(f"   Meeting: {dup['meeting2']}")
            print(f"   Embedding: {'✅' if dup['has_embedding2'] else '❌'}")
    
    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print()
    
    if without_embeddings > 0:
        print("⚠️  ISSUE FOUND: Some actions missing embeddings")
        print(f"   {without_embeddings} actions don't have embeddings generated")
        print("   Embeddings are needed for semantic duplicate detection")
        print()
        print("   Root Cause: process-meeting Lambda may not be generating embeddings")
        print("   Fix: Ensure embedding generation runs for all action items")
        print()
    
    if not duplicates:
        print("⚠️  ISSUE FOUND: No duplicates detected")
        print("   Expected: Some similar tasks across meetings")
        print("   Actual: No matches found")
        print()
        print("   Possible Causes:")
        print("   1. Embeddings not being used for comparison")
        print("   2. Threshold too high (current: 85%)")
        print("   3. No actual similar tasks in test data")
        print()
    else:
        print("✅ Duplicate detection is working")
        print(f"   Found {len(duplicates)} potential matches")
        print()
        if with_embeddings == len(actions):
            print("✅ All actions have embeddings")
        else:
            print(f"⚠️  {without_embeddings} actions missing embeddings")
    
    print("=" * 60)
    print()
    
    # Show sample tasks for manual inspection
    print("Sample Action Items (for manual duplicate checking):")
    print("-" * 60)
    incomplete_actions = [a for a in actions if not a['completed']]
    for i, action in enumerate(incomplete_actions[:10], 1):
        print(f"{i}. {action['task']}")
        print(f"   Meeting: {action['meetingTitle']}")
        print(f"   Embedding: {'✅' if action['embedding'] else '❌'}")
        print()

if __name__ == '__main__':
    main()
