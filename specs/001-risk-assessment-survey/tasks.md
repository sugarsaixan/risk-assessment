# Tasks: Risk Assessment Survey System (Updated)

**Input**: Design documents from `/specs/001-risk-assessment-survey/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec. Tests are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Note**: Main branch UI has been merged. This update adds Question Groups (Бүлэг) and Submission Contact (Хариулагч) entities.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md in backend/
- [x] T002 Create frontend directory structure per plan.md in frontend/
- [x] T003 [P] Initialize Python project with FastAPI, SQLAlchemy, Pydantic in backend/pyproject.toml
- [x] T004 [P] Initialize React project with Vite, TypeScript, TailwindCSS in frontend/package.json
- [x] T005 [P] Configure Python linting (ruff) and formatting in backend/pyproject.toml
- [x] T006 [P] Configure TypeScript strict mode and ESLint in frontend/tsconfig.json
- [x] T007 Create docker-compose.yml with PostgreSQL and MinIO services at project root
- [x] T008 [P] Configure TailwindCSS with dark mode in frontend/tailwind.config.js
- [x] T009 [P] Create backend environment configuration loader in backend/src/core/config.py

**Checkpoint**: Project skeleton ready, dependencies installed ✅

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T010 Create SQLAlchemy async engine and session factory in backend/src/core/database.py
- [x] T011 Initialize Alembic with async support in backend/alembic/
- [x] T012 [P] Create database enum types in backend/src/models/enums.py
- [x] T013 [P] Create base SQLAlchemy model with UUID primary key in backend/src/models/base.py
- [x] T014 Create ApiKey model in backend/src/models/api_key.py
- [x] T015 Create initial Alembic migration for api_keys table
- [x] T016 Implement API key authentication in backend/src/core/auth.py
- [x] T017 [P] Create FastAPI app instance in backend/src/main.py
- [x] T018 [P] Configure slowapi rate limiter in backend/src/core/rate_limit.py
- [x] T019 [P] Create S3/MinIO client in backend/src/core/storage.py
- [x] T020 [P] Create base Pydantic schemas in backend/src/schemas/common.py
- [x] T021 [P] Create CLI command to generate API keys in backend/src/cli.py
- [x] T022 [P] Create React app entry point in frontend/src/main.tsx
- [x] T023 [P] Create API client service in frontend/src/services/api.ts
- [x] T024 [P] Create TypeScript type definitions in frontend/src/types/api.ts

**Checkpoint**: Foundation ready ✅

---

## Phase 3: User Story 1 - Admin Creates Assessment Link (Priority: P1) 🎯 MVP

**Goal**: Admin can create questionnaire types, groups, questions with options, respondents, and generate one-time assessment links

**Independent Test**: Call Admin API to create type → group → questions → options → respondent → assessment. Verify returned URL contains valid token format.

### Implementation for User Story 1

#### Backend Models (Existing + New)

- [x] T025 [P] [US1] Create QuestionnaireType model in backend/src/models/questionnaire_type.py
- [x] T025a [P] [US1] **NEW**: Create QuestionGroup model (type_id, name, display_order, weight, is_active) in backend/src/models/question_group.py
- [x] T026 [P] [US1] Update Question model to reference group_id instead of type_id in backend/src/models/question.py
- [x] T027 [P] [US1] Create QuestionOption model in backend/src/models/question_option.py
- [x] T028 [P] [US1] Create Respondent model in backend/src/models/respondent.py
- [x] T029 [P] [US1] Update Assessment model to include groups in snapshot in backend/src/models/assessment.py
- [x] T030a [US1] **NEW**: Create Alembic migration to add question_groups table in backend/alembic/versions/
- [x] T030b [US1] **NEW**: Create Alembic migration to change questions.type_id → questions.group_id in backend/alembic/versions/
- [x] T031a [US1] Export QuestionGroup model in backend/src/models/__init__.py

#### Backend Schemas (Existing + New)

- [x] T032 [P] [US1] Create QuestionnaireType Pydantic schemas in backend/src/schemas/questionnaire_type.py
- [x] T032a [P] [US1] **NEW**: Create QuestionGroup Pydantic schemas (Create, Update, Response) in backend/src/schemas/question_group.py
- [x] T033a [P] [US1] Update Question schemas to use group_id in backend/src/schemas/question.py
- [x] T034 [P] [US1] Create QuestionOption Pydantic schemas in backend/src/schemas/question_option.py
- [x] T035 [P] [US1] Create Respondent Pydantic schemas in backend/src/schemas/respondent.py
- [x] T036 [P] [US1] Update Assessment schemas to include groups in snapshot in backend/src/schemas/assessment.py

#### Backend Repositories (Existing + New)

- [x] T037 [P] [US1] Create QuestionnaireTypeRepository in backend/src/repositories/questionnaire_type.py
- [x] T037a [P] [US1] **NEW**: Create QuestionGroupRepository with CRUD and list-by-type in backend/src/repositories/question_group.py
- [x] T038a [P] [US1] Update QuestionRepository to filter by group_id in backend/src/repositories/question.py
- [x] T039 [P] [US1] Create QuestionOptionRepository in backend/src/repositories/question_option.py
- [x] T040 [P] [US1] Create RespondentRepository in backend/src/repositories/respondent.py
- [x] T041 [P] [US1] Create AssessmentRepository in backend/src/repositories/assessment.py

#### Backend Services

- [x] T042a [US1] Update SnapshotService to include groups in Type → Group → Question hierarchy in backend/src/services/snapshot.py
- [x] T043 [US1] Implement TokenService in backend/src/services/token.py
- [x] T044 [US1] Implement AssessmentService in backend/src/services/assessment.py

#### Backend API Routes (Existing + New)

- [x] T045 [US1] Create Admin API router structure in backend/src/api/admin/__init__.py
- [x] T046 [P] [US1] Implement /types endpoints in backend/src/api/admin/types.py
- [x] T046a [P] [US1] **NEW**: Implement POST/GET/PATCH /groups endpoints in backend/src/api/admin/groups.py
- [x] T047a [P] [US1] Update /questions endpoints to use group_id filter in backend/src/api/admin/questions.py
- [x] T048 [P] [US1] Implement /respondents endpoints in backend/src/api/admin/respondents.py
- [x] T049 [US1] Implement /assessments endpoints in backend/src/api/admin/assessments.py
- [x] T050a [US1] Register groups routes in backend/src/main.py

**Checkpoint**: Admin can configure questionnaire hierarchy and generate assessment links via API

---

## Phase 4: User Story 2 - Respondent Completes Assessment (Priority: P1) 🎯 MVP

**Goal**: Respondent accesses link, sees form with Type→Group→Question hierarchy, answers YES/NO questions, enters contact info, submits, and sees hierarchical results

**Independent Test**: Access valid assessment URL, complete all questions, enter contact info (Овог, Нэр, email, phone, Албан тушаал), submit. Verify results page shows per-group, per-type, and overall scores.

### Backend Implementation for User Story 2

#### Backend Models (Existing + New)

- [x] T051 [P] [US2] Create Answer model in backend/src/models/answer.py
- [x] T052 [P] [US2] Create Attachment model in backend/src/models/attachment.py
- [x] T053a [P] [US2] Update AssessmentScore model to include group_id for group-level scores in backend/src/models/assessment_score.py
- [x] T053b [P] [US2] **NEW**: Create SubmissionContact model (assessment_id, last_name, first_name, email, phone, position) in backend/src/models/submission_contact.py
- [x] T054a [US2] Create Alembic migration for submission_contacts table in backend/alembic/versions/
- [x] T054b [US2] Create Alembic migration to add group_id to assessment_scores table in backend/alembic/versions/

#### Backend Schemas (Existing + New)

- [x] T055 [P] [US2] Create Answer Pydantic schemas in backend/src/schemas/answer.py
- [x] T056 [P] [US2] Create Attachment Pydantic schemas in backend/src/schemas/attachment.py
- [x] T057a [P] [US2] **NEW**: Create SubmissionContact Pydantic schemas (Input, Response) in backend/src/schemas/submission_contact.py
- [x] T057b [P] [US2] Update public API schemas to include contact input and group results in backend/src/schemas/public.py

#### Backend Services

- [x] T058a [US2] **UPDATE**: Implement hierarchical ScoringService (Question→Group→Type→Overall) in backend/src/services/scoring.py
- [x] T059a [US2] Update SubmissionService to save submission contact and calculate group scores in backend/src/services/submission.py
- [x] T060 [US2] Implement UploadService in backend/src/services/upload.py

#### Backend API Routes

- [x] T061 [US2] Create Public API router structure in backend/src/api/public/__init__.py
- [x] T062a [US2] Update GET /a/{token} to return Type→Group→Question hierarchy in backend/src/api/public/assessment.py
- [x] T063 [US2] Implement POST /a/{token}/upload endpoint in backend/src/api/public/assessment.py
- [x] T064a [US2] Update POST /a/{token}/submit to require contact info and return group scores in backend/src/api/public/assessment.py
- [x] T065 [US2] Register public routes in backend/src/main.py

### Frontend Implementation for User Story 2 (UI from main branch)

#### Frontend Types and Schemas

- [x] T066a [P] [US2] Update TypeScript types to include QuestionGroup and SubmissionContact in frontend/src/types/api.ts
- [x] T067a [P] [US2] Update Zod schemas to include contact validation in frontend/src/schemas/assessment.ts

#### Frontend Components (Update existing)

- [x] T068 [P] [US2] ProgressBar component exists in frontend/src/components/ProgressBar.tsx
- [x] T069a [P] [US2] Update QuestionCard to render within group context in frontend/src/components/QuestionCard.tsx
- [x] T070 [P] [US2] CommentField component exists in frontend/src/components/CommentField.tsx
- [x] T071 [P] [US2] ImageUpload component exists in frontend/src/components/ImageUpload.tsx
- [x] T072a [P] [US2] Update TypeScoreCard to show group scores within type in frontend/src/components/TypeScoreCard.tsx
- [x] T073 [P] [US2] OverallScoreCard component exists in frontend/src/components/OverallScoreCard.tsx
- [x] T073a [P] [US2] **NEW**: Create ContactForm component for submission contact info in frontend/src/components/ContactForm.tsx

#### Frontend Pages (Update existing)

- [x] T074a [US2] Update AssessmentForm to display Type→Group→Question hierarchy and include ContactForm in frontend/src/pages/AssessmentForm.tsx
- [x] T075a [US2] Update Results page to display group scores within types in frontend/src/pages/Results.tsx
- [x] T076 [P] [US2] ExpiredLink page exists in frontend/src/pages/ExpiredLink.tsx
- [x] T077 [P] [US2] UsedLink page exists in frontend/src/pages/UsedLink.tsx
- [x] T078 [P] [US2] NotFound page exists in frontend/src/pages/NotFound.tsx

#### Frontend Hooks and Services

- [x] T079a [US2] Update useAssessment hook to handle hierarchical data in frontend/src/hooks/useAssessment.ts
- [x] T080 [US2] useUpload hook exists in frontend/src/hooks/useUpload.ts
- [x] T081a [US2] Update assessment service to include contact in submit request in frontend/src/services/assessment.ts

#### Frontend Routing (Existing)

- [x] T082 [US2] Routes configured in frontend/src/App.tsx

#### Frontend Styling (Existing)

- [x] T083 [US2] Mobile-first responsive styles in frontend/src/index.css
- [x] T084 [US2] Dark/light mode toggle in frontend/src/hooks/useTheme.tsx

**Checkpoint**: Full respondent flow works with hierarchical display and contact collection

---

## Phase 5: User Story 3 - Admin Configures Questionnaire Types and Groups (Priority: P2)

**Goal**: Admin can create, update, and deactivate questionnaire types and groups with full CRUD

**Independent Test**: Create type via API, add groups to type, update weights, deactivate group. Verify excluded from new assessments.

### Implementation for User Story 3

- [x] T085 [US3] List types endpoint with pagination exists in backend/src/api/admin/types.py
- [x] T086 [US3] Get single type endpoint exists in backend/src/api/admin/types.py
- [x] T086a [US3] **NEW**: Add list groups by type_id endpoint in backend/src/api/admin/groups.py
- [x] T086b [US3] **NEW**: Add get/update/deactivate group endpoints in backend/src/api/admin/groups.py
- [x] T087a [US3] Ensure deactivated groups are excluded from snapshots in backend/src/services/snapshot.py

**Checkpoint**: Full type and group management available via API

---

## Phase 6: User Story 4 - Admin Configures Questions and Options (Priority: P2)

**Goal**: Admin can create questions within groups with YES/NO options

**Independent Test**: Create question within group, configure options. Verify conditional fields appear in public form.

### Implementation for User Story 4

- [x] T088a [US4] Update list questions to filter by group_id in backend/src/api/admin/questions.py
- [x] T089 [US4] Get single question endpoint exists in backend/src/api/admin/questions.py
- [x] T090 [US4] Option validation exists in backend/src/schemas/question_option.py

**Checkpoint**: Full question and option configuration available via API

---

## Phase 7: User Story 5 - Admin Retrieves Assessment Results (Priority: P2)

**Goal**: Admin can retrieve assessment results with per-group, per-type scores, overall score, contact info, and optional breakdown

**Independent Test**: Complete assessment, fetch results via API. Verify group scores, type scores, overall score, and contact info returned.

### Implementation for User Story 5

- [x] T091a [US5] Update AssessmentResults schema to include GroupScore and SubmissionContact in backend/src/schemas/results.py
- [x] T092a [US5] Update ResultsService to include group scores and contact info in backend/src/services/results.py
- [x] T093a [US5] Update GET /assessments/{id}/results to return hierarchical scores and contact in backend/src/api/admin/assessments.py

**Checkpoint**: Full assessment results with hierarchical scores and contact info

---

## Phase 8: User Story 6 - Admin Manages Respondents (Priority: P3) ✅ COMPLETE

**Goal**: Admin can create and manage respondent records

- [x] T094 [US6] List respondents endpoint exists in backend/src/api/admin/respondents.py
- [x] T095 [US6] Get single respondent endpoint exists in backend/src/api/admin/respondents.py
- [x] T096 [US6] Update respondent endpoint exists in backend/src/api/admin/respondents.py

**Checkpoint**: Full respondent management available via API ✅

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T097 [P] OpenAPI documentation in backend/src/main.py
- [x] T098 [P] Request logging exists
- [x] T099 [P] Health check endpoint in backend/src/api/health.py
- [ ] T100 [P] Create backend Dockerfile in backend/Dockerfile
- [ ] T101 [P] Create frontend Dockerfile in frontend/Dockerfile
- [ ] T102 Update docker-compose.yml with all services
- [x] T103 [P] Input sanitization in backend/src/core/validators.py
- [x] T104 [P] WCAG AA contrast verification in frontend/src/utils/contrast.ts
- [ ] T105 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Setup (Phase 1) ✅
        │
        ▼
Foundational (Phase 2) ✅
        │
        ├─────────────────────────────────┐
        │                                 │
        ▼                                 ▼
   US1 (Phase 3)                    US6 (Phase 8) ✅
   + QuestionGroup                  Admin Manages Respondents
   + Updated Snapshot
        │
        ▼
   US2 (Phase 4)
   + SubmissionContact
   + Hierarchical Scoring
   + Contact Form UI
        │
        ├───────────────┬─────────────────┐
        │               │                 │
        ▼               ▼                 ▼
   US3 (Phase 5)   US4 (Phase 6)    US5 (Phase 7)
   Group CRUD      Question CRUD    Results w/Contact
```

