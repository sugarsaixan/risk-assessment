"""Data models for the test assessment SMS distribution tool."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ProcessingStatus(str, Enum):
    """Status of processing a phone number."""

    SUCCESS = "SUCCESS"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    FAILED_ASSESSMENT = "FAILED_ASSESSMENT"
    FAILED_SMS = "FAILED_SMS"


class ErrorStage(str, Enum):
    """Stage where error occurred."""

    VALIDATION = "VALIDATION"
    ASSESSMENT = "ASSESSMENT"
    SMS = "SMS"


class ErrorType(str, Enum):
    """Type of error that occurred."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    API_ERROR = "API_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    RATE_LIMIT = "RATE_LIMIT"


class AssessmentRequest(BaseModel):
    """Request payload for assessment creation API."""

    respondent_id: str
    selected_type_ids: list[str]
    expires_in_days: int = 30

    @field_validator("respondent_id", "selected_type_ids", mode="before")
    @classmethod
    def validate_uuids(cls, v: str | list[str]) -> str | list[str]:
        """Validate UUID format."""
        import uuid

        if isinstance(v, str):
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        elif isinstance(v, list):
            for item in v:
                try:
                    uuid.UUID(item)
                except ValueError:
                    raise ValueError(f"Invalid UUID format: {item}")
        return v

    @field_validator("selected_type_ids")
    @classmethod
    def validate_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure selected_type_ids is not empty."""
        if not v:
            raise ValueError("selected_type_ids must contain at least one type")
        return v

    @field_validator("expires_in_days")
    @classmethod
    def validate_expires(cls, v: int) -> int:
        """Validate expiration days."""
        if not 1 <= v <= 365:
            raise ValueError("expires_in_days must be between 1 and 365")
        return v


class AssessmentResponse(BaseModel):
    """Response from assessment creation API."""

    id: str
    url: str
    expires_at: str

    @field_validator("id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format."""
        import uuid

        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError(f"Invalid UUID format in response: {v}")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith("https://"):
            raise ValueError(f"Assessment URL must use HTTPS: {v}")
        return v


class SMSRequest(BaseModel):
    """Request payload for SMS API."""

    to: str
    message: str

    @field_validator("to")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format (Mongolian: 8 digits, starts with 8 or 9)."""
        # Remove non-numeric characters
        digits_only = "".join(c for c in v if c.isdigit())

        if len(digits_only) != 8:
            raise ValueError(f"Phone number must be 8 digits (Mongolian format): {v}")

        if not digits_only.startswith(("8", "9")):
            raise ValueError(f"Phone number must start with 8 or 9 (Mongolian mobile): {v}")

        return digits_only

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        """Validate message length."""
        if len(v) > 160:
            raise ValueError(f"SMS message too long ({len(v)} > 160 characters)")
        if not v:
            raise ValueError("SMS message cannot be empty")
        return v


class SMSResponse(BaseModel):
    """Response from SMS API."""

    message: str = ""
    status: str

    def is_successful(self) -> bool:
        """Check if SMS was sent successfully."""
        return "success" in self.status.lower()


class ProcessingResult(BaseModel):
    """Result of processing a single phone number."""

    phone_number: str
    status: ProcessingStatus
    assessment_id: str | None = None
    assessment_url: str | None = None
    error_message: str | None = None
    error_stage: ErrorStage | None = None
    error_type: ErrorType | None = None
    retry_count: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_error_fields(self) -> "ProcessingResult":
        """Ensure error fields are set correctly for failed status."""
        if self.status != ProcessingStatus.SUCCESS:
            if not self.error_message:
                raise ValueError("error_message must be set for failed processing")
        return self


class ProcessingSummary(BaseModel):
    """Aggregate summary of all processing results."""

    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    validation_error_count: int = 0
    assessment_error_count: int = 0
    sms_error_count: int = 0
    results: list[ProcessingResult] = Field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float:
        """Calculate total processing duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

    def add_result(self, result: ProcessingResult) -> None:
        """Add a processing result and update statistics."""
        self.results.append(result)
        self.total_count += 1

        if result.status == ProcessingStatus.SUCCESS:
            self.success_count += 1
        else:
            self.failure_count += 1

            if result.error_stage == ErrorStage.VALIDATION:
                self.validation_error_count += 1
            elif result.error_stage == ErrorStage.ASSESSMENT:
                self.assessment_error_count += 1
            elif result.error_stage == ErrorStage.SMS:
                self.sms_error_count += 1
