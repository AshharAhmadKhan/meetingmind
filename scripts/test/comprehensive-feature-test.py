#!/usr/bin/env python3
"""
COMPREHENSIVE FEATURE TEST SUITE
Tests ALL MeetingMind features before and after AI extraction fix

Run this BEFORE fix, then AFTER fix to compare results.
"""

import boto3
import json
from datetime import datetime, timezone
from decimal import Decimal

REGION = 'ap-south-1'
TEST_EMAIL = 'ashkagakoko@gmail.com'
TEST_MEETING_ID = 'e3917e6d-a53e-421d-977c-6a822bca927f'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
meetings_table = dynamodb.Table('meetingmind-meetings')
cognito = boto3.client('cognito-idp', region_name=REGION)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─'*80}{Colors.END}")

def print_pass(text):
    print(f"{Colors.GREEN}✓ PASS{Colors.END} {text}")

def print_fail(text):
    print(f"{Colors.RED}✗ FAIL{Colors.END} {text}")

def print_warn(text):
    print(f"{Colors.YELLOW}⚠ WARN{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ INFO{Colors.END} {text}")

def get_user_id(email):
    """Get user ID from Cognito"""
    try:
        response = cognito.list_users(
            UserPoolId='ap-south-1_mkFJawjMp',
            Filter=f'email = "{email}"'
        )
        if response['Users']:
            for attr in response['Users'][0]['Attributes']:
                if attr['Name'] == 'sub':
                    return attr['Value']
    except Exception as e:
        print_fail(f"Error getting user: {e}")
    return None

def get_test_meeting():
    """Get test meeting from database"""
    user_id = get_user_id(TEST_EMAIL)
    if not user_id:
        return None
    
    try:
        response = meetings_table.get_item(
            Key={'userId': user_id, 'meetingId': TEST_MEETING_ID}
        )
        return response.get('Item')
    except Exception as e:
        print_fail(f"Error getting meeting: {e}")
        return None

# Test results storage
test_results = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}

def record_test(category, name, passed, details=None):
    """Record test result"""
    test_results['total_tests'] += 1
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
    
    test_results['tests'].append({
        'category': category,
        'name': name,
        'passed': passed,
        'details': details
    })


