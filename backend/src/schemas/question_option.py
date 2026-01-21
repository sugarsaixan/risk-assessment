"""Pydantic schemas for QuestionOption."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.enums import OptionType


class QuestionOptionConfig(BaseModel):
    """Schema for configuring a question option (YES or NO)."""

    option_type: OptionType = Field(..., description="YES or NO")
    score: int = Field(default=0, ge=0, description="Points awarded for this option")
    require_comment: bool = Field(default=False, description="Comment required when selected")
    require_image: bool = Field(default=False, description="Image required when selected")
    comment_min_len: int = Field(
        default=0,
        ge=0,
        le=2000,
        description="Minimum comment characters",
    )
    max_images: int = Field(default=3, ge=1, le=10, description="Maximum images allowed")
    image_max_mb: int = Field(default=5, ge=1, le=20, description="Maximum image size in MB")

    @model_validator(mode="after")
    def validate_comment_requirement(self) -> "QuestionOptionConfig":
        """Ensure comment_min_len is set only if comment is required."""
        if self.comment_min_len > 0 and not self.require_comment:
            raise ValueError("comment_min_len can only be set if require_comment is true")
        return self


class QuestionOptionsSet(BaseModel):
    """Schema for setting both YES and NO options for a question."""

    yes: QuestionOptionConfig = Field(..., description="Configuration for YES option")
    no: QuestionOptionConfig = Field(..., description="Configuration for NO option")

    @model_validator(mode="after")
    def validate_option_types(self) -> "QuestionOptionsSet":
        """Ensure option types are correct."""
        if self.yes.option_type != OptionType.YES:
            raise ValueError("yes option must have option_type=YES")
        if self.no.option_type != OptionType.NO:
            raise ValueError("no option must have option_type=NO")
        return self


class QuestionOptionResponse(BaseModel):
    """Schema for question option response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question_id: UUID
    option_type: OptionType
    score: int
    require_comment: bool
    require_image: bool
    comment_min_len: int
    max_images: int
    image_max_mb: int
