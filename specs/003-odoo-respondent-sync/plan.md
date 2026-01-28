# Implementation Plan: Odoo ERP Respondent Integration

**Branch**: `003-odoo-respondent-sync` | **Date**: 2026-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-odoo-respondent-sync/spec.md`

## Summary

Replace standalone respondent CRUD with Odoo ERP as the source of truth for respondent data. The assessment creation endpoint is modified to accept inline respondent data (odoo_id, name, kind, registration_no) and perform an atomic upsert. Optional Odoo employee data (employee_id, employee_name) is stored on each assessment for audit trail. Standalone respondent endpoints are removed. New query parameters allow filtering assessments by Odoo respondent ID and employee ID.

## Technical Context

**Language/Version**: Python 3.11+ (backend only — no frontend changes)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic 2.x, asyncpg
**Storage**: PostgreSQL (existing, via asyncpg)
**Testing**: pytest with pytest-asyncio, httpx test client
**Target Platform**: Linux server (Docker)
**Project Type**: Web application (backend-only changes for this feature)
**Performance Goals**: Assessment creation with respondent upsert completes within 2 seconds (SC-001)
**Constraints**: Atomic respondent upsert to prevent duplicates under concurrent requests
**Scale/Scope**: Backend API changes only; ~11 files modified, 1 file removed, 1 migration added

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is not yet configured (template placeholders only). No gates to enforce. Proceeding.

**Post-Phase 1 re-check**: No violations. The design follows existing project patterns (repository → service → API layers), uses existing authentication, and makes minimal additive changes.

## Project Structure

### Documentation (this feature)

```text
specs/003-odoo-respondent-sync/
├── plan.md              # This file
├── research.md          # Phase 0 output — research decisions
├── data-model.md        # Phase 1 output — entity changes
├── quickstart.md        # Phase 1 output — setup and usage guide
├── contracts/
│   └── admin-api.yaml   # Phase 1 output — OpenAPI contract for modified endpoints
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── admin/
│   │   │   ├── __init__.py          # Remove respondent router import
│   │   │   ├── assessments.py       # Modify: new schema, odoo_id + employee_id query params
│   │   │   └── respondents.py       # REMOVE: all respondent CRUD endpoints
│   │   └── public/
│   │       └── assessment.py        # No changes
│   ├── core/
│   │   └── config.py                # No changes
│   ├── models/
│   │   ├── respondent.py            # Modify: add odoo_id column
│   │   └── assessment.py            # Modify: add employee_id, employee_name columns
│   ├── repositories/
│   │   └── respondent.py            # Modify: add upsert, odoo_id lookup methods
│   ├── schemas/
│   │   ├── assessment.py            # Modify: inline respondent + employee in AssessmentCreate
│   │   └── respondent.py            # Modify: add RespondentInline, remove Create/Update
│   ├── services/
│   │   └── assessment.py            # Modify: respondent upsert + employee storage in create flow
│   └── main.py                      # Modify: remove respondent OpenAPI tag
├── migrations/
│   └── versions/
│       └── YYYYMMDD_add_odoo_fields.py  # New: add odoo_id, employee_id, employee_name
└── tests/
    └── ...                          # Update tests for new contract
```

**Structure Decision**: Existing web application structure (backend/frontend split). This feature only modifies the backend. No new directories needed; changes are within existing files and one migration addition.

## Complexity Tracking

No constitution violations to justify.