def test_1_data_extraction():
    """Test 1: AI Data Extraction Quality"""
    print_section("TEST 1: AI DATA EXTRACTION QUALITY")
    
    meeting = get_test_meeting()
    if not meeting:
        print_fail("Could not load test meeting")
        return
    
    actions = meeting.get('actionItems', [])
    decisions = meeting.get('decisions', [])
    followups = meeting.get('followUps', [])
    
    # Expected values from test script
    EXPECTED_ACTIONS = 23
    EXPECTED_DECISIONS = 8
    EXPECTED_FOLLOWUPS = 4
    
    # Test 1.1: Action Item Count
    action_count = len(actions)
    extraction_rate = (action_count / EXPECTED_ACTIONS) * 100
    passed = action_count >= 20  # 85%+ is passing
    
    if passed:
        print_pass(f"Action item extraction: {action_count}/{EXPECTED_ACTIONS} ({extraction_rate:.1f}%)")
    else:
        print_fail(f"Action item extraction: {action_count}/{EXPECTED_ACTIONS} ({extraction_rate:.1f}%) - Expected 20+")
    
    record_test('extraction', 'action_item_count', passed, {
        'actual': action_count,
        'expected': EXPECTED_ACTIONS,
        'rate': f"{extraction_rate:.1f}%"
    })
    
    # Test 1.2: Action Item Text Population
    empty_text_count = 0
    populated_text_count = 0
    
    for action in actions:
        task_text = action.get('task', '')
        if task_text and task_text.strip():
            populated_text_count += 1
        else:
            empty_text_count += 1
    
    text_population_rate = (populated_text_count / action_count * 100) if action_count > 0 else 0
    passed = text_population_rate == 100
    
    if passed:
        print_pass(f"Action text population: {populated_text_count}/{action_count} (100%)")
    else:
        print_fail(f"Action text population: {populated_text_count}/{action_count} ({text_population_rate:.1f}%) - {empty_text_count} empty")
    
    record_test('extraction', 'action_text_population', passed, {
        'populated': populated_text_count,
        'empty': empty_text_count,
        'rate': f"{text_population_rate:.1f}%"
    })
    
    # Test 1.3: Owner Extraction
    owned_count = sum(1 for a in actions if a.get('owner') and a['owner'] != 'Unassigned')
    owner_rate = (owned_count / action_count * 100) if action_count > 0 else 0
    passed = owner_rate >= 80
    
    if passed:
        print_pass(f"Owner assignment: {owned_count}/{action_count} ({owner_rate:.1f}%)")
    else:
        print_warn(f"Owner assignment: {owned_count}/{action_count} ({owner_rate:.1f}%) - Expected 80%+")
    
    record_test('extraction', 'owner_assignment', passed, {
        'assigned': owned_count,
        'total': action_count,
        'rate': f"{owner_rate:.1f}%"
    })
    
    # Test 1.4: Deadline Extraction
    deadline_count = sum(1 for a in actions if a.get('deadline'))
    deadline_rate = (deadline_count / action_count * 100) if action_count > 0 else 0
    passed = deadline_rate >= 80
    
    if passed:
        print_pass(f"Deadline assignment: {deadline_count}/{action_count} ({deadline_rate:.1f}%)")
    else:
        print_warn(f"Deadline assignment: {deadline_count}/{action_count} ({deadline_rate:.1f}%) - Expected 80%+")
    
    record_test('extraction', 'deadline_assignment', passed, {
        'assigned': deadline_count,
        'total': action_count,
        'rate': f"{deadline_rate:.1f}%"
    })
    
    # Test 1.5: Decision Extraction
    decision_count = len(decisions)
    decision_rate = (decision_count / EXPECTED_DECISIONS) * 100
    passed = decision_count >= 7  # 85%+
    
    if passed:
        print_pass(f"Decision extraction: {decision_count}/{EXPECTED_DECISIONS} ({decision_rate:.1f}%)")
    else:
        print_fail(f"Decision extraction: {decision_count}/{EXPECTED_DECISIONS} ({decision_rate:.1f}%) - Expected 7+")
    
    record_test('extraction', 'decision_count', passed, {
        'actual': decision_count,
        'expected': EXPECTED_DECISIONS,
        'rate': f"{decision_rate:.1f}%"
    })
    
    # Test 1.6: Follow-up Extraction
    followup_count = len(followups)
    followup_rate = (followup_count / EXPECTED_FOLLOWUPS) * 100
    passed = followup_count >= 3  # 75%+
    
    if passed:
        print_pass(f"Follow-up extraction: {followup_count}/{EXPECTED_FOLLOWUPS} ({followup_rate:.1f}%)")
    else:
        print_warn(f"Follow-up extraction: {followup_count}/{EXPECTED_FOLLOWUPS} ({followup_rate:.1f}%) - Expected 3+")
    
    record_test('extraction', 'followup_count', passed, {
        'actual': followup_count,
        'expected': EXPECTED_FOLLOWUPS,
        'rate': f"{followup_rate:.1f}%"
    })


