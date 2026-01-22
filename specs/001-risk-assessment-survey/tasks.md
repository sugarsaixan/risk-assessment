# Tasks: Risk Assessment Survey System

**Input**: Design documents from `/specs/001-risk-assessment-survey/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec. Tests are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Create frontend directory structure per plan.md in frontend/
- [x] T003 [P] Initialize Python project with pyproject.toml including FastAPI, SQLAlchemy, Pydantic, passlib, argon2-cffi, slowapi, aioboto3, python-magic, alembic, asyncpg, pytest, httpx in backend/pyproject.toml
- [x] T004 [P] Initialize React project with Vite, TypeScript, TailwindCSS, react-hook-form, zod, react-router-dom, react-dropzone, axios in frontend/package.json
- [x] T005 [P] Configure Python linting (ruff) and formatting in backend/pyproject.toml
- [x] T006 [P] Configure TypeScript strict mode and ESLint in frontend/tsconfig.json and frontend/.eslintrc.cjs
- [x] T007 Create docker-compose.yml with PostgreSQL and MinIO services at project root
- [x] T008 [P] Configure TailwindCSS with dark mode and Noto Sans font in frontend/tailwind.config.js
- [x] T009 [P] Create backend environment configuration loader in backend/src/core/config.py

**Checkpoint**: Project skeleton ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create SQLAlchemy async engine and session factory in backend/src/core/database.py
- [x] T011 Initialize Alembic with async support in backend/alembic/
- [x] T012 [P] Create database enum types (ScoringMethod, RespondentKind, OptionType, AssessmentStatus, RiskRating) in backend/src/models/enums.py
- [x] T013 [P] Create base SQLAlchemy model with UUID primary key and timestamps in backend/src/models/base.py
- [x] T014 Create ApiKey model with key_hash, name, is_active, last_used_at in backend/src/models/api_key.py
- [x] T015 Create initial Alembic migration for api_keys table in backend/alembic/versions/
- [x] T016 Implement API key authentication dependency using APIKeyHeader and Argon2 verification in backend/src/core/auth.py
- [x] T017 [P] Create FastAPI app instance with CORS and error handlers in backend/src/main.py
- [x] T018 [P] Configure slowapi rate limiter (30 req/min/IP) for public endpoints in backend/src/core/rate_limit.py
- [x] T019 [P] Create S3/MinIO client configuration and upload helper in backend/src/core/storage.py
- [x] T020 [P] Create base Pydantic schemas (PaginatedResponse, Error) in backend/src/schemas/common.py
- [x] T021 [P] Create CLI command to generate and hash API keys in backend/src/cli.py
- [x] T022 [P] Create React app entry point with router setup in frontend/src/main.tsx
- [x] T023 [P] Create API client service with axios instance in frontend/src/services/api.ts
- [x] T024 [P] Create TypeScript type definitions from API contracts in frontend/src/types/api.ts

**Checkpoint**: Foundation ready - database connected, auth working, storage configured

---

## Phase 3: User Story 1 - Admin Creates Assessment Link (Priority: P1) 🎯 MVP

**Goal**: Admin can create questionnaire types, questions with options, respondents, and generate one-time assessment links with question snapshots

**Independent Test**: Call Admin API to create type → questions → options → respondent → assessment. Verify returned URL contains valid token format.

### Implementation for User Story 1

#### Models

- [x] T025 [P] [US1] Create QuestionnaireType model (name, scoring_method, thresholds, weight, is_active) in backend/src/models/questionnaire_type.py
- [x] T026 [P] [US1] Create Question model (type_id, text, display_order, weight, is_critical, is_active) in backend/src/models/question.py
- [x] T027 [P] [US1] Create QuestionOption model (question_id, option_type, score, require_comment, require_image, comment_min_len, max_images, image_max_mb) in backend/src/models/question_option.py
- [x] T028 [P] [US1] Create Respondent model (kind, name, registration_no) in backend/src/models/respondent.py
- [x] T029 [P] [US1] Create Assessment model (respondent_id, token_hash, selected_type_ids, questions_snapshot, expires_at, status, completed_at) in backend/src/models/assessment.py
- [x] T030 [US1] Create Alembic migration for questionnaire_types, questions, question_options, respondents, assessments tables in backend/alembic/versions/
- [x] T031 [US1] Export all models in backend/src/models/__init__.py

#### Schemas

- [x] T032 [P] [US1] Create QuestionnaireType Pydantic schemas (Create, Update, Response) in backend/src/schemas/questionnaire_type.py
- [x] T033 [P] [US1] Create Question Pydantic schemas (Create, Update, Response) in backend/src/schemas/question.py
- [x] T034 [P] [US1] Create QuestionOption Pydantic schemas (Config, Response) in backend/src/schemas/question_option.py
- [x] T035 [P] [US1] Create Respondent Pydantic schemas (Create, Update, Response) in backend/src/schemas/respondent.py
- [x] T036 [P] [US1] Create Assessment Pydantic schemas (Create, Created, Response) in backend/src/schemas/assessment.py

#### Repositories

- [x] T037 [P] [US1] Create QuestionnaireTypeRepository with CRUD operations in backend/src/repositories/questionnaire_type.py
- [x] T038 [P] [US1] Create QuestionRepository with CRUD and list-by-type operations in backend/src/repositories/question.py
- [x] T039 [P] [US1] Create QuestionOptionRepository with set-options operation in backend/src/repositories/question_option.py
- [x] T040 [P] [US1] Create RespondentRepository with CRUD and search operations in backend/src/repositories/respondent.py
- [x] T041 [P] [US1] Create AssessmentRepository with create and find-by-token operations in backend/src/repositories/assessment.py

#### Services

- [x] T042 [US1] Implement SnapshotService to deep copy questions/options for assessment creation in backend/src/services/snapshot.py
- [x] T043 [US1] Implement TokenService to generate secure tokens and SHA-256 hashes in backend/src/services/token.py
- [x] T044 [US1] Implement AssessmentService (create assessment with snapshot, generate public URL) in backend/src/services/assessment.py

#### API Routes

- [x] T045 [US1] Create Admin API router structure in backend/src/api/admin/__init__.py
- [x] T046 [P] [US1] Implement POST/GET/PATCH /types endpoints in backend/src/api/admin/types.py
- [x] T047 [P] [US1] Implement POST/GET/PATCH /questions and PUT /questions/{id}/options endpoints in backend/src/api/admin/questions.py
- [x] T048 [P] [US1] Implement POST/GET/PATCH /respondents endpoints in backend/src/api/admin/respondents.py
- [x] T049 [US1] Implement POST/GET /assessments endpoints in backend/src/api/admin/assessments.py
- [x] T050 [US1] Register all admin routes with auth dependency in backend/src/main.py

**Checkpoint**: Admin can configure questionnaire and generate assessment links via API

---

## Phase 4: User Story 2 - Respondent Completes Assessment (Priority: P1) 🎯 MVP

**Goal**: Respondent accesses link, sees form in Mongolian Cyrillic, answers YES/NO questions with conditional comments/images, submits, and sees results

**Independent Test**: Access valid assessment URL, complete all questions with required fields, submit. Verify results page shows correct scores in Mongolian.

### Backend Implementation for User Story 2

#### Models

- [ ] T051 [P] [US2] Create Answer model (assessment_id, question_id, selected_option, comment, score_awarded) in backend/src/models/answer.py
- [ ] T052 [P] [US2] Create Attachment model (answer_id, storage_key, original_name, size_bytes, mime_type) in backend/src/models/attachment.py
- [ ] T053 [P] [US2] Create AssessmentScore model (assessment_id, type_id, raw_score, max_score, percentage, risk_rating) in backend/src/models/assessment_score.py
- [ ] T054 [US2] Create Alembic migration for answers, attachments, assessment_scores tables in backend/alembic/versions/

#### Schemas

- [ ] T055 [P] [US2] Create Answer Pydantic schemas (Input, Response) in backend/src/schemas/answer.py
- [ ] T056 [P] [US2] Create Attachment Pydantic schemas (Upload, Response) in backend/src/schemas/attachment.py
- [ ] T057 [P] [US2] Create public API schemas (AssessmentForm, SubmitRequest, SubmitResponse, TypeResult, OverallResult, ErrorResponse) in backend/src/schemas/public.py

#### Services

- [ ] T058 [US2] Implement ScoringService with type score and overall score calculation logic in backend/src/services/scoring.py
- [ ] T059 [US2] Implement SubmissionService (validate answers, check required fields, save answers, calculate scores) in backend/src/services/submission.py
- [ ] T060 [US2] Implement UploadService (validate image type/size, upload to S3, create attachment record) in backend/src/services/upload.py

#### API Routes

- [ ] T061 [US2] Create Public API router structure in backend/src/api/public/__init__.py
- [ ] T062 [US2] Implement GET /a/{token} endpoint (return form data or error status) with rate limiting in backend/src/api/public/assessment.py
- [ ] T063 [US2] Implement POST /a/{token}/upload endpoint (handle multipart image upload) with rate limiting in backend/src/api/public/assessment.py
- [ ] T064 [US2] Implement POST /a/{token}/submit endpoint (validate, score, return results) with rate limiting in backend/src/api/public/assessment.py
- [ ] T065 [US2] Register public routes in backend/src/main.py

### Frontend Implementation for User Story 2

#### Core Setup

- [ ] T066 [P] [US2] Create Mongolian string constants file in frontend/src/constants/mn.ts
- [ ] T067 [P] [US2] Create Zod validation schemas for form data in frontend/src/schemas/assessment.ts

#### Components

- [ ] T068 [P] [US2] Create ProgressBar component showing "X / Y асуулт" in frontend/src/components/ProgressBar.tsx
- [ ] T069 [P] [US2] Create QuestionCard component with YES/NO buttons ("Тийм" / "Үгүй") in frontend/src/components/QuestionCard.tsx
- [ ] T070 [P] [US2] Create CommentField component with character counter (max 2000) in frontend/src/components/CommentField.tsx
- [ ] T071 [P] [US2] Create ImageUpload component with drag-drop, preview, and progress in frontend/src/components/ImageUpload.tsx
- [ ] T072 [P] [US2] Create TypeScoreCard component for displaying per-type results in frontend/src/components/TypeScoreCard.tsx
- [ ] T073 [P] [US2] Create OverallScoreCard component for displaying overall result in frontend/src/components/OverallScoreCard.tsx

#### Pages

- [ ] T074 [US2] Create AssessmentForm page with react-hook-form, conditional fields, validation in frontend/src/pages/AssessmentForm.tsx
- [ ] T075 [US2] Create Results page displaying type scores and overall score with risk ratings in frontend/src/pages/Results.tsx
- [ ] T076 [P] [US2] Create ExpiredLink page showing "Линкний хугацаа дууссан байна." in frontend/src/pages/ExpiredLink.tsx
- [ ] T077 [P] [US2] Create UsedLink page showing "Энэ линк аль хэдийн ашиглагдсан байна." in frontend/src/pages/UsedLink.tsx
- [ ] T078 [P] [US2] Create NotFound page for invalid tokens in frontend/src/pages/NotFound.tsx

#### Hooks and Services

- [ ] T079 [US2] Create useAssessment hook to fetch form data and handle loading/error states in frontend/src/hooks/useAssessment.ts
- [ ] T080 [US2] Create useUpload hook to handle image upload with progress tracking in frontend/src/hooks/useUpload.ts
- [ ] T081 [US2] Create assessment API service (getForm, uploadImage, submit) in frontend/src/services/assessment.ts

#### Routing

- [ ] T082 [US2] Configure routes for /a/:token (form), /a/:token/results, error pages in frontend/src/App.tsx

#### Styling

- [ ] T083 [US2] Apply mobile-first responsive styles to all components in frontend/src/index.css
- [ ] T084 [US2] Implement dark/light mode toggle with system preference detection in frontend/src/hooks/useTheme.ts

**Checkpoint**: Full respondent flow works - access link, complete form, see results

---

## Phase 5: User Story 3 - Admin Configures Questionnaire Types (Priority: P2)

**Goal**: Admin can create, update, and deactivate questionnaire types with full CRUD operations

**Independent Test**: Create type via API, update thresholds, deactivate it. Verify type is excluded from new assessments but historical data intact.

### Implementation for User Story 3

- [ ] T085 [US3] Add list types endpoint with pagination and is_active filter in backend/src/api/admin/types.py
- [ ] T086 [US3] Add get single type endpoint in backend/src/api/admin/types.py
- [ ] T087 [US3] Ensure deactivated types are excluded from assessment creation validation in backend/src/services/assessment.py

**Checkpoint**: Full questionnaire type management available via API

---

## Phase 6: User Story 4 - Admin Configures Questions and Options (Priority: P2)

**Goal**: Admin can create questions with YES/NO options, configure conditional requirements

**Independent Test**: Create question with options where NO requires comment (min 50 chars) and image. Verify conditional fields appear in public form.

### Implementation for User Story 4

- [ ] T088 [US4] Add list questions endpoint with pagination and type_id filter in backend/src/api/admin/questions.py
- [ ] T089 [US4] Add get single question endpoint including options in backend/src/api/admin/questions.py
- [ ] T090 [US4] Add validation for option configurations (exactly YES and NO required) in backend/src/schemas/question_option.py

**Checkpoint**: Full question and option configuration available via API

---

## Phase 7: User Story 5 - Admin Retrieves Assessment Results (Priority: P2)

**Goal**: Admin can retrieve assessment results with per-type scores, overall score, and optional answer breakdown

**Independent Test**: Complete an assessment, fetch results via API with breakdown=true. Verify all scores, ratings, and answer details returned.

### Implementation for User Story 5

- [ ] T091 [US5] Create AssessmentResults Pydantic schema with TypeScore, OverallScore, AnswerBreakdown in backend/src/schemas/results.py
- [ ] T092 [US5] Implement ResultsService to format scores and optionally include answer breakdown in backend/src/services/results.py
- [ ] T093 [US5] Implement GET /assessments/{id}/results endpoint with breakdown query param in backend/src/api/admin/assessments.py

**Checkpoint**: Full assessment results retrieval available via API

---

## Phase 8: User Story 6 - Admin Manages Respondents (Priority: P3)

**Goal**: Admin can create and manage respondent records (ORG or PERSON types)

**Independent Test**: Create respondents of both types, update details, verify they appear in assessment selection.

### Implementation for User Story 6

- [ ] T094 [US6] Add list respondents endpoint with pagination, kind filter, and name search in backend/src/api/admin/respondents.py
- [ ] T095 [US6] Add get single respondent endpoint in backend/src/api/admin/respondents.py
- [ ] T096 [US6] Add update respondent endpoint in backend/src/api/admin/respondents.py

**Checkpoint**: Full respondent management available via API

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T097 [P] Add OpenAPI documentation customization (title, description, tags) in backend/src/main.py
- [ ] T098 [P] Add request logging middleware in backend/src/core/logging.py
- [ ] T099 [P] Add health check endpoint in backend/src/api/health.py
- [ ] T100 [P] Create backend Dockerfile with multi-stage build in backend/Dockerfile
- [ ] T101 [P] Create frontend Dockerfile with nginx in frontend/Dockerfile
- [ ] T102 Update docker-compose.yml to include backend and frontend services
- [ ] T103 [P] Add input sanitization for Mongolian text fields in backend/src/core/validators.py
- [ ] T104 [P] Add WCAG AA contrast verification for UI components
- [ ] T105 Run quickstart.md validation - verify all setup steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
        │
        ├─────────────────────────────────┐
        │                                 │
        ▼                                 ▼
   US1 (Phase 3)                    US6 (Phase 8)*
   Admin Creates Assessment         Admin Manages Respondents
        │                                 │
        │                                 │ (can be parallel)
        ▼                                 │
   US2 (Phase 4)  ◄───────────────────────┘
   Respondent Completes
        │
        ├───────────────┬─────────────────┐
        │               │                 │
        ▼               ▼                 ▼
   US3 (Phase 5)   US4 (Phase 6)    US5 (Phase 7)
   Config Types    Config Questions  Get Results
```

