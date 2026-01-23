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
    GroupScore,
    OverallScore,
    SubmissionContactInfo,
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
        # Fetch assessment with respondent and submission contact
        stmt = (
            select(Assessment)
            .options(
                selectinload(Assessment.respondent),
                selectinload(Assessment.submission_contact),
            )
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

        # Separate type scores, group scores, and overall score
        type_scores_map: dict[str, TypeScore] = {}
        group_scores_map: dict[str, list[GroupScore]] = {}
        overall_score_data: OverallScore | None = None

        # Build lookups from snapshot for names
        type_lookup = self._build_type_lookup(assessment.questions_snapshot)
        group_lookup = self._build_group_lookup(assessment.questions_snapshot)

        for score in scores:
            if score.type_id is None and score.group_id is None:
                # Overall score (no type_id and no group_id)
                overall_score_data = OverallScore(
                    raw_score=score.raw_score,
                    max_score=score.max_score,
                    percentage=float(score.percentage),
                    risk_rating=score.risk_rating,
                )
            elif score.group_id is not None:
                # Group-level score
                group_info = group_lookup.get(str(score.group_id), {})
                group_score = GroupScore(
                    group_id=score.group_id,
                    group_name=group_info.get("name", "Unknown"),
                    raw_score=score.raw_score,
                    max_score=score.max_score,
                    percentage=float(score.percentage),
                    risk_rating=score.risk_rating,
                )
                type_id_str = group_info.get("type_id", str(score.type_id) if score.type_id else "")
                if type_id_str not in group_scores_map:
                    group_scores_map[type_id_str] = []
                group_scores_map[type_id_str].append(group_score)
            elif score.type_id is not None:
                # Type-level score (no group_id)
                type_name = type_lookup.get(str(score.type_id), "Unknown")
                type_scores_map[str(score.type_id)] = TypeScore(
                    type_id=score.type_id,
                    type_name=type_name,
                    raw_score=score.raw_score,
                    max_score=score.max_score,
                    percentage=float(score.percentage),
                    risk_rating=score.risk_rating,
                    groups=[],
                )

        # Attach group scores to their parent type scores
        for type_id_str, type_score in type_scores_map.items():
            type_score.groups = group_scores_map.get(type_id_str, [])

        type_scores = list(type_scores_map.values())

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

        # Build contact info if available
        contact_info: SubmissionContactInfo | None = None
        if assessment.submission_contact:
            contact_info = SubmissionContactInfo(
                last_name=assessment.submission_contact.last_name,
                first_name=assessment.submission_contact.first_name,
                email=assessment.submission_contact.email,
                phone=assessment.submission_contact.phone,
                position=assessment.submission_contact.position,
            )

        return AssessmentResultsResponse(
            assessment_id=assessment.id,
            respondent_id=assessment.respondent_id,
            respondent_name=assessment.respondent.name,
            status=assessment.status.value,
            completed_at=assessment.completed_at,
            contact=contact_info,
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

    def _build_group_lookup(self, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Build lookup dict from group_id to group data.

        Args:
            snapshot: Questions snapshot JSONB.

        Returns:
            Dict mapping group_id to group data including type_id.
        """
        lookup = {}
        for type_data in snapshot.get("types", []):
            type_id = type_data.get("id")
            for group in type_data.get("groups", []):
                group_id = group.get("id")
                if group_id:
                    lookup[str(group_id)] = {
                        "name": group.get("name", "Unknown"),
                        "type_id": str(type_id) if type_id else "",
                    }
        return lookup

    def _build_question_lookup(
        self, snapshot: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Build lookup dict from question_id to question data.

        Args:
            snapshot: Questions snapshot JSONB (hierarchical Type→Group→Question).

        Returns:
            Dict mapping question_id to question data including type and group info.
        """
        lookup = {}
        for type_data in snapshot.get("types", []):
            type_id = type_data.get("id")
            type_name = type_data.get("name", "Unknown")

            # Handle hierarchical structure (Type → Group → Questions)
            for group in type_data.get("groups", []):
                group_id = group.get("id")
                group_name = group.get("name", "Unknown")

                for question in group.get("questions", []):
                    question_id = question.get("id")
                    if question_id:
                        lookup[str(question_id)] = {
                            "text": question.get("text", ""),
                            "type_id": type_id,
                            "type_name": type_name,
                            "group_id": group_id,
                            "group_name": group_name,
                            "options": question.get("options", {}),
                        }

            # Also handle flat structure for backwards compatibility
            for question in type_data.get("questions", []):
                question_id = question.get("id")
                if question_id and str(question_id) not in lookup:
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
