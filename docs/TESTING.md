# Testing Guide

Comprehensive testing documentation for MeetingMind.

**Last Updated:** February 22, 2026

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

MeetingMind uses a multi-layered testing approach:

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test Lambda functions with AWS services
- **End-to-End Tests**: Test complete user workflows
- **Manual Tests**: Test UI/UX and edge cases

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   └── backend/             # Backend unit tests
├── integration/             # Integration tests
│   ├── core/                # Core functionality tests
│   ├── features/            # Feature-specific tests
│   └── ...
└── README.md                # Testing overview
```

## Running Tests

### Prerequisites

```bash
# Install Python dependencies
pip install boto3 requests python-dotenv

# Set AWS credentials
export AWS_PROFILE=your-profile
export AWS_REGION=ap-south-1
```

### Run All Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/integration/test-fix1-live.py

# Run with verbose output
python tests/integration/test-fix1-live.py -v
```

### Run Tests by Category

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Feature tests
python -m pytest tests/integration/features/
```

## Test Categories

### 1. Unit Tests

Test individual Lambda functions in isolation.

**Example: Test Action Update**
```python
# tests/integration/test-update-action-lambda.py
import boto3
import json

def test_update_action_status():
    """Test updating action item status"""
    lambda_client = boto3.client('lambda', region_name='ap-south-1')
    
    payload = {
        'meetingId': 'test-meeting-id',
        'actionId': 'action-1',
        'updates': {
            'status': 'done',
            'completed': True
        }
    }
    
    response = lambda_client.invoke(
        FunctionName='meetingmind-update-action',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read())
    assert result['statusCode'] == 200
    assert 'updated' in result['body']
```

### 2. Integration Tests

Test Lambda functions with real AWS services.

**Example: Test Meeting Processing**
```python
# tests/integration/test-upload-flow.py
import boto3
import time

def test_meeting_processing_pipeline():
    """Test complete meeting processing pipeline"""
    s3 = boto3.client('s3', region_name='ap-south-1')
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # 1. Upload audio file
    s3.upload_file(
        'test-audio.mp3',
        'meetingmind-audio',
        'test-user__test-meeting__test.mp3'
    )
    
    # 2. Wait for processing
    time.sleep(60)
    
    # 3. Verify meeting in DynamoDB
    table = dynamodb.Table('meetingmind-meetings')
    response = table.get_item(
        Key={
            'userId': 'test-user',
            'meetingId': 'test-meeting'
        }
    )
    
    assert 'Item' in response
    assert response['Item']['status'] == 'DONE'
    assert len(response['Item']['actionItems']) > 0
```

### 3. End-to-End Tests

Test complete user workflows from UI to database.

**Example: Test Team Collaboration**
```python
# tests/integration/features/test-team-collaboration-flow.py
import requests

def test_team_collaboration_workflow():
    """Test complete team collaboration workflow"""
    base_url = 'https://api.meetingmind.com'
    
    # 1. User A creates team
    response = requests.post(
        f'{base_url}/teams',
        headers={'Authorization': f'Bearer {token_a}'},
        json={'name': 'Test Team'}
    )
    team_id = response.json()['teamId']
    invite_code = response.json()['inviteCode']
    
    # 2. User B joins team
    response = requests.post(
        f'{base_url}/teams/join',
        headers={'Authorization': f'Bearer {token_b}'},
        json={'inviteCode': invite_code}
    )
    assert response.status_code == 200
    
    # 3. User A uploads meeting
    response = requests.post(
        f'{base_url}/meetings',
        headers={'Authorization': f'Bearer {token_a}'},
        json={'title': 'Team Meeting', 'teamId': team_id}
    )
    meeting_id = response.json()['meetingId']
    
    # 4. User B can see meeting
    response = requests.get(
        f'{base_url}/meetings/{meeting_id}',
        headers={'Authorization': f'Bearer {token_b}'}
    )
    assert response.status_code == 200
