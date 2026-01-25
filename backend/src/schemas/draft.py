"""Pydantic schemas for assessment draft save/load."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DraftAnswer(BaseModel):
    """Schema for a single answer in a draft."""

    question_id: UUID = Field(..., description="Question UUID")
    selected_option: Optional[str] = Field(
        None,
        pattern="^(YES|NO)$",
        description="Selected option: YES or NO",
    )
    comment: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional comment text",
    )
    attachment_ids: list[UUID] = Field(
        default_factory=list,
        max_length=10,
        description="List of uploaded attachment UUIDs",
    )


class DraftSaveRequest(BaseModel):
    """Schema for saving draft progress."""

    answers: list[DraftAnswer] = Field(
        ...,
        description="List of answered questions",
    )
    current_type_index: Optional[int] = Field(
        None,
        ge=0,
        description="Current questionnaire type position (UI state)",
    )
    current_group_index: Optional[int] = Field(
        None,
        ge=0,
        description="Current group position within type (UI state)",
    )


class DraftResponse(BaseModel):
    """Schema for loading draft from server."""

    model_config = ConfigDict(from_attributes=True)

    answers: list[DraftAnswer] = Field(
        ...,
        description="List of saved answers",
    )
    current_type_index: Optional[int] = Field(
        None,
        description="Saved questionnaire type position",
    )
    current_group_index: Optional[int] = Field(
        None,
        description="Saved group position",
    )
    last_saved_at: datetime = Field(
        ...,
        description="When the draft was last saved",
    )


class DraftSaveResponse(BaseModel):
    """Response after successfully saving draft."""

    last_saved_at: datetime = Field(
        ...,
        description="Server timestamp of save",
    )
    message: str = Field(
        default="Хадгалагдсан",
        description="Success message (Mongolian)",
    )
