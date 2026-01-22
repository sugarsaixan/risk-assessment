"""Request logging middleware for the application."""

import logging
import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings

# Configure logger
logger = logging.getLogger("risk_assessment")


def setup_logging() -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Log request details and response status."""
        # Generate request ID
        request_id = str(uuid4())[:8]

        # Record start time
        start_time = time.perf_counter()

        # Get request details
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        client_ip = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(
            f"[{request_id}] --> {method} {path}"
            + (f"?{query}" if query else "")
            + f" | IP: {client_ip}"
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[{request_id}] <-- {method} {path} | "
                f"ERROR: {type(e).__name__}: {e} | "
                f"{duration:.2f}ms"
            )
            raise

        # Calculate duration
        duration = (time.perf_counter() - start_time) * 1000

        # Log response
        status_code = response.status_code
        log_level = logging.INFO if status_code < 400 else logging.WARNING
        if status_code >= 500:
            log_level = logging.ERROR

        logger.log(
            log_level,
            f"[{request_id}] <-- {method} {path} | "
            f"{status_code} | {duration:.2f}ms",
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
