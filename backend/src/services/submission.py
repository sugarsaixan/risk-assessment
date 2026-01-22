"""Service for handling assessment submissions."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.answer import Answer
from src.models.assessment import Assessment
from src.models.enums import AssessmentStatus
from src.repositories.assessment import AssessmentRepository
from src.schemas.answer import AnswerInput
from src.schemas.public import OverallResult, SubmitResponse, TypeResult
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

        Args:
            snapshot: Questions snapshot from assessment.
            answers: Submitted answers.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Build question lookup from snapshot
        questions_by_id: dict[str, dict[str, Any]] = {}
        for type_data in snapshot.get("types", []):
            for question in type_data.get("questions", []):
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

    async def process_submission(
        self,
        assessment: Assessment,
        answers: list[AnswerInput],
    ) -> SubmitResponse:
        """Process a valid assessment submission.

        Args:
            assessment: The assessment being submitted.
            answers: Validated answers.

        Returns:
            SubmitResponse with calculated scores.
        """
        snapshot = assessment.questions_snapshot

        # Build answers and calculate scores
        answers_by_question: dict[str, int] = {}

        for answer_input in answers:
            question_id = str(answer_input.question_id)

            # Find the question in snapshot to get score
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

            # TODO: Link attachments to answer (T060)

        await self.session.flush()

        # Calculate scores per type
        type_scores = []
        for type_data in snapshot.get("types", []):
            type_score = self.scoring_service.calculate_type_score(
                type_data, answers_by_question
            )
            type_scores.append(type_score)

        # Calculate overall score
        overall_score = self.scoring_service.calculate_overall_score(type_scores)

        # Save scores to database
        await self.scoring_service.save_scores(
            assessment.id, type_scores, overall_score
        )

        # Mark assessment as completed
        await self.assessment_repo.mark_completed(
            assessment, datetime.now(timezone.utc)
        )

        # Build response
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

        Args:
            snapshot: Questions snapshot.
            question_id: Question ID.
            selected_option: "YES" or "NO".

        Returns:
            Score value for the selected option.
        """
        for type_data in snapshot.get("types", []):
            for question in type_data.get("questions", []):
                if question["id"] == question_id:
                    options = question.get("options", {})
                    return options.get(selected_option, {}).get("score", 0)
        return 0
