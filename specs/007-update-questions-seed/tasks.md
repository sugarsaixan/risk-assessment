# Implementation Tasks: Questions Seed with Custom Scoring Format

**Feature Branch**: `007-update-questions-seed`
**Date**: 2026-02-08
**Status**: Ready for Implementation

## Overview

This document breaks down the implementation of the questions seed update feature into sequentially executable tasks. Tasks are organized by user story priority (P1 → P2 → P3) to enable incremental delivery and independent testing.

**Tech Stack**: Python 3.11+, SQLAlchemy 2.0 (async), asyncpg, pytest
**Project Type**: Backend-only module update
**Target Performance**: Complete seed operation in under 30 seconds

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **User Stories (Phases 2-3)**: Can run in parallel after Setup
  - US1 (Phase 2): Core parsing logic - implements custom scoring format
  - US2 (Phase 2): Seed script integration - database operations
  - US3 (Phase 3): Verification support - manual testing instructions
  - US4 (Phase 3): Edge case handling - error recovery
- **Polish (Phase 4)**: Depends on US1 and US2 completion

### Within Each Phase

- Implementation tasks run sequentially (tests → parsing → database → integration)
- Tasks marked [P] can run in parallel (different files, no dependencies)
- File-based coordination: Tasks affecting the same file must run sequentially

### Parallel Opportunities

- T003 and T004 can run in parallel (different test files)
- T010 and T011 can run in parallel after T009 (parsing helper functions)
- T015 and T016 can run in parallel (type and group creation functions)

---

## Phase 1: Setup

**Goal**: Prepare project structure and testing infrastructure

- [X] T001 Verify backend project structure and dependencies
  - Ensure `backend/src/seeds/questions_seed.py` exists
  - Verify Python 3.11+ environment
  - Check dependencies: SQLAlchemy 2.0, asyncpg, pytest, pytest-asyncio
  - Verify PostgreSQL database connection configured
  - Confirm existing models: QuestionnaireType, QuestionGroup, Question, QuestionOption

---

## Phase 2: User Story 1 - Developer Updates Question Format (P1)

**Goal**: Implement parsing logic for new markdown format with custom scoring

**Independent Test**: Create sample markdown file with new format, run parsing functions, verify extracted data matches expected structure (question text, option, score, hierarchy)

**Checkpoint**: Can parse any markdown file with new format and extract all question data correctly

- [X] T002 [P] [US1] Create type definitions for parsed data structures in backend/src/seeds/questions_seed.py
  - Add `ParsedQuestion` dataclass with fields: text, option_text, score
  - Add `ParsedGroup` dataclass with fields: name, questions (list)
  - Add `ParsedType` dataclass with fields: name, groups (list)
  - Add `ParsedQuestionData` dataclass with fields: types (list)
  - Add `SeedStats` dataclass with fields: types_created, groups_created, questions_created, options_created, errors

- [X] T003 [P] [US1] Create unit test file structure in backend/tests/unit/test_questions_seed.py
  - Create test file with pytest imports and fixtures
  - Add async session fixture for database tests
  - Add sample markdown test data fixtures

- [X] T004 [P] [US1] Create integration test file structure in backend/tests/integration/test_seed_integration.py
  - Create test file with pytest async configuration
  - Add database session fixtures
  - Add test markdown files in tests/fixtures/ directory

- [X] T005 [US1] Implement inverse scoring calculation function in backend/src/seeds/questions_seed.py
  - Create function `calculate_scores(option_text: str, score: int) -> tuple[int, int]`
  - Logic: if option_text == "Үгүй" and score == 1, return (1, 0)
  - Logic: if option_text == "Тийм" and score == 1, return (0, 1)
  - Logic: otherwise, return (0, 0)
  - Add docstring with examples and Mongolian option text handling

- [X] T006 [US1] Implement line parser function in backend/src/seeds/questions_seed.py
  - Create function `parse_question_line(line: str) -> tuple[str, str, int]`
  - Strip leading/trailing whitespace from line
  - Split line by whitespace from right (rsplit) with maxsplit=2
  - Validate parts count (must be 3): question_text, option_text, score
  - Convert score to integer, handle ValueError with default 0
  - Validate option_text is "Үгүй" or "Тийм"
  - Return (question_text, option_text, score)
  - Add error handling for malformed lines (log warning, return None)

