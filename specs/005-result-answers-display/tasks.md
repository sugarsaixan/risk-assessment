# Tasks: Result Page User Answers Display

**Input**: Design documents from `/specs/005-result-answers-display/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in feature specification. Manual testing only (per quickstart.md).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Type definitions and translations shared by both user stories

- [x] T001 [P] Add `AnswerBreakdown` interface and extend `SubmitResponse` in `frontend/src/types/api.ts`
- [x] T002 [P] Add Mongolian translation strings for answers section in `frontend/src/constants/mn.ts` (keys: `answers.title`, `answers.show`, `answers.hide`, `answers.attachments`, answer option labels "Тийм"/"Үгүй")

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend and service changes that MUST be complete before any frontend user story work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `breakdown` query parameter to public results endpoint in `backend/src/api/public/assessment.py` — accept `breakdown: bool = Query(False)` and pass `include_breakdown=breakdown` to `results_service.get_results()`, include `answer_breakdown` in response when present
- [x] T004 Update `getAssessmentResults` in `frontend/src/services/assessment.ts` to accept `includeBreakdown` parameter (default `true`) and append `?breakdown=true` query string when enabled

**Checkpoint**: Backend returns `answer_breakdown` via `?breakdown=true`, frontend service requests it

---

## Phase 3: User Story 1 — View Individual Answers on Results Page (Priority: P1) 🎯 MVP

**Goal**: Display all submitted question answers grouped by type in a new "Хариултууд" section on the Results page

**Independent Test**: Navigate to `/a/{token}/results` for a completed assessment, expand the Answers section, and verify all answers appear with question text, selected option (Тийм/Үгүй), comments, and attachment counts, grouped by type name

### Implementation for User Story 1

- [x] T005 [US1] Create `AnswersSection` component in `frontend/src/components/AnswersSection.tsx` — accepts `answers: AnswerBreakdown[]` prop, groups answers by `type_name`, renders each group with header and answer rows showing: question text, selected option with color (green for YES / red for NO using "Тийм"/"Үгүй"), comment if present, attachment count badge if > 0, and score as "X/Y"
- [x] T006 [US1] Integrate `AnswersSection` into `frontend/src/pages/Results.tsx` — pass `results.answer_breakdown` to component, place below existing score content (after TypeScoreCards and Summary)

**Checkpoint**: Answers section visible on results page with all submitted answers displayed and grouped by type

---

## Phase 4: User Story 2 — Collapse/Expand Answers Section (Priority: P1)

**Goal**: Users can collapse or expand the answers section; section starts collapsed by default

**Independent Test**: Load results page and verify section is collapsed. Click header to expand, verify answers appear. Click again to collapse.

### Implementation for User Story 2

- [x] T007 [US2] Add collapse/expand state to `AnswersSection` in `frontend/src/components/AnswersSection.tsx` — use `useState(false)` for `isExpanded`, add clickable header with chevron icon (rotating via `transition-transform`), conditionally render answer content based on `isExpanded`, show answer count in header (e.g., "Хариултууд (25)"), follow `TypeScoreCard.tsx` collapsible pattern
- [x] T008 [US2] Verify default collapsed state and toggle indicator in `frontend/src/components/AnswersSection.tsx` — ensure chevron points down when collapsed and up when expanded (FR-008), ensure toggle responds instantly (SC-002)

**Checkpoint**: Answers section starts collapsed, toggles on click with smooth animation and clear state indicator

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and edge case handling

- [x] T009 Verify existing results page content is unchanged (FR-006) — OverallScoreCard, TypeScoreCards, Summary, theme toggle all function correctly
- [x] T010 Run quickstart.md manual testing checklist (all 10 tests) from `specs/005-result-answers-display/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (types must exist first)
- **User Story 1 (Phase 3)**: Depends on Phase 2 (backend endpoint and service must work)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (component must exist before adding collapse behavior)
- **Polish (Phase 5)**: Depends on Phases 3 and 4

### Within Each User Story

- Models/types before services
- Services before components
- Components before page integration

### Parallel Opportunities

- T001 and T002 can run in parallel (different files, no dependencies)
- T003 and T004 can run in parallel after Phase 1 (backend vs frontend, independent)

---

## Parallel Example: Phase 1

```bash
# Launch setup tasks together:
Task: "Add AnswerBreakdown interface in frontend/src/types/api.ts"
Task: "Add MN translations in frontend/src/constants/mn.ts"
```

## Parallel Example: Phase 2

```bash
# Launch foundational tasks together:
Task: "Add breakdown param to backend endpoint in backend/src/api/public/assessment.py"
Task: "Update frontend service in frontend/src/services/assessment.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (types + translations)
2. Complete Phase 2: Foundational (backend endpoint + frontend service)
3. Complete Phase 3: User Story 1 (AnswersSection component + integration)
4. **STOP and VALIDATE**: Answers display correctly on results page
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add User Story 1 → Test: answers visible → Deploy (MVP!)
3. Add User Story 2 → Test: collapse/expand works → Deploy
4. Polish → Full manual testing → Final deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Both user stories are P1 priority but US2 depends on US1 (component must exist)
- No automated tests — manual testing per quickstart.md
- Backend change is minimal (one parameter addition to existing endpoint)
- Frontend follows existing TypeScoreCard collapsible pattern