### New Tasks Summary

| Category | New Tasks | Description |
|----------|-----------|-------------|
| QuestionGroup Model | T025a, T030a, T030b, T031a | New entity for question grouping |
| QuestionGroup Schema | T032a, T033a | Pydantic schemas |
| QuestionGroup Repository | T037a, T038a | CRUD operations |
| QuestionGroup API | T046a, T047a, T050a | Admin endpoints |
| SubmissionContact Model | T053b, T054a, T054b | New entity for form contact |
| SubmissionContact Schema | T057a, T057b | Pydantic schemas |
| Hierarchical Scoring | T053a, T058a, T059a | Group→Type→Overall calculation |
| Frontend Updates | T066a, T067a, T069a, T072a, T073a, T074a, T075a, T079a, T081a | UI for groups and contact |
| Group Admin | T086a, T086b, T087a, T088a | Full group management |
| Results Update | T091a, T092a, T093a | Include groups and contact in results |

---

## Implementation Priority

### Immediate (New Entities)

1. **T025a**: Create QuestionGroup model
2. **T053b**: Create SubmissionContact model
3. **T030a, T054a**: Database migrations
4. **T032a, T057a**: Pydantic schemas
5. **T037a**: QuestionGroup repository
6. **T046a**: Groups API endpoints

### Next (Update Existing)

