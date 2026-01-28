# Data Model: Odoo ERP Respondent Integration

**Feature Branch**: `003-odoo-respondent-sync`
**Date**: 2026-01-28

## Entity Changes

### Respondent (Modified)

**Table**: `respondents`

| Column          | Type           | Nullable | Constraints           | Change   |
|-----------------|----------------|----------|-----------------------|----------|
| id              | UUID           | No       | PK, default uuid4     | Existing |
| odoo_id         | String(100)    | Yes      | Unique (partial: WHERE odoo_id IS NOT NULL) | **New** |
| kind            | Enum(ORG,PERSON) | No     | Indexed               | Existing |
| name            | String(300)    | No       | Indexed               | Existing |
| registration_no | String(50)     | Yes      |                       | Existing |
| created_at      | DateTime(tz)   | No       | server_default=now()  | Existing |
| updated_at      | DateTime(tz)   | No       | server_default=now(), onupdate=now() | Existing |

**New Index**: `ix_respondents_odoo_id` — partial unique index on `odoo_id` where `odoo_id IS NOT NULL`

**Lookup Strategy**:
1. Primary lookup: by `odoo_id` (new, for Odoo-initiated requests)
2. Legacy fallback: by `kind` + `registration_no` (for linking pre-existing respondents)
3. Internal: by `id` (existing, for assessment references)

### Assessment (Modified)

**Table**: `assessments`

| Column             | Type           | Nullable | Constraints           | Change   |
|--------------------|----------------|----------|-----------------------|----------|
| id                 | UUID           | No       | PK, default uuid4     | Existing |
| respondent_id      | UUID           | No       | FK → respondents.id   | Existing |
| token_hash         | String         | No       | Unique                | Existing |
| selected_type_ids  | Array[UUID]    | No       |                       | Existing |
| questions_snapshot | JSONB          | No       |                       | Existing |
| expires_at         | DateTime(tz)   | No       |                       | Existing |
| status             | Enum           | No       | PENDING/COMPLETED/EXPIRED | Existing |
| completed_at       | DateTime(tz)   | Yes      |                       | Existing |
| employee_id        | String(100)    | Yes      | Indexed               | **New** |
| employee_name      | String(300)    | Yes      |                       | **New** |
| created_at         | DateTime(tz)   | No       | server_default=now()  | Existing |

**New Index**: `ix_assessments_employee_id` — standard index on `employee_id` (for query filtering)

**Employee data behavior**:
- Immutable per assessment (captured at creation time, never updated)
- Both fields are optional (NULL when Odoo does not provide employee data)
- `employee_id` is a string consistent with `odoo_id` on respondent (supports Odoo XML/external IDs)
- `employee_name` is the display name for audit/UI purposes

## State Transitions

### Respondent Lifecycle (Modified)

```
[Odoo sends request with new odoo_id]
    → Created (odoo_id set, name/kind/registration_no from Odoo)

[Odoo sends request with existing odoo_id]
    → Updated (name, registration_no refreshed from latest Odoo data)

[Odoo sends request matching legacy respondent by kind+registration_no]
    → Linked (existing respondent gets odoo_id set, data updated)
```

### Assessment Lifecycle (Unchanged)

```
PENDING → COMPLETED (on submission)
PENDING → EXPIRED (on expiration check)
```

Employee data is written at creation and never modified through the lifecycle.

## Validation Rules

### Respondent (from Odoo request)

| Field           | Rule                                                          |
|-----------------|---------------------------------------------------------------|
| odoo_id         | Required, string, max 100 chars, must be unique among respondents |
| name            | Required, string, 1-300 chars                                 |
| kind            | Required, must be "ORG" or "PERSON"                           |
| registration_no | Required when kind=ORG, optional when kind=PERSON, max 50 chars |

### Employee (from Odoo request)

| Field         | Rule                                           |
|---------------|-------------------------------------------------|
| employee_id   | Optional, string, max 100 chars                 |
| employee_name | Optional, string, max 300 chars                 |

Note: If `employee_id` is provided, `employee_name` should also be provided (but not enforced at validation level — both are independently optional).

### Assessment Creation (modified request)

| Field                        | Rule                                                |
|------------------------------|-----------------------------------------------------|
| respondent.odoo_id           | Required                                            |
| respondent.name              | Required, 1-300 chars                               |
| respondent.kind              | Required, ORG or PERSON                             |
| respondent.registration_no   | Required if kind=ORG, optional if kind=PERSON       |
| employee_id                  | Optional, max 100 chars                             |
| employee_name                | Optional, max 300 chars                             |
| selected_type_ids            | Required, non-empty list of valid active type UUIDs |
| expires_in_days              | Optional, 1-365, default 30                         |

## Migration

### Alembic Migration: `add_odoo_and_employee_fields`

**Operations (upgrade)**:
1. Add column `odoo_id` to `respondents` table (nullable String(100))
2. Create partial unique index `ix_respondents_odoo_id` on `odoo_id` WHERE `odoo_id IS NOT NULL`
3. Add column `employee_id` to `assessments` table (nullable String(100))
4. Add column `employee_name` to `assessments` table (nullable String(300))
5. Create index `ix_assessments_employee_id` on `employee_id`

**Operations (downgrade)**:
1. Drop index `ix_assessments_employee_id`
2. Drop column `employee_name` from `assessments`
3. Drop column `employee_id` from `assessments`
4. Drop index `ix_respondents_odoo_id`
5. Drop column `odoo_id` from `respondents`

**Data migration**: None required. Existing records have NULL for all new columns.
