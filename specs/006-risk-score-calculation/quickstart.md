# Quickstart: 006-risk-score-calculation

**Date**: 2026-02-08

## Overview

Update the risk assessment scoring engine and result page to use a new hierarchical calculation model:
- Group → classification label (Хэвийн through Аюултай)
- Type → probability score, consequence score, risk value, risk grade
- Overall → НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, ДААТГАХ ЭСЭХ

## Files to Modify

### Backend

| File | Change |
| ---- | ------ |
| `backend/src/services/scoring.py` | Replace scoring logic with new formulas (group classification, probability/consequence, grade lookup) |
| `backend/src/models/assessment_score.py` | Add new nullable columns (classification_label, probability_score, consequence_score, risk_value, risk_grade, risk_description, insurance_decision) |
| `backend/src/schemas/results.py` | Add new fields to GroupScore, TypeScore, OverallScore |
| `backend/src/schemas/public.py` | Add new fields to GroupResult, TypeResult, OverallResult |
| `backend/src/services/results.py` | Map new DB columns to response schema fields |
| `backend/src/services/submission.py` | No changes expected — calls scoring service which handles the logic |
| Alembic migration | New migration to add columns to assessment_scores table |

### Frontend

| File | Change |
| ---- | ------ |
| `frontend/src/types/api.ts` | Add new fields to GroupResult, TypeResult, OverallResult types |
| `frontend/src/components/OverallScoreCard.tsx` | Display НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, risk description, ДААТГАХ ЭСЭХ |
| `frontend/src/components/TypeScoreCard.tsx` | Display probability, consequence, risk value, grade per type |
| `frontend/src/pages/Results.tsx` | Update layout to accommodate new scoring display hierarchy |

### Tests

| File | Change |
| ---- | ------ |
| `backend/tests/` | Unit tests for new scoring functions (classification, probability, consequence, grade lookup, rounding) |
| `backend/tests/` | Integration tests for full scoring pipeline with known inputs |

## Key Implementation Notes

1. **STDEV.S**: Use `statistics.stdev()` with N≤1 guard returning 0
2. **Rounding**: Use `Decimal.quantize(ROUND_HALF_UP)` for spec-compliant rounding
3. **Backward compatibility**: New DB columns are nullable; old assessments return null for new fields
4. **No new endpoints**: Existing results API extended with additive fields
5. **Grade lookup**: Pure function, no DB storage needed — static business rule
6. **Color mapping**: AAA–A → green, BBB–B → yellow, CCC–C → orange, DDD–D → red