1. **T026, T033a, T038a, T047a**: Update Question to use group_id
2. **T042a, T062a**: Update snapshot service and API
3. **T058a, T059a, T064a**: Hierarchical scoring and submission

### Then (Frontend)

1. **T073a**: ContactForm component
2. **T066a, T067a**: Types and schemas
3. **T074a, T075a**: Page updates

---

## Task Statistics

| Phase | Total | Complete | Remaining | New |
|-------|-------|----------|-----------|-----|
| Phase 1 | 9 | 9 | 0 | 0 |
| Phase 2 | 15 | 15 | 0 | 0 |
| Phase 3 | 26 | 17 | 9 | 9 |
| Phase 4 | 34 | 18 | 16 | 14 |
| Phase 5 | 3 | 2 | 1 | 3 |
| Phase 6 | 3 | 2 | 1 | 1 |
| Phase 7 | 3 | 0 | 3 | 3 |
| Phase 8 | 3 | 3 | 0 | 0 |
| Phase 9 | 9 | 5 | 4 | 0 |
| **Total** | **105** | **71** | **34** | **30** |

---

## Notes

- Main branch UI merged - existing components need updates, not creation
- QuestionGroup and SubmissionContact are new entities requiring full implementation
- Scoring logic must be updated to calculate: Questions → Groups → Types → Overall
- Frontend must NOT calculate scores - display backend results only
- All new migrations should be created incrementally, not modify existing
