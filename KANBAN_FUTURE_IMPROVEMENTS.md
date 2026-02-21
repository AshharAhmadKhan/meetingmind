# Kanban Future Improvements

**Last Updated:** 2026-02-21  
**Status:** Deferred for future sprint

This document tracks structural improvements for the Kanban feature that are NOT critical for current release but should be addressed in future iterations.

---

## 1. Within-Column Reordering (Priority: MEDIUM)

**Current State:** Cards cannot be reordered within the same column.

**Impact:** Users cannot prioritize tasks within a status.

**Implementation:**
- Add `order` field to action schema (float, Lexorank-style)
- Update `process-meeting` Lambda to assign initial orders
- Add `reorderAction` API endpoint
- Implement drag-and-drop reordering in UI
- Add migration script for existing actions

**Effort:** 1-2 days  
**Risk:** MEDIUM - Requires schema change and data migration

---

## 2. Optimistic Locking / Concurrency Control (Priority: HIGH)

**Current State:** Last-write-wins. Concurrent updates clobber each other.

**Impact:** In team environments, users can lose each other's changes.

**Scenario:**
```
User A: Moves card-1 to "Done"
User B: Moves card-2 to "Blocked" (at same time)
Result: Only User B's change persists, User A's change lost
```

**Implementation:**
- Add `version` field to meeting documents
- Use DynamoDB conditional updates
- Implement retry logic with exponential backoff
- Add conflict resolution UI ("Someone else modified this, refresh?")

**Effort:** 1-2 days  
**Risk:** MEDIUM - Changes update logic, needs careful testing

---

## 3. Real-Time Sync (Priority: LOW)

**Current State:** Changes only visible after page refresh.

**Impact:** Team members don't see each other's updates in real-time.

**Implementation:**
- Add WebSocket connection (AWS API Gateway WebSocket)
- Broadcast status changes to all connected clients
- Handle concurrent drag conflicts
- Add presence indicators ("John is viewing this board")

**Effort:** 3-4 days  
**Risk:** HIGH - Complex infrastructure, potential state thrashing

---

## 4. Comprehensive Test Coverage (Priority: CRITICAL)

**Current State:** ZERO tests for Kanban functionality.

**Impact:** Cannot safely refactor or add features.

**Required Tests:**

### Unit Tests (Frontend)
- `KanbanBoard.handleDragStart` - Sets activeId correctly
- `KanbanBoard.handleDragEnd` - Detects drop targets (column vs card)
- `KanbanBoard.getStatus` - Derives status from action correctly
- `ActionsOverview.handleStatusChange` - Optimistic update + API call
- `ActionsOverview.handleStatusChange` - Rollback on error

### Integration Tests (Backend)
- `PUT /meetings/{id}/actions/{id}` - Updates status
- `PUT /meetings/{id}/actions/{id}` - Validates status values
- `PUT /meetings/{id}/actions/{id}` - Handles concurrent updates
- `PUT /meetings/{id}/actions/{id}` - Returns 404 for missing action
- `PUT /meetings/{id}/actions/{id}` - Enforces team permissions

### E2E Tests
- Drag card from todo → in_progress
- Drag card from in_progress → done
- Drag card to empty column
- Drag multiple cards in sequence
- Drag card while filter active
- Drag card during network failure
- Concurrent drags from two users

**Effort:** 2-3 days  
**Risk:** LOW - Tests don't affect production code

---

## 5. Improved Error Handling (Priority: MEDIUM)

**Current State:** On API failure, entire state refreshed (loses other pending changes).

**Impact:** If one update fails, all optimistic updates lost.

**Implementation:**
- Queue optimistic updates
- Retry failed updates individually
- Show per-card error states
- Add "Undo" functionality

**Effort:** 1 day  
**Risk:** LOW - Additive changes only

---

## 6. Performance Optimization (Priority: LOW)

**Current State:** All actions loaded on page load, no pagination.

**Impact:** With 1000+ actions, page becomes slow.

**Implementation:**
- Add pagination to `GET /all-actions`
- Implement virtual scrolling in Kanban columns
- Lazy load actions as user scrolls
- Add caching layer (Redis)

**Effort:** 2-3 days  
**Risk:** MEDIUM - Changes data loading patterns

---

## 7. Accessibility Improvements (Priority: MEDIUM)

**Current State:** Keyboard navigation not fully supported.

**Impact:** Users with disabilities cannot use Kanban effectively.

**Implementation:**
- Add keyboard shortcuts (arrow keys to move between cards)
- Add screen reader announcements for drag-and-drop
- Ensure focus management during drag
- Add ARIA labels and roles

**Effort:** 1-2 days  
**Risk:** LOW - Additive changes only

---

## 8. Mobile Support (Priority: LOW)

**Current State:** Drag-and-drop doesn't work well on touch devices.

**Impact:** Mobile users cannot use Kanban.

**Implementation:**
- Add touch sensor to @dnd-kit
- Optimize column layout for mobile (vertical stacking)
- Add swipe gestures for status change
- Test on iOS and Android

**Effort:** 2-3 days  
**Risk:** MEDIUM - Touch interactions complex

---

## 9. Analytics & Monitoring (Priority: HIGH)

**Current State:** No metrics on Kanban usage or failures.

**Impact:** Cannot detect issues or measure improvements.

**Implementation:**
- Add CloudWatch metrics for:
  - Drop success rate
  - API call latency
  - Error rates
  - Concurrent update conflicts
- Add user analytics:
  - Most used status transitions
  - Average time in each status
  - Bottleneck detection

**Effort:** 1 day  
**Risk:** LOW - Monitoring only, no functional changes

---

## 10. Visual Improvements (Priority: LOW)

**Current State:** Basic styling, no animations.

**Impact:** UX feels clunky.

**Implementation:**
- Add smooth card animations during drag
- Add column highlight on drag-over
- Add success/error toast notifications
- Add loading states during API calls
- Add empty state illustrations

**Effort:** 1-2 days  
**Risk:** LOW - CSS/animation changes only

---

## Implementation Priority

**Sprint 1 (Next 2 weeks):**
1. Comprehensive Test Coverage (#4) - CRITICAL
2. Optimistic Locking (#2) - HIGH
3. Analytics & Monitoring (#9) - HIGH

**Sprint 2 (Weeks 3-4):**
4. Within-Column Reordering (#1) - MEDIUM
5. Improved Error Handling (#5) - MEDIUM
6. Accessibility Improvements (#7) - MEDIUM

**Sprint 3 (Weeks 5-6):**
7. Performance Optimization (#6) - LOW
8. Visual Improvements (#10) - LOW

**Future (3+ months):**
9. Real-Time Sync (#3) - LOW (complex, needs infrastructure)
10. Mobile Support (#8) - LOW (separate mobile strategy needed)

---

## Notes

- All improvements should be behind feature flags
- Gradual rollout (10% → 50% → 100%)
- Monitor error rates and rollback if needed
- Update this document as priorities change
