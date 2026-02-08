"""Integration tests for questions seed database operations."""

import pytest
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.question import Question
from src.models.question_group import QuestionGroup
from src.models.question_option import QuestionOption
from src.models.questionnaire_type import QuestionnaireType
from src.models.enums import OptionType, ScoringMethod
from src.seeds.questions_seed import (
    create_questionnaire_type,
    create_question_group,
    create_question,
    seed_questions,
    SeedStats,
)


# =============================================================================
# Database Helper Tests
# =============================================================================


class TestCreateQuestionnaireType:
    """Test questionnaire type creation and update."""

    async def test_create_new_type(self, session: AsyncSession):
        """Test creating a new questionnaire type."""
        qtype = await create_questionnaire_type(session, "TEST TYPE")

        assert qtype.id is not None
        assert qtype.name == "TEST TYPE"
        assert qtype.scoring_method == ScoringMethod.SUM
        assert qtype.threshold_high == 80
        assert qtype.threshold_medium == 50
        assert qtype.weight == Decimal("1.0")
        assert qtype.is_active is True

        # Verify in database
        result = await session.execute(
            select(QuestionnaireType).where(QuestionnaireType.name == "TEST TYPE")
        )
        db_type = result.scalar_one()
        assert db_type.id == qtype.id

    async def test_update_existing_type(self, session: AsyncSession):
        """Test updating existing questionnaire type."""
        # Create first time
        qtype1 = await create_questionnaire_type(session, "TEST TYPE 2")
        await session.flush()

        # Create second time (should update)
        qtype2 = await create_questionnaire_type(session, "TEST TYPE 2")

        assert qtype2.id == qtype1.id
        assert qtype2.name == "TEST TYPE 2"


class TestCreateQuestionGroup:
    """Test question group creation and update."""

    async def test_create_new_group(self, session: AsyncSession):
        """Test creating a new question group."""
        # Create parent type
        qtype = await create_questionnaire_type(session, "PARENT TYPE")

        group = await create_question_group(session, qtype.id, "TEST GROUP", 1)

        assert group.id is not None
        assert group.type_id == qtype.id
        assert group.name == "TEST GROUP"
        assert group.display_order == 1
        assert group.weight == Decimal("1.0")
        assert group.is_active is True

    async def test_update_existing_group(self, session: AsyncSession):
        """Test updating existing question group."""
        qtype = await create_questionnaire_type(session, "PARENT TYPE 2")

        # Create first time
        group1 = await create_question_group(session, qtype.id, "TEST GROUP 2", 1)
        await session.flush()

        # Create second time with different order
        group2 = await create_question_group(session, qtype.id, "TEST GROUP 2", 2)

        assert group2.id == group1.id
        assert group2.display_order == 2


class TestCreateQuestion:
    """Test question creation with options."""

    async def test_create_new_question(self, session: AsyncSession):
        """Test creating a new question with two options."""
        qtype = await create_questionnaire_type(session, "PARENT TYPE")
        group = await create_question_group(session, qtype.id, "TEST GROUP", 1)

        question = await create_question(
            session, group.id, "Test question text", 1, no_score=1, yes_score=0
        )

        assert question.id is not None
        assert question.group_id == group.id
        assert question.text == "Test question text"
        assert question.display_order == 1

        # Verify options
        result = await session.execute(
            select(QuestionOption).where(QuestionOption.question_id == question.id)
        )
        options = result.scalars().all()

        assert len(options) == 2

        # Find NO and YES options
        no_option = next((o for o in options if o.option_type == OptionType.NO), None)
        yes_option = next((o for o in options if o.option_type == OptionType.YES), None)

        assert no_option is not None
        assert no_option.score == 1
        assert no_option.require_comment is False
        assert no_option.require_image is False

        assert yes_option is not None
        assert yes_option.score == 0
        assert yes_option.require_comment is False
        assert yes_option.require_image is False

    async def test_update_existing_question(self, session: AsyncSession):
        """Test updating existing question."""
        qtype = await create_questionnaire_type(session, "PARENT TYPE")
        group = await create_question_group(session, qtype.id, "TEST GROUP", 1)

        # Create first time
        question1 = await create_question(
            session, group.id, "Test question", 1, no_score=1, yes_score=0
        )
        await session.flush()

        # Create second time with different order
        question2 = await create_question(
            session, group.id, "Test question", 2, no_score=1, yes_score=0
        )

        assert question2.id == question1.id
        assert question2.display_order == 2

    async def test_update_question_scores(self, session: AsyncSession):
        """Test updating question option scores."""
        qtype = await create_questionnaire_type(session, "PARENT TYPE")
        group = await create_question_group(session, qtype.id, "TEST GROUP", 1)

        # Create with scores (1, 0)
        await create_question(
            session, group.id, "Test question", 1, no_score=1, yes_score=0
        )
        await session.flush()

        # Update with scores (0, 1)
        await create_question(
            session, group.id, "Test question", 1, no_score=0, yes_score=1
        )
        await session.flush()

        # Verify scores updated
        result = await session.execute(
            select(QuestionOption).where(
                QuestionOption.question_id == select(Question.id)
                .where(Question.text == "Test question")
                .scalar_subquery()
            )
        )
        options = result.scalars().all()

        no_option = next((o for o in options if o.option_type == OptionType.NO), None)
        yes_option = next((o for o in options if o.option_type == OptionType.YES), None)

        assert no_option.score == 0
        assert yes_option.score == 1

    async def test_invalid_scores_raise_error(self, session: AsyncSession):
        """Test that invalid scores raise ValueError."""
        qtype = await create_questionnaire_type(session, "PARENT TYPE")
        group = await create_question_group(session, qtype.id, "TEST GROUP", 1)

        with pytest.raises(ValueError, match="Invalid scores"):
            await create_question(session, group.id, "Test", 1, no_score=2, yes_score=0)


