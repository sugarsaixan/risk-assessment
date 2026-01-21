"""Service for calculating assessment scores."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment_score import AssessmentScore
from src.models.enums import RiskRating


class ScoringService:
    """Service for calculating per-type and overall assessment scores."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def calculate_risk_rating(
        self,
        percentage: float,
        threshold_high: int,
        threshold_medium: int,
    ) -> RiskRating:
        """Calculate risk rating based on percentage and thresholds.

        Args:
            percentage: Score percentage (0-100).
            threshold_high: Threshold for LOW risk (>= this = low).
            threshold_medium: Threshold for MEDIUM risk (>= this = medium).

        Returns:
            RiskRating: LOW, MEDIUM, or HIGH.
        """
        if percentage >= threshold_high:
            return RiskRating.LOW
        elif percentage >= threshold_medium:
            return RiskRating.MEDIUM
        else:
            return RiskRating.HIGH

    def calculate_type_score(
        self,
        type_data: dict[str, Any],
        answers_by_question: dict[str, int],
    ) -> dict[str, Any]:
        """Calculate score for a single questionnaire type.

        Args:
            type_data: Type data from snapshot including questions.
            answers_by_question: Map of question_id -> score_awarded.

        Returns:
            Dict with raw_score, max_score, percentage, risk_rating.
        """
        raw_score = 0
        max_score = 0

        for question in type_data.get("questions", []):
            question_id = question["id"]
            options = question.get("options", {})

            # Get max possible score for this question
            yes_score = options.get("YES", {}).get("score", 0)
            no_score = options.get("NO", {}).get("score", 0)
            question_max = max(yes_score, no_score)
            max_score += question_max

            # Get awarded score
            if question_id in answers_by_question:
                raw_score += answers_by_question[question_id]

        # Calculate percentage
        percentage = (raw_score / max_score * 100) if max_score > 0 else 0.0

        # Calculate risk rating
        risk_rating = self.calculate_risk_rating(
            percentage,
            type_data.get("threshold_high", 80),
            type_data.get("threshold_medium", 50),
        )

        return {
            "type_id": type_data["id"],
            "type_name": type_data["name"],
            "raw_score": raw_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "risk_rating": risk_rating,
            "weight": type_data.get("weight", 1.0),
        }

    def calculate_overall_score(
        self,
        type_scores: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate overall score from type scores.

        Uses weighted average based on type weights.

        Args:
            type_scores: List of type score results.

        Returns:
            Dict with raw_score, max_score, percentage, risk_rating.
        """
        total_raw = sum(ts["raw_score"] for ts in type_scores)
        total_max = sum(ts["max_score"] for ts in type_scores)

        # Weighted percentage calculation
        total_weighted_percentage = sum(
            ts["percentage"] * ts["weight"] for ts in type_scores
        )
        total_weight = sum(ts["weight"] for ts in type_scores)

        overall_percentage = (
            total_weighted_percentage / total_weight if total_weight > 0 else 0.0
        )

        # Use default thresholds for overall rating
        risk_rating = self.calculate_risk_rating(overall_percentage, 80, 50)

        return {
            "raw_score": total_raw,
            "max_score": total_max,
            "percentage": round(overall_percentage, 2),
            "risk_rating": risk_rating,
        }

    async def save_scores(
        self,
        assessment_id: UUID,
        type_scores: list[dict[str, Any]],
        overall_score: dict[str, Any],
    ) -> list[AssessmentScore]:
        """Save calculated scores to database.

        Args:
            assessment_id: Assessment UUID.
            type_scores: List of per-type score results.
            overall_score: Overall score result.

        Returns:
            List of created AssessmentScore records.
        """
        scores = []

        # Save per-type scores
        for ts in type_scores:
            score = AssessmentScore(
                assessment_id=assessment_id,
                type_id=UUID(ts["type_id"]),
                raw_score=ts["raw_score"],
                max_score=ts["max_score"],
                percentage=Decimal(str(ts["percentage"])),
                risk_rating=ts["risk_rating"],
            )
            self.session.add(score)
            scores.append(score)

        # Save overall score (type_id = NULL)
        overall = AssessmentScore(
            assessment_id=assessment_id,
            type_id=None,
            raw_score=overall_score["raw_score"],
            max_score=overall_score["max_score"],
            percentage=Decimal(str(overall_score["percentage"])),
            risk_rating=overall_score["risk_rating"],
        )
        self.session.add(overall)
        scores.append(overall)

        await self.session.flush()
        return scores
