"""SMS API service for sending SMS messages."""

import sys
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .config import Configuration
    from .http_client import AsyncHttpClient
    from .models import SMSRequest, SMSResponse
except ImportError:
    scripts_dir = Path(__file__).parent
    backend_dir = scripts_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from scripts.config import Configuration
    from scripts.http_client import AsyncHttpClient
    from scripts.models import SMSRequest, SMSResponse


class SMSService:
    """Service for interacting with the SMS API."""

    def __init__(self, config: Configuration):
        """Initialize the SMS service.

        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        self.client = AsyncHttpClient(
            base_url=config.sms_api.base_url,
            headers={
                "x-api-key": config.sms_api.api_key,
                "Content-Type": "application/json",
            },
            retry_attempts=config.processing.retry_attempts,
            retry_delay_seconds=config.processing.retry_delay_seconds,
        )

    async def send_sms(self, to: str, message: str) -> SMSResponse:
        """Send an SMS message.

        Args:
            to: Phone number to send SMS to (will be validated)
            message: SMS message content

        Returns:
            SMSResponse with status

        Raises:
            APIException: If API request fails
            NetworkException: If network error occurs
        """
        # Build request (will validate phone number and message)
        request = SMSRequest(to=to, message=message)

        # Make API call
        response_data = await self.client.post(
            endpoint="/api/v1/sms",
            json=request.model_dump(),
        )

        # Parse response
        return SMSResponse(**response_data)
