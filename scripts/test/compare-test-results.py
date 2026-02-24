#!/usr/bin/env python3
"""
Compare test results before and after fix
Shows improvements in a beautiful format
"""

import json
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_report(filename):
    """Load test report from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.RED}Error: {filename} not found{Colors.END}")
        return None

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(100)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*100}{Colors.END}\n")

def compare_reports(before, after):
    """Compare two test reports and show improvements"""
    
    print_header("BEFORE vs AFTER FIX COMPARISON")
    
    # Overall comparison
    print(f"{Colors.BOLD}OVERALL RESULTS:{Colors.END}\n")
    print(f"{'Metric':<30} {'Before':<20} {'After':<20} {'Change':<20}")
    print(f"{'-'*90}")
    
    before_total = before['total_tests']
    after_total = after['total_tests']
    before_passed = before['passed']
    after_passed = after['passed']
    before_rate = (before_passed / before_total * 100) if before_total > 0 else 0
    after_rate = (after_passed / after_total * 100) if after_total > 0 else 0
    
    print(f"{'Total Tests':<30} {before_total:<20} {after_total:<20} {'':<20}")
    print(f"{'Passed Tests':<30} {before_passed:<20} {after_passed:<20} {Colors.GREEN}+{after_passed - before_passed}{Colors.END}")
    print(f"{'Failed Tests':<30} {before['failed']:<20} {after['failed']:<20} {Colors.GREEN}{after['failed'] - before['failed']}{Colors.END}")
    
    rate_change = after_rate - before_rate
    rate_color = Colors.GREEN if rate_change > 0 else Colors.RED if rate_change < 0 else Colors.YELLOW
    print(f"{'Pass Rate':<30} {before_rate:.1f}%{'':<15} {after_rate:.1f}%{'':<15} {rate_color}{rate_change:+.1f}%{Colors.END}")
    
    # Category comparison
    print(f"\n{Colors.BOLD}RESULTS BY CATEGORY:{Colors.END}\n")
    
    # Group tests by category
    before_cats = {}
    after_cats = {}
    
    for test in before['tests']:
        cat = test['category']
        if cat not in before_cats:
            before_cats[cat] = {'passed': 0, 'total': 0}
        before_cats[cat]['total'] += 1
        if test['passed']:
            before_cats[cat]['passed'] += 1
    
    for test in after['tests']:
        cat = test['category']
        if cat not in after_cats:
            after_cats[cat] = {'passed': 0, 'total': 0}
        after_cats[cat]['total'] += 1
        if test['passed']:
            after_cats[cat]['passed'] += 1
    
    print(f"{'Category':<20} {'Before':<25} {'After':<25} {'Improvement':<20}")
    print(f"{'-'*90}")
    
    for cat in sorted(set(list(before_cats.keys()) + list(after_cats.keys()))):
        before_data = before_cats.get(cat, {'passed': 0, 'total': 0})
        after_data = after_cats.get(cat, {'passed': 0, 'total': 0})
        
        before_str = f"{before_data['passed']}/{before_data['total']}"
        after_str = f"{after_data['passed']}/{after_data['total']}"
        
        before_pct = (before_data['passed'] / before_data['total'] * 100) if before_data['total'] > 0 else 0
        after_pct = (after_data['passed'] / after_data['total'] * 100) if after_data['total'] > 0 else 0
        improvement = after_pct - before_pct
        
        imp_color = Colors.GREEN if improvement > 0 else Colors.RED if improvement < 0 else Colors.YELLOW
        print(f"{cat.upper():<20} {before_str:<10} ({before_pct:.1f}%){'':<10} {after_str:<10} ({after_pct:.1f}%){'':<10} {imp_color}{improvement:+.1f}%{Colors.END}")
    
    # Show fixed tests
    before_failed = {f"{t['category']}.{t['name']}" for t in before['tests'] if not t['passed']}
    after_failed = {f"{t['category']}.{t['name']}" for t in after['tests'] if not t['passed']}
    
    fixed_tests = before_failed - after_failed
    new_failures = after_failed - before_failed
    
    if fixed_tests:
        print(f"\n{Colors.BOLD}{Colors.GREEN}TESTS FIXED ({len(fixed_tests)}):{Colors.END}")
        for test_name in sorted(fixed_tests):
            print(f"  ✓ {test_name}")
    
    if new_failures:
        print(f"\n{Colors.BOLD}{Colors.RED}NEW FAILURES ({len(new_failures)}):{Colors.END}")
        for test_name in sorted(new_failures):
            print(f"  ✗ {test_name}")
    
    # Show key metrics improvements
    print(f"\n{Colors.BOLD}KEY METRICS IMPROVEMENTS:{Colors.END}\n")
    
    # Find extraction tests
    before_extraction = {t['name']: t for t in before['tests'] if t['category'] == 'extraction'}
    after_extraction = {t['name']: t for t in after['tests'] if t['category'] == 'extraction'}
    
    metrics = [
        ('action_item_count', 'Action Item Extraction'),
        ('action_text_population', 'Action Text Population'),
        ('decision_count', 'Decision Extraction'),
    ]
    
    for test_name, display_name in metrics:
        if test_name in before_extraction and test_name in after_extraction:
            before_test = before_extraction[test_name]
            after_test = after_extraction[test_name]
            
            if before_test.get('details') and after_test.get('details'):
                before_rate = before_test['details'].get('rate', 'N/A')
                after_rate = after_test['details'].get('rate', 'N/A')
                
                status_before = Colors.GREEN + "✓" if before_test['passed'] else Colors.RED + "✗"
                status_after = Colors.GREEN + "✓" if after_test['passed'] else Colors.RED + "✗"
                
                print(f"{display_name:<30} {status_before} {before_rate:<15}{Colors.END} → {status_after} {after_rate:<15}{Colors.END}")
    
    # Final verdict
    print(f"\n{Colors.BOLD}FINAL VERDICT:{Colors.END}\n")
    
    if after_rate >= 95:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 EXTRAORDINARY: System is now operating at peak performance!{Colors.END}")
    elif after_rate >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}✨ EXCELLENT: Significant improvements achieved!{Colors.END}")
    elif after_rate >= 80:
        print(f"{Colors.YELLOW}{Colors.BOLD}👍 GOOD: Notable improvements, minor issues remain{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  NEEDS WORK: Some improvements but more work needed{Colors.END}")
    
    print()

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare-test-results.py <before_report.json> <after_report.json>")
        sys.exit(1)
    
    before_file = sys.argv[1]
    after_file = sys.argv[2]
    
    before = load_report(before_file)
    after = load_report(after_file)
    
    if not before or not after:
        sys.exit(1)
    
    compare_reports(before, after)

if __name__ == '__main__':
    main()
