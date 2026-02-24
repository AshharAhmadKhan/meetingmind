# Implementation Checklist - Race Condition & Health Score Fixes

## Pre-Implementation Checkpoint ✅
- [x] Current state committed (commit: 066ac5e)
- [x] Comprehensive diagnosis completed
- [x] Implementation plan documented
- [ ] All tests passing before changes

## Phase 1: Fix Race Condition in Action Updates

### Step 1.1: Create Test Suite
- [ ] Create `tests/test-race-condition.py` - Test concurrent updates
- [ ] Create `tests/test-action-update.py` - Test single updates
- [ ] Run baseline tests (expect failures)

### Step 1.2: Implement Atomic Updates
- [ ] Backup `backend/functions/update-action/app.py`
- [ ] Rewrite to use DynamoDB atomic update expressions
- [ ] Handle action index lookup
- [ ] Handle owner/deadline updates atomically
- [ ] Add error handling for concurrent modifications

### Step 1.3: Test Race Condition Fix
- [ ] Test 1: Single action update
- [ ] Test 2: 10 rapid sequential updates
- [ ] Test 3: 10 concurrent updates (simulate race)
- [ ] Test 4: Update with owner change
- [ ] Test 5: Update with deadline change
- [ ] Test 6: Update with status change
- [ ] Verify all updates persist after refresh

## Phase 2: Fix Health Score Recalculation

### Step 2.1: Create Shared Health Module
- [ ] Create `backend/layers/shared-health/python/health_calculator.py`
- [ ] Implement `calculate_health_score()` function
- [ ] Implement `generate_autopsy()` function
- [ ] Add unit tests for health calculations

### Step 2.2: Update Lambda Functions
- [ ] Update `backend/functions/process-meeting/app.py` to use shared module
- [ ] Update `backend/functions/update-action/app.py` to recalculate health
- [ ] Update `backend/template.yaml` to add SharedHealthLayer

### Step 2.3: Test Health Score Recalculation
- [ ] Test 1: Complete 1 action, verify score increases
- [ ] Test 2: Complete 5 actions, verify score continues to increase
- [ ] Test 3: Refresh page, verify score persists
- [ ] Test 4: Verify grade changes (F → D → C → B → A)
- [ ] Test 5: Verify autopsy appears/disappears correctly
- [ ] Test 6: Verify health label updates

## Phase 3: Integration Testing

### Step 3.1: End-to-End Tests
- [ ] Test complete user workflow
- [ ] Test with meeting 3d3 (12/22 completed)
- [ ] Test with fresh meeting (0 completed)
- [ ] Test with fully completed meeting (22/22)
- [ ] Test team member access
- [ ] Test concurrent users

### Step 3.2: Performance Testing
- [ ] Measure action update latency (before/after)
- [ ] Measure health calculation time
- [ ] Verify no timeout issues
- [ ] Check CloudWatch metrics

### Step 3.3: Regression Testing
- [ ] Meeting Detail page works
- [ ] Meeting List page works
- [ ] Graveyard works
- [ ] Debt Analytics works
- [ ] All Actions page works
- [ ] Email notifications work
- [ ] ROI calculation works

## Phase 4: Deployment

### Step 4.1: Pre-Deployment
- [ ] All tests passing (100%)
- [ ] Code review completed
- [ ] Backup current deployment
- [ ] Document rollback procedure

### Step 4.2: Deploy to Production
- [ ] Build backend: `sam build`
- [ ] Deploy backend: `sam deploy`
- [ ] Verify Lambda functions updated
- [ ] Check CloudWatch logs for errors

### Step 4.3: Post-Deployment Verification
- [ ] Test with meeting 3d3
- [ ] Click 10 actions rapidly
- [ ] Verify all 10 persist
- [ ] Verify health score updates
- [ ] Monitor for 30 minutes

## Phase 5: Validation

### Step 5.1: User Acceptance Testing
- [ ] User tests rapid clicking (10+ actions)
- [ ] User verifies all updates persist
- [ ] User verifies health score updates
- [ ] User verifies grade changes
- [ ] User confirms issue resolved

### Step 5.2: Monitoring
- [ ] Monitor CloudWatch logs (24 hours)
- [ ] Check error rates
- [ ] Check latency metrics
- [ ] Verify no new issues

## Rollback Plan (If Needed)

### Rollback Steps
1. [ ] Revert to commit 066ac5e
2. [ ] Rebuild: `sam build`
3. [ ] Redeploy: `sam deploy`
4. [ ] Verify rollback successful
5. [ ] Investigate issues
6. [ ] Fix and retry

## Success Criteria

- [ ] ✅ Race condition eliminated (10/10 updates persist)
- [ ] ✅ Health score recalculates on action update
- [ ] ✅ Grade updates correctly (F → B for meeting 3d3)
- [ ] ✅ Autopsy updates correctly
- [ ] ✅ No breaking changes
- [ ] ✅ No performance degradation (< 200ms per update)
- [ ] ✅ All existing features work
- [ ] ✅ User confirms issues resolved

## Notes

- Test thoroughly before deploying
- Monitor closely after deployment
- Have rollback plan ready
- Document any issues encountered
