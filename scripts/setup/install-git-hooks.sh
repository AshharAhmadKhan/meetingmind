#!/bin/bash
# Install Git Hooks for MeetingMind
# This script sets up pre-commit hooks to run CI tests

echo "========================================================================"
echo "INSTALLING MEETINGMIND GIT HOOKS"
echo "========================================================================"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Run this script from the project root directory"
    exit 1
fi

# Make hooks executable
echo "Making hooks executable..."
chmod +x .githooks/pre-commit

# Configure git to use custom hooks directory
echo "Configuring git to use .githooks directory..."
git config core.hooksPath .githooks

# Verify installation
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================"
    echo "✅ GIT HOOKS INSTALLED SUCCESSFULLY"
    echo "========================================================================"
    echo ""
    echo "Pre-commit hook is now active!"
    echo ""
    echo "What this means:"
    echo "  • CI tests will run automatically before each commit"
    echo "  • Commits will be blocked if critical tests fail"
    echo "  • This ensures code quality and prevents regressions"
    echo ""
    echo "To test the hook:"
    echo "  git commit -m \"test commit\""
    echo ""
    echo "To bypass the hook (NOT RECOMMENDED):"
    echo "  git commit --no-verify -m \"your message\""
    echo ""
    echo "To uninstall:"
    echo "  git config --unset core.hooksPath"
    echo ""
else
    echo ""
    echo "❌ Failed to install git hooks"
    exit 1
fi
