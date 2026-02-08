# Tasks: Hide Result and Show Confirmation Page

**Input**: Design documents from `/specs/004-hide-result-confirmation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec - tests omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Frontend-only changes for this feature

---

## Phase 1: Setup

**Purpose**: No setup required - existing project infrastructure

This feature builds on an existing codebase with all infrastructure already in place. No new dependencies or configuration needed.

**Checkpoint**: Ready to proceed to implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared components before user story implementation

- [x] T001 [P] Create ConfirmationPage component in frontend/src/pages/ConfirmationPage.tsx displaying "Таны хүсэлтийг хүлээж авлаа" message only, styled consistently with existing pages (reference ExpiredLink.tsx for pattern)
- [x] T002 [P] Add confirmation route `/a/:token/confirmation` to React Router in frontend/src/App.tsx within AssessmentLayout, positioned after /contact route

**Checkpoint**: Foundation ready - confirmation page exists and is routable

---

## Phase 3: User Story 1 & 3 - Survey Completion Confirmation + Redirection (Priority: P1) 🎯 MVP

**Goal**: Users see confirmation page with "Таны хүсэлтийг хүлээж авлаа" after survey submission instead of results

**Independent Test**: Complete a survey, submit contact info, verify confirmation page displays instead of results page

**Note**: User Stories 1 and 3 are combined as they are both P1 priority and tightly coupled - the confirmation display (US1) and the redirect to it (US3) form a single coherent change.

### Implementation for User Story 1 & 3

- [x] T003 [US1] Modify ContactPage.tsx handleSubmit function (around line 136-137) to navigate to `/a/${token}/confirmation` instead of `/a/${token}/results` in frontend/src/pages/ContactPage.tsx
- [x] T004 [US1] Remove results state passing from navigation call in ContactPage.tsx (no longer needed for confirmation page)

**Checkpoint**: User Story 1 & 3 complete - survey submission redirects to confirmation page with message

---

## Phase 4: User Story 2 - Direct URL Access to Results (Priority: P2)

**Goal**: Administrators can still access results via direct URL

**Independent Test**: Navigate directly to `/a/:token/results` URL and verify results page still functions

### Implementation for User Story 2

- [x] T005 [US2] Add public results endpoint GET /a/{token}/results in backend/src/api/public/assessment.py to fetch results for completed assessments
- [x] T006 [US2] Add getAssessmentResults function in frontend/src/services/assessment.ts to call the new endpoint
- [x] T010 [US2] Update Results.tsx in frontend/src/pages/Results.tsx to fetch results from API when no navigation state is available

**Checkpoint**: User Story 2 complete - results page accessible via direct URL

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and edge case handling

- [x] T007 Verify confirmation page handles direct access without prior survey completion (displays message regardless)
- [x] T008 Verify Mongolian text "Таны хүсэлтийг хүлээж авлаа" renders correctly with UTF-8 encoding
- [x] T009 Run quickstart.md manual testing validation (complete survey flow, direct URL access, confirmation page content)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No action required - existing infrastructure
- **Foundational (Phase 2)**: Creates ConfirmationPage and route - BLOCKS US1/US3
- **User Story 1 & 3 (Phase 3)**: Depends on Foundational - modifies navigation
- **User Story 2 (Phase 4)**: Verification only - no dependencies, can run in parallel with Phase 3
- **Polish (Phase 5)**: Depends on all implementation phases complete

### User Story Dependencies

- **User Story 1 & 3 (P1)**: Depends on T001, T002 (confirmation page and route must exist)
- **User Story 2 (P2)**: No dependencies - verification of preserved functionality

### Within Each Phase

- Foundational: T001 and T002 can run in parallel (different files)
- US1/US3: T003 depends on foundational; T004 follows T003
- US2: T005 and T006 are verification tasks, can run in parallel

### Parallel Opportunities

```
Phase 2 (parallel):
  T001 - Create ConfirmationPage.tsx
  T002 - Add route to App.tsx

Phase 3 + 4 (can overlap):
  T003, T004 - Modify ContactPage navigation
  T005, T006 - Verify results page (verification, no conflicts)
```

---

## Parallel Example: Foundational Phase

```bash
# Launch both foundational tasks together:
Task: "Create ConfirmationPage component in frontend/src/pages/ConfirmationPage.tsx"
Task: "Add confirmation route to React Router in frontend/src/App.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 3)

1. Complete Phase 2: Foundational (T001, T002 in parallel)
2. Complete Phase 3: User Story 1 & 3 (T003, T004)
3. **STOP and VALIDATE**: Complete survey flow, verify confirmation page
4. Deploy/demo if ready

### Incremental Delivery

1. Add ConfirmationPage + Route → Foundation ready
2. Modify navigation → Survey redirects to confirmation (MVP!)
3. Verify results page → Admin access confirmed
4. Polish → Edge cases validated

### Single Developer Strategy

Recommended execution order:
1. T001 → T002 (can be done together or sequentially)
2. T003 → T004 (sequential, same file)
3. T005 → T006 (verification)
4. T007 → T008 → T009 (final validation)

Total estimated tasks: 9 tasks
- Foundational: 2 tasks
- User Story 1 & 3: 2 tasks
- User Story 2: 2 tasks (verification only)
- Polish: 3 tasks

---

## Notes

- No backend changes required - frontend only
- No new dependencies to install
- No database migrations
- Results continue to be processed and stored (unchanged)
- Only the post-submission navigation target changes
- Commit after each task or logical group
