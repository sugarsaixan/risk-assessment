# Implementation Plan: Questions Seed with Custom Scoring Format

**Branch**: `007-update-questions-seed` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-update-questions-seed/spec.md`

## Summary

Update the existing questions seed script (`src/seeds/questions_seed.py`) to parse markdown files with a new format that supports custom scoring per question option. The current script hardcodes YES=1, NO=0; the updated version will parse question lines with format `{question_text} {option_text} {score}` where option_text is "Үгүй" or "Тийм" and score is 0 or 1. The script implements inverse scoring logic: if one option has score 1, the other automatically gets score 0. All options have `require_comment=False` and `require_image=False` with minimal safe defaults.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLAlchemy 2.0 (async), asyncpg, Pydantic 2.x, pathlib
**Storage**: PostgreSQL (existing database with questionnaire_types, question_groups, questions, question_options tables)
**Testing**: pytest (async), pytest-asyncio
**Target Platform**: Linux/macOS backend server
**Project Type**: Backend-only (Python module update, no frontend changes)
**Performance Goals**: Complete seed operation in under 30 seconds for ~300 questions (~600 options)
**Constraints**: UTF-8 encoding required for Mongolian Cyrillic text; async/await pattern required; existing database schema
**Scale/Scope**: ~6-10 questionnaire types, ~20-30 groups, ~200-300 questions, ~400-600 options

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution file exists (`.specify/memory/constitution.md` is template only)

**Result**: SKIP constitution checks - no project constitution defined

## Project Structure

### Documentation (this feature)

```text
specs/007-update-questions-seed/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command) ✓
├── data-model.md        # Phase 1 output (/speckit.plan command) ✓
├── quickstart.md        # Phase 1 output (/speckit.plan command) ✓
├── contracts/           # Phase 1 output (/speckit.plan command) ✓
│   └── questions-seed-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── questionnaire_type.py   # Existing model
│   │   ├── question_group.py       # Existing model
│   │   ├── question.py             # Existing model
│   │   └── question_option.py      # Existing model
│   ├── seeds/
│   │   └── questions_seed.py       # TO BE MODIFIED
│   ├── core/
│   │   └── database.py             # Existing async session factory
│   └── models/
│       └── enums.py                # Existing enums (OptionType, ScoringMethod)
└── tests/
    ├── unit/
    │   └── test_questions_seed.py  # TO BE CREATED
    └── integration/
        └── test_seed_integration.py # TO BE CREATED

