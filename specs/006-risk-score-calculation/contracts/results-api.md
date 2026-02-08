# API Contract: Results API Changes

**Date**: 2026-02-08
**Affects**: `GET /a/{token}/results`, `POST /a/{token}/submit` response

## Schema Changes

### GroupResult (extended)

```json
{
  "group_id": "uuid",
  "group_name": "string",
  "raw_score": 0,
  "max_score": 0,
  "percentage": 0.0,
  "risk_rating": "LOW|MEDIUM|HIGH",
  "sum_score": 0,
  "classification_label": "Хэвийн|Хянахуйц|Анхаарах|Ноцтой|Аюултай"
}
```

New fields: `sum_score` (integer), `classification_label` (string)

### TypeResult (extended)

```json
{
  "type_id": "uuid",
  "type_name": "string",
  "raw_score": 0,
  "max_score": 0,
  "percentage": 0.0,
  "risk_rating": "LOW|MEDIUM|HIGH",
  "groups": ["GroupResult[]"],
  "probability_score": 0.0,
  "consequence_score": 0.0,
  "risk_value": 0,
  "risk_grade": "AAA|AA|A|BBB|BB|B|CCC|CC|C|DDD|DD|D",
  "risk_description": "string"
}
```

New fields: `probability_score` (decimal), `consequence_score` (decimal), `risk_value` (integer), `risk_grade` (string), `risk_description` (string)

### OverallResult (extended)

```json
{
  "raw_score": 0,
  "max_score": 0,
  "percentage": 0.0,
  "risk_rating": "LOW|MEDIUM|HIGH",
  "total_risk": 0,
  "total_grade": "AAA|AA|A|BBB|BB|B|CCC|CC|C|DDD|DD|D",
  "risk_description": "string",
  "insurance_decision": "Даатгана|Даатгахгүй"
}
```

New fields: `total_risk` (integer, НИЙТ ЭРСДЭЛ), `total_grade` (string, НИЙТ ЗЭРЭГЛЭЛ), `risk_description` (string), `insurance_decision` (string, ДААТГАХ ЭСЭХ)

## Backward Compatibility

- All new fields are **additive** — existing fields remain unchanged
- For **existing assessments** (completed before this feature), new fields will be `null` in the API response
- Frontend must handle `null` values gracefully (show old-style display when new fields are absent)
- No breaking changes to the API contract

## Endpoints Affected

1. **`GET /a/{token}/results?breakdown=true`** — response extended with new fields
2. **`POST /a/{token}/submit`** — response extended with new fields (same SubmitResponse schema)

No new endpoints required.
