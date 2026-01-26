# Tasks: Submit-Then-Contact Workflow

**Input**: Design documents from `/specs/002-submit-contact-workflow/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Extends**: 001-risk-assessment-survey (modifies existing implementation)

**Tests**: Not explicitly requested - test tasks not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in descriptions

## Path Conventions

- **Backend**: `backend/src/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (React/TypeScript)

---

## Phase 1: Setup (Database & Infrastructure)

**Purpose**: Database migration and foundational backend infrastructure for drafts

- [X] T001 Create Alembic migration for assessment_drafts table in backend/alembic/versions/xxx_add_assessment_drafts.py
- [X] T002 [P] Create AssessmentDraft SQLAlchemy model in backend/src/models/assessment_draft.py
- [X] T003 [P] Create draft Pydantic schemas (DraftSaveRequest, DraftResponse, DraftAnswer) in backend/src/schemas/draft.py
- [X] T004 Run migration to create assessment_drafts table

---

## Phase 2: Foundational (Backend Draft Service)

**Purpose**: Core draft save/load functionality - MUST complete before frontend can integrate

**⚠️ CRITICAL**: Frontend draft features depend on this phase

- [X] T005 Create DraftRepository with upsert/get/delete operations in backend/src/repositories/draft.py
- [X] T006 Create DraftService with save_draft, load_draft, delete_draft methods in backend/src/services/draft.py
- [X] T007 Add GET /a/{token}/draft endpoint to load draft in backend/src/api/public/assessment.py
- [X] T008 Add PUT /a/{token}/draft endpoint to save draft in backend/src/api/public/assessment.py
- [X] T009 Modify GET /a/{token} endpoint to include draft field in response in backend/src/api/public/assessment.py

**Checkpoint**: Backend draft API ready - frontend integration can begin

---

## Phase 3: User Story 1 - Questionnaire Before Contact (Priority: P1) 🎯 MVP

**Goal**: Separate questionnaire from contact collection; users complete all questions first, then see contact form page

**Independent Test**: Access assessment link, complete all questions, click Submit, verify navigation to /contact page, fill contact info, confirm, see results

### Implementation for User Story 1

#### Backend Changes (US1)

- [X] T010 [US1] Modify POST /a/{token}/submit to accept contact info in request body in backend/src/api/public/assessment.py
- [X] T011 [US1] Update submission logic to delete draft after successful submit in backend/src/api/public/assessment.py

#### Frontend Changes (US1)

- [X] T012 [P] [US1] Create ContactPage component with form fields (Овог, Нэр, email, phone, Албан тушаал) in frontend/src/pages/ContactPage.tsx
- [X] T013 [US1] Add /a/:token/contact route to React Router in frontend/src/App.tsx
- [X] T014 [US1] Modify AssessmentForm to remove embedded contact fields in frontend/src/pages/AssessmentForm.tsx
- [X] T015 [US1] Update AssessmentForm Submit button to navigate to /contact page in frontend/src/pages/AssessmentForm.tsx
- [X] T016 [US1] Create AssessmentContext to share form state between pages in frontend/src/contexts/AssessmentContext.tsx
- [X] T017 [US1] Wrap routes with AssessmentContext provider in frontend/src/App.tsx
- [X] T018 [US1] Update ContactPage to submit with contact info in request body in frontend/src/pages/ContactPage.tsx
- [X] T019 [US1] Add Mongolian UI text labels (Илгээх, Хариулагчийн мэдээлэл, Баталгаажуулах) in frontend/src/pages/ContactPage.tsx

**Checkpoint**: User Story 1 complete - questionnaire and contact are separated, full flow works

---

## Phase 4: User Story 2 - Cancel Contact Entry (Priority: P2)

**Goal**: Allow respondent to go back from contact page to review/modify questionnaire answers

**Independent Test**: Complete questionnaire, click Submit, on contact page click Back, verify return to questionnaire with all answers preserved

### Implementation for User Story 2

- [X] T020 [US2] Add Буцах (Back) button to ContactPage in frontend/src/pages/ContactPage.tsx
- [X] T021 [US2] Implement back navigation that preserves form state in AssessmentContext in frontend/src/pages/ContactPage.tsx
- [X] T022 [US2] Verify AssessmentForm restores answers from context on return in frontend/src/pages/AssessmentForm.tsx

**Checkpoint**: User Story 2 complete - back navigation works, answers preserved

---

## Phase 5: User Story 3 - Save Progress and Resume (Priority: P1)

**Goal**: Enable server-side draft storage so users can save progress and resume from any device

**Independent Test**: Partially complete questionnaire, click Save, close browser, reopen link on different device, verify all saved answers restored

### Implementation for User Story 3

#### Frontend Draft Service (US3)

- [X] T023 [P] [US3] Create draft API service with saveDraft, loadDraft functions in frontend/src/services/draft.ts
- [X] T024 [P] [US3] Create useAutoSave hook with 30s interval and debounced change detection in frontend/src/hooks/useAutoSave.ts
- [X] T025 [P] [US3] Create SaveButton component with loading/success/error states in frontend/src/components/SaveButton.tsx
- [X] T026 [P] [US3] Create AutoSaveIndicator component showing Хадгалагдсан/Хадгалж байна status in frontend/src/components/AutoSaveIndicator.tsx

