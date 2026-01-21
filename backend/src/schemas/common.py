"""Common Pydantic schemas used across the API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    code: str | None = Field(None, description="Error code for client handling")


class ErrorDetail(BaseModel):
    """Detailed error with field information."""

    loc: list[str] = Field(..., description="Location of the error (field path)")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Validation error response with field-level details."""

    detail: list[ErrorDetail] = Field(..., description="List of validation errors")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response.

        Args:
            items: List of items for the current page.
            total: Total number of items across all pages.
            page: Current page number (1-indexed).
            page_size: Number of items per page.

        Returns:
            PaginatedResponse instance.
        """
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class SuccessResponse(BaseModel):
    """Simple success response."""

    success: bool = Field(True, description="Operation success status")
    message: str | None = Field(None, description="Optional success message")
