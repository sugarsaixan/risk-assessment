# API Contract: Questions Seed Parser

**Feature**: 007-update-questions-seed
**Version**: 1.0.0
**Date**: 2026-02-08

## Overview

This document defines the internal API contract for the questions seed parsing module. The parser is responsible for reading markdown files from the `questions/` folder and extracting hierarchical question data with custom scoring.

**Note**: This is an internal module API, not a web API. The "endpoints" described here are Python function signatures.

## Module Structure

```python
# src/seeds/questions_seed.py

def parse_markdown_file(file_path: Path) -> ParsedQuestionData
    """Parse a single markdown file and extract question data."""

def create_questionnaire_type(session: AsyncSession, name: str) -> QuestionnaireType
    """Create or update a questionnaire type."""

def create_question_group(session: AsyncSession, type_id: UUID, name: str, order: int) -> QuestionGroup
    """Create or update a question group."""

def create_question(session: AsyncSession, group_id: UUID, text: str, order: int,
                   no_score: int, yes_score: int) -> Question
    """Create or update a question with two options (NO and YES)."""

async def seed_questions(session: AsyncSession) -> SeedStats
    """Main entry point: Parse all markdown files and seed database."""
```

## Type Definitions

### ParsedQuestionData

**Description**: Data structure returned by parsing a single markdown file

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ParsedQuestion:
    """A single question with parsed option and score."""
    text: str
    option_text: str  # "Үгүй" or "Тийм"
    score: int  # 0 or 1

@dataclass
class ParsedGroup:
    """A group of questions with a name."""
    name: str
    questions: List[ParsedQuestion]

@dataclass
class ParsedType:
    """A questionnaire type containing multiple groups."""
    name: str
    groups: List[ParsedGroup]

@dataclass
class ParsedQuestionData:
    """Complete parsed data from one markdown file."""
    types: List[ParsedType]
```

### SeedStats

**Description**: Statistics returned by seed_questions function

```python
@dataclass
class SeedStats:
    """Summary statistics from seed operation."""
    types_created: int
    groups_created: int
    questions_created: int
    options_created: int
    errors: int
```

## Function Contracts

### parse_markdown_file()

**Signature**:
```python
def parse_markdown_file(file_path: Path) -> ParsedQuestionData:
    """Parse a single markdown file and extract question data.

    Args:
        file_path: Path to markdown file (must exist, readable, UTF-8 encoded)

    Returns:
        ParsedQuestionData with all types, groups, and questions found in file

    Raises:
        FileNotFoundError: If file_path does not exist
        UnicodeDecodeError: If file is not valid UTF-8
        ValueError: If file format is invalid (no parseable content)

    Example:
        >>> data = parse_markdown_file(Path("questions/fire_safety.md"))
        >>> len(data.types)
        1
        >>> data.types[0].name
        'ГАЛЫН АЮУЛГҮЙ БАЙДАЛ'
    """
```

**Algorithm**:
1. Open file with UTF-8 encoding
2. Read line by line
3. Track current state: current_type, current_group
4. For each line:
   - Skip empty lines and comments (# prefix)
   - If no indent: Parse as type header, set current_type, reset current_group
   - If 4-space indent: Parse as group header, set current_group under current_type
   - If 8-space indent: Parse as question line, extract text + option + score, add to current_group
5. Return ParsedQuestionData

**Error Handling**:
- Invalid UTF-8: Raise UnicodeDecodeError with file path
- No parseable content: Raise ValueError with file path
- Malformed question line: Log warning, skip question (don't raise)

**Preconditions**:
- file_path exists
- file_path is a regular file (not directory)
- File has .md extension

**Postconditions**:
- Returned ParsedQuestionData.types is non-empty
- All ParsedQuestion objects have valid text, option_text, score
- All option_text values are "Үгүй" or "Тийм"
- All score values are 0 or 1

---

### create_questionnaire_type()

**Signature**:
```python
async def create_questionnaire_type(
    session: AsyncSession,
    name: str
) -> QuestionnaireType:
    """Create or update a questionnaire type.

    Args:
        session: Async SQLAlchemy session
        name: Type name in Mongolian Cyrillic

    Returns:
        Created or updated QuestionnaireType instance

    Raises:
        SQLAlchemyError: If database operation fails

    Example:
        >>> qtype = await create_questionnaire_type(session, "ГАЛЫН АЮУЛГҮЙ БАЙДАЛ")
        >>> qtype.name
        'ГАЛЫН АЮУЛГҮЙ БАЙДАЛ'
        >>> qtype.scoring_method
        <ScoringMethod.SUM: 'SUM'>
    """