#### Frontend Integration (US3)

- [X] T027 [US3] Integrate useAutoSave hook into AssessmentForm in frontend/src/pages/AssessmentForm.tsx
- [X] T028 [US3] Add SaveButton and AutoSaveIndicator to AssessmentForm layout in frontend/src/pages/AssessmentForm.tsx
- [X] T029 [US3] Update useAssessment hook to load draft on initial page load in frontend/src/hooks/useAssessment.ts
- [X] T030 [US3] Implement network error handling with retry logic in useAutoSave in frontend/src/hooks/useAutoSave.ts
- [X] T031 [US3] Add Mongolian error message "Хадгалж чадсангүй" for save failures in frontend/src/hooks/useAutoSave.ts

**Checkpoint**: User Story 3 complete - save/resume works across devices

---

## Phase 6: Admin Cleanup (Supporting Feature)

**Goal**: Enable admin to cleanup orphaned drafts and images for expired assessments

**Independent Test**: Create expired assessment with draft, call DELETE /admin/cleanup/drafts, verify draft deleted

### Implementation

- [X] T032 [P] Create cleanup service with cleanup_drafts, cleanup_images methods in backend/src/services/cleanup.py
- [X] T033 Add DELETE /admin/cleanup/drafts endpoint in backend/src/api/admin/cleanup.py
- [X] T034 Add DELETE /admin/cleanup/images endpoint in backend/src/api/admin/cleanup.py
- [X] T035 Register cleanup router in admin API in backend/src/api/admin/__init__.py

**Checkpoint**: Admin cleanup endpoints available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and edge case handling

- [X] T100 [P] Add form validation to ContactPage (email format, phone format, required fields) in frontend/src/pages/ContactPage.tsx
- [X] T101 [P] Handle network failure during auto-save with user-friendly retry option in frontend/src/hooks/useAutoSave.ts
- [X] T102 [P] Add loading states to ContactPage during submission in frontend/src/pages/ContactPage.tsx
- [X] T103 [P] Ensure mobile-responsive layout for ContactPage in frontend/src/pages/ContactPage.tsx
- [X] T104 [P] Add rate limiting awareness to draft API calls in frontend/src/services/draft.ts
- [X] T105 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → [US1, US2, US3 can run in parallel] → Phase 6 (Admin) → Phase 7 (Polish)
```

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 (Backend Draft API). Can start after T009.
- **User Story 2 (P2)**: Depends on US1 completion (ContactPage must exist). Start after T019.
- **User Story 3 (P1)**: Depends on Phase 2 (Backend Draft API). Can run parallel with US1 after T009.

### Within Each Phase

- Models/schemas before services
- Services before API endpoints
- Backend endpoints before frontend integration
- Core components before integration tasks

### Parallel Opportunities

**Phase 1 (after T001 migration created):**
- T002, T003 can run in parallel

**Phase 3 User Story 1 (after T011):**
- T012 (ContactPage) can run parallel with T014-T015 (AssessmentForm modifications)

**Phase 5 User Story 3:**
- T023, T024, T025, T026 can all run in parallel
- Then T027-T031 are sequential integration

**Phase 6 Admin:**
- T032 (service) first, then T033, T034 can run in parallel

**Phase 7 Polish:**
- All tasks marked [P] can run in parallel

---

## Parallel Execution Examples

### Backend Draft Infrastructure (Phase 1-2)
```bash
# After migration created:
Task: "Create AssessmentDraft SQLAlchemy model in backend/src/models/assessment_draft.py"
Task: "Create draft Pydantic schemas in backend/src/schemas/draft.py"
```

### User Story 3 Components (Phase 5)
```bash
# Launch all frontend draft components together:
Task: "Create draft API service in frontend/src/services/draft.ts"
Task: "Create useAutoSave hook in frontend/src/hooks/useAutoSave.ts"
Task: "Create SaveButton component in frontend/src/components/SaveButton.tsx"
Task: "Create AutoSaveIndicator component in frontend/src/components/AutoSaveIndicator.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 3)

1. Complete Phase 1: Setup (database migration)
2. Complete Phase 2: Foundational (draft API)
3. Complete User Story 1 (separate contact page) - Core workflow change
4. Complete User Story 3 (save/resume) - Critical for real-world use
5. **STOP and VALIDATE**: Test complete assessment flow with save/resume
6. Deploy/demo if ready

### Incremental Delivery

1. **Setup + Foundational** → Draft backend ready
2. **+ User Story 1** → Contact page separated (visible UI change)
3. **+ User Story 3** → Save/resume works (major feature)
4. **+ User Story 2** → Back navigation polished
5. **+ Admin Cleanup** → Maintenance capability
6. **+ Polish** → Production-ready

### Critical Path

```
T001 → T004 → T005 → T006 → T007/T008/T009 → [T010-T019 for US1] → [T023-T031 for US3]
```

---

## Notes

- This feature modifies existing 001-risk-assessment-survey code
- All frontend changes are additive (new pages, components) or modificative (existing pages)
- Backend adds new table, new endpoints, and modifies existing submit endpoint
- No test tasks included (not explicitly requested)
- Admin cleanup (Phase 6) is lower priority - can be deferred post-MVP
- All Mongolian text labels specified in requirements
