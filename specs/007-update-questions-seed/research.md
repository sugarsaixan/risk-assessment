# Research: Questions Seed Custom Scoring Format

**Feature**: 007-update-questions-seed
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document captures research findings for updating the questions seed script to support custom scoring per question option, replacing the hardcoded YES=1, NO=0 pattern with a flexible format parsed from markdown files.

## Technology Decisions

### Markdown File Format

**Decision**: Tab/whitespace-separated format with question text, option text, and score

**Rationale**:
- Simple and human-readable for developers editing markdown files
- Easy to parse with Python's string split() method
- Consistent with existing markdown file structure used in the project
- Supports Mongolian Cyrillic text (Үгүй, Тийм) with UTF-8 encoding

**Format Example**:
```
Type Name
    Group Name
        Question text here        Үгүй    1
        Another question        Тийм    0
```

**Alternatives Considered**:
- JSON/YAML format: More structured but harder for non-technical users to edit
- CSV format: Less readable for hierarchical data (types → groups → questions)
- Custom DSL: Overly complex for this use case

### File System Discovery

**Decision**: Use glob pattern to discover all `*.md` files in `questions/` folder

**Rationale**:
- Automatic discovery without manual configuration
- Supports multiple markdown files for better organization
- Consistent with Python best practices (pathlib.Path.glob)
- Handles both absolute and relative paths

**Implementation**: `pathlib.Path("questions").glob("**/*.md")`

**Alternatives Considered**:
- Hardcoded file list: Less flexible, requires updates when files change
- Configuration file: Adds unnecessary complexity for simple file discovery
- Recursive search with os.walk: More verbose than pathlib

### Encoding Handling

**Decision**: Assume UTF-8 encoding, catch UnicodeDecodeError with helpful error message

**Rationale**:
- UTF-8 is the standard encoding for Markdown files with non-ASCII text
- Python 3's open() defaults to UTF-8 on most systems
- Explicit error handling helps developers diagnose encoding issues
- Avoids silent data corruption

**Implementation**: `open(file_path, encoding="utf-8")` with try/except for UnicodeDecodeError

**Alternatives Considered**:
- Automatic encoding detection (chardet): Adds dependency, slower, overkill for this case
- System default encoding: Unreliable across platforms (Windows vs Linux)
- Latin-1 fallback: Would corrupt Mongolian Cyrillic text

### Parsing Strategy

**Decision**: Line-by-line parsing with indentation-based hierarchy detection

**Rationale**:
- Markdown indentation naturally represents hierarchy (types → groups → questions)
- Simple state machine approach (current_type → current_group → current_question)
- Easy to implement and debug
- Handles variable indentation (tabs vs spaces) with strip()

**Algorithm**:
1. Track current type and group state
2. Detect type level: no leading whitespace, ends with colon
3. Detect group level: 4-space indent, ends with colon
4. Detect question level: 8-space indent, contains option text and score
5. Split question line: text + whitespace + option + whitespace + score

**Alternatives Considered**:
- Regular expressions: More powerful but harder to read and maintain
- Markdown parser library (markdown-it, python-markdown): Overkill, doesn't handle custom format
- AST parsing: Excessive complexity for simple line-based format

### Database Update Strategy

**Decision**: Use SQLAlchemy Core with async session, upsert by question text + group + type

**Rationale**:
- Existing codebase uses SQLAlchemy with async/await pattern
- Upsert (update or insert) handles idempotent seed script runs
- Natural key lookup (type_name + group_name + question_text) avoids hardcoding IDs
- Async pattern matches existing database operations in the project

**Implementation**:
```python
# Check if question exists by natural key
existing = await session.execute(
    select(Question)
    .join(QuestionGroup)
    .join(QuestionnaireType)
    .where(QuestionnaireType.name == type_name)
    .where(QuestionGroup.name == group_name)
    .where(Question.text == question_text)
)
# Update if exists, insert if new
```

**Alternatives Considered**:
- Delete all and re-insert: Loses foreign key relationships, inefficient
- ID-based upsert: Requires tracking IDs from previous runs, complex
- Synchronous SQLAlchemy: Inconsistent with existing async patterns

### Error Handling Strategy

**Decision**: Continue-on-error with detailed logging, summary report at end

**Rationale**:
- One malformed question shouldn't prevent importing hundreds of valid questions
- Detailed error messages (file:line) help developers fix issues quickly
- Summary report shows success/failure counts for visibility
- Matches user expectation from spec (FR-008: "log clear error messages")

**Implementation**:
```python
try:
    # Parse and insert question
except ValueError as e:
    logger.error(f"{file_path}:{line_num}: {str(e)}")
    errors += 1
    continue
```

**Alternatives Considered**:
- Fail-fast: Stops entire import on first error, poor UX for large question sets
- Silent failures: Hides problems, makes debugging impossible
- Exception-only: No visibility into what went wrong

### Testing Approach

**Decision**: Unit tests for parsing logic, integration tests for database operations

