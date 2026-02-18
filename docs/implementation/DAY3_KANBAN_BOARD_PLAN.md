# Day 3: Kanban Board Implementation Plan

**Status:** 📋 PLANNING - Awaiting Approval  
**Estimated Time:** 4-6 hours  
**Priority:** 🔴 HIGH - Major feature gap in spec

---

## Overview

Add a drag-and-drop Kanban board view to the Actions Overview page, allowing users to visualize and manage action items across all meetings in a visual workflow.

---

## Current State

**What Exists:**
- ✅ `ActionsOverview.jsx` page with list view
- ✅ `get-all-actions` Lambda (backend ready)
- ✅ Filtering by status, owner, team
- ✅ Duplicate detection feature
- ✅ Stats display (total, completed, pending)

**What's Missing:**
- ❌ Kanban board view
- ❌ Drag-and-drop functionality
- ❌ Status columns (To Do, In Progress, Blocked, Done)
- ❌ Visual workflow management
- ❌ Bulk operations

---

## Proposed Solution

### Architecture

```
ActionsOverview.jsx
├── View Toggle (List / Kanban)
├── Existing List View (keep as-is)
└── NEW: Kanban Board View
    ├── Column: To Do
    ├── Column: In Progress
    ├── Column: Blocked
    └── Column: Done
```

### Implementation Approach

**Option A: Pure React (Recommended)**
- No external dependencies
- Lightweight and fast
- Full control over behavior
- ~300 lines of code

**Option B: Use react-beautiful-dnd**
- External library (adds 50KB)
- More polished animations
- Less code to write
- Requires npm install

**Recommendation:** Option A (Pure React) - keeps bundle small, no new dependencies

---

## Detailed Implementation Plan

### Phase 1: Data Model (30 min)

**Add Status Field to Actions:**
- Currently: `completed: boolean`
- Proposed: Add `status: 'todo' | 'in_progress' | 'blocked' | 'done'`
- Backward compatible: `completed = (status === 'done')`

**Migration Strategy:**
- Frontend derives status from existing data:
  - `completed === true` → `status = 'done'`
  - `completed === false` → `status = 'todo'`
- Backend update (optional): Add status field to DynamoDB schema
- No breaking changes

### Phase 2: Kanban Component (2 hours)

**File:** `frontend/src/components/KanbanBoard.jsx`

**Features:**
1. **Four Columns:**
   - To Do (default for incomplete items)
   - In Progress (user-moved items)
   - Blocked (items with issues)
   - Done (completed items)

2. **Drag-and-Drop:**
   - Drag action cards between columns
   - Visual feedback during drag
   - Drop zones highlight on hover
   - Smooth animations

3. **Action Cards:**
   - Task name
   - Owner avatar/name
   - Deadline with countdown
   - Risk score badge
   - Meeting source
   - Quick actions (edit, delete)

4. **Column Headers:**
   - Column name
   - Item count
   - Color-coded
   - Collapse/expand

**Component Structure:**
```jsx
<KanbanBoard>
  <Column status="todo">
    <ActionCard />
    <ActionCard />
  </Column>
  <Column status="in_progress">
    <ActionCard />
  </Column>
  <Column status="blocked">
    <ActionCard />
  </Column>
  <Column status="done">
    <ActionCard />
  </Column>
</KanbanBoard>
```

### Phase 3: Drag-and-Drop Logic (1.5 hours)

**Implementation:**
```javascript
// 1. Track drag state
const [draggedItem, setDraggedItem] = useState(null)
const [dragOverColumn, setDragOverColumn] = useState(null)

// 2. Drag handlers
onDragStart(item) {
  setDraggedItem(item)
}

onDragOver(column) {
  setDragOverColumn(column)
}

onDrop(targetColumn) {
  // Update item status
  updateActionStatus(draggedItem.id, targetColumn)
  // Clear drag state
  setDraggedItem(null)
  setDragOverColumn(null)
}
```

**API Update:**
- Use existing `updateAction` API
- Add status field to update payload
- Backend: Store status in DynamoDB

### Phase 4: View Toggle (30 min)

**Add Toggle Button:**
```jsx
<div style={s.viewToggle}>
  <button 
    onClick={() => setView('list')}
    style={view === 'list' ? s.activeBtn : s.inactiveBtn}>
    📋 List
  </button>
  <button 
    onClick={() => setView('kanban')}
    style={view === 'kanban' ? s.activeBtn : s.inactiveBtn}>
    📊 Kanban
  </button>
</div>
```

**Conditional Rendering:**
```jsx
{view === 'list' ? (
  <ListView actions={filteredActions} />
) : (
  <KanbanBoard actions={filteredActions} />
)}
```

### Phase 5: Styling (1 hour)

**Design System:**
- Column colors:
  - To Do: `#e8c06a` (yellow)
  - In Progress: `#6a9ae8` (blue)
  - Blocked: `#e87a6a` (red)
  - Done: `#c8f04a` (green)

- Card design:
  - Dark background: `#1a1a1a`
  - Border: `1px solid #333`
  - Hover: Lift effect with shadow
  - Drag: Opacity 0.5, rotate 2deg

- Animations:
  - Drag: 200ms ease
  - Drop: 300ms spring
  - Hover: 150ms ease

### Phase 6: Bulk Operations (1 hour)

**Features:**
1. **Multi-select:**
   - Checkbox on each card
   - Select all in column
   - Shift-click range select

2. **Bulk Actions:**
   - Move selected to column
   - Assign to owner
   - Set deadline
   - Mark complete
   - Delete

