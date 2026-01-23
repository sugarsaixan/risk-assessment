"""Service for creating question snapshots for assessments."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import OptionType
from src.repositories.question import QuestionRepository
from src.repositories.question_group import QuestionGroupRepository
from src.repositories.questionnaire_type import QuestionnaireTypeRepository


class SnapshotService:
    """Service for creating deep copies of questions/options for assessments.

    When an assessment is created, we snapshot the current state of questions
    and options so that later changes don't affect in-progress assessments.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.type_repo = QuestionnaireTypeRepository(session)
        self.group_repo = QuestionGroupRepository(session)
        self.question_repo = QuestionRepository(session)

    async def create_snapshot(self, type_ids: list[UUID]) -> dict[str, Any]:
        """Create a snapshot of questions and options for the given types.

        Args:
            type_ids: List of QuestionnaireType IDs to include in the snapshot.

        Returns:
            Snapshot dictionary with hierarchical structure:
            {
                "types": [
                    {
                        "id": "uuid",
                        "name": "Type Name",
                        "threshold_high": 80,
                        "threshold_medium": 50,
                        "weight": 1.0,
                        "groups": [
                            {
                                "id": "uuid",
                                "name": "Group Name",
                                "display_order": 1,
                                "weight": 1.0,
                                "questions": [
                                    {
                                        "id": "uuid",
                                        "text": "Question text",
                                        "display_order": 1,
                                        "weight": 1.0,
                                        "is_critical": false,
                                        "options": {
                                            "YES": {...},
                                            "NO": {...}
                                        }
                                    }
                                ]
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

        # Get all active groups for these types
        groups = await self.group_repo.get_active_by_type_ids(type_ids)
        groups_by_type: dict[UUID, list] = {}
        for group in groups:
            if group.type_id not in groups_by_type:
                groups_by_type[group.type_id] = []
            groups_by_type[group.type_id].append(group)

        # Get all questions for these groups
        group_ids = [g.id for g in groups]
        questions = await self.question_repo.get_by_group_ids_with_options(
            group_ids, is_active=True
        )
        questions_by_group: dict[UUID, list] = {}
        for question in questions:
            if question.group_id not in questions_by_group:
                questions_by_group[question.group_id] = []
            questions_by_group[question.group_id].append(question)

        snapshot_types = []

        for qtype in types:
            type_groups = groups_by_type.get(qtype.id, [])
            snapshot_groups = []

            for group in type_groups:
                group_questions = questions_by_group.get(group.id, [])
                snapshot_questions = []

                for question in group_questions:
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
                        "weight": float(question.weight),
                        "is_critical": question.is_critical,
                        "options": options_dict,
                    })

                # Sort questions by display_order
                snapshot_questions.sort(key=lambda q: q["display_order"])

                snapshot_groups.append({
                    "id": str(group.id),
                    "name": group.name,
                    "display_order": group.display_order,
                    "weight": float(group.weight),
                    "questions": snapshot_questions,
                })

            # Sort groups by display_order
            snapshot_groups.sort(key=lambda g: g["display_order"])

            snapshot_types.append({
                "id": str(qtype.id),
                "name": qtype.name,
                "threshold_high": qtype.threshold_high,
                "threshold_medium": qtype.threshold_medium,
                "weight": float(qtype.weight),
                "groups": snapshot_groups,
            })

        return {"types": snapshot_types}

    def get_total_questions(self, snapshot: dict[str, Any]) -> int:
        """Get total number of questions in a snapshot."""
        total = 0
        for qtype in snapshot.get("types", []):
            for group in qtype.get("groups", []):
                total += len(group.get("questions", []))
        return total

    def get_question_ids(self, snapshot: dict[str, Any]) -> list[str]:
        """Get all question IDs from a snapshot."""
        question_ids = []
        for qtype in snapshot.get("types", []):
            for group in qtype.get("groups", []):
                for question in group.get("questions", []):
                    question_ids.append(question["id"])
        return question_ids