```

**Algorithm**:
1. Query existing type by name
2. If exists:
   - Update updated_at timestamp
   - Return existing instance
3. If not exists:
   - Create new QuestionnaireType with hardcoded defaults:
     - scoring_method = ScoringMethod.SUM
     - threshold_high = 80
     - threshold_medium = 50
     - weight = Decimal("1.0")
     - is_active = True
   - Add to session
   - Flush to get ID
   - Return new instance

**Error Handling**:
- Database connection error: Raise SQLAlchemyError
- Constraint violation: Raise SQLAlchemyError (duplicate name)

**Preconditions**:
- session is active (not closed)
- name is non-empty string

**Postconditions**:
- Returned QuestionnaireType has valid ID
- Type is persisted in database (committed by caller)
- Type has is_active = True

---

### create_question_group()

**Signature**:
```python
async def create_question_group(
    session: AsyncSession,
    type_id: UUID,
    name: str,
    order: int
) -> QuestionGroup:
    """Create or update a question group.

    Args:
        session: Async SQLAlchemy session
        type_id: Parent questionnaire type ID
        name: Group name in Mongolian Cyrillic
        order: Display order within type (1, 2, 3...)

    Returns:
        Created or updated QuestionGroup instance

    Raises:
        SQLAlchemyError: If database operation fails
        FileNotFoundError: If type_id does not exist

    Example:
        >>> group = await create_question_group(session, type_id, "Галын хор", 1)
        >>> group.name
        'Галын хор'
        >>> group.display_order
        1
    """
```

**Algorithm**:
1. Query existing group by (type_id, name)
2. If exists:
   - Update display_order if changed
   - Update updated_at timestamp
   - Return existing instance
3. If not exists:
   - Create new QuestionGroup:
     - type_id = type_id (parameter)
     - name = name (parameter)
     - display_order = order (parameter)
     - weight = Decimal("1.0")
     - is_active = True
   - Add to session
   - Flush to get ID
   - Return new instance

**Error Handling**:
- type_id not found: Raise SQLAlchemyError (foreign key violation)
- Database connection error: Raise SQLAlchemyError
- Constraint violation: Raise SQLAlchemyError (duplicate name within type)

**Preconditions**:
- session is active
- type_id exists in questionnaire_types table
- name is non-empty string
- order > 0

**Postconditions**:
- Returned QuestionGroup has valid ID
- Group is persisted in database
- Group.type_id matches type_id parameter
- Group has is_active = True

---

### create_question()

**Signature**:
```python
async def create_question(
    session: AsyncSession,
    group_id: UUID,
    text: str,
    order: int,
    no_score: int,
    yes_score: int
) -> Question:
    """Create or update a question with two options (NO and YES).

    Args:
        session: Async SQLAlchemy session
        group_id: Parent question group ID
        text: Question text in Mongolian Cyrillic
        order: Display order within group (1, 2, 3...)
        no_score: Score for Үгүй (NO) option (0 or 1)
        yes_score: Score for Тийм (YES) option (0 or 1)

    Returns:
        Created or updated Question instance

    Raises:
        SQLAlchemyError: If database operation fails
        FileNotFoundError: If group_id does not exist
        ValueError: If no_score or yes_score not in {0, 1}

    Example:
        >>> question = await create_question(
        ...     session, group_id,
        ...     "Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх",
        ...     1, no_score=1, yes_score=0
        ... )
        >>> question.text
        'Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх'
    """
```

**Algorithm**:
1. Validate scores: no_score in {0, 1}, yes_score in {0, 1}
2. Query existing question by (group_id, text)
3. If exists:
   - Update display_order if changed
   - Update updated_at timestamp
   - Delete existing options (will recreate)
   - Return existing instance
4. If not exists:
   - Create new Question:
     - group_id = group_id (parameter)
     - text = text (parameter)
     - display_order = order (parameter)
     - weight = Decimal("1.0")
     - is_critical = False
     - is_active = True
   - Add to session
   - Flush to get ID
5. Create NO option:
   - question_id = question.id
   - option_type = OptionType.NO
   - score = no_score
   - require_comment = False
   - require_image = False
   - comment_min_len = 0
   - max_images = 0
   - image_max_mb = 1
6. Create YES option:
   - question_id = question.id
   - option_type = OptionType.YES
   - score = yes_score
   - require_comment = False
   - require_image = False
   - comment_min_len = 0
   - max_images = 0
   - image_max_mb = 1
7. Return question instance

**Error Handling**:
- group_id not found: Raise SQLAlchemyError (foreign key violation)
- Invalid score (not 0 or 1): Raise ValueError
- Database connection error: Raise SQLAlchemyError
- Constraint violation: Raise SQLAlchemyError (duplicate text within group)

**Preconditions**:
- session is active
- group_id exists in question_groups table
- text is non-empty string
- order > 0
- no_score in {0, 1}
- yes_score in {0, 1}

**Postconditions**:
- Returned Question has valid ID
- Question is persisted in database
- Question.group_id matches group_id parameter
- Question has exactly 2 QuestionOption children (NO and YES)
- NO option has score = no_score parameter
- YES option has score = yes_score parameter
- Both options have require_comment = False, require_image = False

---

### seed_questions()

**Signature**:
```python
async def seed_questions(session: AsyncSession) -> SeedStats:
    """Main entry point: Parse all markdown files and seed database.

    This is the primary function called by `python -m src.seeds.questions_seed`.

    Args:
        session: Async SQLAlchemy session

    Returns:
        SeedStats with counts of created/updated entities and errors

    Raises:
        FileNotFoundError: If questions/ folder does not exist
        SQLAlchemyError: If critical database operation fails

    Example:
        >>> stats = await seed_questions(session)
        >>> stats.types_created
        6
        >>> stats.questions_created
        243
        >>> stats.errors
        0
    """
