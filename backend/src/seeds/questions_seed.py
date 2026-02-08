"""Seed script to import questions from markdown files into the database.

Run with: python -m src.seeds.questions_seed
"""

import asyncio
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.models.question import Question
from src.models.question_group import QuestionGroup
from src.models.question_option import QuestionOption
from src.models.questionnaire_type import QuestionnaireType
from src.models.enums import OptionType, ScoringMethod


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes for Parsed Question Data
# =============================================================================


@dataclass
class ParsedQuestion:
    """A single question with parsed option and score.

    Attributes:
        text: Question text in Mongolian Cyrillic.
        option_text: "Үгүй" or "Тийм".
        score: 0 or 1.
    """

    text: str
    option_text: str  # "Үгүй" or "Тийм"
    score: int  # 0 or 1


@dataclass
class ParsedGroup:
    """A group of questions with a name.

    Attributes:
        name: Group name in Mongolian Cyrillic.
        questions: List of questions in this group.
    """

    name: str
    questions: list[ParsedQuestion] = field(default_factory=list)


@dataclass
class ParsedType:
    """A questionnaire type containing multiple groups.

    Attributes:
        name: Type name in Mongolian Cyrillic.
        groups: List of groups in this type.
    """

    name: str
    groups: list[ParsedGroup] = field(default_factory=list)


@dataclass
class ParsedQuestionData:
    """Complete parsed data from one markdown file.

    Attributes:
        types: List of questionnaire types found in the file.
    """

    types: list[ParsedType] = field(default_factory=list)


@dataclass
class SeedStats:
    """Summary statistics from seed operation.

    Attributes:
        types_created: Number of types created or updated.
        groups_created: Number of groups created or updated.
        questions_created: Number of questions created or updated.
        options_created: Number of options created or updated.
        errors: Number of errors encountered during seeding.
    """

    types_created: int = 0
    groups_created: int = 0
    questions_created: int = 0
    options_created: int = 0
    errors: int = 0


# =============================================================================
# Inverse Scoring Logic
# =============================================================================


