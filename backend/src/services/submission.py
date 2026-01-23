"""Service for handling assessment submissions with contact info and hierarchical scoring."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.answer import Answer
from src.models.assessment import Assessment
from src.models.submission_contact import SubmissionContact
from src.repositories.assessment import AssessmentRepository
from src.schemas.answer import AnswerInput
from src.schemas.public import GroupResult, OverallResult, SubmitResponse, TypeResult
from src.schemas.submission_contact import SubmissionContactInput
from src.services.scoring import ScoringService


class SubmissionService:
    """Service for validating and processing assessment submissions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.scoring_service = ScoringService(session)

    def validate_answers(
        self,
        snapshot: dict[str, Any],
        answers: list[AnswerInput],
    ) -> list[str]:
        """Validate submitted answers against snapshot requirements.

        Supports hierarchical snapshot structure: Type → Group → Question

        Args:
            snapshot: Questions snapshot from assessment.
            answers: Submitted answers.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Build question lookup from snapshot (now with groups)
        questions_by_id: dict[str, dict[str, Any]] = {}
        for type_data in snapshot.get("types", []):
            for group_data in type_data.get("groups", []):
                for question in group_data.get("questions", []):
                    questions_by_id[question["id"]] = question

        # Track answered questions
        answered_ids = set()

        for answer in answers:
            question_id = str(answer.question_id)
            answered_ids.add(question_id)

            # Check question exists in snapshot
            if question_id not in questions_by_id:
                errors.append(f"Question {question_id} not found in assessment")
                continue

            question = questions_by_id[question_id]
            options = question.get("options", {})
            option_key = answer.selected_option.value  # "YES" or "NO"
            option_config = options.get(option_key, {})

            # Check comment requirement
            if option_config.get("require_comment", False):
                min_len = option_config.get("comment_min_len", 0)
                if not answer.comment or len(answer.comment) < min_len:
                    errors.append(
                        f"Question {question_id}: Comment required with minimum {min_len} characters"
                    )

            # Check image requirement
            if option_config.get("require_image", False):
                if not answer.attachment_ids:
                    errors.append(f"Question {question_id}: At least one image required")

            # Check max images
            max_images = option_config.get("max_images", 3)
            if len(answer.attachment_ids) > max_images:
                errors.append(
                    f"Question {question_id}: Maximum {max_images} images allowed"
                )

        # Check all questions are answered
        for question_id in questions_by_id:
            if question_id not in answered_ids:
                errors.append(f"Question {question_id} not answered")

        return errors

    async def save_submission_contact(
        self,
        assessment_id: UUID,
        contact: SubmissionContactInput,
    ) -> SubmissionContact:
        """Save submission contact information.

        Args:
            assessment_id: Assessment UUID.
            contact: Contact input data.

        Returns:
            Created SubmissionContact record.
        """
        submission_contact = SubmissionContact(
            assessment_id=assessment_id,
            last_name=contact.last_name,
            first_name=contact.first_name,
            email=contact.email,
            phone=contact.phone,
            position=contact.position,
        )
        self.session.add(submission_contact)
        await self.session.flush()
        return submission_contact

    async def process_submission(
        self,
        assessment: Assessment,
        contact: SubmissionContactInput,
        answers: list[AnswerInput],
    ) -> SubmitResponse:
        """Process a valid assessment submission.

        Args:
            assessment: The assessment being submitted.
            contact: Contact information of the person submitting.
            answers: Validated answers.

        Returns:
            SubmitResponse with calculated hierarchical scores.
        """
        snapshot = assessment.questions_snapshot

        # Save submission contact
        await self.save_submission_contact(assessment.id, contact)

        # Build answers and calculate scores
        answers_by_question: dict[str, int] = {}

        for answer_input in answers:
            question_id = str(answer_input.question_id)

            # Find the score for this answer from snapshot
            score_awarded = self._get_score_for_answer(
                snapshot, question_id, answer_input.selected_option.value
            )

            # Create answer record
            answer = Answer(
                assessment_id=assessment.id,
                question_id=answer_input.question_id,
                selected_option=answer_input.selected_option,
                comment=answer_input.comment,
                score_awarded=score_awarded,
            )
            self.session.add(answer)

            answers_by_question[question_id] = score_awarded

        await self.session.flush()

        # Calculate scores per type (includes group scores)
        type_scores = []
        for type_data in snapshot.get("types", []):
            type_score = self.scoring_service.calculate_type_score(
                type_data, answers_by_question
            )
            type_scores.append(type_score)

        # Calculate overall score
        overall_score = self.scoring_service.calculate_overall_score(type_scores)

        # Save scores to database (group, type, and overall)
        await self.scoring_service.save_scores(
            assessment.id, type_scores, overall_score
        )

        # Mark assessment as completed
        await self.assessment_repo.mark_completed(
            assessment, datetime.now(timezone.utc)
        )

        # Build response with hierarchical structure
        return SubmitResponse(
            assessment_id=str(assessment.id),
            type_results=[
                TypeResult(
                    type_id=ts["type_id"],
                    type_name=ts["type_name"],
                    raw_score=ts["raw_score"],
                    max_score=ts["max_score"],
                    percentage=ts["percentage"],
                    risk_rating=ts["risk_rating"],
                    groups=[
                        GroupResult(
                            group_id=gs["group_id"],
                            group_name=gs["group_name"],
                            raw_score=gs["raw_score"],
                            max_score=gs["max_score"],
                            percentage=gs["percentage"],
                            risk_rating=gs["risk_rating"],
                        )
                        for gs in ts.get("groups", [])
                    ],
                )
                for ts in type_scores
            ],
            overall_result=OverallResult(
                raw_score=overall_score["raw_score"],
                max_score=overall_score["max_score"],
                percentage=overall_score["percentage"],
                risk_rating=overall_score["risk_rating"],
            ),
        )

    def _get_score_for_answer(
        self,
        snapshot: dict[str, Any],
        question_id: str,
        selected_option: str,
    ) -> int:
        """Get the score for a specific answer from snapshot.

        Supports hierarchical snapshot: Type → Group → Question

        Args:
            snapshot: Questions snapshot.
            question_id: Question ID.
            selected_option: "YES" or "NO".

        Returns:
            Score value for the selected option.
        """
        for type_data in snapshot.get("types", []):
            for group_data in type_data.get("groups", []):
                for question in group_data.get("questions", []):
                    if question["id"] == question_id:
                        options = question.get("options", {})
                        return options.get(selected_option, {}).get("score", 0)
        return 0
