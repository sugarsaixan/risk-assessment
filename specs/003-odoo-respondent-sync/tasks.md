# Tasks: Odoo ERP Respondent Integration

**Input**: Design documents from `/specs/003-odoo-respondent-sync/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/admin-api.yaml

**Tests**: Not explicitly requested in the feature specification. Test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/migrations/`, `backend/tests/`

---

## Phase 1: Setup (Database Migration)

**Purpose**: Add odoo_id to respondents and employee fields to assessments — required before any code changes

- [x] T001 Create Alembic migration to: (1) add nullable `odoo_id` String(100) column with partial unique index (`WHERE odoo_id IS NOT NULL`) to `respondents` table, (2) add nullable `employee_id` String(100) column with standard index and nullable `employee_name` String(300) column to `assessments` table, in `backend/migrations/versions/`

**Checkpoint**: Migration applied. `respondents` has `odoo_id`, `assessments` has `employee_id` + `employee_name`. All existing records have NULL for new columns.

---

## Phase 2: Foundational (Model, Schema & Repository Changes)

**Purpose**: Core model, schema, and repository modifications that ALL user stories depend on. Must complete before any user story work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 [P] Add `odoo_id` mapped column (nullable String(100), unique partial index) to the Respondent model in `backend/src/models/respondent.py`
- [x] T003 [P] Add `employee_id` (nullable String(100), indexed) and `employee_name` (nullable String(300)) mapped columns to the Assessment model in `backend/src/models/assessment.py`
- [x] T004 [P] Add `RespondentInline` Pydantic schema (odoo_id: str, name: str 1-300 chars, kind: RespondentKind, registration_no: str | None max 50 chars) with conditional validator (registration_no required when kind=ORG) in `backend/src/schemas/respondent.py`. Remove `RespondentCreate` and `RespondentUpdate` schemas.
- [x] T005 [P] Modify `AssessmentCreate` schema to replace `respondent_id: UUID` with `respondent: RespondentInline` nested object, add optional `employee_id: str | None` (max 100) and `employee_name: str | None` (max 300) fields. Add `respondent_id: UUID` to `AssessmentCreated` response. Add `respondent_odoo_id: str | None`, `employee_id: str | None`, `employee_name: str | None` to `AssessmentResponse` and `AssessmentList` schemas. All in `backend/src/schemas/assessment.py`
- [x] T006 Add `get_by_odoo_id(odoo_id: str)` and `find_by_kind_and_registration(kind: RespondentKind, registration_no: str)` lookup methods to `RespondentRepository` in `backend/src/repositories/respondent.py`
- [x] T007 Add `upsert_from_odoo(odoo_id: str, name: str, kind: RespondentKind, registration_no: str | None)` method to `RespondentRepository` in `backend/src/repositories/respondent.py` that: (1) looks up by `odoo_id`, (2) if found updates `name`/`registration_no`/`updated_at`, (3) if not found tries `kind`+`registration_no` match to link legacy respondents by setting their `odoo_id`, (4) if still not found creates new respondent. Returns the Respondent instance. Use INSERT ON CONFLICT for atomicity per R1 in research.md.

**Checkpoint**: Foundation ready. Respondent model has `odoo_id`, Assessment model has `employee_id`/`employee_name`, schemas accept inline respondent + employee data, repository can upsert by Odoo ID.

---

## Phase 3: User Story 1 — Odoo Creates Assessment with Respondent + Employee Data (Priority: P1) 🎯 MVP

**Goal**: Odoo sends a single API request with inline respondent data, optional employee data, and assessment configuration. The system creates/matches the respondent, stores employee info on the assessment, and returns an assessment link.

**Independent Test**: Send `POST /admin/assessments` with a `respondent` object (odoo_id, name, kind, registration_no), optional `employee_id`/`employee_name`, and `selected_type_ids`. Verify respondent is created/matched, employee data stored on assessment, and link URL + respondent_id are returned.

### Implementation for User Story 1

