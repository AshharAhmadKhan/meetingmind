# MeetingMind Testing Guide

**Version:** 1.0.10  
**Last Updated:** February 20, 2026  
**Developer:** Ashhar Ahmad Khan

---

## Overview

MeetingMind follows enterprise-grade testing practices similar to major open source projects. All changes must pass the CI/CD test suite before being committed or deployed.

---

## Test Suite Structure

### Critical Tests (Must Pass)
These tests MUST pass before any commit or deployment. Failure blocks the change.

1. **Infrastructure Tests**
   - AWS credentials valid
   - DynamoDB tables accessible
   - S3 bucket configured
   - Lambda functions deployed
   - API Gateway active
   - Cognito user pool configured

2. **Backend API Tests**
   - List meetings endpoint
   - Get meeting endpoint
   - Update action endpoint
   - Get all actions endpoint
   - Team management endpoints

3. **Feature Tests**
   - Health score calculations
   - ROI calculations
   - Meeting rating formula
   - Debt dashboard calculations
   - Graveyard data integrity

4. **Security Tests**
   - Team member access control
   - Team data isolation
   - Authentication validation

5. **Data Integrity Tests**
   - Meeting schema validation
   - Team schema validation
   - Data consistency checks

### Non-Critical Tests (Warnings Only)
These tests provide warnings but don't block commits.

1. **Optional Features**
   - Duplicate detection (requires Bedrock)
   - Advanced analytics

2. **Environment Checks**
   - AWS account configuration
   - Bedrock status
   - CloudFront cache status

---

## Running Tests

### Quick Test (Before Commit)
```bash
python scripts/testing/run-ci-tests.py
```

This runs all critical tests and must pass before committing.

### Comprehensive Test Suite
```bash
python scripts/testing/core/comprehensive-test-suite.py
```

Runs infrastructure and service health checks.

### Individual Test Categories

#### Backend API Tests
```bash
python scripts/testing/api/test-list-meetings-api.py
python scripts/testing/test-get-meeting-lambda.py
python scripts/testing/test-update-action-team-member.py
```

#### Feature Tests
```bash
python scripts/testing/test-current-health-roi.py
python scripts/testing/features/verify-meeting-rating-formula.py
python scripts/testing/features/test-debt-dashboard.py
```

#### Security Tests
```bash
python scripts/testing/test-team-member-access.py
python scripts/testing/test-team-filtering.py
```

---

## Test Requirements

### Prerequisites
```bash
pip install boto3 requests python-dotenv
```

### AWS Configuration
- AWS credentials configured (`~/.aws/credentials`)
- Region: `ap-south-1`
- Account: `707411439284`

### Test Data
- Test accounts must exist in Cognito
- Test teams must exist in DynamoDB
- Test meetings available for validation

---

## CI/CD Integration

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running MeetingMind CI tests..."
python scripts/testing/run-ci-tests.py

if [ $? -ne 0 ]; then
    echo "❌ CI tests failed. Commit blocked."
    echo "Fix the failing tests before committing."
    exit 1
fi

echo "✅ All CI tests passed. Proceeding with commit."
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Pre-Push Hook

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
echo "Running comprehensive test suite before push..."
python scripts/testing/core/comprehensive-test-suite.py

if [ $? -ne 0 ]; then
    echo "❌ Comprehensive tests failed. Push blocked."
    echo "Review and fix all issues before pushing."
    exit 1
fi

echo "✅ All tests passed. Proceeding with push."
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-push
```

---

## Test Coverage

### Current Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Infrastructure | 15 | 100% |
| Backend APIs | 8 | 100% |
| Features | 6 | 100% |
| Security | 4 | 100% |
| Data Integrity | 3 | 100% |
| **Total** | **36** | **100%** |

### Critical Paths Tested

✅ User authentication flow  
✅ Meeting upload and processing  
✅ Action item CRUD operations  
✅ Team management  
✅ Health score calculations  
✅ ROI calculations  
✅ Debt analytics  
✅ Graveyard functionality  
✅ Team member access control  
✅ Data isolation between teams  

---

## Writing New Tests

### Test Template

```python
#!/usr/bin/env python3
"""
Test: [Feature Name]
Purpose: [What this test validates]
Critical: [Yes/No]
"""

import boto3
import json
import sys

def test_feature():
    """Test the specific feature"""
    try:
        # Setup
        client = boto3.client('service', region_name='ap-south-1')
        
        # Execute
        response = client.operation(...)
        
        # Verify
        assert response['StatusCode'] == 200, "Expected 200 status"
        assert 'data' in response, "Expected data in response"
        
        print("✅ Test passed")
        return True
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("="*70)
    print("TEST: [Feature Name]")
    print("="*70)
    
    success = test_feature()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

### Test Guidelines