questions/
├── fire_safety.md         # Example markdown file (user-provided)
├── electrical_safety.md   # Example markdown file (user-provided)
└── ...
```

**Structure Decision**: Backend-only update (Option 1: Single project). The feature only modifies the Python seed script and related tests. No frontend changes, no new projects, no web interfaces. All changes are in `backend/src/seeds/questions_seed.py` and test files.

## Complexity Tracking

> **No violations** - Feature is straightforward backend script update with no architectural complexity.

## Phase 0: Research & Technical Decisions ✓

**Status**: Complete

**Artifacts**: [research.md](research.md)

**Key Decisions**:

1. **Markdown Format**: Tab/whitespace-separated format (question text, option text, score)
   - Simple for developers to edit
   - Easy to parse with string operations
   - Supports Mongolian Cyrillic (UTF-8)

2. **File Discovery**: Glob pattern `questions/*.md` with pathlib
   - Automatic discovery without configuration
   - Supports multiple markdown files

3. **Encoding**: UTF-8 with explicit error handling
   - Standard for Markdown with non-ASCII text
   - Helpful error messages for developers

4. **Parsing**: Line-by-line with indentation-based hierarchy
   - Simple state machine (type → group → question)
   - Handles variable whitespace

5. **Database**: Async SQLAlchemy with upsert by natural key
   - Idempotent seed script runs
   - Consistent with existing codebase patterns

6. **Error Handling**: Continue-on-error with detailed logging
   - One bad question doesn't stop entire import
   - File:line error messages

7. **Testing**: Unit tests for parsing, integration tests for database
   - Fast unit tests for edge cases
   - End-to-end integration tests

8. **Dependencies**: No new dependencies needed
   - Use existing SQLAlchemy, asyncpg, pathlib
   - Python standard library sufficient

## Phase 1: Design & Contracts ✓

**Status**: Complete

**Artifacts**:
- [data-model.md](data-model.md) - Entity relationships, validation rules, state transitions
- [contracts/questions-seed-api.md](contracts/questions-seed-api.md) - Function signatures, parsing algorithms, error handling
- [quickstart.md](quickstart.md) - Usage examples, troubleshooting, best practices

**Design Summary**:

### Data Model

Four main entities in hierarchical structure:
1. **QuestionnaireType** (top-level category)
2. **QuestionGroup** (within type)
3. **Question** (within group, has Mongolian text)
4. **QuestionOption** (NO and YES options with scores)

**Key Constraints**:
- Natural key uniqueness: (type_name, group_name, question_text)
- Each question has exactly 2 options (NO and YES)
- Inverse scoring: If one option is 1, other is 0
- All options: `require_comment=False`, `require_image=False`

### Parsing API

**Main Functions**:
```python
def parse_markdown_file(file_path: Path) -> ParsedQuestionData
async def create_questionnaire_type(session, name) -> QuestionnaireType
async def create_question_group(session, type_id, name, order) -> QuestionGroup
async def create_question(session, group_id, text, order, no_score, yes_score) -> Question
async def seed_questions(session) -> SeedStats
```

**Inverse Scoring Logic**:
```python
if option == "Үгүй" and score == 1:
    no_score, yes_score = 1, 0
elif option == "Тийм" and score == 1:
    no_score, yes_score = 0, 1
else:
    no_score, yes_score = 0, 0
```

### Quickstart Guide

Step-by-step instructions for:
1. Preparing markdown files with custom scoring format
2. Running seed script: `python -m src.seeds.questions_seed`
3. Verifying import (database queries, admin API)
4. Handling errors (encoding, invalid scores, malformed lines)
5. Best practices (UTF-8, organization, backups, testing)

## Phase 2: Implementation Tasks

**Status**: Not started - Run `/speckit.tasks` to generate tasks.md

**Next Command**: `/speckit.tasks` to create detailed task breakdown

**Estimated Tasks** (preview):
- Update questions_seed.py with new parsing logic
- Add inverse scoring calculation function
- Implement upsert by natural key
- Add error handling and logging
- Create unit tests for parsing
- Create integration tests for database operations
- Update CLAUDE.md with tech stack information
- Test with sample markdown files

## Testing Strategy

### Unit Tests

**File**: `backend/tests/unit/test_questions_seed.py`

**Test Cases**:
1. `test_parse_question_line_valid()` - Parse valid question line
2. `test_parse_question_line_missing_score()` - Handle missing score (use default 0)
3. `test_parse_question_line_invalid_option()` - Handle invalid option text (skip question)
4. `test_inverse_scoring_үгүй_1()` - Test Үгүй with score 1 → (1, 0)
5. `test_inverse_scoring_тийм_1()` - Test Тийм with score 1 → (0, 1)
6. `test_inverse_scoring_both_0()` - Test both scores 0 → (0, 0)
7. `test_parse_markdown_file()` - Parse complete file with types, groups, questions
8. `test_parse_markdown_encoding_error()` - Handle non-UTF-8 files

### Integration Tests

**File**: `backend/tests/integration/test_seed_integration.py`

**Test Cases**:
1. `test_seed_creates_new_questions()` - Fresh database import
2. `test_seed_updates_existing_questions()` - Re-run seed script
3. `test_seed_upsert_by_natural_key()` - Update questions by (type, group, text)
4. `test_seed_error_handling()` - Continue on error with malformed questions
5. `test_seed_summary_report()` - Verify statistics returned

### Manual Testing

**Test Markdown Files**:
- `questions/test_valid.md` - All valid questions
- `questions/test_malformed.md` - Intentional errors (missing scores, wrong options)
- `questions/test_encoding.md` - UTF-8 encoding with Mongolian text

**Verification Steps**:
1. Run seed script: `python -m src.seeds.questions_seed`
2. Check output summary (types, groups, questions, options, errors)
3. Query database: Verify scores match markdown files
4. Spot-check: Random questions, compare with source

## Migration Strategy

**Schema Changes**: None (all fields already exist)

**Data Migration**: Not applicable (seed script creates/updates data)

**Backward Compatibility**: Not supported (spec: out of scope)

**Deployment Steps**:
1. Update `backend/src/seeds/questions_seed.py` in development
2. Test with sample markdown files
3. Run unit tests: `pytest backend/tests/unit/test_questions_seed.py`
4. Run integration tests: `pytest backend/tests/integration/test_seed_integration.py`
5. Commit changes with markdown files
6. Deploy to production (no database migration needed)

## Rollback Plan

If issues discovered after deployment:

1. **Immediate Rollback**:
   ```bash
   git revert <commit-hash>
   # Redeploy previous version of questions_seed.py
   ```

2. **Data Recovery**:
   - Questions created by new seed script remain in database
   - Old seed script can still read existing questions
   - No data loss (only new fields may have default values)

3. **Markdown Files**:
   - Revert markdown files to old format if needed
   - Or keep new format (old script will ignore custom scores)

## Success Criteria

From spec - measurable outcomes:

- **SC-001**: Developers can update question markdown files with custom scores in under 5 minutes per file
- **SC-002**: Seed script completes successfully for all question files in under 30 seconds
- **SC-003**: All imported questions have 100% score accuracy matching markdown file values
- **SC-004**: Seed script handles at least 95% of edge cases (missing scores, invalid formats) without crashing
- **SC-005**: Developers can run seed script successfully on first attempt without debugging parsing errors
- **SC-006**: Question import success rate is 100% for properly formatted markdown files
- **SC-007**: Seed script provides clear error messages for 100% of parsing failures

## Risk Assessment

### Low Risk

- **Complexity**: Simple parsing logic, well-defined format
- **Testing**: Straightforward unit and integration tests
- **Rollback**: Easy to revert script changes
- **Data**: No schema changes, no data migration

### Medium Risk

- **Encoding**: UTF-8 issues could corrupt Mongolian text (mitigated by explicit error handling)
- **Performance**: Large question sets (>1000) may need optimization (estimated <30 seconds for current scale)

### High Risk

None identified

## Dependencies

### Internal

- Existing database models (QuestionnaireType, QuestionGroup, Question, QuestionOption)
- Async session factory (`src.core.database.async_session_factory`)
- Enums (OptionType.NO, OptionType.YES, ScoringMethod.SUM)

### External

- Python 3.11+
- SQLAlchemy 2.0 (async)
- asyncpg (PostgreSQL driver)
- pytest and pytest-asyncio (testing)

## Open Questions

**None** - All technical decisions resolved in Phase 0 research.

## Post-Implementation Checklist

After implementation, verify:

- [ ] Seed script parses markdown files correctly
- [ ] Inverse scoring logic works (if Үгүй=1, then Тийм=0)
- [ ] All options have `require_comment=False`, `require_image=False`
- [ ] Database upsert works by natural key
- [ ] Error messages include file path and line number
- [ ] Summary report prints accurate counts
- [ ] UTF-8 encoding handled correctly
- [ ] Performance <30 seconds for all files
- [ ] Unit tests pass (pytest)
- [ ] Integration tests pass (pytest)
- [ ] Manual testing with sample markdown files successful
- [ ] CLAUDE.md updated with tech stack (done via update-agent-context.sh)
