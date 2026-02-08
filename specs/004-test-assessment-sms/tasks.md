# Tasks: Test Assessment SMS Distribution Tool

**Feature**: 004-test-assessment-sms
**Branch**: `004-test-assessment-sms`
**Input**: Design documents from `/specs/004-test-assessment-sms/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this implementation unless explicitly requested later.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `backend/scripts/`, `backend/tests/` at repository root
- This is a standalone utility script in the backend directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend/scripts directory and __init__.py in backend/scripts/
- [X] T002 Create configuration template file backend/scripts/config_template.yml with assessment_api, sms_api, message_template, and processing sections
- [X] T003 [P] Update backend/.gitignore to exclude config.yml (keep template)
- [X] T004 [P] Check and add httpx dependency to backend/pyproject.toml if not already present
- [X] T005 [P] Check and add pyyaml dependency to backend/pyproject.toml if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create configuration loader module in backend/scripts/config.py with load_config() function to parse YAML and expand environment variables
- [X] T007 Create Pydantic models in backend/scripts/models.py for Configuration, AssessmentRequest, AssessmentResponse, SMSRequest, SMSResponse, ProcessingResult, and ProcessingSummary per data-model.md
- [X] T008 Create phone number validator in backend/scripts/validators.py with normalize_phone_number() and validate_phone_number() functions for Mongolian numbers
- [X] T009 Create httpx client wrapper in backend/scripts/http_client.py with AsyncHttpClient class for making API calls with retry logic
- [X] T010 Create base exception classes in backend/scripts/exceptions.py for ValidationException, APIException, and NetworkException

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Single Test User Invitation (Priority: P1) 🎯 MVP

**Goal**: Create a test risk assessment and send an SMS invitation with a unique link to a single test user

**Independent Test**: Run the script with one phone number, receive the SMS, and confirm the link opens a valid assessment page

### Implementation for User Story 1

- [X] T011 [P] [US1] Create AssessmentService class in backend/scripts/assessment_service.py with create_assessment() async method to call assessment API
- [X] T012 [P] [US1] Create SMSService class in backend/scripts/sms_service.py with send_sms() async method to call SMS API
- [X] T013 [US1] Create process_single_phone_number() async function in backend/scripts/processor.py that validates number, creates assessment, and sends SMS with error handling
- [X] T014 [US1] Create CLI argument parser in backend/scripts/test_assessment_sms.py using argparse with input_file, --config, --respondent-id, --type-ids, --expires-in-days, --dry-run, and --verbose flags
- [X] T015 [US1] Implement main() async function in backend/scripts/test_assessment_sms.py that loads config, reads phone numbers from input file, and processes each number
- [X] T016 [US1] Create console report formatter in backend/scripts/reporters.py with generate_console_report() function for human-readable output
- [X] T017 [US1] Add phone number file parsing in backend/scripts/test_assessment_sms.py with support for comments (#), blank lines, and basic error handling
- [X] T018 [US1] Implement dry-run mode in backend/scripts/test_assessment_sms.py to validate input without making API calls
- [X] T019 [US1] Add verbose logging in backend/scripts/test_assessment_sms.py for detailed per-number processing information

**Checkpoint**: At this point, User Story 1 should be fully functional - can create one assessment and send one SMS

---

## Phase 4: User Story 2 - Bulk Test User Invitations (Priority: P2)

**Goal**: Create multiple test risk assessments and send SMS invitations to a list of test users at once

**Independent Test**: Provide a list of phone numbers, run the script, and verify all recipients receive unique SMS links

### Implementation for User Story 2

- [X] T020 [P] [US2] Create process_phone_numbers_batch() async function in backend/scripts/processor.py that processes multiple phone numbers concurrently
- [X] T021 [US2] Implement asyncio.Semaphore-based concurrency limiting in backend/scripts/processor.py with configurable max_concurrent setting from config
- [X] T022 [US2] Add retry logic with exponential backoff in backend/scripts/http_client.py for transient failures (network errors, 5xx, 429 status codes)
- [X] T023 [US2] Create continue-on-error handling in backend/scripts/processor.py to collect results and continue processing on individual failures
- [X] T024 [US2] Add --max-concurrent, --retry-attempts, and --retry-delay-seconds CLI flags to backend/scripts/test_assessment_sms.py
- [X] T025 [US2] Implement progress indicator in backend/scripts/test_assessment_sms.py showing current/total numbers processed

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - can process single or multiple phone numbers

---

## Phase 5: User Story 3 - Verification and Reporting (Priority: P3)

**Goal**: Generate summary reports showing which assessments were created, which SMS were sent, and any failures with reasons

**Independent Test**: Run the script and check console output for success/failure counts and error details

### Implementation for User Story 3

- [X] T026 [P] [US3] Create ProcessingSummary model in backend/scripts/models.py with aggregate statistics (total_count, success_count, failure_count, duration_seconds)
- [X] T027 [P] [US3] Implement generate_json_report() function in backend/scripts/reporters.py with full results in JSON format per data-model.md schema
- [X] T028 [P] [US3] Implement generate_csv_report() function in backend/scripts/reporters.py with spreadsheet-compatible columns
- [X] T029 [US3] Add --output-format and --output-file CLI flags to backend/scripts/test_assessment_sms.py for console/json/csv options
- [X] T030 [US3] Implement summary statistics collection in backend/scripts/processor.py tracking validation errors, assessment errors, and SMS errors separately
- [X] T031 [US3] Add detailed error reporting in backend/scripts/reporters.py with phone number, stage, error type, and error message for each failure
- [X] T032 [US3] Implement exit code handling in backend/scripts/test_assessment_sms.py to return non-zero exit code if any failures occurred

**Checkpoint**: All user stories should now be independently functional - single/bulk processing with full reporting

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T033 [P] Add docstrings to all modules and functions following Google Python Style Guide
- [ ] T034 [P] Create README.md in backend/scripts/ with usage examples and quick reference
- [ ] T035 Add input validation for CLI arguments in backend/scripts/test_assessment_sms.py with clear error messages
- [ ] T036 Implement graceful shutdown handling in backend/scripts/test_assessment_sms.py for keyboard interrupts
- [ ] T037 Add PII protection in backend/scripts/test_assessment_sms.py to avoid logging full phone numbers in non-verbose mode
- [ ] T038 Add shebang line and executable permissions to backend/scripts/test_assessment_sms.py for direct execution
- [ ] T039 Run validation using quickstart.md examples to ensure all documented use cases work correctly
- [ ] T040 Create test fixture files in backend/tests/test_scripts/fixtures/phone_numbers.txt with valid and invalid phone numbers for manual testing

**Checkpoint**: Implementation complete with documentation, error handling, and user experience improvements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T005) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion (T006-T010)
- **User Story 2 (Phase 4)**: Depends on US1 completion - extends single processing to batch
- **User Story 3 (Phase 5)**: Depends on US2 completion - adds reporting to batch processing
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 completion - builds upon single processing logic
- **User Story 3 (P3)**: Depends on US2 completion - reports on batch processing results

### Within Each User Story

**User Story 1**:
- T011 and T012 (services) can run in parallel
- T013 (processor) depends on T011, T012
- T014-T019 build incrementally on the script

**User Story 2**:
- T020-T025 build incrementally on US1 foundation
- Batch processing extends single processing logic

**User Story 3**:
- T026-T028 (reporters) can run in parallel
- T029-T032 integrate reporting into the main script

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005 can run in parallel
- **Foundational (Phase 2)**: No parallel opportunities (each module builds on concepts)
- **User Story 1**: T011 and T012 can run in parallel
- **User Story 3**: T026, T027, T028 can run in parallel
- **Polish (Phase 6)**: T033 and T034 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch API services in parallel:
Task T011: "Create AssessmentService class in backend/scripts/assessment_service.py"
Task T012: "Create SMSService class in backend/scripts/sms_service.py"

# After services complete, continue with processor and script
```

