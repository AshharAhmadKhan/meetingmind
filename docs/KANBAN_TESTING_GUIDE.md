# Kanban Board - Complete Testing Guide

**App URL:** https://dcfx593ywvy92.cloudfront.net  
**Test Date:** Feb 19, 2026  
**Feature:** Day 3 - Kanban Board with Drag & Drop

---

## Pre-Test Setup

### 1. Create Test Meeting (If Database is Empty)

**Steps:**
1. Go to https://dcfx593ywvy92.cloudfront.net
2. Log in with your credentials
3. Click "Upload Meeting" button
4. Fill in meeting details:
   - **Title:** "Q1 Planning Meeting"
   - **Audio File:** Any audio file (or use mock if Transcribe not ready)
5. Wait for processing to complete (~2-3 minutes)
6. Verify meeting appears on Dashboard

**Expected Result:**
- Meeting shows up with status "DONE"
- Action items are extracted
- Each action has: task, owner, deadline, risk score

---

## Test Suite 1: Basic Kanban Functionality

### Test 1.1: Access Kanban Board

**Steps:**
1. From Dashboard, click "View All Actions" or navigate to `/actions`
2. Look for the view toggle buttons at the top

**Expected Result:**
- ✅ Page loads without errors
- ✅ Two buttons visible: "📋 List" and "📊 Kanban"
- ✅ List view is active by default (yellow button)
- ✅ Action items are displayed grouped by meeting

**Screenshot Opportunity:** Full page with both view buttons

---

### Test 1.2: Switch to Kanban View

**Steps:**
1. Click the "📊 Kanban" button

**Expected Result:**
- ✅ Button turns yellow (active state)
- ✅ List view disappears
- ✅ Four columns appear:
  - To Do (yellow border)
  - In Progress (blue border)
  - Blocked (red border)
  - Done (green border)
- ✅ Each column shows item count
- ✅ Action items appear in appropriate columns

**Screenshot Opportunity:** Full Kanban board with all 4 columns

---

### Test 1.3: Verify Initial Column Distribution

**Steps:**
1. Check which column each action item is in

**Expected Result:**
- ✅ Incomplete items (completed=false) → "To Do" column
- ✅ Completed items (completed=true) → "Done" column
- ✅ All columns are visible even if empty
- ✅ Empty columns show "No items" placeholder

---

## Test Suite 2: Drag & Drop Functionality

### Test 2.1: Drag from To Do to In Progress

**Steps:**
1. Find an action card in "To Do" column
2. Click and hold on the card
3. Drag it to "In Progress" column
4. Release mouse button

**Expected Result:**
- ✅ Card follows cursor while dragging
- ✅ Card opacity changes to 0.5 during drag
- ✅ Card appears in "In Progress" column after drop
- ✅ "To Do" count decreases by 1
- ✅ "In Progress" count increases by 1
- ✅ No console errors

**Screenshot Opportunity:** Mid-drag with card being moved

---

### Test 2.2: Verify Persistence After Refresh

**Steps:**
1. After moving a card (Test 2.1), refresh the page (F5)
2. Switch back to Kanban view

**Expected Result:**
- ✅ Card is still in "In Progress" column
- ✅ Status persisted in backend
- ✅ No data loss

---

### Test 2.3: Drag to Blocked Column

**Steps:**
1. Drag a card from any column to "Blocked"
2. Observe the change

**Expected Result:**
- ✅ Card moves to Blocked column
- ✅ Red border indicates blocked status
- ✅ Status updates in backend

---

### Test 2.4: Drag to Done Column

**Steps:**
1. Drag a card from any column to "Done"
2. Check the card's appearance

**Expected Result:**
- ✅ Card moves to Done column
- ✅ Green border indicates completion
- ✅ Card opacity may change (completed state)

---

### Test 2.5: Drag Within Same Column (Reordering)

**Steps:**
1. In a column with multiple cards, drag one card above/below another
2. Release

**Expected Result:**
- ✅ Card reorders within the column
- ✅ No status change
- ✅ Smooth animation

---

## Test Suite 3: Risk Score Visualization

### Test 3.1: Verify Risk Gradient

**Steps:**
1. Look at action cards in any column
2. Observe the background gradient and left border

**Expected Result:**
- ✅ Cards with high risk (75-100) have red gradient and border
- ✅ Cards with medium risk (50-74) have orange gradient and border
- ✅ Cards with low risk (25-49) have yellow gradient and border
- ✅ Cards with minimal risk (0-24) have green gradient and border
- ✅ Gradient fills from left based on risk percentage

**Screenshot Opportunity:** Close-up of cards with different risk levels

---

### Test 3.2: Risk Badge Display

**Steps:**
1. Check each action card for risk badge