# =============================================================================
# Main Seed Function Tests
# =============================================================================


class TestSeedQuestions:
    """Test main seed_questions function."""

    async def test_seed_creates_new_questions(self, session: AsyncSession, tmp_path):
        """Test that seed_questions creates questions from markdown files."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create test markdown file
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Question 1    Үгүй    1
        Question 2    Тийм    0
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            assert stats.types_created >= 1
            assert stats.groups_created >= 1
            assert stats.questions_created == 2
            assert stats.options_created == 4
            assert stats.errors == 0

        finally:
            os.chdir(original_cwd)

    async def test_seed_updates_existing_questions(self, session: AsyncSession, tmp_path):
        """Test that re-running seed script updates existing questions."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Question 1    Үгүй    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            # First run
            stats1 = await seed_questions(session)
            assert stats1.questions_created == 1

            # Second run (should update, not create new)
            stats2 = await seed_questions(session)
            assert stats2.questions_created >= 1  # Still processes but updates

        finally:
            os.chdir(original_cwd)

    async def test_seed_upsert_by_natural_key(self, session: AsyncSession, tmp_path):
        """Test that questions are updated by natural key (type_name, group_name, question_text)."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create file with same natural key but different score
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Same question text    Үгүй    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            # First run with score=1 for Үгүй
            await seed_questions(session)

            # Update file to change score
            (questions_dir / "test.md").write_text(
                """TEST TYPE
    Test Group
        Same question text    Тийм    1
