# Quickstart: Result Page User Answers Display

**Feature**: 005-result-answers-display
**Date**: 2026-02-08

## Prerequisites

- Backend running: `cd backend && uvicorn src.main:app --reload`
- Frontend running: `cd frontend && npm run dev`
- A completed assessment with answers (token available)

## Manual Testing Checklist

### Test 1: Answers Section Visibility (FR-001)

1. Navigate to `/a/{token}/results` for a completed assessment
2. Verify the "Хариултууд" (Answers) section appears below the score content
3. Section should show a header with count, e.g., "Хариултууд (25)"

**Expected**: Section visible below TypeScoreCards and Summary

### Test 2: Collapsed Default State (FR-004)

1. Navigate to results page (fresh load)
2. Observe the Answers section state

**Expected**: Section is collapsed, only header visible with expand indicator

### Test 3: Expand/Collapse Toggle (FR-003, SC-002)

1. Click the Answers section header or toggle button
2. Observe the section expanding
3. Click again to collapse

**Expected**:
- Toggle responds instantly (< 1 second)
- No page reload
- Chevron icon rotates on expand/collapse

### Test 4: Answer Display Content (FR-002)

1. Expand the Answers section
2. Verify each answer shows:
   - Question text
   - Selected option (Тийм/Үгүй) with color indicator
   - Comment (if submitted)
   - Attachment count indicator (if any)

**Expected**: All submitted answers visible with complete information

### Test 5: Grouped by Type (FR-007)

1. Expand the Answers section
2. Observe the grouping structure

**Expected**: Answers grouped by questionnaire type name (matching TypeScoreCards)

### Test 6: Attachment Indicator (FR-005)

1. Find an answer that had attachments submitted
2. Verify indicator shows attachment count

**Expected**: Badge like "📎 2" or similar indicator

### Test 7: Empty Comment Handling (Edge Case)

1. Find an answer without a comment
2. Verify no empty comment area is shown

**Expected**: Clean layout without empty comment space

### Test 8: Large Dataset (SC-005, Edge Case)

1. Navigate to a results page with 50+ questions
2. Measure page load time
3. Expand the Answers section

**Expected**:
- Page loads within 2 seconds
- Answers section renders smoothly
- Scrolling is smooth within expanded section

### Test 9: Existing Content Preserved (FR-006)

1. Navigate to results page
2. Verify all existing content still works:
   - OverallScoreCard displays correctly
   - TypeScoreCards with group breakdown work
   - Summary section displays scores
   - Theme toggle works

**Expected**: No regression in existing functionality

### Test 10: Toggle State Indicator (FR-008)

1. Observe the expand/collapse control
2. Verify visual indicator shows current state

**Expected**: Clear icon (chevron pointing down when collapsed, up when expanded) or text indicator

## API Verification

### Test Backend Endpoint

```bash
# Without breakdown (default)
curl http://localhost:8000/a/{token}/results

# With breakdown
curl "http://localhost:8000/a/{token}/results?breakdown=true"
```

**Expected**: Second request includes `answer_breakdown` array in response

## Browser Verification

Test in multiple browsers:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari (if available)

Verify:
- UTF-8 Mongolian text renders correctly
- Animations work smoothly
- No layout issues

## Completion Criteria

All tests pass:
- [ ] Test 1: Section visible
- [ ] Test 2: Starts collapsed
- [ ] Test 3: Toggle works
- [ ] Test 4: Answer content complete
- [ ] Test 5: Grouped by type
- [ ] Test 6: Attachment indicator
- [ ] Test 7: Empty comment handling
- [ ] Test 8: Performance OK
- [ ] Test 9: No regressions
- [ ] Test 10: State indicator clear
