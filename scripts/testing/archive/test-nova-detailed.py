import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

print("Testing Nova Lite with detailed error...")
try:
    body = json.dumps({
        'messages': [{'role': 'user', 'content': [{'text': 'Hello'}]}],
        'inferenceConfig': {'maxTokens': 50, 'temperature': 0.1}
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=body
    )
    
    result = json.loads(response['body'].read())
    print("✅ SUCCESS!")
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"\nFull error type: {type(e).__name__}")
