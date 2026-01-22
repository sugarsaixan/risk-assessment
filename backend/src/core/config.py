"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Risk Assessment API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/risk_assessment",
        description="PostgreSQL connection URL with asyncpg driver",
    )

    # S3/MinIO Object Storage
    s3_endpoint_url: str = Field(
        default="http://localhost:9000",
        description="S3-compatible endpoint URL",
    )
    s3_access_key: str = Field(
        default="minioadmin",
        description="S3 access key ID",
    )
    s3_secret_key: str = Field(
        default="minioadmin",
        description="S3 secret access key",
    )
    s3_bucket_name: str = Field(
        default="risk-assessment",
        description="S3 bucket name for attachments",
    )
    s3_region: str = Field(
        default="us-east-1",
        description="S3 region",
    )

    # Security
    api_key_pepper: str = Field(
        default="change-me-in-production",
        description="Pepper for API key hashing (keep secret)",
    )

    # Public URL (for generating assessment links)
    public_url: str = Field(
        default="http://localhost:5173",
        description="Public frontend URL for assessment links",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=30,
        description="Maximum requests per rate limit window",
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds",
    )

    # Assessment defaults
    assessment_default_expiry_days: int = Field(
        default=30,
        description="Default assessment link expiration in days",
    )

    # Upload limits
    upload_max_size_mb: int = Field(
        default=5,
        description="Maximum upload file size in MB",
    )
    upload_max_images_per_question: int = Field(
        default=3,
        description="Maximum images per question answer",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
