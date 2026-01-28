# Quickstart: Odoo ERP Respondent Integration

**Feature Branch**: `003-odoo-respondent-sync`
**Date**: 2026-01-28

## Prerequisites

- PostgreSQL database (existing from 001)
- Python 3.11+ with backend dependencies installed
- Existing 001/002 features deployed (respondents, assessments, drafts all functional)

## Setup

```bash
# Checkout feature branch
git checkout 003-odoo-respondent-sync

# Install dependencies (no new packages required)
cd backend
pip install -r requirements.txt

# Run migration to add odoo_id + employee columns
alembic upgrade head
```

## What Changes

### Modified Endpoint

**Create Assessment** (`POST /admin/assessments`)

Before (001):
```json
{
  "respondent_id": "uuid-of-existing-respondent",
  "selected_type_ids": ["type-uuid-1"],
  "expires_in_days": 30
}
```

After (003):
```json
{
  "respondent": {
    "odoo_id": "res.partner_42",
    "name": "Монгол Компани ХХК",
    "kind": "ORG",
    "registration_no": "1234567"
  },
  "employee_id": "hr.employee_15",
  "employee_name": "Батболд Д.",
  "selected_type_ids": ["type-uuid-1"],
  "expires_in_days": 30
}
```

Response now includes `respondent_id`:
```json
{
  "id": "assessment-uuid",
  "respondent_id": "resolved-respondent-uuid",
  "url": "https://app.example.com/a/token123",
  "expires_at": "2026-02-27T00:00:00Z"
}
```

### New Query Parameters

**List Assessments** (`GET /admin/assessments`)

Filter by Odoo respondent ID:
```
GET /admin/assessments?odoo_id=res.partner_42
```

Filter by employee who created the assessment:
```
GET /admin/assessments?employee_id=hr.employee_15
```

Combine filters:
```
GET /admin/assessments?odoo_id=res.partner_42&employee_id=hr.employee_15&status=COMPLETED
```

### Assessment Responses Now Include Employee Data

```json
{
  "id": "assessment-uuid",
  "respondent_id": "respondent-uuid",
  "respondent_odoo_id": "res.partner_42",
  "employee_id": "hr.employee_15",
  "employee_name": "Батболд Д.",
  "selected_type_ids": ["type-uuid"],
  "expires_at": "2026-02-27T00:00:00Z",
  "status": "PENDING",
  "completed_at": null,
  "created_at": "2026-01-28T00:00:00Z"
}
```

### Removed Endpoints

| Endpoint | Method | Status |
|----------|--------|--------|
| `/admin/respondents` | POST | Removed |
| `/admin/respondents` | GET | Removed |
| `/admin/respondents/{id}` | GET | Removed |
| `/admin/respondents/{id}` | PATCH | Removed |

## Testing the Integration

```bash
# 1. Create assessment with new respondent + employee data
curl -X POST http://localhost:8000/admin/assessments \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "respondent": {
      "odoo_id": "res.partner_42",
      "name": "Test Company",
      "kind": "ORG",
      "registration_no": "REG001"
    },
    "employee_id": "hr.employee_15",
    "employee_name": "Батболд Д.",
    "selected_type_ids": ["type-uuid"],
    "expires_in_days": 30
  }'

# 2. Create assessment WITHOUT employee data (optional)
curl -X POST http://localhost:8000/admin/assessments \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "respondent": {
      "odoo_id": "res.partner_42",
      "name": "Test Company Updated Name",
      "kind": "ORG",
      "registration_no": "REG001"
    },
    "selected_type_ids": ["type-uuid"],
    "expires_in_days": 30
  }'

# 3. Query assessments by Odoo respondent ID
curl http://localhost:8000/admin/assessments?odoo_id=res.partner_42 \
  -H "X-API-Key: your-api-key"

# 4. Query assessments by employee ID
curl http://localhost:8000/admin/assessments?employee_id=hr.employee_15 \
  -H "X-API-Key: your-api-key"

# 5. Combined filter: employee + status
curl "http://localhost:8000/admin/assessments?employee_id=hr.employee_15&status=COMPLETED" \
  -H "X-API-Key: your-api-key"
```

## Files Modified

| File | Change |
|------|--------|
| `backend/src/models/respondent.py` | Add `odoo_id` column |
| `backend/src/models/assessment.py` | Add `employee_id`, `employee_name` columns |
| `backend/src/schemas/respondent.py` | Add `RespondentInline` schema; remove `RespondentCreate`, `RespondentUpdate` |
| `backend/src/schemas/assessment.py` | Replace `respondent_id` with inline `respondent` + optional employee fields in `AssessmentCreate`; add employee fields to response schemas |
| `backend/src/repositories/respondent.py` | Add `get_by_odoo_id`, `upsert_from_odoo`, `find_by_kind_and_registration` methods |
| `backend/src/services/assessment.py` | Modify `create_assessment` to handle inline respondent upsert + employee storage |
| `backend/src/api/admin/assessments.py` | Update endpoint to use new schema; add `odoo_id` + `employee_id` query params |
| `backend/src/api/admin/respondents.py` | Remove file (all endpoints deprecated) |
| `backend/src/api/admin/__init__.py` | Remove respondent router import |
| `backend/src/main.py` | Remove respondent tag from OpenAPI |
| `backend/migrations/versions/` | New migration for `odoo_id`, `employee_id`, `employee_name` columns |
| `backend/tests/` | Update tests for new contract |
