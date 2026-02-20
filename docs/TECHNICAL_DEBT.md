# Technical Debt Register

**Last Updated**: February 21, 2026  
**Total Items**: 2  
**High Priority**: 0 | **Medium Priority**: 1 | **Low Priority**: 1

---

## Active Technical Debt

### TD-001: Inefficient Team Query Performance
**Priority**: 🟡 Medium  
**Status**: Open  
**Created**: February 21, 2026  
**File**: `backend/functions/list-user-teams/app.py:26`

**Description**:  
The `list-user-teams` Lambda function currently performs a full table scan of the teams table and filters results in memory to find teams where the user is a member. This is inefficient and will cause performance degradation at scale.

**Current Implementation**:
```python
# Scan all teams and filter by membership (inefficient but simple for MVP)
# TODO: Add userId-teamId GSI for efficient queries
response = table.scan()

user_teams = []
for team in response.get('Items', []):
    members = team.get('members', [])
    if any(m['userId'] == user_id for m in members):
        user_teams.append({...})
```

**Impact**:
- Performance: O(n) scan of entire teams table
- Cost: Increased DynamoDB read capacity units
- Scalability: Unacceptable at >1000 teams
- User Experience: Slow team list loading

**Proposed Solution**:
1. Add Global Secondary Index (GSI) to teams table:
   - Partition Key: `userId` (from members array)
   - Sort Key: `teamId`
   - Projection: ALL or KEYS_ONLY
2. Update Lambda to query GSI instead of scanning
3. Expected performance: O(1) query with direct userId lookup

**Estimated Effort**: 2-3 hours
- DynamoDB GSI creation: 30 minutes
- Lambda code update: 1 hour
- Testing: 1 hour
- Deployment: 30 minutes

**Blockers**: None - can be implemented anytime

**Acceptance Criteria**:
- [ ] GSI created on teams table
- [ ] Lambda updated to use GSI query
- [ ] Performance test shows <100ms response time
- [ ] No regression in functionality
- [ ] Documentation updated

**Notes**:
- Acceptable for MVP with <100 teams
- Critical for production scale
- Consider implementing before public launch

---

### TD-002: Within-Column Reordering Not Implemented
**Priority**: 🟢 Low  
**Status**: Open  
**Created**: February 21, 2026  
**File**: `frontend/src/components/KanbanBoard.jsx:312`

**Description**:  
The Kanban board currently only supports moving action items between columns (status changes). Users cannot reorder items within the same column to prioritize tasks.

**Current Implementation**:
```javascript
// Same column reordering
if (overStatus && activeStatus === overStatus) {
  // TODO: Implement onReorder callback for within-column reordering
  // For now, we skip this as backend doesn't support order field yet
  return;
}
```

**Impact**:
- UX: Users cannot prioritize tasks within a column
- Workaround: Users must move items between columns to reorder
- Severity: Low (nice-to-have feature, not blocking)

**Proposed Solution**:
1. Add `order` field to action items in DynamoDB schema
2. Implement `onReorder` callback in KanbanBoard component
3. Create backend API endpoint to update action order
4. Update drag-and-drop logic to handle within-column moves

**Estimated Effort**: 4-6 hours
- DynamoDB schema change: 1 hour
- Backend API endpoint: 2 hours
- Frontend logic: 2 hours
- Testing: 1 hour

**Blockers**: 
- Requires DynamoDB schema change (add `order` field)
- Need to decide on ordering strategy (integer, float, or timestamp)

**Acceptance Criteria**:
- [ ] Action items have `order` field
- [ ] Users can drag items within same column
- [ ] Order persists across page reloads
- [ ] Order is maintained when new items are added
- [ ] No performance degradation

**Notes**:
- Consider using fractional indexing for order field
- May need migration script for existing action items
- Low priority - defer until user feedback requests it

---

## Resolved Technical Debt

None yet.

---

## Debt Metrics

**Total Debt**: 2 items  
**Estimated Total Effort**: 6-9 hours  
**Average Age**: 0 days (all created today)  
**Debt Trend**: Stable

---

## Review Schedule

- **Weekly**: Review new debt items from code reviews
- **Monthly**: Prioritize and schedule debt resolution
- **Quarterly**: Analyze debt trends and impact

---

## Contributing

When adding technical debt:
1. Create a new section with unique ID (TD-XXX)
2. Include all required fields (Priority, Status, File, Description, Impact, Solution, Effort, Blockers)
3. Update the summary metrics at the top
4. Link to relevant GitHub issues if applicable

