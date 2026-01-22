"""API key authentication for admin endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_session
from src.models.api_key import ApiKey

# API key header configuration
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=True,
    description="API key for admin authentication",
)

# Password/key hashing context using Argon2
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_api_key(api_key: str) -> str:
    """Hash an API key using Argon2.

    Args:
        api_key: The plain text API key.

    Returns:
        The Argon2 hash of the API key.
    """
    # Include pepper for additional security
    peppered_key = f"{api_key}{settings.api_key_pepper}"
    return pwd_context.hash(peppered_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash.

    Args:
        plain_key: The plain text API key to verify.
        hashed_key: The stored Argon2 hash.

    Returns:
        True if the key matches, False otherwise.
    """
    peppered_key = f"{plain_key}{settings.api_key_pepper}"
    try:
        return pwd_context.verify(peppered_key, hashed_key)
    except Exception:
        return False


async def get_api_key(
    api_key: Annotated[str, Depends(api_key_header)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ApiKey:
    """Dependency that validates the API key and returns the ApiKey record.

    Args:
        api_key: The API key from the X-API-Key header.
        session: Database session.

    Returns:
        The validated ApiKey model instance.

    Raises:
        HTTPException: 401 if key is invalid or inactive.
    """
    # Query all active API keys
    stmt = select(ApiKey).where(ApiKey.is_active == True)  # noqa: E712
    result = await session.execute(stmt)
    api_keys = result.scalars().all()

    # Check the provided key against all active keys
    # This is necessary because Argon2 hashes include salt,
    # so we can't do a direct database lookup
    matched_key: ApiKey | None = None
    for stored_key in api_keys:
        if verify_api_key(api_key, stored_key.key_hash):
            matched_key = stored_key
            break

    if matched_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Update last_used_at timestamp
    await session.execute(
        update(ApiKey)
        .where(ApiKey.id == matched_key.id)
        .values(last_used_at=datetime.now(timezone.utc))
    )

    return matched_key


# Type alias for dependency injection
CurrentApiKey = Annotated[ApiKey, Depends(get_api_key)]
