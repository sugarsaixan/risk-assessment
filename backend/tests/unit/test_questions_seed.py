"""Unit tests for questions seed parsing logic."""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.seeds.questions_seed import (
    ParsedQuestion,
    ParsedGroup,
    ParsedType,
    ParsedQuestionData,
    calculate_scores,
    parse_question_line,
    parse_markdown_file,
)


# =============================================================================
# Inverse Scoring Tests
# =============================================================================


class TestCalculateScores:
    """Test inverse scoring calculation."""

    def test_үгүй_1(self):
        """Test Үгүй with score 1 → (1, 0)."""
        no_score, yes_score = calculate_scores("Үгүй", 1)
        assert no_score == 1
        assert yes_score == 0

    def test_тийм_1(self):
        """Test Тийм with score 1 → (0, 1)."""
        no_score, yes_score = calculate_scores("Тийм", 1)
        assert no_score == 0
        assert yes_score == 1

    def test_both_0(self):
        """Test both scores 0 → (0, 0)."""
        no_score, yes_score = calculate_scores("Үгүй", 0)
        assert no_score == 0
        assert yes_score == 0

    def test_тийм_0(self):
        """Test Тийм with score 0 → (0, 0)."""
        no_score, yes_score = calculate_scores("Тийм", 0)
        assert no_score == 0
        assert yes_score == 0


# =============================================================================
# Line Parser Tests
# =============================================================================


class TestParseQuestionLine:
    """Test question line parsing."""

    def test_parse_valid_line(self):
        """Test parsing valid question line."""
        line = "Question text here\t\tҮгүй\t\t1"
        result = parse_question_line(line, "test.md", 1)
        assert result is not None
        text, option, score = result
        assert text == "Question text here"
        assert option == "Үгүй"
        assert score == 1

    def test_parse_valid_line_тийм(self):
        """Test parsing valid question line with Тийм."""
        line = "Another question\t\tТийм\t\t0"
        result = parse_question_line(line, "test.md", 2)
        assert result is not None
        text, option, score = result
        assert text == "Another question"
        assert option == "Тийм"
        assert score == 0

    def test_parse_missing_score(self):
        """Test parsing line with missing score (should use default 0)."""
        # When score is missing, the function should use default 0
        line = "QuestionText\t\tҮгүй"  # Single word question
        result = parse_question_line(line, "test.md", 3)
        assert result is not None
        text, option, score = result
        assert text == "QuestionText"
        assert option == "Үгүй"
        assert score == 0  # Default

    def test_parse_invalid_option(self):
        """Test parsing line with invalid option text."""
        line = "Question text\t\tMaybe\t\t1"
        result = parse_question_line(line, "test.md", 4)
        assert result is None  # Should skip

    def test_parse_invalid_score(self):
        """Test parsing line with invalid score."""
        line = "Question text\t\tҮгүй\t\t2"
        result = parse_question_line(line, "test.md", 5)
        assert result is not None
        text, option, score = result
        assert text == "Question text"
        assert option == "Үгүй"
        assert score == 0  # Default

    def test_parse_extra_whitespace(self):
        """Test parsing line with extra whitespace."""
        line = "Question text\t\tҮгүй\t\t1\t\t"
        result = parse_question_line(line, "test.md", 6)
        assert result is not None
        text, option, score = result
        assert text == "Question text"
        assert option == "Үгүй"
        assert score == 1


# =============================================================================
# File Parser Tests
# =============================================================================


