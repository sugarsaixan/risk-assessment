"""Phone number validation for Mongolian numbers."""

import re
from typing import Final


# Mongolian mobile number patterns
MONGOLIAN_MOBILE_PATTERN: Final = re.compile(r"^(?:\+976)?\s*(\d{8})$")
MONGOLIAN_PREFIXES: Final = {"8", "9"}


def normalize_phone_number(phone_number: str) -> str | None:
    """Normalize a phone number to 8-digit Mongolian format.

    Args:
        phone_number: Raw phone number (may include spaces, dashes, country code)

    Returns:
        Normalized 8-digit phone number, or None if invalid

    Examples:
        >>> normalize_phone_number("89113840")
        '89113840'
        >>> normalize_phone_number("+976 8911-3840")
        '89113840'
        >>> normalize_phone_number("8911 38 40")
        '89113840'
        >>> normalize_phone_number("12345")
        None
    """
    if not phone_number:
        return None

    # Remove all non-numeric characters (except + at start)
    stripped = phone_number.strip()
    if not stripped:
        return None

    # Extract digits only
    digits = "".join(c for c in stripped if c.isdigit())

    # Handle country code +976
    if stripped.startswith("+"):
        if stripped.startswith("+976"):
            # Remove the country code prefix
            if len(digits) > 8:
                digits = digits[3:]  # Remove "976"
        else:
            # International number but not Mongolia
            return None

    # Validate length
    if len(digits) != 8:
        return None

    # Validate prefix (must start with 8 or 9 for Mongolian mobile)
    if digits[0] not in MONGOLIAN_PREFIXES:
        return None

    return digits


def validate_phone_number(phone_number: str) -> tuple[bool, str | None]:
    """Validate a phone number and return normalized form.

    Args:
        phone_number: Raw phone number

    Returns:
        Tuple of (is_valid, normalized_number_or_error_message)

    Examples:
        >>> validate_phone_number("89113840")
        (True, '89113840')
        >>> validate_phone_number("12345")
        (False, 'Invalid phone number: must be 8 digits')
        >>> validate_phone_number("abcdefgh")
        (False, 'Invalid phone number: must contain only digits')
    """
    if not phone_number:
        return False, "Invalid phone number: empty"

    normalized = normalize_phone_number(phone_number)

    if normalized is None:
        # Determine specific error
        stripped = phone_number.strip()
        if not stripped:
            return False, "Invalid phone number: empty"

        # Check if it has non-numeric characters
        if any(not c.isdigit() and c not in " +-" for c in stripped):
            return False, "Invalid phone number: contains invalid characters"

        # Extract digits for validation
        digits = "".join(c for c in stripped if c.isdigit())

        # Check length
        if len(digits) < 8:
            return False, "Invalid phone number: too short (must be 8 digits)"
        if len(digits) > 8:
            return False, f"Invalid phone number: too long ({len(digits)} digits, must be 8)"

        # Check prefix
        if len(digits) >= 8 and digits[0] not in MONGOLIAN_PREFIXES:
            return False, "Invalid phone number: must start with 8 or 9 (Mongolian mobile)"

        return False, "Invalid phone number: format not recognized"

    return True, normalized