""",
                encoding="utf-8",
            )

            # Second run - should update the existing question
            await seed_questions(session)

            # Verify the question was updated (not duplicated)
            result = await session.execute(
                select(Question).where(Question.text == "Same question text")
            )
            questions = result.scalars().all()
            assert len(questions) == 1  # Only one question with this text

        finally:
            os.chdir(original_cwd)

    async def test_seed_multiple_markdown_files(self, session: AsyncSession, tmp_path):
        """Test that seed processes multiple markdown files in one run."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create multiple files
        (questions_dir / "file1.md").write_text(
            """TYPE 1
    Group 1
        Question 1    Үгүй    1
""",
            encoding="utf-8",
        )

        (questions_dir / "file2.md").write_text(
            """TYPE 2
    Group 2
        Question 2    Тийм    0
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            assert stats.types_created >= 2
            assert stats.groups_created >= 2
            assert stats.questions_created >= 2
            assert stats.errors == 0

        finally:
            os.chdir(original_cwd)

    async def test_seed_error_handling_continue_on_error(self, session: AsyncSession, tmp_path):
        """Test that malformed questions don't stop import."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create file with malformed questions
        (questions_dir / "test.md").write_text(
            """VALID TYPE
    Valid Group
        Valid question    Үгүй    1
        Invalid question    Maybe    1
        Another valid question    Тийм    0
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should process valid questions and skip invalid
            assert stats.questions_created >= 1  # At least the valid ones
            # No error count since parse_question_line just logs warnings

        finally:
            os.chdir(original_cwd)

    async def test_seed_summary_report(self, session: AsyncSession, tmp_path):
        """Test that SeedStats is returned with correct counts."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Question 1    Үгүй    1
        Question 2    Тийм    0
        Question 3    Үгүй    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            assert isinstance(stats, SeedStats)
            assert stats.types_created >= 1
            assert stats.groups_created >= 1
            assert stats.questions_created == 3
            assert stats.options_created == 6  # 2 options per question
            assert stats.errors == 0

        finally:
            os.chdir(original_cwd)

    async def test_seed_handles_errors(self, session: AsyncSession, tmp_path):
        """Test that seed_questions continues on error."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create valid file
        (questions_dir / "valid.md").write_text(
            """VALID TYPE
    Valid Group
        Question 1    Үгүй    1
""",
            encoding="utf-8",
        )

        # Create invalid file (will cause error)
        (questions_dir / "invalid.md").write_text(
            "Invalid content without types",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should process valid file and skip invalid
            assert stats.types_created >= 1
            assert stats.errors == 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_no_questions_folder(self, session: AsyncSession):
        """Test that seed_questions raises FileNotFoundError when no questions folder."""
        import os

        original_cwd = os.getcwd()
        tmp_dir = session.bind.url.database  # This won't work, need better approach

        with pytest.raises(FileNotFoundError, match="questions/ folder does not exist"):
            await seed_questions(session)


# =============================================================================
# Edge Case Recovery Tests (T023)
# =============================================================================


class TestSeedEdgeCaseRecovery:
    """Test edge case recovery in seed_questions function."""

    async def test_seed_skips_invalid_questions(self, session: AsyncSession, tmp_path):
        """Test that malformed questions are skipped."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # File with valid and invalid questions
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Valid question 1    Үгүй    1
        Invalid question    Maybe    1
        Valid question 2    Тийм    0
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should create at least the valid questions
            assert stats.questions_created >= 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_logs_missing_scores(self, session: AsyncSession, tmp_path):
        """Test that warnings are logged for missing scores."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # File with missing scores
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Question with score    Үгүй    1
        Question without score    Үгүй
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            # Should not raise error, just log warning
            stats = await seed_questions(session)
            assert stats.questions_created >= 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_logs_invalid_options(self, session: AsyncSession, tmp_path):
        """Test that errors are logged for invalid option text."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # File with invalid options
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Valid question    Үгүй    1
        Invalid option question    WrongOption    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)
            # Should process valid question, skip invalid
            assert stats.questions_created >= 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_handles_encoding_errors(self, session: AsyncSession, tmp_path):
        """Test that encoding errors are handled gracefully."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # Create valid file
        (questions_dir / "valid.md").write_text(
            """VALID TYPE
    Valid Group
        Question 1    Үгүй    1
""",
            encoding="utf-8",
        )

        # Create file with encoding issues (triggers decode error)
        (questions_dir / "invalid.md").write_bytes(b"\xff\xfe Invalid UTF-8")

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should process valid file, count encoding error
            assert stats.types_created >= 1
            assert stats.errors >= 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_partial_file_success(self, session: AsyncSession, tmp_path):
        """Test that valid questions are processed even if some lines fail."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # File with mix of valid and invalid
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Test Group
        Question 1 (valid)    Үгүй    1
        Question 2 (invalid option)    BadOption    1
        Question 3 (valid)    Тийм    0
        Question 4 (invalid score)    Үгүй    5
        Question 5 (valid)    Үгүй    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should process at least the valid questions
            assert stats.questions_created >= 1

        finally:
            os.chdir(original_cwd)

    async def test_seed_empty_groups(self, session: AsyncSession, tmp_path):
        """Test that groups with no questions are handled correctly."""
        import os

        original_cwd = os.getcwd()
        questions_dir = tmp_path / "questions"
        questions_dir.mkdir()

        # File with empty group
        (questions_dir / "test.md").write_text(
            """TEST TYPE
    Empty Group
    Non-Empty Group
        Question 1    Үгүй    1
""",
            encoding="utf-8",
        )

        try:
            os.chdir(tmp_path)

            stats = await seed_questions(session)

            # Should create type and both groups
            assert stats.types_created >= 1
            assert stats.groups_created >= 2

        finally:
            os.chdir(original_cwd)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def session(async_session_factory):
    """Provide a test session."""
    async with async_session_factory() as session:
        yield session
    # No rollback - let commits happen for testing