def calculate_scores(option_text: str, score: int) -> tuple[int, int]:
    """Calculate NO and YES scores based on parsed option.

    Implements inverse scoring logic: if one option has score 1,
    the other gets score 0. Both can have score 0.

    Args:
        option_text: "Үгүй" or "Тийм".
        score: Parsed score (0 or 1).

    Returns:
        Tuple of (no_score, yes_score).

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


# =============================================================================
# Parsing Functions
# =============================================================================


def parse_question_line(
    line: str, file_path: str, line_number: int
) -> tuple[str, str, int] | None:
    """Parse a single question line to extract text, option, and score.

    Question line format (8+ space indent or 2+ tabs):
        Question text here[TAB]Үгүй/Тийм[TAB]0/1

    Args:
        line: The line to parse.
        file_path: Path to file for error messages.
        line_number: Line number for error messages.

    Returns:
        Tuple of (question_text, option_text, score) or None if parsing fails.
    """
    try:
        # Strip leading whitespace (spaces/tabs) first
        content = line.lstrip()

        # Split by tab
        parts = content.split('\t')

        # Clean up each part (strip whitespace)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) < 2:
            # Not enough parts even for text + option
            logger.warning(
                f"{file_path}:{line_number}: Warning: Question line missing parts, "
                f"skipping: '{content[:80]}'"
            )
            return None

        if len(parts) == 2:
            # Missing score, use default 0
            text, option_text = parts[0], parts[1]
            score_str = None
        else:
            # Has all three parts
            text, option_text, score_str = parts[0], parts[1], parts[2]

        # Validate option text first (before trying to parse score)
        if option_text not in ("Үгүй", "Тийм"):
            logger.warning(
                f"{file_path}:{line_number}: Warning: Invalid option '{option_text}', "
                f"skipping question: '{text[:50]}'"
            )
            return None

        # Validate and convert score if present
        if score_str is None:
            score = 0
        else:
            try:
                score = int(score_str.strip())
                if score not in (0, 1):
                    logger.warning(
                        f"{file_path}:{line_number}: Warning: Invalid score '{score_str}', "
                        f"using default 0: '{text[:50]}'"
                    )
                    score = 0
            except ValueError:
                logger.warning(
                    f"{file_path}:{line_number}: Warning: Score not an integer '{score_str}', "
                    f"using default 0: '{text[:50]}'"
                )
                score = 0

        return (text, option_text, score)

    except Exception as e:
        logger.warning(
            f"{file_path}:{line_number}: Warning: Failed to parse question line: {e}"
        )
        return None


def parse_markdown_file(file_path: Path) -> ParsedQuestionData:
    """Parse a single markdown file and extract question data.

    File format:
        Filename: Type - TYPE NAME.md (extract type name from filename)
           Group Name (3-space indent, no tabs)
           \t\tQuestion text\t\tOption\t\tScore (3 spaces + 2 tabs)

    Args:
        file_path: Path to markdown file (must exist, readable, UTF-8 encoded).

    Returns:
        ParsedQuestionData with all types, groups, and questions found in file.

    Raises:
        FileNotFoundError: If file_path does not exist.
        UnicodeDecodeError: If file is not valid UTF-8.
        ValueError: If file format is invalid (no parseable content).
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Extract type name from filename
    # Format: "Type - TYPE NAME.md" or "Type - TYPE NAME something.md"
    filename = file_path.stem  # Get filename without extension
    if filename.startswith("Type - "):
        type_name = filename[7:].strip()  # Remove "Type - " prefix
    else:
        type_name = filename
        logger.warning(
            f"{file_path}: Warning: Filename doesn't follow 'Type - NAME.md' format, "
            f"using '{type_name}' as type name"
        )

    # Create the type for this file
    current_type = ParsedType(name=type_name)
    result = ParsedQuestionData(types=[current_type])
    current_group: ParsedGroup | None = None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                # Count leading spaces and tabs character by character
                leading_spaces = 0
                leading_tabs = 0
                for char in line:
                    if char == ' ':
                        leading_spaces += 1
                    elif char == '\t':
                        leading_tabs += 1
                    else:
                        break

                # Check if line contains tabs (used as separators between parts)
                has_tabs = '\t' in line

                # Group header (0 leading spaces, NO leading tabs)
                # Groups have no indentation at all, but may have trailing tabs.
                # Key difference from question lines: group headers DON'T end with Үгүй/Тийм option.
                if leading_spaces == 0 and leading_tabs == 0:
                    # Check if this looks like a question line (ends with Үгүй or Тийм option)
                    # Split by tabs and check the last non-empty part
                    parts = [p.strip() for p in line.split('\t') if p.strip()]
                    last_part = parts[-1] if parts else ""
                    is_question_line = last_part in ("Үгүй", "Тийм")

                    if not is_question_line:
                        # This is a group header (with or without trailing tabs)
                        # Remove trailing tabs, colon, and whitespace
                        group_name = stripped.rstrip(":\t").strip()
                        current_group = ParsedGroup(name=group_name)
                        current_type.groups.append(current_group)
                    else:
                        # This is a question line with no indentation
                        # Treat it as a question if we have a group
                        if current_group is not None:
                            parsed = parse_question_line(line, str(file_path), line_number)
                            if parsed:
                                text, option_text, score = parsed
                                text = text.strip()
                                question = ParsedQuestion(
                                    text=text, option_text=option_text, score=score
                                )
                                current_group.questions.append(question)
                        else:
                            logger.warning(
                                f"{file_path}:{line_number}: Warning: Question without "
                                f"group, skipping: '{stripped[:50]}'"
                            )

                # Question line (5-7 leading spaces OR leading tabs AND has tabs for separators)
                # Format: "       Question text\t\tOption\t\tScore" (5-7 spaces + tabs)
                # OR: "\tQuestion text\t\tOption\t\tScore" (tab + tabs)
                elif (leading_spaces >= 5 or leading_tabs > 0) and has_tabs:
                    if current_group is None:
                        logger.warning(
                            f"{file_path}:{line_number}: Warning: Question without "
                            f"group, skipping: '{stripped[:50]}'"
                        )
                        continue

                    parsed = parse_question_line(line, str(file_path), line_number)
                    if parsed:
                        text, option_text, score = parsed
                        # Strip leading whitespace from question text
                        text = text.strip()
                        question = ParsedQuestion(
                            text=text, option_text=option_text, score=score
                        )
                        current_group.questions.append(question)

                # Skip other lines
                else:
                    logger.debug(
                        f"{file_path}:{line_number}: Skipping line (spaces={leading_spaces}, "
                        f"tabs={leading_tabs}): '{stripped[:50]}'"
                    )

    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"File is not valid UTF-8 encoding: {file_path}",
        )

    # Validate we got something
    total_questions = sum(len(g.questions) for g in current_type.groups)
    if total_questions == 0:
        raise ValueError(f"No parseable content in {file_path}")

    return result


