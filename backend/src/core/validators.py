"""Input validation and sanitization utilities for Mongolian text fields."""

import re
import unicodedata
from typing import Annotated

from pydantic import AfterValidator, Field


def sanitize_mongolian_text(value: str) -> str:
    """Sanitize and normalize Mongolian Cyrillic text input.

    Operations:
    - Normalize Unicode (NFC form for consistent representation)
    - Strip leading/trailing whitespace
    - Collapse multiple spaces into single space
    - Remove control characters except newlines and tabs
    - Preserve Mongolian Cyrillic characters (U+0400-U+04FF)

    Args:
        value: Input string to sanitize.

    Returns:
        Sanitized and normalized string.
    """
    if not value:
        return value

    # Normalize Unicode to NFC (composed form)
    normalized = unicodedata.normalize("NFC", value)

    # Remove control characters except \n and \t
    # Keep: printable chars, newlines, tabs
    cleaned = "".join(
        char
        for char in normalized
        if char in ("\n", "\t") or not unicodedata.category(char).startswith("C")
    )

    # Collapse multiple whitespace (but preserve single newlines)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)  # Collapse spaces/tabs
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # Max 2 consecutive newlines

    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def validate_mongolian_text(value: str) -> str:
    """Validate that text contains valid Mongolian Cyrillic characters.

    Allows:
    - Cyrillic characters (U+0400-U+04FF) - Russian/Mongolian Cyrillic
    - Basic Latin (A-Z, a-z) for technical terms
    - Numbers (0-9)
    - Common punctuation and whitespace
    - Mongolian-specific characters

    Args:
        value: Input string to validate.

    Returns:
        The validated string.

    Raises:
        ValueError: If string contains invalid characters.
    """
    if not value:
        return value

    # Sanitize first
    sanitized = sanitize_mongolian_text(value)

    # Define allowed character pattern
    # Cyrillic: \u0400-\u04FF
    # Basic Latin: A-Za-z
    # Numbers: 0-9
    # Common punctuation: .,;:!?'"()-/\n\t
    # Whitespace and common symbols
    allowed_pattern = re.compile(
        r"^[\u0400-\u04FFA-Za-z0-9\s.,;:!?'\"()\-/\n\t@#%&*+=_<>[\]{}|\\~`№₮]+$"
    )

    if not allowed_pattern.match(sanitized):
        # Find invalid characters for error message
        invalid_chars = set()
        for char in sanitized:
            if not re.match(
                r"[\u0400-\u04FFA-Za-z0-9\s.,;:!?'\"()\-/\n\t@#%&*+=_<>[\]{}|\\~`№₮]",
                char,
            ):
                invalid_chars.add(char)

        if invalid_chars:
            chars_display = ", ".join(f"'{c}' (U+{ord(c):04X})" for c in invalid_chars)
            raise ValueError(f"Invalid characters in text: {chars_display}")

    return sanitized


def validate_no_script_injection(value: str) -> str:
    """Validate that text does not contain potential script injection patterns.

    Checks for:
    - HTML/XML tags
    - JavaScript event handlers
    - URL schemes (javascript:, data:, vbscript:)

    Args:
        value: Input string to validate.

    Returns:
        The validated string.

    Raises:
        ValueError: If potential injection pattern detected.
    """
    if not value:
        return value

    # Check for HTML tags
    if re.search(r"<[a-zA-Z/]", value):
        raise ValueError("HTML tags are not allowed")

    # Check for dangerous URL schemes
    dangerous_schemes = ["javascript:", "data:", "vbscript:", "file:"]
    value_lower = value.lower()
    for scheme in dangerous_schemes:
        if scheme in value_lower:
            raise ValueError(f"URL scheme '{scheme}' is not allowed")

    # Check for event handlers
    if re.search(r"on\w+\s*=", value_lower):
        raise ValueError("Event handlers are not allowed")

    return value


def validate_comment_text(value: str) -> str:
    """Validate comment text with full sanitization.

    Applies all validation rules:
    - Mongolian text sanitization
    - Character validation
    - Script injection prevention

    Args:
        value: Comment text to validate.

    Returns:
        Validated and sanitized comment text.
    """
    if not value:
        return value

    value = validate_no_script_injection(value)
    value = validate_mongolian_text(value)
    return value


# Pydantic annotated types for use in schemas
SanitizedStr = Annotated[str, AfterValidator(sanitize_mongolian_text)]
ValidatedMongolianStr = Annotated[str, AfterValidator(validate_mongolian_text)]
SafeCommentStr = Annotated[str, AfterValidator(validate_comment_text)]


# Field factories for common use cases
def mongolian_name_field(
    max_length: int = 255,
    description: str = "Name in Mongolian Cyrillic",
) -> str:
    """Create a field for Mongolian names."""
    return Field(
        ...,
        max_length=max_length,
        description=description,
        json_schema_extra={"example": "Бат-Эрдэнэ"},
    )


def mongolian_text_field(
    max_length: int = 2000,
    description: str = "Text in Mongolian Cyrillic",
) -> str:
    """Create a field for Mongolian text content."""
    return Field(
        ...,
        max_length=max_length,
        description=description,
    )
