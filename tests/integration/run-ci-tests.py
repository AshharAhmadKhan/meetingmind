#!/usr/bin/env python3
"""
MeetingMind CI/CD Test Suite
Must pass before any commits or deployments

This is the master test runner that validates:
1. Infrastructure (AWS services)
2. Backend APIs (Lambda functions)
3. Data integrity (DynamoDB)
4. Feature correctness (calculations, formulas)
5. Security (authentication, authorization)

Exit code 0 = All tests passed, safe to commit/deploy
Exit code 1 = Tests failed, DO NOT commit/deploy
"""

import sys
import os
import subprocess
from datetime import datetime

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestSuite:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.failed_suites = []
    
    def run_test(self, name, script_path, critical=True):
        """Run a test script and track results"""
        self.total_tests += 1
        
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Running: {name}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
        
        try:
            # Set environment for subprocess
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
                encoding='utf-8',
                errors='replace'
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode == 0:
                self.passed_tests += 1
                print(f"{Colors.GREEN}✅ {name} PASSED{Colors.RESET}")
                return True
            else:
                self.failed_tests += 1
                self.failed_suites.append((name, critical))
                print(f"{Colors.RED}❌ {name} FAILED{Colors.RESET}")
                return False
                
        except subprocess.TimeoutExpired:
            self.failed_tests += 1
            self.failed_suites.append((name, critical))
            print(f"{Colors.RED}❌ {name} TIMEOUT{Colors.RESET}")
            return False
        except FileNotFoundError:
            self.skipped_tests += 1
            print(f"{Colors.YELLOW}⚠️  {name} SKIPPED (file not found){Colors.RESET}")
            return None
        except Exception as e:
            self.failed_tests += 1
            self.failed_suites.append((name, critical))
            print(f"{Colors.RED}❌ {name} ERROR: {e}{Colors.RESET}")
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUITE SUMMARY{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"Total Tests:   {self.total_tests}")
        print(f"{Colors.GREEN}✅ Passed:     {self.passed_tests}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed:     {self.failed_tests}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️  Skipped:    {self.skipped_tests}{Colors.RESET}")
        
        if self.failed_suites:
            print(f"\n{Colors.RED}FAILED TESTS:{Colors.RESET}")
            for name, critical in self.failed_suites:
                status = "CRITICAL" if critical else "NON-CRITICAL"
                print(f"  {Colors.RED}❌{Colors.RESET} {name} ({status})")
        
        # Calculate pass rate
        if self.total_tests > 0:
            pass_rate = (self.passed_tests / self.total_tests) * 100
            print(f"\n{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.RESET}")
        
        # Determine if tests passed
        critical_failures = [name for name, critical in self.failed_suites if critical]
        
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        if critical_failures:
            print(f"{Colors.RED}{Colors.BOLD}❌ CI TESTS FAILED - DO NOT COMMIT/DEPLOY{Colors.RESET}")
            print(f"{Colors.RED}Critical failures: {len(critical_failures)}{Colors.RESET}")
            return False
        elif self.failed_tests > 0:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  CI TESTS PASSED WITH WARNINGS{Colors.RESET}")
            print(f"{Colors.YELLOW}Non-critical failures: {self.failed_tests}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL CI TESTS PASSED - SAFE TO COMMIT/DEPLOY{Colors.RESET}")
            return True

