"""Exception classes for the test assessment SMS distribution tool."""


class BaseScriptException(Exception):
    """Base exception for all script errors."""

    def __init__(self, message: str, error_type: str = "UNKNOWN"):
        """Initialize the exception.

        Args:
            message: Error message
            error_type: Type of error
        """
        self.error_type = error_type
        super().__init__(message)


class ValidationException(BaseScriptException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        """Initialize the exception.

        Args:
            message: Validation error message
        """
        super().__init__(message, error_type="VALIDATION_ERROR")


class APIException(BaseScriptException):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int | None = None, error_type: str = "API_ERROR"):
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code (if available)
            error_type: Type of error
        """
        self.status_code = status_code
        super().__init__(message, error_type=error_type)


class NetworkException(BaseScriptException):
    """Raised when network request fails."""

    def __init__(self, message: str, error_type: str = "NETWORK_ERROR"):
        """Initialize the exception.

        Args:
            message: Error message
            error_type: Type of error
        """
        super().__init__(message, error_type=error_type)


class ConfigurationException(BaseScriptException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str):
        """Initialize the exception.

        Args:
            message: Configuration error message
        """
        super().__init__(message, error_type="CONFIGURATION_ERROR")
