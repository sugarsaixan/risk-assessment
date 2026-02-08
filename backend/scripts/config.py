"""Configuration loader for the test assessment SMS distribution tool."""

import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class AssessmentAPIConfig(BaseModel):
    """Assessment API configuration."""

    base_url: str
    api_key: str
    session_id: str
    respondent_id: str
    selected_type_ids: list[str]
    expires_in_days: int = 30

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base_url ends with / if needed."""
        if not v.startswith("https://"):
            raise ValueError(f"Assessment API base_url must use HTTPS: {v}")
        return v.rstrip("/")


class SMSAPIConfig(BaseModel):
    """SMS API configuration."""

    base_url: str
    api_key: str

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base_url ends with / if needed."""
        if not v.startswith("https://"):
            raise ValueError(f"SMS API base_url must use HTTPS: {v}")
        return v.rstrip("/")


class ProcessingConfig(BaseModel):
    """Processing options configuration."""

    max_concurrent: int = 10
    retry_attempts: int = 2
    retry_delay_seconds: int = 5

    @field_validator("max_concurrent", "retry_attempts", "retry_delay_seconds")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Ensure positive integers."""
        if v <= 0:
            raise ValueError(f"Must be positive: {v}")
        return v


class Configuration(BaseModel):
    """Complete configuration for the SMS distribution tool."""

    assessment_api: AssessmentAPIConfig
    sms_api: SMSAPIConfig
    message_template: str = "Sain baina uu. Ersdeliiin unelgeenii asuulga bogloh holboos: {url}"
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    @field_validator("message_template")
    @classmethod
    def validate_message_template(cls, v: str) -> str:
        """Ensure message template contains {url} placeholder."""
        if "{url}" not in v:
            raise ValueError("Message template must contain {url} placeholder")
        if len(v) > 160:
            raise ValueError(f"Message template too long ({len(v)} > 160 characters)")
        return v


def _expand_env_vars(value: Any) -> Any:
    """Expand environment variables in configuration values.

    Supports ${VAR_NAME} syntax.
    """
    if isinstance(value, str):
        # Match ${VAR_NAME} pattern
        pattern = re.compile(r'\$\{([^}]+)\}')

        def replace_env_var(match: re.Match) -> str:
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is None:
                raise ValueError(f"Environment variable {var_name} not set (referenced in config)")
            return env_value

        return pattern.sub(replace_env_var, value)
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


def load_config(config_path: str | Path | None = None) -> Configuration:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config.yml file. If None, looks for
                    backend/scripts/config.yml

    Returns:
        Validated Configuration object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    if config_path is None:
        # Default to config.yml in scripts directory
        script_dir = Path(__file__).parent
        config_path = script_dir / "config.yml"

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Copy config_template.yml to config.yml and configure your API credentials."
        )

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    # Expand environment variables
    expanded_config = _expand_env_vars(raw_config)

    # Validate and create Configuration object
    return Configuration(**expanded_config)