**Expected Result:**
- ✅ Badge shows "Risk: X/100" format
- ✅ Badge color matches risk level
- ✅ Badge is readable and prominent

---

## Test Suite 4: Card Information Display

### Test 4.1: Verify Card Content

**Steps:**
1. Examine an action card in detail

**Expected Result:**
- ✅ Task description is visible and readable
- ✅ Owner name is shown (or "Unassigned")
- ✅ Deadline is displayed with countdown
  - "Xd left" for future deadlines
  - "Due today" for today
  - "Xd overdue" for past deadlines
- ✅ Risk score badge is present
- ✅ Meeting title is shown at bottom (italicized, gray)

---

### Test 4.2: Deadline Formatting

**Steps:**
1. Find cards with different deadline scenarios

**Expected Result:**
- ✅ Future deadline: "5d left" (green/yellow)
- ✅ Today: "Due today" (yellow)
- ✅ Overdue: "3d overdue" (red)
- ✅ No deadline: Shows "No deadline"

---

## Test Suite 5: Filters in Kanban View

### Test 5.1: Status Filter

**Steps:**
1. In Kanban view, change "STATUS" dropdown to "Incomplete"
2. Observe columns

**Expected Result:**
- ✅ Only incomplete items show in To Do, In Progress, Blocked
- ✅ Done column is empty
- ✅ Item counts update correctly

---

### Test 5.2: Owner Filter

**Steps:**
1. Select a specific owner from "OWNER" dropdown
2. Observe columns

**Expected Result:**
- ✅ Only items assigned to that owner are visible
- ✅ All columns update accordingly
- ✅ Item counts reflect filtered results

---

### Test 5.3: Combined Filters

**Steps:**
1. Set STATUS to "Incomplete"
2. Set OWNER to a specific person
3. Observe results

**Expected Result:**
- ✅ Only incomplete items for that owner show
- ✅ Filters work together correctly
- ✅ No errors

---

## Test Suite 6: View Toggle Behavior

### Test 6.1: Switch Between Views

**Steps:**
1. Start in Kanban view
2. Click "📋 List" button
3. Click "📊 Kanban" button again

**Expected Result:**
- ✅ Smooth transition between views
- ✅ No data loss
- ✅ Filters persist across views
- ✅ Active button highlights correctly

---

### Test 6.2: Filters Persist Across Views

**Steps:**
1. In List view, set a filter (e.g., Owner = "Ashhar")
2. Switch to Kanban view
3. Verify filter is still applied

**Expected Result:**
- ✅ Same filtered results in both views
- ✅ Filter dropdown shows correct selection
- ✅ Item count matches

---

## Test Suite 7: Team Selector Integration

### Test 7.1: Team Selector in Kanban

**Steps:**
1. If you have multiple teams, use Team Selector dropdown
2. Switch to Kanban view
3. Change team

**Expected Result:**
- ✅ Kanban board updates with new team's actions
- ✅ Columns repopulate correctly
- ✅ No errors

---

## Test Suite 8: Duplicate Detection in Kanban

### Test 8.1: Check Duplicates Button

**Steps:**
1. In Kanban view, click "🔍 Check Duplicates" button
2. Wait for scan to complete

**Expected Result:**
- ✅ Button shows "🔍 Scanning..." during scan
- ✅ Duplicate results panel appears
- ✅ Kanban board remains visible below
- ✅ No layout issues

---

## Test Suite 9: Mobile Responsiveness

### Test 9.1: Mobile View (if possible)

**Steps:**
1. Open app on mobile device or use browser DevTools (F12 → Toggle Device Toolbar)
2. Navigate to Actions Overview
3. Switch to Kanban view

**Expected Result:**
- ✅ Columns stack vertically on mobile
- ✅ Drag-and-drop still works (touch events)
- ✅ Cards are readable
- ✅ View toggle buttons are accessible

---

## Test Suite 10: Error Handling

### Test 10.1: Network Error Simulation

**Steps:**
1. Open DevTools (F12) → Network tab
2. Set throttling to "Offline"
3. Try to drag a card
4. Turn network back online

**Expected Result:**
- ✅ Error message appears
- ✅ Card reverts to original position (rollback)
- ✅ No data corruption
- ✅ User is informed of the issue

---

## Test Suite 11: Integration with Other Features

### Test 11.1: Navigate to Meeting Detail

**Steps:**
1. In List view, click "View Meeting →" button
2. Check meeting detail page
3. Go back to Actions Overview
4. Switch to Kanban view

**Expected Result:**
- ✅ Navigation works correctly
- ✅ Meeting detail shows all info
- ✅ Back navigation preserves view state

---

### Test 11.2: Dashboard Integration

