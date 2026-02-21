"""
Test with REAL meeting data from DynamoDB to ensure decimal_to_float works
"""
import boto3
import json
from decimal import Decimal

# New implementation
def decimal_to_float_new(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

# Get real meeting from DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

print("=" * 70)
print("REAL DYNAMODB DATA TEST")
print("=" * 70)

# Get a real meeting
response = table.get_item(
    Key={
        'userId': 'a1a3cd5a-00e1-701f-a07b-b12a35f16664',
        'meetingId': '04023cc8-32b6-4674-ae12-846ee6125aa4'
    }
)

if 'Item' not in response:
    print("❌ Meeting not found")
    exit(1)

item = response['Item']
print(f"\n✅ Retrieved meeting: {item.get('title', 'Unknown')}")

# Check for Decimal fields
decimal_fields = []
def find_decimals(obj, path=""):
    if isinstance(obj, Decimal):
        decimal_fields.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            find_decimals(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_decimals(v, f"{path}[{i}]")

find_decimals(item)

print(f"\n📊 Found {len(decimal_fields)} Decimal fields:")
for path, value in decimal_fields[:10]:  # Show first 10
    print(f"   {path}: {value} (Decimal)")

# Test serialization with new implementation
print("\n🧪 Testing JSON serialization with NEW decimal_to_float:")
try:
    json_str = json.dumps(item, default=decimal_to_float_new)
    print(f"   ✅ Serialization successful ({len(json_str)} bytes)")
    
    # Parse back and verify
    parsed = json.loads(json_str)
    print(f"   ✅ Deserialization successful")
    
    # Verify a few fields
    if 'healthScore' in parsed:
        print(f"   healthScore: {parsed['healthScore']} (type: {type(parsed['healthScore']).__name__})")
    if 'roi' in parsed:
        print(f"   roi: {parsed['roi']} (type: {type(parsed['roi']).__name__})")
    
    print("\n✅ ALL CHECKS PASSED - Real DynamoDB data serializes correctly")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