class TestParseMarkdownFile:
    """Test markdown file parsing."""

    def test_parse_valid_file(self):
        """Test parsing valid markdown file."""
        # Use actual file format: 0 spaces for groups, 5-7 spaces for questions
        content = """Галын хор
       Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх\t\tҮгүй\t\t\t\t\t1
       Монометр нь ногоон түвшинг зааж байгаа эсэх\t\tҮгүй\t\t\t\t\t1
"""
        # Create file with proper name format
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8", prefix="Type - ") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            # Type name should be extracted from filename (without "Type - " prefix)
            assert len(result.types) == 1
            # Filename is like "Type - tmpXXX.md" so type name is "tmpXXX"
            assert result.types[0].name == path.stem[7:]  # Remove "Type - " prefix

            groups = result.types[0].groups
            assert len(groups) == 1
            assert groups[0].name == "Галын хор"

            questions = groups[0].questions
            assert len(questions) == 2
            assert questions[0].text == "Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх"
            assert questions[0].option_text == "Үгүй"
            assert questions[0].score == 1
        finally:
            path.unlink()

    def test_parse_group_with_trailing_tabs(self):
        """Test parsing group header with trailing tabs."""
        # Some files have group headers with trailing tabs: "Group Name\t\t"
        content = """Галын хор\t\t
       Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх\t\tҮгүй\t\t\t\t\t1
"""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            assert len(result.types) == 1
            groups = result.types[0].groups
            assert len(groups) == 1
            assert groups[0].name == "Галын хор"
            assert len(groups[0].questions) == 1
        finally:
            path.unlink()

    def test_parse_question_with_leading_tabs(self):
        """Test parsing question line with leading tabs instead of spaces."""
        # Some files use leading tabs: "\tQuestion text\t\tOption\t\tScore"
        content = """Галын хор
	Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх		Үгүй			1
"""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            assert len(result.types) == 1
            groups = result.types[0].groups
            assert len(groups) == 1
            assert groups[0].name == "Галын хор"
            assert len(groups[0].questions) == 1
            assert groups[0].questions[0].text == "Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх"
            assert groups[0].questions[0].option_text == "Үгүй"
            assert groups[0].questions[0].score == 1
        finally:
            path.unlink()

    def test_parse_multiple_groups(self):
        """Test parsing file with multiple groups."""
        # Groups have 0 spaces, questions have 5+ spaces, tabs as separators
        content = """Галын хор
       Question 1\t\tҮгүй\t\t\t\t\t1
Галд шатах материал
       Question 2\t\tТийм\t\t\t\t\t0
"""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            assert len(result.types) == 1
            groups = result.types[0].groups
            assert len(groups) == 2
            assert groups[0].name == "Галын хор"
            assert groups[1].name == "Галд шатах материал"
        finally:
            path.unlink()

    def test_parse_with_comments(self):
        """Test parsing file with comment lines."""
        # Groups have 0 spaces, questions have 5+ spaces, tabs as separators
        content = """# This is a comment
Галын хор
# Another comment
       Question 1\t\tҮгүй\t\t\t\t\t1
"""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            assert len(result.types) == 1
            assert len(result.types[0].groups[0].questions) == 1
        finally:
            path.unlink()

    def test_parse_with_empty_lines(self):
        """Test parsing file with empty lines."""
        # Groups have 0 spaces, questions have 5+ spaces, tabs as separators
        content = """Галын хор

       Question 1\t\tҮгүй\t\t\t\t\t1
"""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            result = parse_markdown_file(path)

            assert len(result.types) == 1
            assert len(result.types[0].groups[0].questions) == 1
        finally:
            path.unlink()

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_markdown_file(Path("nonexistent.md"))

    def test_parse_empty_file(self):
        """Test parsing empty file."""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="No parseable content"):
                parse_markdown_file(path)
        finally:
            path.unlink()

    def test_parse_encoding_error(self):
        """Test parsing file with invalid encoding."""
        # Create file with non-UTF-8 content
        with NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\xff\xfe Invalid UTF-8")
            path = Path(f.name)

        try:
            with pytest.raises(UnicodeDecodeError):
                parse_markdown_file(path)
        finally:
            path.unlink()


# =============================================================================
# Edge Case Tests (T022)
# =============================================================================


class TestEdgeCaseHandling:
    """Test edge case handling in parsing logic."""

    def test_parse_question_line_empty(self):
        """Test parsing empty string."""
        result = parse_question_line("", "test.md", 1)
        assert result is None  # Should skip empty lines

    def test_parse_question_line_only_text(self):
        """Test parsing line with only question text (missing option and score)."""
        # Line with only text, no option or score
        line = "JustSomeQuestionText"
        result = parse_question_line(line, "test.md", 2)
        # Should return None since it can't find valid option
        assert result is None

    def test_parse_question_line_score_not_integer(self):
        """Test parsing line with non-integer score."""
        line = "Question text\t\tҮгүй\t\tabc"
        result = parse_question_line(line, "test.md", 3)
        assert result is not None
        text, option, score = result
        assert score == 0  # Should use default 0

    def test_parse_question_line_both_scores_1(self):
        """Test that inverse scoring prevents both scores being 1."""
        # This is tested indirectly through calculate_scores
        # If we parse "Үгүй    1", we get (1, 0)
        # If we parse "Тийм    1", we get (0, 1)
        # Both can't be 1 at the same time
        no_score, yes_score = calculate_scores("Үгүй", 1)
        assert (no_score, yes_score) == (1, 0)

        no_score, yes_score = calculate_scores("Тийм", 1)
        assert (no_score, yes_score) == (0, 1)

    def test_parse_markdown_file_empty_file(self):
        """Test parsing file with no parseable content."""
        with NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="No parseable content"):
                parse_markdown_file(path)
        finally:
            path.unlink()

    def test_calculate_scores_invalid_option(self):
        """Test calculate_scores with invalid option text."""
        # Invalid option should return (0, 0) by default logic
        # The validation happens in parse_question_line instead
        no_score, yes_score = calculate_scores("Invalid", 1)
        # Returns (0, 0) since it's not "Үгүй" or "Тийм"
        assert (no_score, yes_score) == (0, 0)
