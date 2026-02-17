# Scripts

Utility scripts for testing and maintenance.

## Day 5 Scripts

### `generate-embeddings.py`
Backfills embeddings for existing action items in DynamoDB.

**Usage:**
```bash
python scripts/generate-embeddings.py
```

**What it does:**
- Queries all meetings for a user
- Generates embeddings for action items without embeddings
- Converts float to Decimal for DynamoDB compatibility
- Updates meetings in DynamoDB

**Output:**
- Total actions processed
- Number of embeddings generated
- Coverage percentage

### `test-lambda-direct.py`
Tests the check-duplicate Lambda function directly.

**Usage:**
```bash
python scripts/test-lambda-direct.py
```

**What it tests:**
- Lambda invocation with test task
- Duplicate detection accuracy
- Similarity score calculation
- Chronic blocker identification

### `test-duplicate-detection.py`
Comprehensive test suite for duplicate detection feature.

**Usage:**
```bash
python scripts/test-duplicate-detection.py
```

**What it tests:**
- Lambda function exists
- API Gateway endpoint
- DynamoDB data and embeddings
- Frontend build
- S3 deployment
- CloudFront configuration

### `test-api-endpoint.py`
Tests the API endpoint via API Gateway (simulates browser request).

**Usage:**
```bash
# Update TEST_EMAIL and TEST_PASSWORD first
python scripts/test-api-endpoint.py
```

**What it tests:**
- Cognito authentication
- API Gateway routing
- Full request/response flow
- End-to-end duplicate detection

## Configuration

All scripts use these AWS resources:
- **Region**: `ap-south-1`
- **Stack**: `meetingmind-stack`
- **Table**: `meetingmind-meetings`
- **User Pool**: `ap-south-1_mkFJawjMp`
- **API URL**: `https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod`

## Requirements

```bash
pip install boto3 requests
```