- [X] T007 [US1] Implement markdown file parser function in backend/src/seeds/questions_seed.py
  - Create function `parse_markdown_file(file_path: Path) -> ParsedQuestionData`
  - Open file with UTF-8 encoding, catch UnicodeDecodeError
  - Initialize empty ParsedQuestionData with empty types list
  - Track state: current_type = None, current_group = None
  - Read file line by line with enumerate for line numbers
  - Skip empty lines and comment lines (starting with #)
  - Detect type headers: line with no leading whitespace
    - Create new ParsedType, set current_type, reset current_group
    - Append to types list when next type starts
  - Detect group headers: line with 4-space indent (or 1-tab)
    - Create new ParsedGroup under current_type
    - Set current_group
  - Detect question lines: line with 8-space indent (or 2-tab)
    - Call parse_question_line() to extract data
    - If parsing succeeds, create ParsedQuestion and append to current_group.questions
  - Return ParsedQuestionData with all parsed types

- [X] T008 [US1] Add unit tests for inverse scoring logic in backend/tests/unit/test_questions_seed.py
  - Test `test_inverse_scoring_үгүй_1`: calculate_scores("Үгүй", 1) → (1, 0)
  - Test `test_inverse_scoring_тийм_1`: calculate_scores("Тийм", 1) → (0, 1)
  - Test `test_inverse_scoring_үгүй_0`: calculate_scores("Үгүй", 0) → (0, 0)
  - Test `test_inverse_scoring_тийм_0`: calculate_scores("Тийм", 0) → (0, 0)
  - Test `test_inverse_scoring_both_zero`: Verify both options return 0

- [X] T009 [US1] Add unit tests for line parser function in backend/tests/unit/test_questions_seed.py
  - Test `test_parse_question_line_valid_үгүй`: Parse valid line with Үгүй option
  - Test `test_parse_question_line_valid_тийм`: Parse valid line with Тийм option
  - Test `test_parse_question_line_missing_score`: Handle missing score (use default 0)
  - Test `test_parse_question_line_invalid_option`: Handle invalid option text (return None)
  - Test `test_parse_question_line_malformed`: Handle completely malformed line (return None)
  - Test `test_parse_question_line_extra_whitespace`: Handle tabs vs spaces

- [X] T010 [P] [US1] Implement type creation helper function in backend/src/seeds/questions_seed.py
  - Create async function `create_questionnaire_type(session: AsyncSession, name: str) -> QuestionnaireType`
  - Query existing type by name using `select(QuestionnaireType).where(QuestionnaireType.name == name)`
  - If exists: update updated_at timestamp, return existing
  - If not exists: create new QuestionnaireType with hardcoded defaults (scoring_method=SUM, thresholds 80/50, weight=1.0, is_active=True)
  - Add to session, flush to get ID, return instance
  - Handle SQLAlchemy errors with logging

- [X] T011 [P] [US1] Implement group creation helper function in backend/src/seeds/questions_seed.py
  - Create async function `create_question_group(session: AsyncSession, type_id: UUID, name: str, order: int) -> QuestionGroup`
  - Query existing group by (type_id, name) using select with join
  - If exists: update display_order and updated_at, return existing
  - If not exists: create new QuestionGroup with type_id, name, display_order=order, weight=1.0, is_active=True
  - Add to session, flush to get ID, return instance
  - Handle SQLAlchemy errors with logging

- [X] T012 [US1] Implement question creation helper function in backend/src/seeds/questions_seed.py
  - Create async function `create_question(session: AsyncSession, group_id: UUID, text: str, order: int, no_score: int, yes_score: int) -> Question`
  - Validate scores are 0 or 1, raise ValueError if invalid
  - Query existing question by (group_id, text) using select with join
  - If exists: update text and display_order, delete existing options (will recreate), return existing
  - If not exists: create new Question with group_id, text, display_order=order, weight=1.0, is_critical=False, is_active=True
  - Add to session, flush to get ID
  - Create NO QuestionOption: option_type=NO, score=no_score, require_comment=False, require_image=False, comment_min_len=0, max_images=0, image_max_mb=1
  - Create YES QuestionOption: option_type=YES, score=yes_score, require_comment=False, require_image=False, comment_min_len=0, max_images=0, image_max_mb=1
  - Return question instance

- [X] T013 [US1] Add unit tests for markdown file parser in backend/tests/unit/test_questions_seed.py
  - Test `test_parse_markdown_file_single_type`: Parse file with one type, one group, multiple questions
  - Test `test_parse_markdown_file_multiple_types`: Parse file with multiple types
  - Test `test_parse_markdown_file_hierarchy`: Verify correct type → group → question nesting
  - Test `test_parse_markdown_file_empty_sections`: Handle types with no questions
  - Test `test_parse_markdown_file_encoding_error`: Handle non-UTF-8 files (raise UnicodeDecodeError)
  - Test `test_parse_markdown_file_comments`: Skip comment lines (starting with #)
  - Test `test_parse_markdown_file_variable_indentation`: Handle tabs vs spaces for indentation

- [X] T014 [US1] Add integration tests for database helper functions in backend/tests/integration/test_seed_integration.py
  - Test `test_create_questionnaire_type_new`: Create new type, verify in database
  - Test `test_create_questionnaire_type_existing`: Update existing type, verify updated_at changed
  - Test `test_create_question_group_new`: Create new group under type
  - Test `test_create_question_group_existing`: Update existing group
  - Test `test_create_question_new`: Create question with two options
  - Test `test_create_question_update_existing`: Update existing question and recreate options
  - Test `test_create_question_inverse_scores`: Verify inverse scoring in created options (no_score=1 → yes_score=0)

**Checkpoint**: Unit tests pass (pytest), integration tests pass, parsing logic complete

---

## Phase 2: User Story 2 - Developer Runs Seed Script (P1)

**Goal**: Integrate parsing logic with database operations to seed questions from markdown files

**Independent Test**: Run seed script against test database with sample markdown files, verify all types/groups/questions/options created with correct scores

**Checkpoint**: Seed script completes successfully, database contains all questions from markdown files with correct scores

- [X] T015 [P] [US2] Implement main seed_questions function in backend/src/seeds/questions_seed.py
  - Create async function `seed_questions(session: AsyncSession) -> SeedStats`
  - Initialize counters: types=0, groups=0, questions=0, options=0, errors=0
  - Verify questions/ folder exists using Path("questions").exists(), raise FileNotFoundError if not
  - Find all markdown files using Path("questions").glob("**/*.md")
  - For each markdown file:
    - Try: Call parse_markdown_file() to get ParsedQuestionData
    - For each ParsedType:
      - Call create_questionnaire_type(), increment types counter
      - For each ParsedGroup:
        - Call create_question_group(), increment groups counter
        - For each ParsedQuestion:
          - Call calculate_scores() to get (no_score, yes_score)
          - Call create_question() with scores, increment questions counter
          - Increment options counter by 2
    - Except Exception as e:
      - Log error with file path and exception details
      - Increment errors counter
      - Continue to next file (don't re-raise)
  - Commit transaction after all files processed
  - Print summary report: divider line, "Seed completed!", counters, divider line
  - Return SeedStats with all counters

- [X] T016 [US2] Update main() function for CLI execution in backend/src/seeds/questions_seed.py
  - Modify existing main() function to call seed_questions()
  - Add logging configuration (basic config with INFO level)
  - Add print statement "Starting question seed..." before processing
  - Add try/except around seed_questions() call to handle critical errors
  - Ensure script is runnable via `python -m src.seeds.questions_seed`
  - Add sys.exit(1) on critical failure

- [X] T017 [US2] Add integration tests for seed_questions function in backend/tests/integration/test_seed_integration.py
  - Test `test_seed_creates_new_questions`: Fresh database import, verify all entities created
  - Test `test_seed_updates_existing_questions`: Re-run seed script with same files, verify updates work
  - Test `test_seed_upsert_by_natural_key`: Update question by (type_name, group_name, question_text)
  - Test `test_seed_multiple_markdown_files`: Process multiple markdown files in one run
  - Test `test_seed_error_handling_continue_on_error`: Malformed questions don't stop import
  - Test `test_seed_summary_report`: Verify SeedStats returned with correct counts
  - Test `test_seed_performance_small_dataset`: Verify <30 seconds for ~300 questions

- [X] T018 [US2] Create sample markdown test files in backend/tests/fixtures/ directory
  - Create `test_valid.md`: Complete valid file with types, groups, questions
  - Create `test_inverse_scoring.md`: Questions with Үгүй=1 and Тийм=1 examples
  - Create `test_malformed.md`: Intentional errors (missing scores, wrong options)
  - Create `test_encoding.md`: UTF-8 file with Mongolian Cyrillic text
  - Ensure all files use UTF-8 encoding

- [X] T019 [US2] Add logging configuration in backend/src/seeds/questions_seed.py
  - Import logging module
  - Configure basic logging with format: `%(levelname)s: %(message)s`
  - Set level to INFO for normal operation
  - Add error logging in parse_markdown_file() for encoding errors
  - Add warning logging in parse_question_line() for skipped questions
  - Add error logging in seed_questions() for file processing exceptions
  - Ensure log messages include file path and line number for debugging

**Checkpoint**: Seed script runs end-to-end, tests pass, sample markdown files process correctly

---

## Phase 3: User Story 3 - Developer Verifies Imported Questions (P2)

**Goal**: Provide verification tools and documentation for developers

**Independent Test**: Developer can verify import success through database queries or admin API, scores match markdown files

**Checkpoint**: Developer has clear instructions and tools to verify import success

- [X] T020 [P] [US3] Create verification query examples in backend/src/seeds/questions_seed.py (as docstring or comment)
  - Add SQL query examples to check imported questions
  - Add query to list all types with counts
  - Add query to show questions with their options and scores
  - Include natural key lookup example
  - Add join query to show full hierarchy (type → group → question → options)

- [X] T021 [US3] Update quickstart guide with verification section in specs/007-update-questions-seed/quickstart.md
  - Already created in Phase 1 (no additional work needed)
  - Document manual verification steps
  - Include database query examples
  - Add admin API verification instructions

**Checkpoint**: Documentation complete, developer can verify imports

---

## Phase 4: User Story 4 - Developer Handles Edge Cases (P3)

**Goal**: Implement robust error handling for edge cases

**Independent Test**: Create malformed markdown files, run seed script, verify graceful handling with appropriate error messages

**Checkpoint**: Edge cases handled without crashes, clear error messages guide fixes

- [X] T022 [US4] Add unit tests for edge case handling in backend/tests/unit/test_questions_seed.py
  - Test `test_parse_question_line_empty`: Handle empty string (return None)
  - Test `test_parse_question_line_only_text`: Handle line with only question text (missing option and score)
  - Test `test_parse_question_line_score_not_integer`: Handle non-integer score (use default 0)
  - Test `test_parse_question_line_both_scores_1`: Handle case where both options would be 1 (invalid but log warning)
  - Test `test_parse_markdown_file_empty_file`: Handle file with no parseable content
  - Test `test_calculate_scores_invalid_option`: Handle invalid option_text (return (0, 0) or raise error)

- [X] T023 [US4] Add integration tests for edge case recovery in backend/tests/integration/test_seed_integration.py
  - Test `test_seed_skips_invalid_questions`: Malformed questions skipped, counted in errors
  - Test `test_seed_logs_missing_scores`: Warning logged for missing scores
  - Test `test_seed_logs_invalid_options`: Error logged for invalid option text
  - Test `test_seed_handles_encoding_errors`: File skipped with clear error message
  - Test `test_seed_partial_file_success`: Valid questions processed even if some lines fail
  - Test `test_seed_empty_groups`: Groups with no questions handled correctly

- [X] T024 [US4] Enhance error messages with context in backend/src/seeds/questions_seed.py
  - Include file path in all error messages
  - Include line number in parsing error messages
  - Add helpful hints for common errors (e.g., "Score must be 0 or 1, not {value}")
  - Add suggestion for UTF-8 encoding issues
  - Format errors consistently: `{file_path}:{line}: {error_type}: {message}`

**Checkpoint**: Edge cases tested and handled, error messages are clear and actionable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Goal**: Final validation and cleanup

**Checkpoint**: All tests pass, documentation complete, feature ready for use

- [X] T025 Run full test suite and verify all tests pass
  - Run unit tests: `pytest backend/tests/unit/test_questions_seed.py -v`
  - Run integration tests: `pytest backend/tests/integration/test_seed_integration.py -v`
  - Verify test coverage for all parsing logic and database operations
  - Fix any failing tests

- [X] T026 Performance test with realistic dataset
  - Create or use existing markdown files with ~300 questions
  - Run seed script and measure execution time
  - Verify completion in under 30 seconds (SC-002 requirement)
  - If >30 seconds: Investigate bottlenecks and optimize

- [X] T027 Manual testing with sample markdown files
  - Create test markdown files in questions/ folder
  - Run seed script: `python -m backend.src.seeds.questions_seed`
  - Verify output summary shows correct counts
  - Query database to verify questions imported correctly
  - Spot-check random questions and verify scores match markdown files

- [X] T028 Verify UTF-8 encoding handling with Mongolian text
  - Create test file with Mongolian Cyrillic text
  - Ensure file saved as UTF-8
  - Run seed script and verify no encoding errors
  - Verify question text stored correctly in database

- [X] T029 Update project documentation in CLAUDE.md
  - Already updated via update-agent-context.sh (no additional work)
  - Verify Python 3.11+ and SQLAlchemy 2.0 async listed
  - Confirm backend-only structure documented

**Checkpoint**: Feature complete, tested, documented, ready for production

---

## Dependencies Summary

### User Story Completion Order

```
Setup (Phase 1)
    ↓
    ├─→ US1 (Phase 2): Parsing Logic [P]
    │       ├─→ T002-T007 (Parsing functions)
    │       ├─→ T008-T009 (Unit tests)
    │       └─→ T010-T014 (Helper functions + tests)
    │
    └─→ US2 (Phase 2): Seed Integration [P]
            ├─→ T015-T016 (Main seed functions)
            ├─→ T017-T019 (Integration + fixtures + logging)
            └─→ Can run parallel with US1 (different files)

US3 (Phase 3): Verification (after US1+US2)
    └─→ Documentation only (no code dependencies)

US4 (Phase 3): Edge Cases (after US1+US2)
    ├─→ T022-T024 (Error handling tests and messages)
    └─→ Can run parallel with US3

Polish (Phase 4): After all user stories
    └─→ T025-T029 (Testing, performance, documentation)
```

### Parallel Execution Opportunities

**Within US1 (Parsing Logic)**:
- T003 and T004: Test file structure (different files)
- T010 and T011: Helper functions (different functions, no dependencies)

**Within US2 (Seed Integration)**:
- T017 and T018: Integration tests and fixture files (different files)

**Across US1 and US2**:
- US1 implementation (T002-T014) and US2 planning (T017-T018) can run in parallel
- US1 tests and US2 implementation can run in parallel after initial setup

**Within Phase 3**:
- T022 and T023: Unit and integration edge case tests (different files)
- US3 and US4 can run in parallel after US1+US2 complete

## Implementation Strategy

### MVP Scope (User Story 1 + 2)

**Minimum Viable Product**: Core parsing and seed functionality

- Complete Phase 1 (Setup)
- Complete US1 (Phase 2): Parsing logic with inverse scoring
- Complete US2 (Phase 2): Seed script with database operations
- Skip US3 and US4 initially (documentation and edge case handling)

**Deliverables**:
- Working seed script that parses new markdown format
- Database correctly populated with questions and custom scores
- Basic tests for core functionality

**Value**: Developers can immediately use the new seed script to import questions with custom scoring

### Incremental Delivery

**Iteration 1**: MVP (US1 + US2)
- Parse markdown files with custom scoring
- Import to database with inverse scoring logic
- Basic error handling

**Iteration 2**: Add US3 (Verification)
- Verification query examples
- Documentation updates
- Manual testing procedures

**Iteration 3**: Add US4 (Edge Cases)
- Comprehensive error handling
- Edge case tests
- Enhanced error messages

**Iteration 4**: Polish (Phase 5)
- Performance optimization
- Full test coverage
- Production readiness

## Success Criteria Validation

Each checkpoint validates specific success criteria from spec.md:

- **US1 Checkpoint**: SC-001 (5 min per file), SC-003 (100% score accuracy)
- **US2 Checkpoint**: SC-002 (<30 seconds), SC-006 (100% success rate), SC-007 (clear error messages)
- **US3 Checkpoint**: SC-005 (first attempt success via verification tools)
- **US4 Checkpoint**: SC-004 (95% edge cases handled)
- **Polish Checkpoint**: All SC criteria validated

## Notes

- **Backend-only feature**: No frontend changes required
- **No database migration**: Schema already supports all needed fields
- **Idempotent**: Seed script can be run multiple times safely
- **UTF-8 critical**: All markdown files must use UTF-8 encoding
- **Inverse scoring**: Core requirement - if one option is 1, other must be 0
- **Performance**: Current scale (<500 questions) well under 30-second target
- **Testing**: Unit tests for parsing logic, integration tests for database operations
- **Error handling**: Continue-on-error approach with detailed logging

## Task Count Summary

- **Total Tasks**: 29
- **Setup Phase**: 1 task (T001)
- **US1 Phase**: 13 tasks (T002-T014) - Parsing logic and tests
- **US2 Phase**: 5 tasks (T015-T019) - Seed integration and tests
- **US3 Phase**: 2 tasks (T020-T021) - Verification support
- **US4 Phase**: 3 tasks (T022-T024) - Edge case handling
- **Polish Phase**: 5 tasks (T025-T029) - Testing and validation

**Parallel Opportunities**: 8 task pairs can run in parallel (marked [P])

**Independent MVP**: US1 + US2 (18 tasks) provides complete seed script functionality
