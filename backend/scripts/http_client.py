"""HTTP client wrapper with retry logic for API calls."""

import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx

# Handle both relative and absolute imports
try:
    from .models import ErrorType
    from .exceptions import APIException, NetworkException
except ImportError:
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.models import ErrorType
    from scripts.exceptions import APIException, NetworkException


class AsyncHttpClient:
    """Async HTTP client with retry logic and error handling."""

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        retry_attempts: int = 2,
        retry_delay_seconds: int = 5,
        timeout: float = 30.0,
    ):
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers to include in all requests
            retry_attempts: Number of retry attempts for transient failures
            retry_delay_seconds: Delay between retries
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.retry_attempts = retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.timeout = timeout

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request with retry logic.

        Args:
            endpoint: API endpoint (path only, base_url is prepended)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request

        Returns:
            Parsed JSON response

        Raises:
            NetworkException: For network errors after all retries
            APIException: For API errors (4xx) that shouldn't be retried
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self.headers, **(headers or {})}

        for attempt in range(self.retry_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        data=data,
                        json=json,
                        headers=request_headers,
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code

                # Don't retry client errors (4xx) except 429 (rate limit)
                if 400 <= status_code < 500 and status_code != 429:
                    error_detail = e.response.text
                    raise APIException(
                        f"API error {status_code}: {error_detail}",
                        status_code=status_code,
                        error_type=ErrorType.API_ERROR,
                    )

                # Retry rate limit errors (429) and server errors (5xx)
                if attempt < self.retry_attempts:
                    delay = self.retry_delay_seconds * (2**attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Last attempt failed
                    if status_code == 429:
                        raise APIException(
                            f"Rate limit exceeded after {self.retry_attempts} retries",
                            status_code=status_code,
                            error_type=ErrorType.RATE_LIMIT,
                        )
                    else:
                        raise APIException(
                            f"Server error {status_code} after {self.retry_attempts} retries",
                            status_code=status_code,
                            error_type=ErrorType.API_ERROR,
                        )

            except (httpx.NetworkError, httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < self.retry_attempts:
                    delay = self.retry_delay_seconds * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise NetworkException(
                        f"Network error after {self.retry_attempts} retries: {str(e)}",
                        error_type=ErrorType.NETWORK_ERROR,
                    )

            except httpx.HTTPError as e:
                # Other HTTP errors (shouldn't normally happen)
                raise NetworkException(
                    f"HTTP error: {str(e)}",
                    error_type=ErrorType.NETWORK_ERROR,
                )

        # Shouldn't reach here, but just in case
        raise NetworkException(
            f"Request failed after {self.retry_attempts} retries",
            error_type=ErrorType.NETWORK_ERROR,
        )
