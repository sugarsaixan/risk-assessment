"""Service for draft save/load/delete operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment_draft import AssessmentDraft
from src.models.enums import AssessmentStatus
from src.repositories.assessment import AssessmentRepository
from src.repositories.draft import DraftRepository
from src.schemas.draft import DraftResponse, DraftSaveRequest, DraftSaveResponse


class DraftService:
    """Service for draft business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.draft_repo = DraftRepository(session)
        self.assessment_repo = AssessmentRepository(session)

    async def save_draft(
        self,
        assessment_id: UUID,
        data: DraftSaveRequest,
    ) -> DraftSaveResponse:
        """Save or update draft for an assessment.

        Args:
            assessment_id: The assessment UUID.
            data: Draft data to save.

        Returns:
            DraftSaveResponse with timestamp and success message.

        Raises:
            ValueError: If assessment not found or not in PENDING status.
        """
        # Validate assessment exists and is pending
        assessment = await self.assessment_repo.get_by_id(assessment_id)
        if assessment is None:
            raise ValueError("Assessment not found")

        if assessment.status != AssessmentStatus.PENDING:
            raise ValueError("Assessment is not in pending status")

        # Convert to dict for JSONB storage
        draft_data = {
            "answers": [answer.model_dump(mode="json") for answer in data.answers],
            "current_type_index": data.current_type_index,
            "current_group_index": data.current_group_index,
        }

        # Upsert draft
        draft = await self.draft_repo.upsert(assessment_id, draft_data)

        return DraftSaveResponse(
            last_saved_at=draft.last_saved_at,
            message="Хадгалагдсан",
        )

    async def load_draft(
        self,
        assessment_id: UUID,
    ) -> DraftResponse | None:
        """Load draft for an assessment.

        Args:
            assessment_id: The assessment UUID.

        Returns:
            DraftResponse if draft exists, None otherwise.
        """
        draft = await self.draft_repo.get_by_assessment_id(assessment_id)

        if draft is None:
            return None

        return self._draft_to_response(draft)

    async def delete_draft(self, assessment_id: UUID) -> bool:
        """Delete draft for an assessment.

        Typically called after successful submission.

        Args:
            assessment_id: The assessment UUID.

        Returns:
            True if draft was deleted, False if no draft existed.
        """
        return await self.draft_repo.delete(assessment_id)

    def _draft_to_response(self, draft: AssessmentDraft) -> DraftResponse:
        """Convert draft model to response schema."""
        from src.schemas.draft import DraftAnswer

        draft_data = draft.draft_data
        answers = [
            DraftAnswer(**answer) for answer in draft_data.get("answers", [])
        ]

        return DraftResponse(
            answers=answers,
            current_type_index=draft_data.get("current_type_index"),
            current_group_index=draft_data.get("current_group_index"),
            last_saved_at=draft.last_saved_at,
        )
