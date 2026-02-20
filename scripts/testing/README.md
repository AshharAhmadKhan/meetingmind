# Testing Scripts

**Last Updated:** February 20, 2026

Comprehensive test suite for MeetingMind.

## Directory Structure

```
scripts/testing/
├── README.md              # This file
├── core/                  # Core test utilities
│   ├── comprehensive-test-suite.py
│   ├── run-all-tests.py
│   ├── create-comprehensive-test-meeting.py
│   ├── fix-test-meeting-status.py
│   ├── compare-meeting-formats.py
│   └── verify-test-meeting.py
├── api/                   # API endpoint tests
│   ├── test-api-endpoint.py
│   ├── test-debt-api-call.py
│   ├── test-duplicate-api-call.py
│   ├── test-list-meetings-api.py
│   ├── test-team-meetings-api.py
│   └── simulate-api-calls.py
├── features/              # Feature-specific tests
│   ├── test-debt-dashboard.py
│   ├── test-duplicate-detection.py
│   ├── test-duplicate-lambda-direct.py
│   ├── test-graveyard-data.py
│   ├── check-graveyard-data.py
│   ├── test-view-invite-code.py
│   └── verify-meeting-rating-formula.py
├── archive/               # Old/deprecated tests
│   ├── test-nova-*.py
│   ├── simulate-*.py
│   ├── test-throttle*.py
│   └── test-v1-*.py
└── [other test scripts]   # Uncategorized tests
```

## Quick Start

### Run All Tests
```bash
python scripts/testing/core/run-all-tests.py
```

### Run Comprehensive Test Suite
```bash
python scripts/testing/core/comprehensive-test-suite.py
```

### Create Test Meeting
```bash
python scripts/testing/core/create-comprehensive-test-meeting.py
```

## Test Categories

### Core Tests
Essential test utilities and comprehensive test suites.

**Key Scripts:**
- `comprehensive-test-suite.py` - Full system verification (80 tests)
- `run-all-tests.py` - Quick test runner
- `create-comprehensive-test-meeting.py` - Creates test meeting with all features
- `compare-meeting-formats.py` - Identifies V1 vs V2 meeting structures

**When to Use:**
- Before deployment
- After major changes
- To verify system health

### API Tests
Tests for API Gateway endpoints and Lambda functions.

**Key Scripts:**
- `test-api-endpoint.py` - Generic API endpoint tester
- `test-list-meetings-api.py` - Tests meeting list endpoint
- `test-team-meetings-api.py` - Tests team filtering
- `test-debt-api-call.py` - Tests debt analytics endpoint

**When to Use:**
- After API changes
- To debug CORS issues
- To verify authentication

### Feature Tests
Tests for specific MeetingMind features.

**Key Scripts:**
- `test-debt-dashboard.py` - Tests debt calculation
- `test-duplicate-detection.py` - Tests semantic search
- `test-graveyard-data.py` - Tests graveyard logic
- `verify-meeting-rating-formula.py` - Verifies health score formula

**When to Use:**
- After feature changes
- To verify calculations
- To test edge cases

### Archive
Old or deprecated tests kept for reference.

**Contents:**
- Nova model tests (testing complete)
- Throttling tests (issue resolved)
- V1 migration tests (migration complete)
- Simulation scripts (replaced by real tests)

**When to Use:**
- Historical reference only
- Do not use for active testing

## Common Test Patterns

### Testing Lambda Functions
```python
import boto3

lambda_client = boto3.client('lambda', region_name='ap-south-1')

response = lambda_client.invoke(
    FunctionName='meetingmind-FUNCTION_NAME',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

result = json.loads(response['Payload'].read())
```

### Testing API Endpoints
```python
import requests

headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://API_URL/endpoint',
    headers=headers
)

assert response.status_code == 200
```

### Testing DynamoDB
```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('meetingmind-meetings')

response = table.get_item(
    Key={'userId': user_id, 'meetingId': meeting_id}
)

assert 'Item' in response
```

## Test Data

### Test Accounts
- **Main:** thecyberprinciples@gmail.com (userId: c1c38d2a-1081-7088-7c71-0abc19a150e9)
- **Member 1:** thehiddenif@gmail.com
- **Member 2:** whispersbehindthecode@gmail.com

### Test Teams
- **V1 Team:** Project V1 - Legacy (teamId: 95febcb2-97e2-4395-bdde-da8475dbae0d)
- **V2 Team:** Project V2 - Active (teamId: df29c543-a4d0-4c80-a086-6c11712d66f3)

### Test Meetings
- **Comprehensive Test:** c12dbaa2-8125-4861-8d98-77b5719328ec (7 action items, all features)
- **V1 Meetings:** 3 historical meetings (D, F, GHOST grades)
- **V2 Meetings:** 3 active meetings (various states)

## Writing New Tests

### Test Script Template
```python
#!/usr/bin/env python3
"""
Brief description of what this test does
"""

import boto3
import json

def test_feature():
    """Test specific feature"""
    # Setup
    client = boto3.client('service', region_name='ap-south-1')
    
    # Execute
    response = client.operation(...)
    
    # Verify
    assert response['StatusCode'] == 200
    print("✅ Test passed")

def main():
    print("\n" + "="*70)
    print("TEST NAME")
    print("="*70)
    
    try:
        test_feature()
        print("\n✅ All tests passed")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)

if __name__ == '__main__':
    main()
```

### Best Practices
1. Use descriptive test names
2. Include setup and teardown
3. Print clear success/failure messages
4. Use assertions to verify results
5. Handle errors gracefully
6. Document expected behavior
7. Clean up test data after running

## Troubleshooting Tests

### Tests Fail with Import Errors
```bash
pip install boto3 requests python-dotenv
```

### Tests Fail with 403 Errors
- Verify AWS credentials configured
- Check Cognito user exists
- Verify JWT token is valid

### Tests Fail with Connection Errors
- Check AWS region (ap-south-1)
- Verify internet connection
- Check AWS service status

### Tests Fail with Data Errors
- Verify test data exists
- Check DynamoDB table names
- Verify user IDs and team IDs

## CI/CD Integration

### Pre-Deployment Checks
```bash
# Run comprehensive test suite
python scripts/testing/core/comprehensive-test-suite.py

# Exit code 0 = safe to deploy
# Exit code 1 = deployment blocked
```

### Post-Deployment Verification
```bash
# Verify API endpoints
python scripts/testing/api/test-api-endpoint.py

# Verify features
python scripts/testing/features/test-debt-dashboard.py
python scripts/testing/features/test-graveyard-data.py
```

## Performance Testing

### Load Testing
```bash
# Test concurrent requests
python scripts/testing/test-concurrent-requests.py
```

### Latency Testing
```bash
# Measure API response times
python scripts/testing/test-api-latency.py
```

## Security Testing

### Authentication Testing
```bash
# Test JWT validation
python scripts/testing/test-auth-validation.py
```

### Authorization Testing
```bash
# Test team member access
python scripts/testing/test-team-member-access.py
```

## Monitoring

### CloudWatch Logs
```bash
# Tail Lambda logs during testing
aws logs tail /aws/lambda/meetingmind-FUNCTION_NAME --follow
```

### X-Ray Traces
- View traces in AWS X-Ray console
- Identify performance bottlenecks
- Debug distributed transactions

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md)
- Review [TESTING.md](../../docs/TESTING.md)
- Email: thecyberprinciples@gmail.com

---

**Last Updated:** February 20, 2026 - 7:15 PM IST
