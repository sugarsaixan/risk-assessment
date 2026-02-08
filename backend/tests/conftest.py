"""Pytest configuration and fixtures."""

import asyncio
import pytest

from src.core.database import async_session_factory


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"


@pytest.fixture
async def async_session_factory():
    """Provide async session factory for tests."""
    # Use the existing session factory from the app
    yield async_session_factory