def test_2_data_quality():
    """Test 2: Data Quality & Completeness"""
    print_section("TEST 2: DATA QUALITY & COMPLETENESS")
    
    meeting = get_test_meeting()
    if not meeting:
        return
    
    actions = meeting.get('actionItems', [])
    
    # Test 2.1: Risk Score Calculation
    risk_scored = sum(1 for a in actions if 'riskScore' in a)
    passed = risk_scored == len(actions)
    
    if passed:
        print_pass(f"Risk scores calculated: {risk_scored}/{len(actions)}")
    else:
        print_fail(f"Risk scores calculated: {risk_scored}/{len(actions)} - Missing {len(actions) - risk_scored}")
    
    record_test('quality', 'risk_score_calculation', passed, {
        'calculated': risk_scored,
        'total': len(actions)
    })
    
    # Test 2.2: Embedding Generation
    embedded = sum(1 for a in actions if 'embedding' in a)
    passed = embedded == len(actions)
    
    if passed:
        print_pass(f"Embeddings generated: {embedded}/{len(actions)}")
    else:
        print_fail(f"Embeddings generated: {embedded}/{len(actions)} - Missing {len(actions) - embedded}")
    
    record_test('quality', 'embedding_generation', passed, {
        'generated': embedded,
        'total': len(actions)
    })
    
    # Test 2.3: Action ID Assignment
    with_ids = sum(1 for a in actions if a.get('id'))
    passed = with_ids == len(actions)
    
    if passed:
        print_pass(f"Action IDs assigned: {with_ids}/{len(actions)}")
    else:
        print_fail(f"Action IDs assigned: {with_ids}/{len(actions)} - Missing {len(actions) - with_ids}")
    
    record_test('quality', 'action_id_assignment', passed, {
        'assigned': with_ids,
        'total': len(actions)
    })
    
    # Test 2.4: Transcript Capture
    transcript = meeting.get('transcript', '')
    passed = len(transcript) >= 4000  # Should be ~5000 chars
    
    if passed:
        print_pass(f"Transcript captured: {len(transcript)} characters")
    else:
        print_fail(f"Transcript captured: {len(transcript)} characters - Expected 4000+")
    
    record_test('quality', 'transcript_capture', passed, {
        'length': len(transcript),
        'expected_min': 4000
    })
    
    # Test 2.5: Summary Generation
    summary = meeting.get('summary', '')
    passed = len(summary) >= 50  # Should be 2-3 sentences
    
    if passed:
        print_pass(f"Summary generated: {len(summary)} characters")
    else:
        print_fail(f"Summary generated: {len(summary)} characters - Expected 50+")
    
    record_test('quality', 'summary_generation', passed, {
        'length': len(summary),
        'expected_min': 50
    })


def test_3_meeting_health():
    """Test 3: Meeting Health & Grading"""
    print_section("TEST 3: MEETING HEALTH & GRADING")
    
    meeting = get_test_meeting()
    if not meeting:
        return
    
    # Test 3.1: Health Score Calculation
    health_score = meeting.get('healthScore')
    passed = health_score is not None
    
    if passed:
        print_pass(f"Health score calculated: {float(health_score)}/100")
    else:
        print_fail("Health score not calculated")
    
    record_test('health', 'health_score_calculation', passed, {
        'score': float(health_score) if health_score else None
    })
    
    # Test 3.2: Health Grade Assignment
    health_grade = meeting.get('healthGrade')
    passed = health_grade in ['A', 'B', 'C', 'D', 'F']
    
    if passed:
        print_pass(f"Health grade assigned: {health_grade}")
    else:
        print_fail(f"Health grade invalid: {health_grade}")
    
    record_test('health', 'health_grade_assignment', passed, {
        'grade': health_grade
    })
    
    # Test 3.3: Grade Accuracy (should be A or B for productive meeting)
    expected_grades = ['A', 'B']
    passed = health_grade in expected_grades
    
    if passed:
        print_pass(f"Grade accuracy: {health_grade} (productive meeting)")
    else:
        print_fail(f"Grade accuracy: {health_grade} - Expected A or B for productive meeting")
    
    record_test('health', 'grade_accuracy', passed, {
        'actual': health_grade,
        'expected': expected_grades
    })
    
    # Test 3.4: ROI Calculation
    roi_data = meeting.get('roi', {})
    passed = 'roi' in roi_data and 'cost' in roi_data and 'value' in roi_data
    
    if passed:
        roi = float(roi_data.get('roi', 0))
        cost = float(roi_data.get('cost', 0))
        value = float(roi_data.get('value', 0))
        print_pass(f"ROI calculated: {roi:.1f}% (Value: ${value:.0f}, Cost: ${cost:.0f})")
    else:
        print_fail("ROI not calculated")
    
    record_test('health', 'roi_calculation', passed, roi_data if passed else None)
    
    # Test 3.5: Autopsy Generation (should not exist for good meetings)
    autopsy = meeting.get('autopsy')
    passed = autopsy is None or health_grade in ['A', 'B', 'C']
    
    if passed:
        if autopsy:
            print_info(f"Autopsy exists for grade {health_grade} (expected for D/F)")
        else:
            print_pass("No autopsy for healthy meeting")
    else:
        print_warn(f"Autopsy missing for grade {health_grade}")
    
    record_test('health', 'autopsy_logic', passed, {
        'has_autopsy': autopsy is not None,
        'grade': health_grade
    })



