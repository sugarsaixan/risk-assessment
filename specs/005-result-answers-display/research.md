# Research: Result Page User Answers Display

**Feature**: 005-result-answers-display
**Date**: 2026-02-08

## Executive Summary

This feature requires minimal research as the backend infrastructure already exists. The `answer_breakdown` data structure is fully implemented in the backend's `ResultsService`, and the frontend already has a collapsible UI pattern in `TypeScoreCard.tsx` that can be adapted.

## Existing Infrastructure

### Backend: answer_breakdown Schema

**Location**: `backend/src/schemas/results.py` (lines 46-57)

```python
class AnswerBreakdown(BaseModel):
    """Schema for individual answer in breakdown."""

    question_id: UUID
    question_text: str
    type_id: UUID
    type_name: str
    selected_option: OptionType  # YES or NO
    comment: str | None
    score_awarded: int
    max_score: int
    attachment_count: int
```

### Backend: ResultsService

**Location**: `backend/src/services/results.py`

The `get_results()` method already supports `include_breakdown=True` parameter:
- Line 128: `answer_breakdown: list[AnswerBreakdown] | None = None`
- Line 130: Calls `_get_answer_breakdown()` when breakdown requested
- Line 155: Returns breakdown in `AssessmentResultsResponse`

### Current Public Results Endpoint

**Location**: `backend/src/api/public/assessment.py` (line 325)

```python
results = await results_service.get_results(assessment.id, include_breakdown=False)
```

Currently hardcoded to `False`. Needs to be parameterized.

### Frontend: Collapsible Pattern

**Location**: `frontend/src/components/TypeScoreCard.tsx`

The component uses:
- `useState(false)` for collapse state
- Rotating chevron icon with `transition-transform`
- Conditional rendering: `{showGroups && (<content>)}`
- Toggle button with Mongolian text: "Бүлгүүдийг харах" / "Бүлгүүдийг нуух"

### Frontend: MN Constants Structure

**Location**: `frontend/src/constants/mn.ts`

Organized by feature area. Results section exists at lines 47-58. Need to add:
- `answers.title`: "Хариултууд"
- `answers.show`: "Хариултуудыг харах"
- `answers.hide`: "Хариултуудыг нуух"
- `answers.attachments`: "Хавсралт"

## Data Flow

```
1. User visits /a/:token/results
2. Results.tsx calls getAssessmentResults(token, breakdown=true)
3. Frontend service adds ?breakdown=true to API call
4. Backend public endpoint passes include_breakdown=True to ResultsService
5. Backend returns SubmitResponse with answer_breakdown array
6. Results.tsx passes answers to AnswersSection component
7. AnswersSection groups answers by type_id and renders collapsibly
```

## Grouping Strategy

Answers should be grouped by `type_name` (from answer_breakdown) to match the existing TypeScoreCard organization:

```typescript
// Group answers by type
const answersByType = answers.reduce((acc, answer) => {
  if (!acc[answer.type_name]) {
    acc[answer.type_name] = [];
  }
  acc[answer.type_name].push(answer);
  return acc;
}, {} as Record<string, AnswerBreakdown[]>);
```

## UI/UX Patterns to Follow

1. **Collapse State**: Start collapsed (per FR-004)
2. **Toggle Button**: Use chevron icon with rotation animation
3. **Section Header**: "Хариултууд" with count indicator
4. **Answer Display**:
   - Question text (bold)
   - Selected option: "Тийм" / "Үгүй" with color indicator
   - Comment (if present, in lighter text)
   - Attachment count badge (if > 0)

## No New Dependencies

All functionality can be achieved with existing:
- React hooks (useState)
- TailwindCSS classes
- Existing component patterns

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance with 50+ answers | Low | Medium | Answers are lightweight text; no images loaded |
| Long comments overflow | Low | Low | Use text truncation with expand option |
| Missing answer data | Very Low | Low | Backend always provides complete breakdown |

## Conclusion

This is a straightforward frontend feature with one minor backend modification. The infrastructure is already in place; we just need to:
1. Expose the existing breakdown parameter in the public endpoint
2. Create a new collapsible component following established patterns
3. Integrate into Results.tsx
