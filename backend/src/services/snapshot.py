"""Service for creating question snapshots for assessments."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import OptionType
from src.repositories.question import QuestionRepository
from src.repositories.questionnaire_type import QuestionnaireTypeRepository


class SnapshotService:
    """Service for creating deep copies of questions/options for assessments.

    When an assessment is created, we snapshot the current state of questions
    and options so that later changes don't affect in-progress assessments.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.type_repo = QuestionnaireTypeRepository(session)
        self.question_repo = QuestionRepository(session)

    async def create_snapshot(self, type_ids: list[UUID]) -> dict[str, Any]:
        """Create a snapshot of questions and options for the given types.

        Args:
            type_ids: List of QuestionnaireType IDs to include in the snapshot.

        Returns:
            Snapshot dictionary with structure:
            {
                "types": [
                    {
                        "id": "uuid",
                        "name": "Type Name",
                        "threshold_high": 80,
                        "threshold_medium": 50,
                        "weight": 1.0,
                        "questions": [
                            {
                                "id": "uuid",
                                "text": "Question text",
                                "display_order": 1,
                                "options": {
                                    "YES": {...},
                                    "NO": {...}
                                }
                            }
                        ]
                    }
                ]
            }

        Raises:
            ValueError: If any type_id is not found or inactive.
        """
        # Get all active types
        types = await self.type_repo.get_active_by_ids(type_ids)

        # Verify all requested types were found and are active
        found_ids = {t.id for t in types}
        missing_ids = set(type_ids) - found_ids
        if missing_ids:
            raise ValueError(
                f"Questionnaire types not found or inactive: {list(missing_ids)}"
            )

        snapshot_types = []

        for qtype in types:
            # Get active questions with options
            questions = await self.question_repo.get_by_type_with_options(
                qtype.id, is_active=True
            )

            snapshot_questions = []
            for question in questions:
                # Build options dictionary
                options_dict: dict[str, dict[str, Any]] = {}
                for option in question.options:
                    option_data = {
                        "score": option.score,
                        "require_comment": option.require_comment,
                        "require_image": option.require_image,
                        "comment_min_len": option.comment_min_len,
                        "max_images": option.max_images,
                        "image_max_mb": option.image_max_mb,
                    }
                    if option.option_type == OptionType.YES:
                        options_dict["YES"] = option_data
                    else:
                        options_dict["NO"] = option_data

                # Ensure both YES and NO options exist
                if "YES" not in options_dict or "NO" not in options_dict:
                    raise ValueError(
                        f"Question {question.id} is missing YES or NO option configuration"
                    )

                snapshot_questions.append({
                    "id": str(question.id),
                    "text": question.text,
                    "display_order": question.display_order,
                    "options": options_dict,
                })

            # Sort questions by display_order
            snapshot_questions.sort(key=lambda q: q["display_order"])

            snapshot_types.append({
                "id": str(qtype.id),
                "name": qtype.name,
                "threshold_high": qtype.threshold_high,
                "threshold_medium": qtype.threshold_medium,
                "weight": float(qtype.weight),
                "questions": snapshot_questions,
            })

        return {"types": snapshot_types}

    def get_total_questions(self, snapshot: dict[str, Any]) -> int:
        """Get total number of questions in a snapshot."""
        return sum(len(t["questions"]) for t in snapshot.get("types", []))

    def get_question_ids(self, snapshot: dict[str, Any]) -> list[str]:
        """Get all question IDs from a snapshot."""
        question_ids = []
        for qtype in snapshot.get("types", []):
            for question in qtype.get("questions", []):
                question_ids.append(question["id"])
        return question_ids
