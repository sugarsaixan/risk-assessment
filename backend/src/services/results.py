"""Service for formatting assessment results for admin retrieval."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.answer import Answer
from src.models.assessment import Assessment
from src.models.assessment_score import AssessmentScore
from src.models.enums import OptionType, RiskRating
from src.schemas.results import (
    AnswerBreakdown,
    AssessmentResultsResponse,
    OverallScore,
    TypeScore,
)


class ResultsService:
    """Service for retrieving and formatting assessment results."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_results(
        self,
        assessment_id: UUID,
        include_breakdown: bool = False,
    ) -> AssessmentResultsResponse | None:
        """Get assessment results with optional answer breakdown.

        Args:
            assessment_id: Assessment UUID.
            include_breakdown: Whether to include individual answer details.

        Returns:
            AssessmentResultsResponse or None if not found/not completed.
        """
        # Fetch assessment with respondent
        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.respondent))
            .where(Assessment.id == assessment_id)
        )
        result = await self.session.execute(stmt)
        assessment = result.scalar_one_or_none()

        if assessment is None:
            return None

        # Fetch scores
        scores_stmt = select(AssessmentScore).where(
            AssessmentScore.assessment_id == assessment_id
        )
        scores_result = await self.session.execute(scores_stmt)
        scores = scores_result.scalars().all()

        # Separate type scores and overall score
        type_scores: list[TypeScore] = []
        overall_score_data: OverallScore | None = None

        # Build type lookup from snapshot for names
        type_lookup = self._build_type_lookup(assessment.questions_snapshot)

        for score in scores:
            if score.type_id is None:
                # Overall score
                overall_score_data = OverallScore(
                    raw_score=score.raw_score,
                    max_score=score.max_score,
                    percentage=float(score.percentage),
                    risk_rating=score.risk_rating,
                )
            else:
                # Per-type score
                type_name = type_lookup.get(str(score.type_id), "Unknown")
                type_scores.append(
                    TypeScore(
                        type_id=score.type_id,
                        type_name=type_name,
                        raw_score=score.raw_score,
                        max_score=score.max_score,
                        percentage=float(score.percentage),
                        risk_rating=score.risk_rating,
                    )
                )

        # Handle case where no overall score exists
        if overall_score_data is None:
            overall_score_data = OverallScore(
                raw_score=0,
                max_score=0,
                percentage=0.0,
                risk_rating=RiskRating.HIGH,
            )

        # Optionally include answer breakdown
        answer_breakdown: list[AnswerBreakdown] | None = None
        if include_breakdown:
            answer_breakdown = await self._get_answer_breakdown(
                assessment_id,
                assessment.questions_snapshot,
            )

        return AssessmentResultsResponse(
            assessment_id=assessment.id,
            respondent_id=assessment.respondent_id,
            respondent_name=assessment.respondent.name,
            status=assessment.status.value,
            completed_at=assessment.completed_at,
            type_scores=type_scores,
            overall_score=overall_score_data,
            answer_breakdown=answer_breakdown,
        )

    def _build_type_lookup(self, snapshot: dict[str, Any]) -> dict[str, str]:
        """Build a lookup dict from type_id to type_name from snapshot.

        Args:
            snapshot: Questions snapshot JSONB.

        Returns:
            Dict mapping type_id string to type_name.
        """
        lookup = {}
        for type_data in snapshot.get("types", []):
            type_id = type_data.get("id")
            type_name = type_data.get("name", "Unknown")
            if type_id:
                lookup[str(type_id)] = type_name
        return lookup

    def _build_question_lookup(
        self, snapshot: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Build lookup dict from question_id to question data.

        Args:
            snapshot: Questions snapshot JSONB.

        Returns:
            Dict mapping question_id to question data including type info.
        """
        lookup = {}
        for type_data in snapshot.get("types", []):
            type_id = type_data.get("id")
            type_name = type_data.get("name", "Unknown")

            for question in type_data.get("questions", []):
                question_id = question.get("id")
                if question_id:
                    lookup[str(question_id)] = {
                        "text": question.get("text", ""),
                        "type_id": type_id,
                        "type_name": type_name,
                        "options": question.get("options", {}),
                    }
        return lookup

    async def _get_answer_breakdown(
        self,
        assessment_id: UUID,
        snapshot: dict[str, Any],
    ) -> list[AnswerBreakdown]:
        """Get detailed answer breakdown for an assessment.

        Args:
            assessment_id: Assessment UUID.
            snapshot: Questions snapshot JSONB.

        Returns:
            List of AnswerBreakdown items.
        """
        # Fetch answers with attachments
        stmt = (
            select(Answer)
            .options(selectinload(Answer.attachments))
            .where(Answer.assessment_id == assessment_id)
        )
        result = await self.session.execute(stmt)
        answers = result.scalars().all()

        # Build question lookup from snapshot
        question_lookup = self._build_question_lookup(snapshot)

        breakdown: list[AnswerBreakdown] = []
        for answer in answers:
            question_data = question_lookup.get(str(answer.question_id), {})
            options = question_data.get("options", {})

            # Get max score for this question
            yes_score = options.get("YES", {}).get("score", 0)
            no_score = options.get("NO", {}).get("score", 0)
            max_score = max(yes_score, no_score)

            breakdown.append(
                AnswerBreakdown(
                    question_id=answer.question_id,
                    question_text=question_data.get("text", ""),
                    type_id=UUID(question_data.get("type_id")) if question_data.get("type_id") else answer.question_id,
                    type_name=question_data.get("type_name", "Unknown"),
                    selected_option=answer.selected_option,
                    comment=answer.comment,
                    score_awarded=answer.score_awarded,
                    max_score=max_score,
                    attachment_count=len(answer.attachments),
                )
            )

        return breakdown
