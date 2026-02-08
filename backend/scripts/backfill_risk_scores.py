"""Backfill risk scores for existing completed assessments.

Re-calculates and updates assessment_scores rows with the new risk grading
fields (classification_label, probability_score, consequence_score, risk_value,
risk_grade, risk_description, insurance_decision) for all completed assessments
that were submitted before the new scoring logic was deployed.

Usage:
    cd backend
    python -m scripts.backfill_risk_scores
"""

import asyncio
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_session_context
from src.models.answer import Answer
from src.models.assessment import Assessment
from src.models.assessment_score import AssessmentScore
from src.models.enums import AssessmentStatus
from src.services.scoring import ScoringService


async def backfill_assessment(session: AsyncSession, assessment: Assessment) -> bool:
    """Re-calculate and update scores for a single assessment.

    Returns True if the assessment was updated, False if skipped.
    """
    snapshot = assessment.questions_snapshot
    if not snapshot or not snapshot.get("types"):
        print(f"  [SKIP] {assessment.id}: No snapshot data")
        return False

    # Fetch answers
    stmt = select(Answer).where(Answer.assessment_id == assessment.id)
    result = await session.execute(stmt)
    answers = result.scalars().all()

    if not answers:
        print(f"  [SKIP] {assessment.id}: No answers")
        return False

    # Build answers_by_question lookup
    answers_by_question: dict[str, int] = {}
    for answer in answers:
        answers_by_question[str(answer.question_id)] = answer.score_awarded

    # Re-calculate using scoring service
    scoring = ScoringService(session)

    type_scores = []
    for type_data in snapshot.get("types", []):
        type_score = scoring.calculate_type_score(type_data, answers_by_question)
        type_scores.append(type_score)

    overall_score = scoring.calculate_overall_score(type_scores)

    # Fetch existing score records
    scores_stmt = select(AssessmentScore).where(
        AssessmentScore.assessment_id == assessment.id
    )
    scores_result = await session.execute(scores_stmt)
    existing_scores = scores_result.scalars().all()

    # Build lookup for existing scores
    score_lookup: dict[tuple[str | None, str | None], AssessmentScore] = {}
    for score in existing_scores:
        key = (str(score.type_id) if score.type_id else None,
               str(score.group_id) if score.group_id else None)
        score_lookup[key] = score

    updated_count = 0

    # Update type-level scores
    for ts in type_scores:
        type_id_str = ts["type_id"]
        key = (type_id_str, None)
        if key in score_lookup:
            score = score_lookup[key]
            score.probability_score = Decimal(str(ts["probability_score"])) if ts.get("probability_score") is not None else None
            score.consequence_score = Decimal(str(ts["consequence_score"])) if ts.get("consequence_score") is not None else None
            score.risk_value = ts.get("risk_value")
            score.risk_grade = ts.get("risk_grade")
            score.risk_description = ts.get("risk_description")
            updated_count += 1

        # Update group-level scores
        for gs in ts.get("groups", []):
            group_key = (type_id_str, gs["group_id"])
            if group_key in score_lookup:
                g_score = score_lookup[group_key]
                g_score.classification_label = gs.get("classification_label")
                updated_count += 1

    # Update overall score
    overall_key = (None, None)
    if overall_key in score_lookup:
        o_score = score_lookup[overall_key]
        o_score.risk_value = overall_score.get("risk_value")
        o_score.risk_grade = overall_score.get("risk_grade")
        o_score.risk_description = overall_score.get("risk_description")
        o_score.insurance_decision = overall_score.get("insurance_decision")
        updated_count += 1

    print(f"  [OK] {assessment.id}: Updated {updated_count} score records "
          f"(grade={overall_score.get('risk_grade')}, "
          f"risk={overall_score.get('risk_value')}, "
          f"insurance={overall_score.get('insurance_decision')})")
    return True


async def main() -> None:
    """Run backfill for all completed assessments."""
    print("=== Backfill Risk Scores ===\n")

    async with get_session_context() as session:
        # Fetch all completed assessments
        stmt = (
            select(Assessment)
            .where(Assessment.status == AssessmentStatus.COMPLETED)
            .order_by(Assessment.completed_at)
        )
        result = await session.execute(stmt)
        assessments = result.scalars().all()

        print(f"Found {len(assessments)} completed assessments\n")

        updated = 0
        skipped = 0
        for assessment in assessments:
            if await backfill_assessment(session, assessment):
                updated += 1
            else:
                skipped += 1

        # Commit is handled by get_session_context
        print(f"\n=== Done: {updated} updated, {skipped} skipped ===")


if __name__ == "__main__":
    asyncio.run(main())