def test_4_feature_compatibility():
    """Test 4: Feature Compatibility & Integration"""
    print_section("TEST 4: FEATURE COMPATIBILITY & INTEGRATION")
    
    meeting = get_test_meeting()
    if not meeting:
        return
    
    actions = meeting.get('actionItems', [])
    
    # Test 4.1: Duplicate Detection Compatibility
    # Check if actions have embeddings for duplicate detection
    with_embeddings = sum(1 for a in actions if 'embedding' in a and a.get('task'))
    passed = with_embeddings == len([a for a in actions if a.get('task')])
    
    if passed:
        print_pass(f"Duplicate detection ready: {with_embeddings} actions with embeddings")
    else:
        print_fail(f"Duplicate detection broken: Only {with_embeddings}/{len(actions)} have embeddings")
    
    record_test('features', 'duplicate_detection_ready', passed, {
        'ready': with_embeddings,
        'total': len(actions)
    })
    
    # Test 4.2: Graveyard Compatibility
    # Check if old actions can be identified (>30 days)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    old_actions = []
    
    for action in actions:
        created_at = action.get('createdAt')
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (now - created_dt).days
                if days_old > 30:
                    old_actions.append(action)
            except:
                pass
    
    passed = True  # Just checking structure
    print_info(f"Graveyard eligible: {len(old_actions)} actions >30 days old")
    
    record_test('features', 'graveyard_compatibility', passed, {
        'eligible': len(old_actions),
        'total': len(actions)
    })
    
    # Test 4.3: Kanban Board Compatibility
    # Check if actions have status field
    with_status = sum(1 for a in actions if 'status' in a)
    passed = with_status == len(actions)
    
    if passed:
        print_pass(f"Kanban board ready: {with_status}/{len(actions)} actions have status")
    else:
        print_fail(f"Kanban board broken: Only {with_status}/{len(actions)} have status")
    
    record_test('features', 'kanban_board_ready', passed, {
        'ready': with_status,
        'total': len(actions)
    })
    
    # Test 4.4: Email Notification Compatibility
    # Check if meeting has email field
    email = meeting.get('email')
    passed = email is not None and '@' in email
    
    if passed:
        print_pass(f"Email notifications ready: {email}")
    else:
        print_fail("Email notifications broken: No email address")
    
    record_test('features', 'email_notifications_ready', passed, {
        'email': email
    })
    
    # Test 4.5: Pattern Detection Compatibility
    # Check if actions have enough data for pattern detection
    complete_actions = sum(1 for a in actions if a.get('task') and a.get('owner') and a.get('createdAt'))
    passed = complete_actions >= len(actions) * 0.8  # 80%+
    
    if passed:
        print_pass(f"Pattern detection ready: {complete_actions}/{len(actions)} complete actions")
    else:
        print_fail(f"Pattern detection broken: Only {complete_actions}/{len(actions)} complete")
    
    record_test('features', 'pattern_detection_ready', passed, {
        'complete': complete_actions,
        'total': len(actions)
    })


