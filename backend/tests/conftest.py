"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"