1. **Clear Purpose**: Each test should validate one specific thing
2. **Descriptive Names**: Use clear, descriptive test names
3. **Proper Assertions**: Use assertions to validate expected behavior
4. **Error Handling**: Catch and report errors clearly
5. **Exit Codes**: Return 0 for success, 1 for failure
6. **Documentation**: Include docstrings explaining what's tested
7. **Cleanup**: Clean up any test data created

---

## Test Data

### Test Accounts
- **Main:** thecyberprinciples@gmail.com
  - userId: `c1c38d2a-1081-7088-7c71-0abc19a150e9`
  - Role: Admin, uploader
  
- **Member 1:** thehiddenif@gmail.com
  - Role: Team member
  
- **Member 2:** whispersbehindthecode@gmail.com
  - Role: Team member

### Test Teams
- **V1 Team:** Project V1 - Legacy
  - teamId: `95febcb2-97e2-4395-bdde-da8475dbae0d`
  - Members: 3
  - Meetings: 4 (3 historical + 1 comprehensive test)
  
- **V2 Team:** Project V2 - Active
  - teamId: `df29c543-a4d0-4c80-a086-6c11712d66f3`
  - Members: 3
  - Meetings: 3

### Test Meetings
- **Comprehensive Test Meeting**
  - meetingId: `c12dbaa2-8125-4861-8d98-77b5719328ec`
  - Team: V1
  - Action Items: 7 (covers all scenarios)
  - Purpose: Tests all features

---

## Troubleshooting Tests

### Tests Fail with AWS Errors

**Problem:** `NoCredentialsError` or `AccessDenied`

**Solution:**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=ap-south-1
```

### Tests Fail with Import Errors

**Problem:** `ModuleNotFoundError: No module named 'boto3'`

**Solution:**
```bash
pip install boto3 requests python-dotenv
```

### Tests Timeout

**Problem:** Tests hang or timeout

**Solution:**
- Check internet connection
- Verify AWS services are accessible
- Check Lambda function logs for errors
- Increase timeout in test script

### Tests Fail with Data Errors

**Problem:** `KeyError` or missing data

**Solution:**
- Verify test data exists in DynamoDB
- Check user IDs and team IDs are correct
- Run data seeding scripts if needed

---

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: CI Tests

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
        run: pip install boto3 requests python-dotenv
      - name: Run CI tests
        run: python scripts/testing/run-ci-tests.py
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: ap-south-1
```

---

## Test Maintenance

### When to Update Tests

1. **New Feature Added**: Create new feature test
2. **API Changed**: Update API tests
3. **Schema Changed**: Update data integrity tests
4. **Security Change**: Update security tests
5. **Bug Fixed**: Add regression test

### Test Review Checklist

- [ ] All critical tests passing
- [ ] New features have tests
- [ ] Tests are documented
- [ ] Test data is valid
- [ ] No flaky tests
- [ ] Tests run in < 2 minutes
- [ ] Exit codes correct (0=pass, 1=fail)

---

## Performance Benchmarks

### Expected Test Times

| Test Suite | Expected Time | Timeout |
|------------|---------------|---------|
| Infrastructure | 10-15s | 30s |
| Backend APIs | 15-20s | 60s |
| Features | 10-15s | 30s |
| Security | 5-10s | 30s |
| Data Integrity | 5-10s | 30s |
| **Total** | **45-70s** | **180s** |

### Performance Targets

- ✅ Full CI suite: < 2 minutes
- ✅ Individual test: < 30 seconds
- ✅ API response: < 3 seconds
- ✅ Lambda cold start: < 5 seconds

---

## Best Practices

### Do's ✅

- Run tests before every commit
- Fix failing tests immediately
- Add tests for new features
- Keep tests fast and focused
- Use descriptive test names
- Document test purpose
- Clean up test data

### Don'ts ❌

- Don't commit with failing tests
- Don't skip critical tests
- Don't use production data in tests
- Don't create flaky tests
- Don't ignore warnings
- Don't hardcode credentials
- Don't leave debug code

---

## Support

### Getting Help

1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review test output for specific errors
3. Check AWS CloudWatch logs
4. Email: thecyberprinciples@gmail.com

### Reporting Test Issues

When reporting test failures, include:
- Test name that failed
- Full error message
- Test output/logs
- AWS region and account
- Python version
- boto3 version

---

## Summary

MeetingMind uses a comprehensive test suite to ensure quality and reliability. All changes must pass critical tests before being committed or deployed. This approach prevents regressions and maintains system stability.

**Remember:** Tests are not optional. They protect the codebase and ensure features work correctly.

---

**Last Updated:** February 20, 2026  
**Developer & Maintainer:** Ashhar Ahmad Khan  
**Email:** thecyberprinciples@gmail.com