- [x] T008 [US1] Modify `create_assessment` method in `AssessmentService` (`backend/src/services/assessment.py`) to: (1) extract respondent data from `AssessmentCreate.respondent`, (2) call `RespondentRepository.upsert_from_odoo()` to create/match respondent, (3) pass `employee_id` and `employee_name` from the request to the assessment record creation via `AssessmentRepository.create()`, (4) include `respondent_id` in `AssessmentCreated` response.
- [x] T009 [US1] Update `AssessmentRepository.create()` method in `backend/src/repositories/assessment.py` to accept optional `employee_id` and `employee_name` parameters and store them on the assessment record.
- [x] T010 [US1] Update the `create_assessment` endpoint in `backend/src/api/admin/assessments.py` to use the new `AssessmentCreate` schema with inline respondent + employee data. Ensure error responses include specific messages for: invalid kind, missing registration_no for ORG, invalid type IDs.

**Checkpoint**: `POST /admin/assessments` accepts inline respondent + employee data. Assessment records store employee_id/employee_name. This is the MVP.

---

## Phase 4: User Story 2 — Odoo Manages Full Assessment Lifecycle (Priority: P1)

**Goal**: Odoo can query assessments by respondent Odoo ID or employee ID, and assessment responses include employee data and respondent Odoo ID for full lifecycle management.

**Independent Test**: Create assessments via the Odoo flow, then query `GET /admin/assessments?odoo_id=res.partner_42` and `GET /admin/assessments?employee_id=hr.employee_15`. Verify filtering works and responses include `employee_id`, `employee_name`, and `respondent_odoo_id`.

### Implementation for User Story 2

- [x] T011 [US2] Add `odoo_id: str | None` and `employee_id: str | None` query parameters to `list_assessments` endpoint in `backend/src/api/admin/assessments.py`. For `odoo_id`: resolve to `respondent_id` via `RespondentRepository.get_by_odoo_id()` then filter by respondent. For `employee_id`: filter directly on the assessment's `employee_id` column.
- [x] T012 [US2] Update `get_all` and `count` methods in `AssessmentRepository` (`backend/src/repositories/assessment.py`) to accept and filter by `employee_id` parameter.
- [x] T013 [US2] Update `list_assessments` method in `AssessmentService` (`backend/src/services/assessment.py`) to accept and pass through `odoo_id` and `employee_id` filters.
- [x] T014 [US2] Update assessment response serialization in `list_assessments` and `get_assessment` endpoints (`backend/src/api/admin/assessments.py`) to populate `respondent_odoo_id` (from eagerly loaded respondent relationship), `employee_id`, and `employee_name` in `AssessmentResponse` and `AssessmentList` schemas.

**Checkpoint**: Odoo can filter assessments by `?odoo_id=` and `?employee_id=`. All assessment responses include employee data and respondent Odoo ID.

---

## Phase 5: User Story 3 — Respondent Data Consistency (Priority: P2)

**Goal**: Respondent data updates from Odoo are reflected when creating new assessments. The upsert flow ensures the respondent record always reflects the latest data from Odoo.

**Independent Test**: Create a respondent via assessment creation with name "Company A". Create another assessment with same `odoo_id` but name "Company B". Verify respondent record is updated to "Company B" and `updated_at` is refreshed.

### Implementation for User Story 3

- [x] T015 [US3] Verify and refine the `upsert_from_odoo` method in `RespondentRepository` (`backend/src/repositories/respondent.py`) to ensure it updates `name`, `registration_no`, and refreshes `updated_at` when an existing respondent is found by `odoo_id`. This should already work from T007 but verify edge cases: (1) only name changes, (2) only registration_no changes, (3) both change simultaneously.

**Checkpoint**: Respondent data stays current with Odoo. Historical assessment snapshots remain unaffected.

---

## Phase 6: Deprecation & Cleanup

**Purpose**: Remove standalone respondent endpoints and clean up references

- [x] T016 [P] Remove the respondent router file `backend/src/api/admin/respondents.py` entirely
- [x] T017 [P] Remove `respondents` router import and `include_router(respondents.router, ...)` line from `backend/src/api/admin/__init__.py`
- [x] T018 [P] Remove the `"respondents"` tag entry from `openapi_tags` list in `backend/src/main.py`