**Steps:**
1. From Dashboard, check stats (Total, Done, Pending)
2. Navigate to Actions Overview → Kanban
3. Move a card from To Do to Done
4. Go back to Dashboard

**Expected Result:**
- ✅ Stats update correctly
- ✅ "Done" count increases
- ✅ "Pending" count decreases

---

## Test Suite 12: Performance

### Test 12.1: Large Dataset (if available)

**Steps:**
1. If you have 20+ action items, switch to Kanban view
2. Drag multiple cards
3. Observe performance

**Expected Result:**
- ✅ Smooth 60fps drag animation
- ✅ No lag or stuttering
- ✅ Columns scroll if needed
- ✅ No memory leaks

---

## Test Suite 13: Keyboard Accessibility

### Test 13.1: Keyboard Navigation

**Steps:**
1. In Kanban view, press Tab key repeatedly
2. Try to navigate through cards

**Expected Result:**
- ✅ Cards are focusable with Tab
- ✅ Visual focus indicator appears
- ✅ Can activate drag with keyboard (Space/Enter)
- ✅ Arrow keys move card between columns

---

## Test Suite 14: Edge Cases

### Test 14.1: Empty Columns

**Steps:**
1. Move all cards out of a column
2. Observe empty column

**Expected Result:**
- ✅ Column shows "No items" placeholder
- ✅ Column remains visible
- ✅ Can still drop cards into it

---

### Test 14.2: Single Item

**Steps:**
1. Filter to show only 1 action item
2. Try to drag it

**Expected Result:**
- ✅ Drag works normally
- ✅ No errors
- ✅ Counts update correctly

---

### Test 14.3: No Action Items

**Steps:**
1. Filter to show no results (e.g., Owner that doesn't exist)
2. Switch to Kanban view

**Expected Result:**
- ✅ All columns show "No items"
- ✅ No errors
- ✅ Helpful message displayed

---

## Test Suite 15: Console & Network Checks

### Test 15.1: Console Errors

**Steps:**
1. Open DevTools (F12) → Console tab
2. Perform all drag-and-drop operations
3. Check for errors

**Expected Result:**
- ✅ No red errors in console
- ✅ Only expected API calls logged
- ✅ No warnings about React keys or state

---

### Test 15.2: API Calls

**Steps:**
1. Open DevTools → Network tab
2. Drag a card to new column
3. Observe network requests

**Expected Result:**
- ✅ PUT request to `/meetings/{id}/actions/{id}`
- ✅ Request body includes `status` field
- ✅ Response is 200 OK
- ✅ Response includes updated action

---

## Quick Smoke Test (5 Minutes)

If you're short on time, run this quick test:

1. ✅ Log in to app
2. ✅ Navigate to Actions Overview
3. ✅ Click "📊 Kanban" button
4. ✅ Verify 4 columns appear
5. ✅ Drag one card from To Do to In Progress
6. ✅ Refresh page
7. ✅ Verify card stayed in In Progress
8. ✅ Check console for errors (should be none)

---

## Screenshot Checklist for Article

Capture these for the competition article:

1. ✅ Full Kanban board with all 4 columns populated
2. ✅ Close-up of action card showing risk gradient
3. ✅ Mid-drag animation (card being moved)
4. ✅ View toggle buttons (List/Kanban)
5. ✅ Mobile responsive view (columns stacked)
6. ✅ Risk score badges in different colors
7. ✅ Empty column with placeholder
8. ✅ Filters working in Kanban view

---

## Known Issues / Limitations

- ⚠️ Bedrock Claude still propagating (doesn't affect Kanban)
- ⚠️ Bulk operations not yet implemented (future enhancement)
- ⚠️ Column reordering not available (future enhancement)
- ⚠️ WIP limits not implemented (future enhancement)

---

## Troubleshooting

### Issue: Cards don't move when dragged
**Solution:** Check console for errors, verify API is accessible, check network tab

### Issue: Status doesn't persist after refresh
**Solution:** Check backend deployment, verify DynamoDB table has status field

### Issue: Kanban view is blank
**Solution:** Check if there are any action items, try clearing filters

### Issue: Drag is janky/laggy
**Solution:** Check browser performance, close other tabs, try different browser

---

## Success Criteria

All tests should pass with:
- ✅ No console errors
- ✅ Smooth drag-and-drop (60fps)
- ✅ Status persists after refresh
- ✅ All 4 columns functional
- ✅ Risk gradients display correctly
- ✅ Filters work in Kanban view
- ✅ Mobile responsive
- ✅ Keyboard accessible

---

**Test Status:** Ready for manual testing  
**Automated Tests:** 36/38 passing (95%)  
**Next:** Manual verification of UI/UX