# =============================================================================
# Database Helper Functions
# =============================================================================


async def create_questionnaire_type(
    session: AsyncSession, name: str
) -> QuestionnaireType:
    """Create or update a questionnaire type.

    Args:
        session: Async SQLAlchemy session.
        name: Type name in Mongolian Cyrillic.

    Returns:
        Created or updated QuestionnaireType instance.
    """
    # Check if exists
    result = await session.execute(
        select(QuestionnaireType).where(QuestionnaireType.name == name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update timestamp
        existing.updated_at = existing.updated_at  # Trigger onupdate
        return existing

    # Create new
    qtype = QuestionnaireType(
        id=uuid4(),
        name=name,
        scoring_method=ScoringMethod.SUM,
        threshold_high=80,
        threshold_medium=50,
        weight=Decimal("1.0"),
        is_active=True,
    )
    session.add(qtype)
    await session.flush()
    return qtype


async def create_question_group(
    session: AsyncSession, type_id: uuid4, name: str, order: int
) -> QuestionGroup:
    """Create or update a question group.

    Args:
        session: Async SQLAlchemy session.
        type_id: Parent questionnaire type ID.
        name: Group name in Mongolian Cyrillic.
        order: Display order within type (1, 2, 3...).

    Returns:
        Created or updated QuestionGroup instance.
    """
    # Check if exists by (type_id, name)
    result = await session.execute(
        select(QuestionGroup).where(
            QuestionGroup.type_id == type_id, QuestionGroup.name == name
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update display_order if changed
        if existing.display_order != order:
            existing.display_order = order
        return existing

    # Create new
    group = QuestionGroup(
        id=uuid4(),
        type_id=type_id,
        name=name,
        display_order=order,
        weight=Decimal("1.0"),
        is_active=True,
    )
    session.add(group)
    await session.flush()
    return group


async def create_question(
    session: AsyncSession,
    group_id: uuid4,
    text: str,
    order: int,
    no_score: int,
    yes_score: int,
) -> Question:
    """Create or update a question with two options (NO and YES).

    Args:
        session: Async SQLAlchemy session.
        group_id: Parent question group ID.
        text: Question text in Mongolian Cyrillic.
        order: Display order within group (1, 2, 3...).
        no_score: Score for Үгүй (NO) option (0 or 1).
        yes_score: Score for Тийм (YES) option (0 or 1).

    Returns:
        Created or updated Question instance.
    """
    # Validate scores
    if no_score not in (0, 1) or yes_score not in (0, 1):
        raise ValueError(
            f"Invalid scores: no_score={no_score}, yes_score={yes_score} "
            f"(must be 0 or 1)"
        )

    # Check if exists by (group_id, text)
    result = await session.execute(
        select(Question).where(Question.group_id == group_id, Question.text == text)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update display_order if changed
        if existing.display_order != order:
            existing.display_order = order
        question_id = existing.id
    else:
        # Create new question
        question = Question(
            id=uuid4(),
            group_id=group_id,
            text=text,
            display_order=order,
            weight=Decimal("1.0"),
            is_critical=False,
            is_active=True,
        )
        session.add(question)
        await session.flush()
        question_id = question.id

    # Delete existing options (will recreate)
    await session.execute(
        select(QuestionOption).where(QuestionOption.question_id == question_id)
    )
    # Note: We're not actually deleting here, just querying.
    # In production, we'd do a proper delete or update.

    # Check if options already exist and update/create
    for option_type, score in [
        (OptionType.NO, no_score),
        (OptionType.YES, yes_score),
    ]:
        result = await session.execute(
            select(QuestionOption).where(
                QuestionOption.question_id == question_id,
                QuestionOption.option_type == option_type,
            )
        )
        existing_option = result.scalar_one_or_none()

        if existing_option:
            # Update score if changed
            if existing_option.score != score:
                existing_option.score = score
        else:
            # Create new option
            # Note: max_images=1 due to database constraint ck_max_images_range
            new_option = QuestionOption(
                id=uuid4(),
                question_id=question_id,
                option_type=option_type,
                score=score,
                require_comment=False,
                require_image=False,
                comment_min_len=0,
                max_images=1,  # Minimum allowed by constraint
                image_max_mb=1,
            )
            session.add(new_option)

    await session.flush()

    # Return the question (existing or new)
    result = await session.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one()


# =============================================================================
# Main Seed Function
# =============================================================================


async def seed_questions(session: AsyncSession) -> SeedStats:
    """Main entry point: Parse all markdown files and seed database.

    This is the primary function called by `python -m src.seeds.questions_seed`.

    Args:
        session: Async SQLAlchemy session.

    Returns:
        SeedStats with counts of created/updated entities and errors.
    """
    stats = SeedStats()

    # Find questions folder (relative to project root)
    # When running in Docker, the questions folder is mounted at /app/questions
    # When running locally, it's relative to the backend directory
    questions_dir = Path("/app/questions")
    if not questions_dir.exists():
        # Fallback to local development path
        questions_dir = Path(__file__).parent.parent.parent.parent / "questions"
    if not questions_dir.exists():
        raise FileNotFoundError(
            "questions/ folder does not exist. "
            "Please create it and add markdown files with question data."
        )

    # Find all markdown files (excluding test files)
    md_files = [f for f in questions_dir.glob("*.md") if f.name != "test_valid.md"]
    if not md_files:
        raise FileNotFoundError(
            f"No markdown files found in {questions_dir}/. "
            "Please add .md files with question data."
        )

    logger.info(f"Found {len(md_files)} markdown file(s) in {questions_dir}/")

    # Process each file
    for md_file in md_files:
        try:
            logger.info(f"Processing: {md_file.name}")

            # Parse file
            parsed_data = parse_markdown_file(md_file)

            # Create types, groups, questions
            for parsed_type in parsed_data.types:
                qtype = await create_questionnaire_type(session, parsed_type.name)
                stats.types_created += 1
                logger.info(f"  Type: {qtype.name}")

                for group_order, parsed_group in enumerate(parsed_type.groups, start=1):
                    group = await create_question_group(
                        session, qtype.id, parsed_group.name, group_order
                    )
                    stats.groups_created += 1
                    logger.info(f"    Group: {group.name}")

                    for q_order, parsed_question in enumerate(
                        parsed_group.questions, start=1
                    ):
                        # Calculate inverse scores
                        no_score, yes_score = calculate_scores(
                            parsed_question.option_text, parsed_question.score
                        )

                        # Create question with options
                        await create_question(
                            session,
                            group.id,
                            parsed_question.text,
                            q_order,
                            no_score,
                            yes_score,
                        )
                        stats.questions_created += 1
                        stats.options_created += 2

                    logger.info(f"      Created {len(parsed_group.questions)} questions")

        except Exception as e:
            logger.error(f"Error processing {md_file.name}: {e}")
            stats.errors += 1
            continue

    # Commit all changes
    await session.commit()

    return stats


# =============================================================================
# CLI Entry Point
# =============================================================================


async def main():
    """Main entry point for seeding.

    Run with: python -m src.seeds.questions_seed
    """
    print("Starting question seed...")
    print("=" * 50)

    try:
        async with async_session_factory() as session:
            stats = await seed_questions(session)

        print("=" * 50)
        print("Seed completed!")
        print(f"  Types: {stats.types_created}")
        print(f"  Groups: {stats.groups_created}")
        print(f"  Questions: {stats.questions_created}")
        print(f"  Options: {stats.options_created}")
        if stats.errors > 0:
            print(f"  Errors: {stats.errors}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"Error: {e}")
        import sys

        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error during seed: {e}", exc_info=True)
        print(f"Critical error: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# Verification Queries
# =============================================================================

"""
VERIFICATION QUERIES
====================

After running the seed script, use these SQL queries to verify the import:

1. List all questionnaire types with question counts:
```sql
SELECT
    qt.id,
    qt.name,
    qt.is_active,
    COUNT(DISTINCT qg.id) as group_count,
    COUNT(DISTINCT q.id) as question_count
FROM questionnaire_types qt
LEFT JOIN question_groups qg ON qt.id = qg.type_id
LEFT JOIN questions q ON qg.id = q.group_id
GROUP BY qt.id, qt.name, qt.is_active
ORDER BY qt.name;
```

2. Show questions with their options and scores:
```sql
SELECT
    qt.name as type_name,
    qg.name as group_name,
    q.text as question_text,
    qo.option_type,
    qo.score
FROM questionnaire_types qt
JOIN question_groups qg ON qt.id = qg.type_id
JOIN questions q ON qg.id = q.group_id
JOIN question_options qo ON q.id = qo.question_id
ORDER BY qt.name, qg.name, q.display_order, qo.option_type;
```

3. Lookup by natural key (type_name, group_name, question_text):
```sql
SELECT
    q.id,
    q.text,
    qo.option_type,
    qo.score
FROM questionnaire_types qt
JOIN question_groups qg ON qt.id = qg.type_id AND qt.name = 'YOUR_TYPE_NAME'
JOIN questions q ON qg.id = q.group_id AND q.text = 'YOUR_QUESTION_TEXT'
JOIN question_options qo ON q.id = qo.question_id;
```

4. Verify inverse scoring (NO and YES scores should be opposite):
```sql
SELECT
    qt.name as type_name,
    qg.name as group_name,
    q.text as question_text,
    MAX(CASE WHEN qo.option_type = 'NO' THEN qo.score END) as no_score,
    MAX(CASE WHEN qo.option_type = 'YES' THEN qo.score END) as yes_score,
    CASE
        WHEN MAX(CASE WHEN qo.option_type = 'NO' THEN qo.score END) = 1
        AND MAX(CASE WHEN qo.option_type = 'YES' THEN qo.score END) = 0
        THEN 'Inverse OK'
        WHEN MAX(CASE WHEN qo.option_type = 'NO' THEN qo.score END) = 0
        AND MAX(CASE WHEN qo.option_type = 'YES' THEN qo.score END) = 1
        THEN 'Inverse OK'
        WHEN MAX(CASE WHEN qo.option_type = 'NO' THEN qo.score END) = 0
        AND MAX(CASE WHEN qo.option_type = 'YES' THEN qo.score END) = 0
        THEN 'Both Zero OK'
        ELSE 'CHECK: Both scores are 1!'
    END as scoring_status
FROM questionnaire_types qt
JOIN question_groups qg ON qt.id = qg.type_id
JOIN questions q ON qg.id = q.group_id
JOIN question_options qo ON q.id = qo.question_id
GROUP BY qt.id, qt.name, qg.id, qg.name, q.id, q.text
ORDER BY scoring_status DESC, qt.name, qg.name, q.display_order;
```

5. Full hierarchy display:
```sql
SELECT
    qt.name as type,
    qg.name as group,
    q.text as question,
    STRING_AGG(
        qo.option_type || '=' || qo.score,
        ', ' ORDER BY qo.option_type
    ) as scores
FROM questionnaire_types qt
JOIN question_groups qg ON qt.id = qg.type_id
JOIN questions q ON qg.id = q.group_id
JOIN question_options qo ON q.id = qo.question_id
GROUP BY qt.id, qt.name, qg.id, qg.name, q.id, q.text
ORDER BY qt.name, qg.display_order, q.display_order;
```

6. Count all entities:
```sql
SELECT
    'questionnaire_types' as entity_type,
    COUNT(*) as count
FROM questionnaire_types
UNION ALL
SELECT 'question_groups', COUNT(*) FROM question_groups
UNION ALL
SELECT 'questions', COUNT(*) FROM questions
UNION ALL
SELECT 'question_options', COUNT(*) FROM question_options;
```
"""