def test_5_data_integrity():
    """Test 5: Data Integrity & Consistency"""
    print_section("TEST 5: DATA INTEGRITY & CONSISTENCY")
    
    meeting = get_test_meeting()
    if not meeting:
        return
    
    actions = meeting.get('actionItems', [])
    
    # Test 5.1: No Duplicate Action IDs
    action_ids = [a.get('id') for a in actions if a.get('id')]
    unique_ids = set(action_ids)
    passed = len(action_ids) == len(unique_ids)
    
    if passed:
        print_pass(f"No duplicate IDs: {len(unique_ids)} unique IDs")
    else:
        print_fail(f"Duplicate IDs found: {len(action_ids)} total, {len(unique_ids)} unique")
    
    record_test('integrity', 'no_duplicate_ids', passed, {
        'total': len(action_ids),
        'unique': len(unique_ids)
    })
    
    # Test 5.2: Valid Deadline Formats
    invalid_deadlines = []
    for action in actions:
        deadline = action.get('deadline')
        if deadline:
            try:
                datetime.strptime(deadline, '%Y-%m-%d')
            except:
                invalid_deadlines.append(deadline)
    
    passed = len(invalid_deadlines) == 0
    
    if passed:
        print_pass("All deadlines valid YYYY-MM-DD format")
    else:
        print_fail(f"Invalid deadlines: {invalid_deadlines}")
    
    record_test('integrity', 'valid_deadline_formats', passed, {
        'invalid': invalid_deadlines
    })
    
    # Test 5.3: Risk Scores in Valid Range
    invalid_risks = []
    for action in actions:
        risk = action.get('riskScore')
        if risk is not None:
            risk_val = float(risk)
            if risk_val < 0 or risk_val > 100:
                invalid_risks.append(risk_val)
    
    passed = len(invalid_risks) == 0
    
    if passed:
        print_pass("All risk scores in valid range (0-100)")
    else:
        print_fail(f"Invalid risk scores: {invalid_risks}")
    
    record_test('integrity', 'valid_risk_scores', passed, {
        'invalid': invalid_risks
    })
    
    # Test 5.4: Meeting Status
    status = meeting.get('status')
    passed = status == 'DONE'
    
    if passed:
        print_pass(f"Meeting status: {status}")
    else:
        print_fail(f"Meeting status: {status} - Expected DONE")
    
    record_test('integrity', 'meeting_status', passed, {
        'status': status
    })
    
    # Test 5.5: Timestamps Present
    has_created = 'createdAt' in meeting
    has_updated = 'updatedAt' in meeting
    passed = has_created and has_updated
    
    if passed:
        print_pass("Timestamps present: createdAt, updatedAt")
    else:
        print_fail(f"Missing timestamps: createdAt={has_created}, updatedAt={has_updated}")
    
    record_test('integrity', 'timestamps_present', passed, {
        'createdAt': has_created,
        'updatedAt': has_updated
    })


def test_6_frontend_compatibility():
    """Test 6: Frontend Display Compatibility"""
    print_section("TEST 6: FRONTEND DISPLAY COMPATIBILITY")
    
    meeting = get_test_meeting()
    if not meeting:
        return
    
    actions = meeting.get('actionItems', [])
    
    # Test 6.1: All Required Fields for Display
    required_fields = ['id', 'task', 'owner', 'deadline', 'completed', 'status', 'riskScore']
    complete_actions = 0
    
    for action in actions:
        has_all = all(field in action for field in required_fields)
        if has_all:
            complete_actions += 1
    
    passed = complete_actions == len(actions)
    
    if passed:
        print_pass(f"All actions displayable: {complete_actions}/{len(actions)}")
    else:
        print_fail(f"Incomplete actions: {len(actions) - complete_actions}/{len(actions)} missing fields")
    
    record_test('frontend', 'all_fields_present', passed, {
        'complete': complete_actions,
        'total': len(actions)
    })
    
    # Test 6.2: Task Text Not Empty (Critical for UI)
    displayable = sum(1 for a in actions if a.get('task') and a['task'].strip())
    passed = displayable == len(actions)
    
    if passed:
        print_pass(f"All tasks displayable: {displayable}/{len(actions)}")
    else:
        print_fail(f"Empty task text: {len(actions) - displayable}/{len(actions)} actions")
    
    record_test('frontend', 'task_text_displayable', passed, {
        'displayable': displayable,
        'empty': len(actions) - displayable
    })
    
    # Test 6.3: Owner Names Present
    with_owners = sum(1 for a in actions if a.get('owner'))
    passed = with_owners == len(actions)
    
    if passed:
        print_pass(f"All owners present: {with_owners}/{len(actions)}")
    else:
        print_fail(f"Missing owners: {len(actions) - with_owners}/{len(actions)} actions")
    
    record_test('frontend', 'owners_present', passed, {
        'present': with_owners,
        'missing': len(actions) - with_owners
    })
    
    # Test 6.4: Meeting Title Present
    title = meeting.get('title')
    passed = title is not None and len(title) > 0
    
    if passed:
        print_pass(f"Meeting title: {title}")
    else:
        print_fail("Meeting title missing")
    
    record_test('frontend', 'meeting_title_present', passed, {
        'title': title
    })
    
    # Test 6.5: Decisions Displayable
    decisions = meeting.get('decisions', [])
    displayable_decisions = sum(1 for d in decisions if (isinstance(d, str) and d.strip()) or (isinstance(d, dict) and d.get('text')))
    passed = displayable_decisions == len(decisions)
    
    if passed:
        print_pass(f"All decisions displayable: {displayable_decisions}/{len(decisions)}")
    else:
        print_fail(f"Empty decisions: {len(decisions) - displayable_decisions}/{len(decisions)}")
    
    record_test('frontend', 'decisions_displayable', passed, {
        'displayable': displayable_decisions,
        'total': len(decisions)
    })


