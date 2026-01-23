"""Service for calculating assessment scores with hierarchical structure."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment_score import AssessmentScore
from src.models.enums import RiskRating


class ScoringService:
    """Service for calculating hierarchical assessment scores.

    Scoring hierarchy:
    - Question: Individual score from YES/NO option
    - Group: Weighted average of questions within group
    - Type: Weighted average of groups within type
    - Overall: Weighted average of types
    """

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

    def calculate_group_score(
        self,
        group_data: dict[str, Any],
        answers_by_question: dict[str, int],
        threshold_high: int = 80,
        threshold_medium: int = 50,
    ) -> dict[str, Any]:
        """Calculate score for a single question group.

        Args:
            group_data: Group data from snapshot including questions.
            answers_by_question: Map of question_id -> score_awarded.
            threshold_high: Threshold for LOW risk rating.
            threshold_medium: Threshold for MEDIUM risk rating.

        Returns:
            Dict with group_id, group_name, raw_score, max_score, percentage, risk_rating, weight.
        """
        raw_score = 0
        max_score = 0

        for question in group_data.get("questions", []):
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
            percentage, threshold_high, threshold_medium
        )

        return {
            "group_id": group_data["id"],
            "group_name": group_data["name"],
            "raw_score": raw_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "risk_rating": risk_rating,
            "weight": group_data.get("weight", 1.0),
        }

    def calculate_type_score(
        self,
        type_data: dict[str, Any],
        answers_by_question: dict[str, int],
    ) -> dict[str, Any]:
        """Calculate score for a single questionnaire type with group breakdown.

        Args:
            type_data: Type data from snapshot including groups and questions.
            answers_by_question: Map of question_id -> score_awarded.

        Returns:
            Dict with type_id, type_name, raw_score, max_score, percentage, risk_rating, weight, groups.
        """
        threshold_high = type_data.get("threshold_high", 80)
        threshold_medium = type_data.get("threshold_medium", 50)

        # Calculate scores for each group
        group_scores = []
        for group_data in type_data.get("groups", []):
            group_score = self.calculate_group_score(
                group_data,
                answers_by_question,
                threshold_high,
                threshold_medium,
            )
            group_scores.append(group_score)

        # Aggregate raw scores across all groups
        total_raw = sum(gs["raw_score"] for gs in group_scores)
        total_max = sum(gs["max_score"] for gs in group_scores)

        # Weighted percentage calculation from groups
        if group_scores:
            total_weighted_percentage = sum(
                gs["percentage"] * gs["weight"] for gs in group_scores
            )
            total_weight = sum(gs["weight"] for gs in group_scores)
            type_percentage = (
                total_weighted_percentage / total_weight if total_weight > 0 else 0.0
            )
        else:
            type_percentage = 0.0

        # Calculate risk rating for type
        risk_rating = self.calculate_risk_rating(
            type_percentage, threshold_high, threshold_medium
        )

        return {
            "type_id": type_data["id"],
            "type_name": type_data["name"],
            "raw_score": total_raw,
            "max_score": total_max,
            "percentage": round(type_percentage, 2),
            "risk_rating": risk_rating,
            "weight": type_data.get("weight", 1.0),
            "groups": group_scores,
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

        Saves scores at three levels:
        - Group scores (group_id set, type_id set)
        - Type scores (group_id NULL, type_id set)
        - Overall score (group_id NULL, type_id NULL)

        Args:
            assessment_id: Assessment UUID.
            type_scores: List of per-type score results with nested groups.
            overall_score: Overall score result.

        Returns:
            List of created AssessmentScore records.
        """
        scores = []

        # Save per-type and per-group scores
        for ts in type_scores:
            type_uuid = UUID(ts["type_id"])

            # Save group-level scores
            for gs in ts.get("groups", []):
                group_score = AssessmentScore(
                    assessment_id=assessment_id,
                    type_id=type_uuid,
                    group_id=UUID(gs["group_id"]),
                    raw_score=gs["raw_score"],
                    max_score=gs["max_score"],
                    percentage=Decimal(str(gs["percentage"])),
                    risk_rating=gs["risk_rating"],
                )
                self.session.add(group_score)
                scores.append(group_score)

            # Save type-level score (group_id = NULL)
            type_score = AssessmentScore(
                assessment_id=assessment_id,
                type_id=type_uuid,
                group_id=None,
                raw_score=ts["raw_score"],
                max_score=ts["max_score"],
                percentage=Decimal(str(ts["percentage"])),
                risk_rating=ts["risk_rating"],
            )
            self.session.add(type_score)
            scores.append(type_score)

        # Save overall score (type_id = NULL, group_id = NULL)
        overall = AssessmentScore(
            assessment_id=assessment_id,
            type_id=None,
            group_id=None,
            raw_score=overall_score["raw_score"],
            max_score=overall_score["max_score"],
            percentage=Decimal(str(overall_score["percentage"])),
            risk_rating=overall_score["risk_rating"],
        )
        self.session.add(overall)
        scores.append(overall)

        await self.session.flush()
        return scores