---

## Parallel Example: User Story 3

```bash
# Launch all report formatters in parallel:
Task T027: "Implement generate_json_report() function in backend/scripts/reporters.py"
Task T028: "Implement generate_csv_report() function in backend/scripts/reporters.py"

# After reporters complete, integrate into script
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010) - CRITICAL foundation
3. Complete Phase 3: User Story 1 (T011-T019)
4. **STOP and VALIDATE**: Test with one phone number - receive SMS, verify link works
5. Demo MVP functionality

### Incremental Delivery

1. Complete Setup + Foundational → Infrastructure ready
2. Add User Story 1 → Test with single phone number → MVP complete!
3. Add User Story 2 → Test with multiple phone numbers → Batch processing
4. Add User Story 3 → Test reporting formats → Full feature set
5. Add Polish → Production-ready tool

### Recommended Delivery Order

**MVP** (Minimum Viable Product):
- Setup + Foundational + User Story 1
- **Value**: Can send test assessments one at a time

**v1.0** (Full Feature):
- MVP + User Story 2 + User Story 3
- **Value**: Full batch processing with comprehensive reporting

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- User Stories are sequentially dependent in this feature (US1 → US2 → US3)
- Each user story adds functionality without breaking previous stories
- Tests are not included in this task list unless explicitly requested
- Commit after each task or logical group for easy rollback
- Stop at any checkpoint to validate story independently
- Use the quickstart.md examples for validation testing

---

## Summary

- **Total Tasks**: 40
- **Setup Tasks**: 5
- **Foundational Tasks**: 5
- **User Story 1 Tasks**: 9 (P1 - MVP)
- **User Story 2 Tasks**: 6 (P2)
- **User Story 3 Tasks**: 7 (P3)
- **Polish Tasks**: 8

**Parallel Opportunities Identified**: 7 tasks can run in parallel with others
**MVP Scope**: 19 tasks (Setup + Foundational + US1)
**Independent Test Criteria**: Each user story has clear independent test validation
