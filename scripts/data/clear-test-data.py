#!/usr/bin/env python3
"""
Clear all test data from MeetingMind
Deletes: meetings, teams, and S3 audio files
"""

import boto3
import sys

REGION = 'ap-south-1'
MEETINGS_TABLE = 'meetingmind-meetings'
TEAMS_TABLE = 'meetingmind-teams'
AUDIO_BUCKET = 'meetingmind-audio-707411439284'

def clear_meetings():
    """Delete all meetings from DynamoDB"""
    print("\n📋 Clearing Meetings...")
    print("=" * 60)
    
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    # Scan all items
    response = dynamodb.scan(TableName=MEETINGS_TABLE)
    items = response.get('Items', [])
    
    if not items:
        print("No meetings found")
        return 0
    
    print(f"Found {len(items)} meetings to delete...")
    
    # Delete each item
    deleted = 0
    for item in items:
        meeting_id = item['meetingId']['S']
        user_id = item['userId']['S']
        title = item.get('title', {}).get('S', 'Unknown')
        
        try:
            dynamodb.delete_item(
                TableName=MEETINGS_TABLE,
                Key={
                    'userId': {'S': user_id},
                    'meetingId': {'S': meeting_id}
                }
            )
            deleted += 1
            print(f"  ✓ Deleted: {title} ({meeting_id[:8]}...)")
        except Exception as e:
            print(f"  ✗ Error deleting {meeting_id}: {e}")
    
    print(f"\n✅ Deleted {deleted}/{len(items)} meetings")
    return deleted

def clear_teams():
    """Delete all teams from DynamoDB"""
    print("\n👥 Clearing Teams...")
    print("=" * 60)
    
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    # Scan all items
    try:
        response = dynamodb.scan(TableName=TEAMS_TABLE)
        items = response.get('Items', [])
    except Exception as e:
        print(f"⚠️  Cannot access teams table: {e}")
        return 0
    
    if not items:
        print("No teams found")
        return 0
    
    print(f"Found {len(items)} teams to delete...")
    
    # Delete each item
    deleted = 0
    for item in items:
        team_id = item['teamId']['S']
        team_name = item.get('teamName', {}).get('S', 'Unknown')
        
        try:
            dynamodb.delete_item(
                TableName=TEAMS_TABLE,
                Key={
                    'teamId': {'S': team_id}
                }
            )
            deleted += 1
            print(f"  ✓ Deleted: {team_name} ({team_id[:8]}...)")
        except Exception as e:
            print(f"  ✗ Error deleting {team_id}: {e}")
    
    print(f"\n✅ Deleted {deleted}/{len(items)} teams")
    return deleted

def clear_s3_audio():
    """Delete all audio files from S3"""
    print("\n🎵 Clearing S3 Audio Files...")
    print("=" * 60)
    
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        # List all objects in audio/ prefix
        response = s3.list_objects_v2(
            Bucket=AUDIO_BUCKET,
            Prefix='audio/'
        )
        
        objects = response.get('Contents', [])
        
        if not objects:
            print("No audio files found")
            return 0
        
        print(f"Found {len(objects)} audio files to delete...")
        
        # Delete each object
        deleted = 0
        for obj in objects:
            key = obj['Key']
            try:
                s3.delete_object(Bucket=AUDIO_BUCKET, Key=key)
                deleted += 1
                filename = key.split('/')[-1]
                print(f"  ✓ Deleted: {filename}")
            except Exception as e:
                print(f"  ✗ Error deleting {key}: {e}")
        
        print(f"\n✅ Deleted {deleted}/{len(objects)} audio files")
        return deleted
        
    except Exception as e:
        print(f"⚠️  Cannot access S3 bucket: {e}")
        return 0

def get_data_summary():
    """Get summary of current data"""
    print("\n📊 Current Data Summary")
    print("=" * 60)
    
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    s3 = boto3.client('s3', region_name=REGION)
    
    # Count meetings
    try:
        response = dynamodb.scan(TableName=MEETINGS_TABLE, Select='COUNT')
        meeting_count = response.get('Count', 0)
        print(f"Meetings: {meeting_count}")
    except:
        print("Meetings: Unable to count")
    
    # Count teams
    try:
        response = dynamodb.scan(TableName=TEAMS_TABLE, Select='COUNT')
        team_count = response.get('Count', 0)
        print(f"Teams: {team_count}")
    except:
        print("Teams: Unable to count")
    
    # Count audio files
    try:
        response = s3.list_objects_v2(Bucket=AUDIO_BUCKET, Prefix='audio/')
        audio_count = len(response.get('Contents', []))
        print(f"Audio Files: {audio_count}")
    except:
        print("Audio Files: Unable to count")

if __name__ == '__main__':
    print("=" * 60)
    print("MeetingMind Data Cleanup Tool")
    print("=" * 60)
    
    # Show current data
    get_data_summary()
    
    print("\n⚠️  WARNING: This will delete ALL data:")
    print("  - All meetings from DynamoDB")
    print("  - All teams from DynamoDB")
    print("  - All audio files from S3")
    print("\nThis action CANNOT be undone!")
    
    confirm = input("\nType 'DELETE ALL' to confirm: ")
    
    if confirm == 'DELETE ALL':
        print("\n🗑️  Starting cleanup...")
        
        meetings_deleted = clear_meetings()
        teams_deleted = clear_teams()
        audio_deleted = clear_s3_audio()
        
        print("\n" + "=" * 60)
        print("CLEANUP COMPLETE")
        print("=" * 60)
        print(f"Meetings deleted: {meetings_deleted}")
        print(f"Teams deleted: {teams_deleted}")
        print(f"Audio files deleted: {audio_deleted}")
        print("\n✨ Database is now clean and ready for fresh data!")
        print("=" * 60)
    else:
        print("\n❌ Cancelled. No data was deleted.")
        sys.exit(0)