```

**Algorithm**:
1. Verify questions/ folder exists
2. Find all *.md files using glob pattern
3. Initialize counters: types=0, groups=0, questions=0, options=0, errors=0
4. For each markdown file:
   - Try:
     - Parse file with parse_markdown_file()
     - For each ParsedType:
       - Create questionnaire type, increment types counter
       - For each ParsedGroup:
         - Create question group, increment groups counter
         - For each ParsedQuestion:
           - Determine no_score and yes_score based on inverse scoring logic
           - Create question, increment questions counter
           - Increment options counter by 2
   - Except Exception as e:
     - Log error with file path and line number
     - Increment errors counter
     - Continue to next file
5. Commit transaction
6. Print summary report
7. Return SeedStats

**Error Handling**:
- questions/ folder not found: Raise FileNotFoundError
- Critical database error (connection lost): Raise SQLAlchemyError
- Per-file errors: Log and continue (don't raise)

**Preconditions**:
- session is active
- questions/ folder exists in current working directory or project root

**Postconditions**:
- All valid markdown files processed
- Database contains all types, groups, questions, options from markdown files
- Returned SeedStats reflects actual counts
- Transaction committed (or rolled back on critical error)

## Inverse Scoring Logic

**Specification**: When one option has score 1, the other must have score 0

```python
def calculate_scores(option_text: str, score: int) -> tuple[int, int]:
    """Calculate NO and YES scores based on parsed option.

    Args:
        option_text: "Үгүй" or "Тийм"
        score: Parsed score (0 or 1)

    Returns:
        (no_score, yes_score) tuple

    Examples:
        >>> calculate_scores("Үгүй", 1)
        (1, 0)
        >>> calculate_scores("Тийм", 1)
        (0, 1)
        >>> calculate_scores("Үгүй", 0)
        (0, 0)
    """
    if option_text == "Үгүй" and score == 1:
        return (1, 0)
    elif option_text == "Тийм" and score == 1:
        return (0, 1)
    else:
        # Both can be 0
        return (0, 0)
```

## Error Messages

**Format**: `{file_path}:{line_number}: {error_type}: {message}`

**Examples**:
```
questions/fire_safety.md:15: ValueError: Invalid score '2' (must be 0 or 1)
questions/fire_safety.md:23: ValueError: Invalid option text 'Maybe' (must be Үгүй or Тийм)
questions/electrical.md:8: UnicodeDecodeError: File is not valid UTF-8 encoding
```

**Logging Levels**:
- ERROR: Critical errors that stop file processing (encoding errors)
- WARNING: Recoverable errors (invalid question line, skipped)
- INFO: Progress updates (processing file X of Y)

## Performance Requirements

**From Spec (SC-002)**: Complete in under 30 seconds for all question files

**Benchmarks** (estimated):
- File I/O: ~1 second for 6-10 files
- Parsing: ~2 seconds for ~300 questions
- Database operations: ~10 seconds for ~600 options (upsert)
- Total: ~13 seconds (well under 30-second target)

**Optimization Threshold**:
- If total time > 25 seconds: Consider batch operations
- If total time > 30 seconds: FAIL (spec requirement not met)

## Testing Interface

### Unit Tests

```python
def test_parse_question_line_valid():
    """Test parsing valid question line."""
    line = "Question text here        Үгүй    1"
    text, option, score = parse_question_line(line)
    assert text == "Question text here"
    assert option == "Үгүй"
    assert score == 1

def test_inverse_scoring_logic():
    """Test inverse scoring calculation."""
    no_score, yes_score = calculate_scores("Үгүй", 1)
    assert no_score == 1
    assert yes_score == 0

def test_create_question_with_options():
    """Test question creation with two options."""
    question = await create_question(session, group_id, "Test", 1, 1, 0)
    options = await get_options_for_question(session, question.id)
    assert len(options) == 2
    assert options[0].option_type == OptionType.NO
    assert options[0].score == 1
    assert options[1].option_type == OptionType.YES
    assert options[1].score == 0
```

### Integration Tests

```python
async def test_seed_markdown_file():
    """Test end-to-end seeding of a markdown file."""
    stats = await seed_questions(session)
    assert stats.errors == 0
    assert stats.questions_created > 0

    # Verify database state
    types = await get_all_types(session)
    assert len(types) > 0

    questions = await get_all_questions(session)
    assert len(questions) == stats.questions_created
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-08 | Initial API contract definition |
