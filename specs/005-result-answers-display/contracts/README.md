# API Contracts: Result Page User Answers Display

**Feature**: 005-result-answers-display
**Date**: 2026-02-08

## Overview

This feature extends the existing public results endpoint to include answer breakdown data.

## Modified Endpoint

### GET /a/{token}/results

**Change**: Add optional `breakdown` query parameter.

#### Request

```
GET /a/{token}/results?breakdown=true
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `token` | string | Yes | - | Assessment access token |
| `breakdown` | boolean | No | false | Include individual answer breakdown |

#### Response (200 OK)

When `breakdown=true`:

```json
{
  "assessment_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "type_results": [
    {
      "type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "type_name": "Ажлын орчин",
      "raw_score": 45,
      "max_score": 50,
      "percentage": 90.0,
      "risk_rating": "LOW",
      "groups": [
        {
          "group_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "group_name": "Галын аюулгүй байдал",
          "raw_score": 20,
          "max_score": 20,
          "percentage": 100.0,
          "risk_rating": "LOW"
        }
      ]
    }
  ],
  "overall_result": {
    "raw_score": 85,
    "max_score": 100,
    "percentage": 85.0,
    "risk_rating": "LOW"
  },
  "answer_breakdown": [
    {
      "question_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "question_text": "Ажлын байранд галын аюулгүй байдлын дүрэм баримталдаг уу?",
      "type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "type_name": "Ажлын орчин",
      "selected_option": "YES",
      "comment": "Сард нэг удаа сургалт зохион байгуулдаг",
      "score_awarded": 2,
      "max_score": 2,
      "attachment_count": 1
    },
    {
      "question_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
      "question_text": "Гал унтраагч хэрэгсэл бүрэн хүчинтэй байдаг уу?",
      "type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "type_name": "Ажлын орчин",
      "selected_option": "NO",
      "comment": null,
      "score_awarded": 0,
      "max_score": 2,
      "attachment_count": 0
    }
  ]
}
```

When `breakdown=false` or omitted, the response is the same but without the `answer_breakdown` field.

#### Error Responses

| Status | Error | Description |
|--------|-------|-------------|
| 404 | not_found | Assessment not found |
| 400 | not_completed | Assessment not yet completed |

## Frontend Service Change

### assessment.ts

```typescript
export async function getAssessmentResults(
  token: string,
  includeBreakdown: boolean = true  // Default to true for this feature
): Promise<AssessmentResult<SubmitResponse>> {
  try {
    const params = includeBreakdown ? '?breakdown=true' : '';
    const response = await apiClient.get<SubmitResponse>(`/a/${token}/results${params}`);
    return { success: true, data: response.data };
  } catch (error: unknown) {
    // existing error handling
  }
}
```

## Type Definitions

### AnswerBreakdown

```typescript
export interface AnswerBreakdown {
  question_id: string;
  question_text: string;
  type_id: string;
  type_name: string;
  selected_option: OptionType;
  comment: string | null;
  score_awarded: number;
  max_score: number;
  attachment_count: number;
}
```

### Extended SubmitResponse

```typescript
export interface SubmitResponse {
  assessment_id: string;
  type_results: TypeResult[];
  overall_result: OverallResult;
  answer_breakdown?: AnswerBreakdown[];  // Optional, present when breakdown=true
}
```

## Backend Implementation Note

The backend change is minimal - modify line 325 in `backend/src/api/public/assessment.py`:

```python
# Before:
results = await results_service.get_results(assessment.id, include_breakdown=False)

# After:
from fastapi import Query

@router.get("/{token}/results", ...)
async def get_public_results(
    ...
    breakdown: bool = Query(False, description="Include individual answer breakdown"),
) -> SubmitResponse | JSONResponse:
    ...
    results = await results_service.get_results(assessment.id, include_breakdown=breakdown)
```

And add `answer_breakdown` to the response mapping when present.