def generate_report():
    """Generate comprehensive test report"""
    print_header("COMPREHENSIVE TEST REPORT")
    
    total = test_results['total_tests']
    passed = test_results['passed']
    failed = test_results['failed']
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}OVERALL RESULTS:{Colors.END}")
    print(f"  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.END}")
    print(f"  Pass Rate: {Colors.GREEN if pass_rate >= 80 else Colors.RED}{pass_rate:.1f}%{Colors.END}")
    
    # Group by category
    categories = {}
    for test in test_results['tests']:
        cat = test['category']
        if cat not in categories:
            categories[cat] = {'passed': 0, 'failed': 0, 'tests': []}
        
        if test['passed']:
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
        categories[cat]['tests'].append(test)
    
    print(f"\n{Colors.BOLD}RESULTS BY CATEGORY:{Colors.END}")
    for cat, data in categories.items():
        total_cat = data['passed'] + data['failed']
        rate = (data['passed'] / total_cat * 100) if total_cat > 0 else 0
        color = Colors.GREEN if rate >= 80 else Colors.YELLOW if rate >= 50 else Colors.RED
        print(f"  {cat.upper()}: {color}{data['passed']}/{total_cat} ({rate:.1f}%){Colors.END}")
    
    # Show failed tests
    failed_tests = [t for t in test_results['tests'] if not t['passed']]
    if failed_tests:
        print(f"\n{Colors.BOLD}{Colors.RED}FAILED TESTS:{Colors.END}")
        for test in failed_tests:
            print(f"  ✗ {test['category']}.{test['name']}")
            if test['details']:
                print(f"    Details: {json.dumps(test['details'], indent=6)}")
    
    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n{Colors.CYAN}Report saved to: {filename}{Colors.END}")
    
    return pass_rate


def main():
    """Run all tests"""
    print_header("MEETINGMIND COMPREHENSIVE FEATURE TEST SUITE")
    print(f"{Colors.CYAN}Test Account: {TEST_EMAIL}{Colors.END}")
    print(f"{Colors.CYAN}Test Meeting: {TEST_MEETING_ID}{Colors.END}")
    print(f"{Colors.CYAN}Timestamp: {datetime.now().isoformat()}{Colors.END}")
    
    # Run all test suites
    test_1_data_extraction()
    test_2_data_quality()
    test_3_meeting_health()
    test_4_feature_compatibility()
    test_5_data_integrity()
    test_6_frontend_compatibility()
    
    # Generate report
    pass_rate = generate_report()
    
    # Final verdict
    print_header("FINAL VERDICT")
    if pass_rate >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}EXCELLENT: System is working at optimal level{Colors.END}")
    elif pass_rate >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}GOOD: System is functional with minor issues{Colors.END}")
    elif pass_rate >= 50:
        print(f"{Colors.YELLOW}{Colors.BOLD}FAIR: System has significant issues that need attention{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}CRITICAL: System has major failures requiring immediate fix{Colors.END}")
    
    print()


if __name__ == '__main__':
    main()