*Note: US3, US4, US6 are configuration stories that logically belong before US1, but US1 includes minimal CRUD to be independently testable. These later phases add full CRUD features.

### Within Each User Story

- Models before schemas
- Schemas before repositories
- Repositories before services
- Services before API routes
- Backend before frontend (for US2)

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# All [P] tasks can run in parallel:
T003, T004, T005, T006, T008, T009 # After T001, T002
```

**Phase 2 (Foundational)**:
```bash
# After T010, T011:
T012, T013, T017, T018, T019, T020, T021, T022, T023, T024
```

**Phase 3 (US1 - Models)**:
```bash
# Models can be created in parallel:
T025, T026, T027, T028, T029
```

**Phase 3 (US1 - Schemas)**:
```bash
# After models, schemas in parallel:
T032, T033, T034, T035, T036
```

**Phase 3 (US1 - Repositories)**:
```bash
# After schemas, repositories in parallel:
T037, T038, T039, T040, T041
```

**Phase 4 (US2 - Backend Models)**:
```bash
T051, T052, T053 # In parallel
```

**Phase 4 (US2 - Frontend Components)**:
```bash
# All components can be developed in parallel:
T068, T069, T070, T071, T072, T073, T076, T077, T078
```

---

## Parallel Example: User Story 1 Models

```bash
# Launch all models for User Story 1 together:
Task: "Create QuestionnaireType model in backend/src/models/questionnaire_type.py"
Task: "Create Question model in backend/src/models/question.py"
Task: "Create QuestionOption model in backend/src/models/question_option.py"
Task: "Create Respondent model in backend/src/models/respondent.py"
Task: "Create Assessment model in backend/src/models/assessment.py"
```

## Parallel Example: User Story 2 Frontend Components

```bash
# Launch all frontend components in parallel:
Task: "Create ProgressBar component in frontend/src/components/ProgressBar.tsx"
Task: "Create QuestionCard component in frontend/src/components/QuestionCard.tsx"
Task: "Create CommentField component in frontend/src/components/CommentField.tsx"
Task: "Create ImageUpload component in frontend/src/components/ImageUpload.tsx"
Task: "Create TypeScoreCard component in frontend/src/components/TypeScoreCard.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Admin Creates Assessment)
4. Complete Phase 4: User Story 2 (Respondent Completes Assessment)
5. **STOP and VALIDATE**: Test full flow end-to-end
6. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test admin API → Demo admin flow
3. Add User Story 2 → Test full flow → Deploy MVP!
4. Add User Stories 3, 4, 5, 6 → Enhance admin capabilities
5. Add Polish → Production ready

### Parallel Team Strategy

With multiple developers:

**Developer A (Backend)**:
- Phase 1-2: Setup + Foundational
- Phase 3: US1 backend
- Phase 4: US2 backend
- Phase 5-8: Remaining backend

**Developer B (Frontend)**:
- Phase 1-2: Frontend setup
- Phase 4: US2 frontend (after backend models ready)
- Phase 9: Polish frontend

---

## Task Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| Phase 1 | Setup | 9 | 7 |
| Phase 2 | Foundational | 15 | 11 |
| Phase 3 | US1 - Admin Creates Assessment | 26 | 18 |
| Phase 4 | US2 - Respondent Completes | 34 | 17 |
| Phase 5 | US3 - Config Types | 3 | 0 |
| Phase 6 | US4 - Config Questions | 3 | 0 |
| Phase 7 | US5 - Get Results | 3 | 0 |
| Phase 8 | US6 - Manage Respondents | 3 | 0 |
| Phase 9 | Polish | 9 | 7 |
| **Total** | | **105** | **60** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = Phase 1-4 (Setup + Foundational + US1 + US2)
