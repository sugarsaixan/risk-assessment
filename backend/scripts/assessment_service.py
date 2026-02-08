"""Assessment API service for creating risk assessments."""

import sys
from pathlib import Path
from typing import Any

# Handle both relative and absolute imports
try:
    from .config import Configuration
    from .http_client import AsyncHttpClient
    from .models import AssessmentRequest, AssessmentResponse
except ImportError:
    # Running as script directly
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.config import Configuration
    from scripts.http_client import AsyncHttpClient
    from scripts.models import AssessmentRequest, AssessmentResponse


class AssessmentService:
    """Service for interacting with the Assessment API."""

    def __init__(self, config: Configuration):
        """Initialize the assessment service.

        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        self.client = AsyncHttpClient(
            base_url=config.assessment_api.base_url,
            headers={
                "X-API-Key": config.assessment_api.api_key,
                "Content-Type": "application/json",
            },
            retry_attempts=config.processing.retry_attempts,
            retry_delay_seconds=config.processing.retry_delay_seconds,
        )
        self.session_cookie = f"session_id={config.assessment_api.session_id}"

    async def create_assessment(
        self,
        respondent_id: str | None = None,
        selected_type_ids: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> AssessmentResponse:
        """Create a new risk assessment.

        Args:
            respondent_id: ID of respondent (uses config default if None)
            selected_type_ids: List of assessment type IDs (uses config default if None)
            expires_in_days: Days until expiration (uses config default if None)

        Returns:
            AssessmentResponse with assessment ID and URL

        Raises:
            APIException: If API request fails
            NetworkException: If network error occurs
        """
        # Use defaults from config if not provided
        if respondent_id is None:
            respondent_id = self.config.assessment_api.respondent_id
        if selected_type_ids is None:
            selected_type_ids = self.config.assessment_api.selected_type_ids
        if expires_in_days is None:
            expires_in_days = self.config.assessment_api.expires_in_days

        # Build request
        request = AssessmentRequest(
            respondent_id=respondent_id,
            selected_type_ids=selected_type_ids,
            expires_in_days=expires_in_days,
        )

        # Make API call with session cookie
        response_data = await self.client.post(
            endpoint="/assessment/api/admin/assessments",
            json=request.model_dump(),
            headers={"Cookie": self.session_cookie},
        )

        # Parse response
        return AssessmentResponse(**response_data)