**UI:**
```jsx
{selectedItems.length > 0 && (
  <div style={s.bulkBar}>
    <span>{selectedItems.length} selected</span>
    <button onClick={bulkMoveTo}>Move to...</button>
    <button onClick={bulkAssign}>Assign to...</button>
    <button onClick={bulkComplete}>Mark Done</button>
    <button onClick={clearSelection}>Clear</button>
  </div>
)}
```

---

## Backend Changes

### Option 1: Minimal (Recommended)
- ✅ No backend changes needed
- Frontend derives status from `completed` field
- Use existing `updateAction` API
- Status stored client-side only

### Option 2: Full Implementation
- Add `status` field to DynamoDB schema
- Update `process-meeting` to set initial status
- Update `updateAction` to handle status changes
- Migration script for existing data

**Recommendation:** Start with Option 1, upgrade to Option 2 later if needed

---

## Files to Modify

### New Files:
1. `frontend/src/components/KanbanBoard.jsx` (NEW)
2. `docs/implementation/DAY3_KANBAN_BOARD.md` (NEW)

### Modified Files:
1. `frontend/src/pages/ActionsOverview.jsx`
   - Add view toggle
   - Import KanbanBoard
   - Conditional rendering

2. `frontend/src/utils/api.js` (optional)
   - Add `updateActionStatus()` helper
   - Or reuse existing `updateAction()`

3. `backend/functions/update-action/app.py` (optional)
   - Add status field support
   - Backward compatible

---

## Testing Plan

### Manual Testing:
1. ✅ View toggle switches between list and kanban
2. ✅ All action items appear in correct columns
3. ✅ Drag-and-drop works smoothly
4. ✅ Status updates persist after refresh
5. ✅ Filters work in kanban view
6. ✅ Team selector works in kanban view
7. ✅ Mobile responsive (columns stack vertically)

### Edge Cases:
- Empty columns (show placeholder)
- Single item in column
- Many items in column (scroll)
- Drag outside drop zone (cancel)
- Network error during update (rollback)

---

## User Experience

### Before (Current):
```
Actions Overview
├── Filters (status, owner)
├── Stats (total, done, pending)
└── List View
    └── Grouped by meeting
        └── Action items
```

### After (Proposed):
```
Actions Overview
├── View Toggle [List | Kanban]
├── Filters (status, owner)
├── Stats (total, done, pending)
├── List View (existing)
│   └── Grouped by meeting
└── Kanban View (NEW)
    ├── To Do Column
    ├── In Progress Column
    ├── Blocked Column
    └── Done Column
```

---

## Benefits

### For Users:
- ✅ Visual workflow management
- ✅ Drag-and-drop simplicity
- ✅ Clear status at a glance
- ✅ Better task prioritization
- ✅ Identify bottlenecks (blocked column)

### For Competition:
- ✅ Fills major feature gap in spec
- ✅ Modern, professional UI
- ✅ Demonstrates technical sophistication
- ✅ Differentiates from competitors
- ✅ Screenshot-worthy for article

---

## Risks & Mitigation

### Risk 1: Drag-and-Drop Complexity
- **Mitigation:** Use simple HTML5 drag API, not complex library
- **Fallback:** Click-to-move if drag fails

### Risk 2: Performance with Many Items
- **Mitigation:** Virtualize columns if >100 items
- **Fallback:** Pagination or "Load More"

### Risk 3: Mobile Experience
- **Mitigation:** Stack columns vertically on mobile
- **Fallback:** Hide kanban on mobile, show list only

### Risk 4: Status Field Migration
- **Mitigation:** Derive status from existing `completed` field
- **Fallback:** No backend changes needed

---

## Timeline

### Estimated Breakdown:
- Phase 1: Data Model (30 min)
- Phase 2: Kanban Component (2 hours)
- Phase 3: Drag-and-Drop (1.5 hours)
- Phase 4: View Toggle (30 min)
- Phase 5: Styling (1 hour)
- Phase 6: Bulk Operations (1 hour)
- Testing & Polish (30 min)

**Total: 6.5 hours**

### Minimum Viable Product (MVP):
- Skip Phase 6 (Bulk Operations)
- Basic styling only
- **MVP Time: 4.5 hours**

---

## Alternative: Simplified Kanban

If time is critical, we can build a **simplified version**:

### Simplified Features:
- ✅ 3 columns only (To Do, In Progress, Done)
- ✅ Click-to-move (no drag-and-drop)
- ✅ Basic styling
- ❌ No bulk operations
- ❌ No blocked column

**Simplified Time: 2-3 hours**

---

## Recommendation

**Approach:** Build **MVP Kanban** (4.5 hours)
- Full drag-and-drop
- 4 columns (To Do, In Progress, Blocked, Done)
- Good styling
- Skip bulk operations (can add later)

**Rationale:**
- Fills the major feature gap
- Impressive for competition
- Reasonable time investment
- Can enhance later if needed

---

## Next Steps

**If Approved:**
1. Create `KanbanBoard.jsx` component
2. Implement drag-and-drop logic
3. Add view toggle to ActionsOverview
4. Style and polish
5. Test thoroughly
6. Deploy frontend
7. Document in DAY3_KANBAN_BOARD.md

**If Changes Needed:**
- Adjust scope (MVP vs Full)
- Change approach (library vs pure React)
- Modify timeline
- Alter features

---

## Questions for Review

1. **Scope:** MVP (4.5 hrs) or Full (6.5 hrs) or Simplified (2-3 hrs)?
2. **Approach:** Pure React or use react-beautiful-dnd library?
3. **Backend:** Client-side status only or add to DynamoDB?
4. **Bulk Operations:** Include now or add later?
5. **Mobile:** Full responsive or desktop-only for MVP?

---

**Status:** ⏸️ AWAITING APPROVAL

Please review and let me know:
- ✅ Approve as-is (build MVP)
- 🔄 Request changes (specify)
- ❌ Defer to later (work on something else)