```

### 4. Performance Tests

Test system performance under load.

**Example: Test Rate Limiting**
```python
# tests/integration/test-rate-limiting.py
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def test_rate_limiting():
    """Test API rate limiting"""
    base_url = 'https://api.meetingmind.com'
    
    def make_request():
        return requests.get(
            f'{base_url}/meetings',
            headers={'Authorization': f'Bearer {token}'}
        )
    
    # Send 100 requests concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        responses = [f.result() for f in futures]
    
    # Check for rate limit responses
    rate_limited = [r for r in responses if r.status_code == 429]
    assert len(rate_limited) > 0, "Rate limiting not working"
```

### 5. Data Validation Tests

Test data integrity and calculations.

**Example: Test ROI Calculation**
```python
# tests/integration/test-current-health-roi.py
import boto3

def test_roi_calculation():
    """Test meeting ROI calculation accuracy"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('meetingmind-meetings')
    
    response = table.get_item(
        Key={
            'userId': 'test-user',
            'meetingId': 'test-meeting'
        }
    )
    
    meeting = response['Item']
    roi = meeting['roi']
    
    # Verify ROI calculation
    expected_cost = meeting['roi']['meeting_duration_minutes'] * 5
    assert roi['cost'] == expected_cost
    
    expected_value = (
        roi['decision_count'] * 500 +
        roi['clear_action_count'] * 100
    )
    assert roi['value'] == expected_value
    
    expected_roi = ((roi['value'] - roi['cost']) / roi['cost']) * 100
    assert abs(roi['roi'] - expected_roi) < 0.01
```

## Writing Tests

### Test Naming Convention

```python
# Good
def test_update_action_status():
    pass

def test_meeting_processing_pipeline():
    pass

# Bad
def testAction():
    pass

def check_meeting():
    pass
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_example():
    # Arrange: Set up test data
    meeting_id = 'test-meeting'
    action_id = 'action-1'
    
    # Act: Perform the action
    result = update_action(meeting_id, action_id, {'status': 'done'})
    
    # Assert: Verify the result
    assert result['status'] == 'done'
    assert result['completed'] == True
```

### Mocking AWS Services

Use `moto` for mocking AWS services:

```python
from moto import mock_dynamodb, mock_s3
import boto3

@mock_dynamodb
def test_with_mock_dynamodb():
    # Create mock DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Test with mock table
    table.put_item(Item={'id': '1', 'name': 'Test'})
    response = table.get_item(Key={'id': '1'})
    assert response['Item']['name'] == 'Test'
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install boto3 pytest moto requests
    
    - name: Run unit tests
      run: |
        pytest tests/unit/
    
    - name: Run integration tests
      run: |
        pytest tests/integration/
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_REGION: ap-south-1
```

### Pre-Commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running tests..."
python -m pytest tests/unit/

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed!"
```

## Test Coverage

### Measuring Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/

# Generate coverage report
coverage report

# Generate HTML report
coverage html
```

### Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: 60%+ coverage
- **Critical Paths**: 100% coverage (auth, payment, data loss)

## Troubleshooting

### Common Issues

**Issue: AWS credentials not found**
```bash
# Solution: Set AWS credentials
export AWS_PROFILE=your-profile
export AWS_REGION=ap-south-1
```

**Issue: DynamoDB table not found**
```bash
# Solution: Verify table name and region
aws dynamodb list-tables --region ap-south-1
```

**Issue: Lambda function timeout**
```bash
# Solution: Increase timeout in template.yaml
Timeout: 900  # 15 minutes
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Clean Up**: Always clean up test data after tests
3. **Use Fixtures**: Reuse common test setup code
4. **Test Edge Cases**: Test boundary conditions and error cases
5. **Document Tests**: Add docstrings explaining what each test does
6. **Fast Tests**: Keep unit tests fast (<1 second each)
7. **Realistic Data**: Use realistic test data that mimics production

## Resources

- [AWS Lambda Testing Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Moto Documentation](http://docs.getmoto.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