**Checkpoint**: Respondent CRUD endpoints fully removed. No dangling imports or references.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation, edge case verification, and end-to-end verification

- [x] T019 Verify edge case handling: (1) kind validation rejects values other than ORG/PERSON, (2) registration_no required for ORG returns clear error, (3) invalid questionnaire type IDs return proper error with list of invalid IDs, (4) concurrent upserts for same odoo_id don't create duplicates — check across `backend/src/schemas/respondent.py`, `backend/src/services/assessment.py`, `backend/src/repositories/respondent.py`
- [x] T020 Update existing tests in `backend/tests/` (N/A — no existing tests to update) to use new `AssessmentCreate` schema format (inline respondent instead of respondent_id). Remove any tests for deleted respondent CRUD endpoints.
- [x] T021 Run quickstart.md validation — execute all curl commands from `specs/003-odoo-respondent-sync/quickstart.md` against local server to verify end-to-end flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (migration must be applied first)
- **Phase 3 (US1)**: Depends on Phase 2 — core integration, MVP
- **Phase 4 (US2)**: Depends on Phase 2; benefits from Phase 3 for e2e testing
- **Phase 5 (US3)**: Depends on Phase 2 (T007 specifically); can run in parallel with Phase 4
- **Phase 6 (Cleanup)**: Can start after Phase 2; recommended after Phase 3 is verified
- **Phase 7 (Polish)**: Depends on all prior phases

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P1)**: Depends on Foundational (Phase 2) — Independent of US1 for implementation, but US1 is needed for meaningful query testing
- **User Story 3 (P2)**: Depends on Foundational (Phase 2, specifically T007) — Verification task, independent of US1/US2

### Within Each User Story

- Schemas and repositories before services
- Services before endpoints
- Core implementation before integration

### Parallel Opportunities

- **Phase 2**: T002, T003, T004, T005 can run in parallel (different files)
- **Phase 3 + Phase 5**: Can overlap (different concerns)
- **Phase 4 + Phase 5**: Can run in parallel after Phase 3
- **Phase 6**: T016, T017, T018 can run in parallel (different files)

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch model and schema changes in parallel:
Task: "Add odoo_id column to Respondent model in backend/src/models/respondent.py"
Task: "Add employee columns to Assessment model in backend/src/models/assessment.py"
Task: "Add RespondentInline schema in backend/src/schemas/respondent.py"
Task: "Modify AssessmentCreate schema in backend/src/schemas/assessment.py"
```

## Parallel Example: Phase 6 Deprecation

```bash
# Launch deprecation tasks in parallel:
Task: "Remove respondent router file backend/src/api/admin/respondents.py"
Task: "Remove respondent router import from backend/src/api/admin/__init__.py"
Task: "Remove respondents tag from backend/src/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migration)
2. Complete Phase 2: Foundational (models, schemas, repositories)
3. Complete Phase 3: User Story 1 (assessment creation with inline respondent + employee)
4. **STOP and VALIDATE**: Test assessment creation with inline respondent + employee data
5. Deploy/demo if ready — Odoo can now create assessments

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test query filters → Deploy/Demo
4. Add User Story 3 → Verify data consistency → Deploy/Demo
5. Complete Deprecation → Remove old endpoints
6. Polish → Edge cases, test updates, quickstart validation
7. Each story adds value without breaking previous stories

---

## Notes

- Total tasks: **21**
- Phase 1 (Setup): 1 task
- Phase 2 (Foundational): 6 tasks
- Phase 3 / US1 (MVP): 3 tasks
- Phase 4 / US2: 4 tasks
- Phase 5 / US3: 1 task
- Phase 6 (Deprecation): 3 tasks
- Phase 7 (Polish): 3 tasks
- No new Python packages required
- Backend-only changes — no frontend modifications
- Breaking change to Admin API contract (respondent_id → inline respondent object + employee fields)
- Existing public-facing assessment flow (form completion, submission) is unaffected
- Suggested MVP scope: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)
