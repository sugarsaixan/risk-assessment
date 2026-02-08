# Tasks: Risk Score Calculation & Grading

**Input**: Design documents from `/specs/006-risk-score-calculation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup

**Purpose**: Database migration and shared scoring utilities

- [x] T001 Create Alembic migration to add nullable columns to `assessment_scores` table: `classification_label` (VARCHAR(20)), `probability_score` (DECIMAL(8,4)), `consequence_score` (DECIMAL(8,4)), `risk_value` (INTEGER), `risk_grade` (VARCHAR(3)), `risk_description` (VARCHAR(100)), `insurance_decision` (VARCHAR(20)) in backend/alembic/versions/
- [x] T002 Add new nullable columns to the SQLAlchemy model in backend/src/models/assessment_score.py matching the migration: classification_label (String(20)), probability_score (Numeric(8,4)), consequence_score (Numeric(8,4)), risk_value (Integer), risk_grade (String(3)), risk_description (String(100)), insurance_decision (String(20)) — all nullable

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core scoring functions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Implement group classification function in backend/src/services/scoring.py — a pure function `classify_group(sum_score: int) -> tuple[str, int]` that maps sum score to (classification_label, numeric_value): 0→("Хэвийн",1), 1→("Хянахуйц",2), 2→("Анхаарах",3), 3→("Ноцтой",4), ≥4→("Аюултай",5)
- [x] T004 Implement grade lookup function in backend/src/services/scoring.py — a pure function `lookup_grade(risk_value: int) -> tuple[str, str]` that returns (grade, description) using the grade table: 1→("AAA","Эрсдэл маш бага"), 2-3→("AA","Эрсдэл бага"), 4→("A","Анхаарахгүй, эрсдэл бага"), 5→("BBB","Нийцэхүйц, эрсдэл доогуур"), 6→("BB","Авахуйц, эрсдэл доогуур"), 7-9→("B","Хянахуйц, эрсдэл доогуур"), 10-11→("CCC","Хянахуйц, эрсдэл дунд"), 12-14→("CC","Анхаарах, эрсдэл дунд"), 15→("C","Нэн анхаарах, эрсдэл дунд"), 16→("DDD","Ноцтой, эрсдэл дээгүүр"), 17-20→("DD","Нэн ноцтой, эрсдэл дээгүүр"), ≥21→("D","Аюултай, эрсдэл өндөр")
- [x] T005 Implement helper function `safe_stdev(values: list[float]) -> float` in backend/src/services/scoring.py — returns `statistics.stdev(values)` when len(values) > 1, else returns 0.0. Also implement `round_half_up(value: float) -> int` using `Decimal` with `ROUND_HALF_UP` for spec-compliant rounding
- [x] T006 [P] Add new fields to backend Pydantic schemas in backend/src/schemas/results.py — extend `GroupScore` with `sum_score: int | None = None` and `classification_label: str | None = None`; extend `TypeScore` with `probability_score: float | None = None`, `consequence_score: float | None = None`, `risk_value: int | None = None`, `risk_grade: str | None = None`, `risk_description: str | None = None`; extend `OverallScore` with `total_risk: int | None = None`, `total_grade: str | None = None`, `risk_description: str | None = None`, `insurance_decision: str | None = None`
- [x] T007 [P] Add new fields to public API schemas in backend/src/schemas/public.py — mirror the same new fields from T006 into `GroupResult`, `TypeResult`, `OverallResult` (all Optional/nullable for backward compatibility)
- [x] T008 [P] Add new fields to frontend TypeScript types in frontend/src/types/api.ts — extend `GroupResult` with `sum_score?: number` and `classification_label?: string`; extend `TypeResult` with `probability_score?: number`, `consequence_score?: number`, `risk_value?: number`, `risk_grade?: string`, `risk_description?: string`; extend `OverallResult` with `total_risk?: number`, `total_grade?: string`, `risk_description?: string`, `insurance_decision?: string`

**Checkpoint**: Foundation ready — database columns added, pure scoring functions implemented, schemas extended. User story implementation can now begin.

---

## Phase 3: User Story 1 — Group-Level Risk Classification (Priority: P1) 🎯 MVP

**Goal**: Each question group gets a sum score and Mongolian classification label (Хэвийн through Аюултай)

**Independent Test**: Submit an assessment and verify each group shows its sum score and correct classification label

### Implementation for User Story 1

- [x] T009 [US1] Update `calculate_group_score()` in backend/src/services/scoring.py — after calculating raw_score, compute `sum_score` as the count of score_awarded values > 0 (or sum of score_awarded if each contributes 0/1), then call `classify_group(sum_score)` to get classification_label and numeric_value. Include both in the returned dict alongside existing fields
- [x] T010 [US1] Update `save_scores()` in backend/src/services/scoring.py — when saving group-level AssessmentScore records, populate the new `classification_label` column from the group score dict
- [x] T011 [US1] Update `get_results()` in backend/src/services/results.py — when building GroupScore objects from database records, include `sum_score` (from raw_score) and `classification_label` from the new DB column. Handle NULL gracefully for old assessments
- [x] T012 [US1] Update `TypeScoreCard` group breakdown in frontend/src/components/TypeScoreCard.tsx — for each group row, display `classification_label` as a colored badge next to the group name (use the group's classification to determine color: Хэвийн→green, Хянахуйц→blue, Анхаарах→yellow, Ноцтой→orange, Аюултай→red). Show `sum_score` value. Gracefully hide new elements if classification_label is null (old assessments)

**Checkpoint**: User Story 1 complete — each group shows sum score and Mongolian classification label on the result page.

---

## Phase 4: User Story 2 — Probability & Consequence Scores per Type (Priority: P2)

**Goal**: Each type calculates probability score (МАГАДЛАЛЫН ОНОО) and consequence score (ҮР ДАГАВРЫН ОНОО) from its group data

**Independent Test**: Create assessment with known group scores, verify probability and consequence scores match AVERAGE + 0.618 × STDEV.S formula

### Implementation for User Story 2

- [x] T013 [US2] Update `calculate_type_score()` in backend/src/services/scoring.py — after computing group scores, collect group sum_scores and group numeric_values (from classify_group). Calculate: `probability_score = mean(sum_scores) + 0.618 * safe_stdev(sum_scores)` and `consequence_score = mean(numeric_values) + 0.618 * safe_stdev(numeric_values)`. Add both to the type score dict
- [x] T014 [US2] Update `save_scores()` in backend/src/services/scoring.py — when saving type-level AssessmentScore records, populate `probability_score` and `consequence_score` columns
- [x] T015 [US2] Update `get_results()` in backend/src/services/results.py — when building TypeScore objects, include `probability_score` and `consequence_score` from the new DB columns. Handle NULL for old assessments
- [x] T016 [US2] Update `TypeScoreCard` header in frontend/src/components/TypeScoreCard.tsx — display probability score (МАГАДЛАЛЫН ОНОО) and consequence score (ҮР ДАГАВРЫН ОНОО) as labeled values in the type card header area. Format to 2 decimal places. Gracefully hide if null

**Checkpoint**: User Story 2 complete — each type shows probability and consequence scores on the result page.

---

## Phase 5: User Story 3 — Per-Type Risk Value and Grade (Priority: P3)

**Goal**: Each type calculates ЭРСДЭЛ (probability × consequence), gets a letter grade (AAA–D), and Mongolian description

**Independent Test**: Verify type risk values, grades, and descriptions match the grade lookup table

### Implementation for User Story 3

- [x] T017 [US3] Update `calculate_type_score()` in backend/src/services/scoring.py — after computing probability_score and consequence_score, calculate `risk_value = round_half_up(probability_score * consequence_score)`, then `(risk_grade, risk_description) = lookup_grade(risk_value)`. Add risk_value, risk_grade, risk_description to the type score dict
- [x] T018 [US3] Update `save_scores()` in backend/src/services/scoring.py — when saving type-level AssessmentScore records, populate `risk_value`, `risk_grade`, `risk_description` columns
- [x] T019 [US3] Update `get_results()` in backend/src/services/results.py — when building TypeScore objects, include risk_value, risk_grade, risk_description. Handle NULL for old assessments
- [x] T020 [US3] Update `TypeScoreCard` in frontend/src/components/TypeScoreCard.tsx — display risk value (ЭРСДЭЛ), risk grade as a prominently colored badge (AAA–A→green, BBB–B→yellow, CCC–C→orange, DDD–D→red), and risk description text. Gracefully hide if null

**Checkpoint**: User Story 3 complete — each type shows its risk value, letter grade, and description.

---

## Phase 6: User Story 4 — Overall Risk Aggregation & Insurance Decision (Priority: P4)

**Goal**: НИЙТ ЭРСДЭЛ aggregated from type risk values, НИЙТ ЗЭРЭГЛЭЛ from grade table, ДААТГАХ ЭСЭХ insurance decision

**Independent Test**: Create assessment with multiple types having known risk values, verify overall risk, grade, and insurance decision

### Implementation for User Story 4

- [x] T021 [US4] Update `calculate_overall_score()` in backend/src/services/scoring.py — collect all type risk_values, compute `total_risk = round_half_up(mean(type_risk_values) + 0.618 * safe_stdev(type_risk_values))`, then `(total_grade, risk_description) = lookup_grade(total_risk)`, then `insurance_decision = "Даатгахгүй" if total_risk > 16 else "Даатгана"`. Add total_risk, total_grade (as risk_grade), risk_description, insurance_decision to the overall score dict. Keep existing raw_score/max_score/percentage/risk_rating calculations for backward compatibility
- [x] T022 [US4] Update `save_scores()` in backend/src/services/scoring.py — when saving the overall AssessmentScore record (type_id=NULL, group_id=NULL), populate `risk_value` (total_risk), `risk_grade` (total_grade), `risk_description`, `insurance_decision` columns
- [x] T023 [US4] Update `get_results()` in backend/src/services/results.py — when building OverallScore object, include total_risk, total_grade, risk_description, insurance_decision from the DB record. Handle NULL for old assessments
- [x] T024 [US4] Update `OverallScoreCard` in frontend/src/components/OverallScoreCard.tsx — redesign the main display to prominently show: НИЙТ ЭРСДЭЛ (total risk value as large number), НИЙТ ЗЭРЭГЛЭЛ (letter grade as colored badge), risk description (Mongolian text), and ДААТГАХ ЭСЭХ (insurance decision with positive/negative visual indicator: green "Даатгана" or red "Даатгахгүй"). Keep old display as fallback when new fields are null

**Checkpoint**: User Story 4 complete — overall section shows НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, description, and insurance decision.

---

## Phase 7: User Story 5 — Updated Result Page Display (Priority: P5)

**Goal**: Full result page layout update with complete scoring hierarchy and grade-based color-coding

**Independent Test**: View result page for a completed assessment and verify all new fields visible with correct formatting and colors

### Implementation for User Story 5

- [x] T025 [US5] Update result page layout in frontend/src/pages/Results.tsx — restructure the page to display the full hierarchy: overall risk card at top (НИЙТ ЭРСДЭЛ, grade, insurance), then per-type cards (each with probability, consequence, risk value, grade), then expandable per-group rows (each with sum score and classification). Ensure the summary section at bottom reflects the new scoring model. Remove or deprecate old percentage-centric display elements for new assessments (keep as fallback when new fields are null)
- [x] T026 [US5] Implement grade-based color utility — create a shared color mapping function used by all components: AAA/AA/A→green palette (e.g., green-100/green-600), BBB/BB/B→yellow palette (yellow-100/yellow-600), CCC/CC/C→orange palette (orange-100/orange-600), DDD/DD/D→red palette (red-100/red-600). Can be a simple helper in frontend/src/utils/gradeColors.ts or inline in components
- [x] T027 [US5] Apply consistent color-coding across all grade badges in OverallScoreCard, TypeScoreCard, and group classification labels in frontend/src/components/OverallScoreCard.tsx, frontend/src/components/TypeScoreCard.tsx — ensure all grade displays use the shared color mapping from T026

**Checkpoint**: User Story 5 complete — full result page displays complete scoring hierarchy with color-coded grades.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T028 Verify backward compatibility — test that viewing results for an existing (old) completed assessment still renders correctly with old-style display (null new fields handled gracefully)
- [x] T029 Run full quickstart.md validation — test the complete scoring pipeline end-to-end with a fresh assessment submission, verify all calculated values match expected formulas

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T001, T002 must complete first for T003-T005; T006-T008 can run in parallel with T003-T005)
- **User Stories (Phase 3-7)**: All depend on Phase 2 completion
  - US1 (Phase 3): Can start after Phase 2
  - US2 (Phase 4): Depends on US1 (uses group sum_scores and classify_group from US1's scoring changes)
  - US3 (Phase 5): Depends on US2 (uses probability_score and consequence_score from US2)
  - US4 (Phase 6): Depends on US3 (uses per-type risk_values from US3)
  - US5 (Phase 7): Depends on US4 (displays all fields from all prior stories)
- **Polish (Phase 8)**: Depends on all user stories

### Within Each User Story

- Backend scoring logic → Backend save/results → Frontend display
- Each story builds on the prior story's scoring calculations

### Parallel Opportunities

- T006, T007, T008 can all run in parallel (different files, schema-only changes)
- T003 and T004 can run in parallel (independent pure functions in same file, different function signatures)
- Within each story: backend schema mapping (results.py) and frontend display can be parallelized once scoring logic is done

---

## Parallel Example: Phase 2 (Foundational)

```text
# After T001, T002 complete:

# Parallel batch 1 — pure functions (same file but independent):
Task T003: classify_group() in backend/src/services/scoring.py
Task T004: lookup_grade() in backend/src/services/scoring.py
Task T005: safe_stdev() + round_half_up() in backend/src/services/scoring.py

# Parallel batch 2 — schema changes (different files):
Task T006: backend/src/schemas/results.py
Task T007: backend/src/schemas/public.py
Task T008: frontend/src/types/api.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migration + model)
2. Complete Phase 2: Foundational (pure functions + schemas)
3. Complete Phase 3: User Story 1 (group classification)
4. **STOP and VALIDATE**: Verify groups show classification labels
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (group classification) → Test → Deploy (MVP!)
3. Add US2 (probability/consequence) → Test → Deploy
4. Add US3 (per-type risk/grade) → Test → Deploy
5. Add US4 (overall risk + insurance) → Test → Deploy
6. Add US5 (full page layout + colors) → Test → Deploy
7. Each story adds a visible layer to the result page

### Sequential Execution (Single Developer)

Stories MUST be done in order (US1 → US2 → US3 → US4 → US5) because each calculation layer depends on the previous one.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User stories are **sequential** (not parallelizable) because each calculation layer builds on the prior
- All new DB columns are nullable for backward compatibility
- Frontend components must gracefully handle null (old assessments show old-style display)
- STDEV.S with N≤1 guard → returns 0
- Rounding uses ROUND_HALF_UP via Decimal
- Commit after each task or logical group
