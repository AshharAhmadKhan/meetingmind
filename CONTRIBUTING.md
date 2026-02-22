# Contributing to MeetingMind

Thank you for your interest in contributing to MeetingMind! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- AWS CLI configured
- AWS SAM CLI installed

### Local Setup
1. Clone the repository
   ```bash
   git clone https://github.com/AshharAhmadKhan/meetingmind.git
   cd meetingmind
   ```

2. Install frontend dependencies
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

### Branch Strategy
- `master` - Production branch (protected)
- `develop` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `hotfix/*` - Production hotfix branches

### Creating a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### Making Changes
1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure all tests pass
4. Update documentation if needed
5. Commit your changes following our commit conventions

## Commit Conventions

We follow conventional commits for clear and structured commit history:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(auth): add OAuth2 authentication

Implemented OAuth2 flow for user authentication with Google and GitHub providers.

Closes #123
```

```
fix(upload): preserve teamId during meeting processing

Fixed bug where teamId was lost during status updates in process-meeting Lambda.

Fixes #456
```

## Pull Request Process

### Before Submitting
1. Ensure your code follows the project's coding standards
2. Run all tests and ensure they pass
3. Update documentation for any changed functionality
4. Rebase your branch on the latest `develop` branch

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] PR description clearly explains changes

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Related Issues
Closes #(issue number)
```

## Testing Guidelines

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
python tests/integration/run-ci-tests.py
```

### Test Coverage
- Aim for 80%+ code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters

### JavaScript/React
- Use ES6+ features
- Follow Airbnb style guide
- Use functional components with hooks

### Documentation
- Use clear, concise language
- Include code examples where helpful
- Keep documentation up-to-date with code changes
- Add "Last Updated" timestamp to all documentation files

---

## Questions or Issues?

- Check existing issues before creating new ones
- Use issue templates when available
- Provide detailed reproduction steps for bugs
- Include relevant logs and error messages

---

**Last Updated:** February 22, 2026

## License

By contributing to MeetingMind, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to MeetingMind! 🎉