def main():
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}MEETINGMIND CI/CD TEST SUITE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Validate system before commit/deployment")
    
    suite = TestSuite()
    
    # ============================================================
    # CRITICAL TESTS - Must pass for commit/deploy
    # ============================================================
    
    print(f"\n{Colors.BOLD}PHASE 1: INFRASTRUCTURE TESTS (NON-CRITICAL){Colors.RESET}")
    suite.run_test(
        "Infrastructure Health Check",
        "tests/integration/core/comprehensive-test-suite.py",
        critical=False  # Non-critical because Bedrock Claude payment issue is expected
    )
    
    print(f"\n{Colors.BOLD}PHASE 2: BACKEND API TESTS (CRITICAL){Colors.RESET}")
    suite.run_test(
        "List Meetings API",
        "tests/integration/api/test-list-meetings-api.py",
        critical=True
    )
    suite.run_test(
        "Get Meeting Lambda",
        "tests/integration/test-get-meeting-lambda.py",
        critical=True
    )
    suite.run_test(
        "Update Action API",
        "tests/integration/test-update-action-team-member.py",
        critical=True
    )
    suite.run_test(
        "Get All Actions API",
        "tests/integration/test-get-all-actions-quick.py",
        critical=True
    )
    suite.run_test(
        "Team Meetings API",
        "tests/integration/api/test-team-meetings-api.py",
        critical=True
    )
    suite.run_test(
        "Debt Analytics API",
        "tests/integration/api/test-debt-api-call.py",
        critical=True
    )
    
    print(f"\n{Colors.BOLD}PHASE 3: FEATURE TESTS (CRITICAL){Colors.RESET}")
    suite.run_test(
        "Health Score & ROI Calculations",
        "tests/integration/test-current-health-roi.py",
        critical=True
    )
    suite.run_test(
        "Meeting Rating Formula",
        "tests/integration/features/verify-meeting-rating-formula.py",
        critical=True
    )
    suite.run_test(
        "Debt Dashboard Calculations",
        "tests/integration/features/test-debt-dashboard.py",
        critical=True
    )
    suite.run_test(
        "Graveyard Data Integrity",
        "tests/integration/features/test-graveyard-data.py",
        critical=True
    )
    
    print(f"\n{Colors.BOLD}PHASE 4: SECURITY TESTS (CRITICAL){Colors.RESET}")
    suite.run_test(
        "Team Member Access Control",
        "tests/integration/test-team-member-access.py",
        critical=True
    )
    suite.run_test(
        "Team Filtering & Isolation",
        "tests/integration/test-team-filtering.py",
        critical=True
    )
    
    print(f"\n{Colors.BOLD}PHASE 5: DATA INTEGRITY TESTS (CRITICAL){Colors.RESET}")
    suite.run_test(
        "Meeting Data Integrity",
        "tests/integration/core/verify-test-meeting.py",
        critical=True
    )
    suite.run_test(
        "Team Data Integrity",
        "tests/integration/check-teams.py",
        critical=True
    )
    suite.run_test(
        "Meeting Format Consistency",
        "tests/integration/core/compare-meeting-formats.py",
        critical=True
    )
    suite.run_test(
        "Account Access Check",
        "tests/integration/check-all-accounts.py",
        critical=True
    )
    
    # ============================================================
    # NON-CRITICAL TESTS - Warnings only
    # ============================================================
    
    print(f"\n{Colors.BOLD}PHASE 6: OPTIONAL FEATURE TESTS (NON-CRITICAL){Colors.RESET}")
    suite.run_test(
        "Duplicate Detection",
        "tests/integration/features/test-duplicate-detection.py",
        critical=False
    )
    suite.run_test(
        "View Invite Code",
        "tests/integration/features/test-view-invite-code.py",
        critical=False
    )
    suite.run_test(
        "Graveyard Data Check",
        "tests/integration/features/check-graveyard-data.py",
        critical=False
    )
    suite.run_test(
        "Duplicate Lambda Direct",
        "tests/integration/features/test-duplicate-lambda-direct.py",
        critical=False
    )
    
    print(f"\n{Colors.BOLD}PHASE 7: ENVIRONMENT CHECKS (NON-CRITICAL){Colors.RESET}")
    suite.run_test(
        "AWS Account Configuration",
        "tests/integration/check-aws-account.py",
        critical=False
    )
    suite.run_test(
        "Bedrock Status",
        "tests/integration/check-bedrock-status.py",
        critical=False
    )
    suite.run_test(
        "CloudFront Cache Status",
        "tests/integration/check-cloudfront-cache.py",
        critical=False
    )
    
    # Print final summary
    all_passed = suite.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite error: {e}{Colors.RESET}")
        sys.exit(1)
