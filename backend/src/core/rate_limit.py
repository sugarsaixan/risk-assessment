"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.config import settings

# Create limiter instance using client IP for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Rate limit string for public endpoints
# Format: "{requests} per {period}"
PUBLIC_RATE_LIMIT = f"{settings.rate_limit_requests}/minute"


def get_rate_limit_string(requests_per_minute: int | None = None) -> str:
    """Get rate limit string for decorator.

    Args:
        requests_per_minute: Custom rate limit. Uses default if None.

    Returns:
        Rate limit string in slowapi format.
    """
    if requests_per_minute is None:
        return PUBLIC_RATE_LIMIT
    return f"{requests_per_minute}/minute"