**Rationale**:
- Unit tests fast and focused on edge cases (missing scores, invalid formats)
- Integration tests verify end-to-seed script execution
- Test fixtures with sample markdown files ensure format compatibility
- Matches existing project test structure (tests/unit/, tests/integration/)

**Test Categories**:
1. Parse valid question lines (various formats)
2. Parse invalid lines (missing score, wrong option text)
3. Inverse scoring logic (if Үгүй=1, Тийм=0)
4. Database upsert (update existing, insert new)
5. UTF-8 encoding with Mongolian text

**Alternatives Considered**:
- Manual testing only: No regression protection, unreliable
- End-to-end tests only: Slow to run, hard to pinpoint failures
- Property-based testing: Overkill for deterministic parsing logic

## Dependencies Analysis

### Existing Dependencies (Used)

- **SQLAlchemy 2.0** (async): Database ORM, already used in project
- **asyncpg**: PostgreSQL async driver, already used in project
- **Pydantic**: Data validation, already used in project
- **pathlib**: File system operations (Python stdlib)
- **logging**: Error reporting (Python stdlib)

### New Dependencies Needed

**None** - All required functionality can be implemented with existing dependencies and Python standard library.

**Rationale**: The feature is pure parsing and database operations, both well-supported by existing stack. No external libraries needed for:
- String manipulation (str.split(), str.strip())
- File I/O (pathlib, built-in open())
- Database operations (SQLAlchemy)
- Logging (logging module)

## Performance Considerations

### Expected Scale

Based on existing questions_seed.py:
- **Question types**: 6-10 types
- **Groups per type**: 3-6 groups
- **Questions per group**: 3-10 questions
- **Total questions**: ~200-300 questions
- **Total options**: ~400-600 options (2 per question)

### Performance Targets

From spec (SC-002): "Seed script completes successfully for all question files in under 30 seconds"

**Analysis**:
- Current hardcoded script processes ~300 questions in <5 seconds
- New parsing adds string operations per line (negligible overhead)
- Database upsert slower than bulk insert but still <10 seconds for ~600 records
- File I/O for 6-10 markdown files: <1 second
- **Estimated total time: 10-15 seconds** (well under 30-second target)

**Optimization Opportunities** (if needed):
- Batch upsert operations (SQLAlchemy bulk_update_mappings)
- Parallel file processing (concurrent.futures.ThreadPoolExecutor)
- Connection pooling for async database operations

**Decision**: Implement simple approach first, optimize only if measurements show >30 seconds

## Security Considerations

### File System Access

**Risk**: Path traversal attacks if questions/ location is user-controlled

**Mitigation**:
- Questions folder path is hardcoded or from environment variable
- Validate all file paths are within questions/ directory
- Use pathlib.Path.resolve() to canonicalize paths

### Database Operations

**Risk**: SQL injection from question text

**Mitigation**:
- SQLAlchemy parameterized queries (automatic escaping)
- No raw SQL string concatenation
- Pydantic validation for score values (must be integers)

### File Encoding

**Risk**: Malformed UTF-8 causing crashes or data corruption

**Mitigation**:
- Explicit encoding="utf-8" in open()
- Catch UnicodeDecodeError with helpful error message
- Skip problematic files rather than crashing

## Implementation Constraints

### Python Version

**Constraint**: Python 3.11+ (from CLAUDE.md)

**Implications**:
- Can use modern type hints (union operator `|`, None syntax)
- Can use pathlib improvements
- Can use async/await (already used in project)
- Cannot use Python 3.12+ specific features without upgrade

### Database Schema

**Constraint**: Existing QuestionOption model has require_comment, require_image, comment_min_len, max_images, image_max_mb fields

**Implications**:
- Must set values for these fields even when disabled
- Use minimal safe defaults: `require_comment=False`, `require_image=False`, `comment_min_len=0`, `max_images=0`, `image_max_mb=1`
- No schema changes needed (fields already exist)

### Backward Compatibility

**Constraint**: No backward compatibility (spec: "Backward compatibility with old hardcoded scoring format - Out of Scope")

**Implications**:
- Can completely replace existing questions_seed.py logic
- No need to support dual-format parsing
- Existing database records will be updated by new seed script

## Open Questions Resolved

All questions from technical context have been resolved:

✅ Markdown format: Tab/whitespace-separated with question, option, score
✅ File discovery: Glob pattern in questions/ folder
✅ Encoding: UTF-8 with explicit error handling
✅ Parsing: Line-by-line with indentation hierarchy
✅ Database: Async SQLAlchemy with upsert by natural key
✅ Error handling: Continue-on-error with detailed logging
✅ Testing: Unit + integration tests
✅ Dependencies: No new dependencies needed
✅ Performance: <30 seconds achievable with simple approach
✅ Security: Path validation, parameterized queries, encoding checks
✅ Constraints: Python 3.11+, existing schema, no backward compatibility

## Next Steps

Proceed to Phase 1: Design & Contracts
1. Create data-model.md with entity relationships
2. Define contracts/ with parsing API specification
3. Create quickstart.md with usage examples
