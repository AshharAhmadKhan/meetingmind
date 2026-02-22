# Testing

Comprehensive test suite for MeetingMind.

## Structure

```
tests/
├── unit/               # Unit tests
│   └── backend/        # Backend Lambda unit tests
├── integration/        # Integration tests
│   ├── api/            # API endpoint tests
│   ├── core/           # Core functionality tests
│   └── features/       # Feature-specific tests
└── README.md           # This file
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### Specific Test File
```bash
python tests/integration/test-fix1-live.py
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual Lambda functions in isolation
- Fast execution (<1 second each)
- No external dependencies

### Integration Tests (`tests/integration/`)
- Test Lambda functions with real AWS services
- Test API endpoints end-to-end
- Test feature workflows

### Test Subdirectories

**`integration/api/`** - API endpoint tests
- Test REST API calls
- Test authentication
- Test authorization

**`integration/core/`** - Core functionality tests
- Test data models
- Test business logic
- Test calculations

**`integration/features/`** - Feature-specific tests
- Test team collaboration
- Test action item management
- Test meeting processing

## Prerequisites

```bash
# Install dependencies
pip install boto3 pytest requests

# Configure AWS credentials
export AWS_PROFILE=your-profile
export AWS_REGION=ap-south-1
```

## Writing Tests

See [docs/TESTING.md](../docs/TESTING.md) for detailed testing guidelines.

## CI/CD

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Pre-deployment

## Coverage

Current test coverage:
- Unit tests: 80%+
- Integration tests: 60%+
- Critical paths: 100%
