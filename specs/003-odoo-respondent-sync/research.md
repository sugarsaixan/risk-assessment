# Research: Odoo ERP Respondent Integration

**Feature Branch**: `003-odoo-respondent-sync`
**Date**: 2026-01-28

## R1: Upsert Pattern for Odoo Respondent Matching

**Decision**: Use database-level upsert (INSERT ON CONFLICT) on the `odoo_id` column for atomic respondent creation or update.

**Rationale**: The spec requires that when Odoo sends an assessment creation request, the system must atomically create a new respondent or update an existing one by `odoo_id`. PostgreSQL's `INSERT ... ON CONFLICT ... DO UPDATE` ensures atomicity and prevents race conditions from concurrent requests for the same respondent.

**Alternatives considered**:
- SELECT then INSERT/UPDATE (two-step): Rejected — subject to race conditions between concurrent assessment creation requests for the same respondent (TOCTOU).
- Application-level locking: Rejected — adds complexity and doesn't leverage database guarantees.

## R2: Odoo ID Column Design

**Decision**: Add `odoo_id` as a nullable `String(100)` column with a unique index on the `respondents` table.

**Rationale**:
- String type chosen per clarification (supports both integer IDs and XML/external IDs like `base.res_partner_123`).
- Nullable to preserve backward compatibility with pre-integration respondents that lack an Odoo ID.
- Unique index ensures no duplicates for respondents that do have an Odoo ID.
- Max length 100 accommodates Odoo external IDs which can be lengthy (module.xml_id format).

**Alternatives considered**:
- Integer column: Rejected — clarification confirmed string type to support XML/external IDs.
- Non-nullable: Rejected — breaks existing respondents that don't have Odoo IDs.

## R3: Assessment Creation Request Restructuring

**Decision**: Modify the `POST /admin/assessments` endpoint to accept inline respondent data and optional employee data instead of a `respondent_id` reference. The endpoint performs respondent upsert and stores employee data as part of the assessment creation transaction.

**Rationale**: The spec requires a single request from Odoo that combines respondent data, employee data, and assessment configuration. This reduces round-trips and ensures respondent data is always up-to-date when creating assessments.

**Alternatives considered**:
- Separate respondent upsert endpoint + assessment creation: Rejected — requires two API calls from Odoo and the spec explicitly states respondent endpoints are being removed.
- Keep both `respondent_id` and inline data options: Rejected — the standalone respondent CRUD is being deprecated per clarification.

## R4: Respondent Endpoint Deprecation Strategy

**Decision**: Remove `POST /admin/respondents`, `PATCH /admin/respondents/{id}` endpoints. The router file will be removed entirely since all CRUD operations are being eliminated.

**Rationale**: Per clarification, standalone respondent create/update endpoints are removed. Respondents are only created/updated through the Odoo-initiated assessment creation flow.

**Alternatives considered**:
- Soft deprecation (keep endpoints but add deprecation warnings): Rejected — clarification explicitly chose full removal.
- Keep read endpoints: Rejected — clarification stated no read-only access preserved separately; respondent data is accessible through assessment-related endpoints.

## R5: Legacy Respondent Linking Strategy

**Decision**: When Odoo sends a respondent and no match is found by `odoo_id`, attempt a secondary match by `kind` + `registration_no` combination. If a unique match is found, link the existing respondent by setting its `odoo_id`.

**Rationale**: The spec (FR-017) requires linking pre-existing respondents to Odoo IDs when Odoo sends a matching respondent. Matching by `kind` + `registration_no` is the most reliable composite key since registration numbers are unique within a kind (business/organization registry numbers are unique, person IDs are unique).

**Alternatives considered**:
- Match by name only: Rejected — names are not unique and may have minor spelling differences.
- No automatic linking: Rejected — would create duplicate respondent records and break assessment history.
- Match by registration_no only: Rejected — a person and organization could theoretically share a registration number.

## R6: Query Assessments by Odoo ID and Employee ID

**Decision**: Add `odoo_id` and `employee_id` query parameters to the `GET /admin/assessments` list endpoint. The `odoo_id` filter resolves the respondent first, then filters assessments by `respondent_id`. The `employee_id` filter matches directly against the assessment's `employee_id` column.

**Rationale**: The spec (FR-012, FR-012a) requires querying assessments by both Odoo respondent ID and employee ID. These are additive query parameters that work alongside existing `respondent_id` and `status` filters.

**Alternatives considered**:
- Store `odoo_id` on the assessment record: Rejected — introduces data denormalization; the respondent table is the single source of truth for Odoo IDs.
- Separate endpoints for each filter: Rejected — adding query parameters to the existing list endpoint is more consistent with the existing API patterns.

## R7: Migration Strategy

**Decision**: Single Alembic migration that:
1. Adds `odoo_id` column (nullable, unique index) to `respondents` table
2. Adds `employee_id` column (nullable String(100)) to `assessments` table
3. Adds `employee_name` column (nullable String(300)) to `assessments` table
4. No data migration needed — existing records simply have NULL values for new columns

**Rationale**: All changes are additive nullable columns requiring no data backfill. The unique index on `odoo_id` uses `WHERE odoo_id IS NOT NULL` (partial index) to ensure uniqueness only for non-null values. Employee fields have no uniqueness constraint since multiple assessments can be created by the same employee.

**Alternatives considered**:
- Separate migration per table: Rejected — the changes are part of a single feature and logically belong together.
- Full table restructure: Rejected — only adding columns; existing schema remains intact.

## R8: Employee Data Storage on Assessment

**Decision**: Store `employee_id` (nullable String(100)) and `employee_name` (nullable String(300)) directly on the `assessments` table as denormalized fields.

**Rationale**: Per clarification, employee data is stored on the assessment (not the respondent) as an audit trail of who created each assessment. Denormalization is appropriate here because:
- Employee data is immutable per assessment (captures who created it at that point in time).
- There's no need for a separate employee table — the data is purely for audit/display purposes.
- Employee data is optional (FR-008b) — existing assessments and those created without employee info have NULL values.
- String type for `employee_id` is consistent with `odoo_id` on respondent (supports XML/external IDs).

**Alternatives considered**:
- Separate Employee entity: Rejected — over-engineering for two optional audit fields. No business logic operates on employees independently.
- Employee data on respondent: Rejected — per clarification, different employees can create assessments for the same respondent; storing on respondent would lose this distinction.
