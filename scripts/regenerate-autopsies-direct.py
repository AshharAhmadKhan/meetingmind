#!/usr/bin/env python3
"""
Directly regenerate autopsies using the same logic as process-meeting Lambda.
"""

import boto3
import json
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')
bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

user_id = '41c3fd1a-b061-708b-2e00-0b8f9b7c8e6c'

def generate_autopsy(action_items, decisions, transcript_text, health_score):
    """Generate meeting autopsy for failed meetings."""
    is_ghost = len(decisions) == 0 and len(action_items) == 0
    if health_score >= 60 and not is_ghost:
        return None
    
    # Calculate metrics
    total_actions = len(action_items)
    unowned_count = sum(1 for a in action_items if not a.get('owner') or a['owner'] == 'Unassigned')
    owned_count = total_actions - unowned_count
    decision_count = len(decisions)
    
    # Estimate duration
    word_count = len(transcript_text.split())
    duration_minutes = max(15, min(90, word_count // 150))
    
    # Calculate duplicates
    duplicate_count = 0
    task_texts = [a.get('task', '').lower().strip() for a in action_items if a.get('task')]
    for i, task in enumerate(task_texts):
        if task and len(task) > 10:
            for other_task in task_texts[i+1:]:
                if task in other_task or other_task in task:
                    duplicate_count += 1
                    break
    
    # Speaker distribution
    speaker_lines = {}
    for line in transcript_text.split('\n'):
        if ':' in line:
            speaker = line.split(':')[0].strip()
            if len(speaker) < 30:
                speaker_lines[speaker] = speaker_lines.get(speaker, 0) + 1
    
    total_lines = sum(speaker_lines.values()) if speaker_lines else 1
    speaker_percentages = {k: round((v/total_lines)*100) for k, v in speaker_lines.items()}
    top_speakers = sorted(speaker_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
    speaker_dist = ', '.join([f"{name}: {pct}%" for name, pct in top_speakers]) if top_speakers else "Unknown"
    
    prompt = f"""Write a 2-sentence meeting autopsy. Be direct and slightly uncomfortable.

IMPORTANT: Base your analysis ONLY on these verified facts:
- Total action items: {total_actions}
- Action items WITH owners: {owned_count}
- Action items WITHOUT owners (Unassigned): {unowned_count}
- Decisions made: {decision_count}
- Meeting duration: {duration_minutes} minutes (estimated from transcript)
- Duplicate items: {duplicate_count}
- Speaking time distribution: {speaker_dist}

CRITICAL RULES:
- DO NOT claim action items are unassigned if owned_count > 0
- DO NOT contradict the numbers provided above
- DO NOT penalize short meetings if they have good outputs (decisions + owned actions)
- Focus on REAL problems: unassigned tasks, no decisions, duplicates, unbalanced speaking

Explain specifically why this meeting scored {health_score}/100 based on the facts above.

Format: 'Cause of death: [one sentence]. Prescription: [one sentence].'

Example: "Cause of death: Three people spoke for 85% of the time while five action items were assigned to 'Unassigned.' Prescription: Assign owners before leaving the room."
"""
    
    try:
        body = json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 300,
            'messages': [{'role': 'user', 'content': prompt}]
        })
        
        resp = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        result = json.loads(resp['body'].read())
        autopsy = result['content'][0]['text'].strip()
        return autopsy
        
    except Exception as e:
        print(f"   ❌ Error generating autopsy: {e}")
        # Fallback
        if is_ghost:
            return "Cause of death: Zero decisions and zero action items extracted from this meeting. Prescription: Require clear agenda with expected outcomes before scheduling."
        elif unowned_count > total_actions * 0.5:
            return f"Cause of death: {unowned_count} of {total_actions} action items have no owner. Prescription: Assign explicit owners before ending the meeting."
        else:
            return f"Cause of death: Meeting health score of {health_score}/100 indicates poor execution. Prescription: Review action clarity, ownership, and decision-making process."

# Get all meetings
response = table.query(
    KeyConditionExpression='userId = :uid',
    ExpressionAttributeValues={':uid': user_id}
)

print("Regenerating autopsies with new logic...")
print("=" * 80)

for meeting in response['Items']:
    meeting_id = meeting['meetingId']
    title = meeting['title']
    health_score = meeting.get('healthScore', 100)
    
    # Only generate for F grade meetings
    if health_score < 60:
        print(f"\n📋 {title} (Score: {health_score})")
        
        action_items = meeting.get('actionItems', [])
        decisions = meeting.get('decisions', [])
        transcript = meeting.get('transcript', '')
        
        autopsy = generate_autopsy(action_items, decisions, transcript, health_score)
        
        if autopsy:
            print(f"   🪦 NEW AUTOPSY:")
            print(f"   {autopsy}")
            
            # Save to DynamoDB
            table.update_item(
                Key={'userId': user_id, 'meetingId': meeting_id},
                UpdateExpression='SET autopsy = :a, autopsyGeneratedAt = :t',
                ExpressionAttributeValues={
                    ':a': autopsy,
                    ':t': datetime.now(timezone.utc).isoformat()
                }
            )
            print(f"   ✅ Saved")

print("\n" + "=" * 80)
print("✅ Autopsies regenerated with improved logic!")
