"""Service for assessment creation and management."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.assessment import Assessment
from src.models.enums import AssessmentStatus
from src.repositories.assessment import AssessmentRepository
from src.repositories.respondent import RespondentRepository
from src.schemas.assessment import AssessmentCreate, AssessmentCreated
from src.services.snapshot import SnapshotService
from src.services.token import TokenService


class AssessmentService:
    """Service for assessment business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.respondent_repo = RespondentRepository(session)
        self.snapshot_service = SnapshotService(session)

    async def create_assessment(self, data: AssessmentCreate) -> AssessmentCreated:
        """Create a new assessment with question snapshot.

        Args:
            data: Assessment creation data.

        Returns:
            AssessmentCreated with ID, URL, and expiration.

        Raises:
            ValueError: If respondent not found or types invalid.
        """
        # Verify respondent exists
        respondent = await self.respondent_repo.get_by_id(data.respondent_id)
        if respondent is None:
            raise ValueError(f"Respondent not found: {data.respondent_id}")

        # Create question snapshot
        snapshot = await self.snapshot_service.create_snapshot(data.selected_type_ids)

        # Verify snapshot has questions
        total_questions = self.snapshot_service.get_total_questions(snapshot)
        if total_questions == 0:
            raise ValueError("Selected questionnaire types have no active questions")

        # Generate token
        token, token_hash = TokenService.generate_token_pair()

        # Calculate expiration
        expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)

        # Create assessment
        assessment = await self.assessment_repo.create(
            respondent_id=data.respondent_id,
            token_hash=token_hash,
            selected_type_ids=data.selected_type_ids,
            questions_snapshot=snapshot,
            expires_at=expires_at,
        )

        # Generate public URL
        url = self._generate_public_url(token)

        return AssessmentCreated(
            id=assessment.id,
            url=url,
            expires_at=expires_at,
        )

    def _generate_public_url(self, token: str) -> str:
        """Generate the public assessment URL.

        Args:
            token: The plain text token.

        Returns:
            Full public URL for the assessment.
        """
        return f"{settings.public_url}/a/{token}"

    async def get_by_id(self, assessment_id: UUID) -> Assessment | None:
        """Get an assessment by ID."""
        return await self.assessment_repo.get_by_id(assessment_id)

    async def get_by_token(self, token: str) -> Assessment | None:
        """Get an assessment by token.

        Args:
            token: The plain text token from the URL.

        Returns:
            Assessment if found and token is valid.
        """
        token_hash = TokenService.hash_token(token)
        return await self.assessment_repo.get_by_token_hash(token_hash)

    async def validate_for_submission(self, assessment: Assessment) -> str | None:
        """Validate that an assessment can be submitted.

        Args:
            assessment: The assessment to validate.

        Returns:
            Error message if invalid, None if valid.
        """
        now = datetime.now(timezone.utc)

        # Check if expired
        if assessment.expires_at < now:
            # Update status if still pending
            if assessment.status == AssessmentStatus.PENDING:
                await self.assessment_repo.mark_expired(assessment)
            return "expired"

        # Check if already completed
        if assessment.status == AssessmentStatus.COMPLETED:
            return "already_completed"

        # Check if marked as expired
        if assessment.status == AssessmentStatus.EXPIRED:
            return "expired"

        return None

    async def get_assessment_status(self, token: str) -> tuple[Assessment | None, str | None]:
        """Get assessment and validate its status.

        Args:
            token: The plain text token from the URL.

        Returns:
            Tuple of (assessment, error_status).
            - If assessment is valid: (assessment, None)
            - If assessment is invalid: (assessment, "expired"|"already_completed")
            - If not found: (None, "not_found")
        """
        assessment = await self.get_by_token(token)

        if assessment is None:
            return None, "not_found"

        error = await self.validate_for_submission(assessment)
        return assessment, error

    async def list_assessments(
        self,
        *,
        respondent_id: UUID | None = None,
        status: AssessmentStatus | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[Assessment], int]:
        """List assessments with optional filtering.

        Returns:
            Tuple of (assessments, total_count).
        """
        assessments = await self.assessment_repo.get_all(
            respondent_id=respondent_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        total = await self.assessment_repo.count(
            respondent_id=respondent_id,
            status=status,
        )
        return assessments, total
