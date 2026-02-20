# Install Git Hooks for MeetingMind (Windows PowerShell)
# This script sets up pre-commit hooks to run CI tests

Write-Host ""
Write-Host "========================================================================"
Write-Host "INSTALLING MEETINGMIND GIT HOOKS"
Write-Host "========================================================================"
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: Not in a git repository" -ForegroundColor Red
    Write-Host "   Run this script from the project root directory"
    exit 1
}

# Configure git to use custom hooks directory
Write-Host "Configuring git to use .githooks directory..."
git config core.hooksPath .githooks

# Verify installation
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================================"
    Write-Host "✅ GIT HOOKS INSTALLED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Pre-commit hook is now active!"
    Write-Host ""
    Write-Host "What this means:"
    Write-Host "  • CI tests will run automatically before each commit"
    Write-Host "  • Commits will be blocked if critical tests fail"
    Write-Host "  • This ensures code quality and prevents regressions"
    Write-Host ""
    Write-Host "To test the hook:"
    Write-Host "  git commit -m `"test commit`""
    Write-Host ""
    Write-Host "To bypass the hook (NOT RECOMMENDED):"
    Write-Host "  git commit --no-verify -m `"your message`""
    Write-Host ""
    Write-Host "To uninstall:"
    Write-Host "  git config --unset core.hooksPath"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to install git hooks" -ForegroundColor Red
    exit 1
}
