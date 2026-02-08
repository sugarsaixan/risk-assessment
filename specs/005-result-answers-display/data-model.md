# Data Model: Result Page User Answers Display

**Feature**: 005-result-answers-display
**Date**: 2026-02-08

## Overview

No new database tables required. This feature uses existing `answer_breakdown` data from the `ResultsService`.

## TypeScript Types (Frontend)

### New: AnswerBreakdown Interface

**File**: `frontend/src/types/api.ts`

```typescript
export interface AnswerBreakdown {
  question_id: string;
  question_text: string;
  type_id: string;
  type_name: string;
  selected_option: OptionType;  // "YES" | "NO"
  comment: string | null;
  score_awarded: number;
  max_score: number;
  attachment_count: number;
}
```

### Modified: SubmitResponse Interface

**File**: `frontend/src/types/api.ts`

```typescript
export interface SubmitResponse {
  assessment_id: string;
  type_results: TypeResult[];
  overall_result: OverallResult;
  answer_breakdown?: AnswerBreakdown[];  // NEW: optional, included when requested
}
```

## Component Props

### AnswersSection Props

```typescript
interface AnswersSectionProps {
  answers: AnswerBreakdown[];
  className?: string;
}
```

### AnswerRow Props (internal)

```typescript
interface AnswerRowProps {
  answer: AnswerBreakdown;
}
```

## Data Grouping Structure

Answers are grouped by `type_name` for display:

```typescript
type GroupedAnswers = Record<string, AnswerBreakdown[]>;

// Example structure after grouping:
{
  "Ажлын орчин": [
    { question_text: "...", selected_option: "YES", ... },
    { question_text: "...", selected_option: "NO", ... }
  ],
  "Хөдөлмөрийн аюулгүй байдал": [
    { question_text: "...", selected_option: "YES", ... }
  ]
}
```

## State Management

### Results.tsx State

```typescript
// Existing state (unchanged)
const [results, setResults] = useState<SubmitResponse | undefined>(stateResults);
const [isLoading, setIsLoading] = useState(!stateResults);
const [error, setError] = useState<string | null>(null);

// answer_breakdown is now part of results.answer_breakdown
```

### AnswersSection State

```typescript
// Collapse state - starts collapsed per FR-004
const [isExpanded, setIsExpanded] = useState(false);
```

## API Response Format

### GET /a/{token}/results?breakdown=true

```json
{
  "assessment_id": "uuid",
  "type_results": [...],
  "overall_result": {...},
  "answer_breakdown": [
    {
      "question_id": "uuid",
      "question_text": "Ажлын байранд галын аюулгүй байдлын дүрэм баримталдаг уу?",
      "type_id": "uuid",
      "type_name": "Ажлын орчин",
      "selected_option": "YES",
      "comment": "Сард нэг удаа сургалт зохион байгуулдаг",
      "score_awarded": 2,
      "max_score": 2,
      "attachment_count": 1
    }
  ]
}
```

## Display Mapping

| Field | Display |
|-------|---------|
| `question_text` | Question text (primary) |
| `selected_option` | "Тийм" (green) or "Үгүй" (red) |
| `comment` | Displayed below answer if present |
| `attachment_count` | Badge showing count, e.g., "📎 2" |
| `type_name` | Group header |
| `score_awarded/max_score` | Optional: show as "2/2" |
