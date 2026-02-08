# Implementation Plan: Risk Score Calculation & Grading

**Branch**: `006-risk-score-calculation` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-risk-score-calculation/spec.md`

## Summary

Replace the existing percentage-based scoring model (LOW/MEDIUM/HIGH) with a new hierarchical risk grading system. Groups get Mongolian classification labels based on sum scores (0–5). Types compute probability and consequence scores using AVERAGE + 0.618 × STDEV.S, multiplied together for a per-type risk value mapped to letter grades (AAA–D). Overall risk aggregates type risk values with the same formula, determines a total grade, and produces an insurance decision (ДААТГАХ ЭСЭХ). The result page displays the full hierarchy with color-coded grades.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic 2.x, asyncpg (backend); React 18, React Router v6, TailwindCSS (frontend)
**Storage**: PostgreSQL (existing `assessment_scores` table, add nullable columns)
**Testing**: pytest (backend), existing test infrastructure
**Target Platform**: Web application (server + SPA)
**Project Type**: Web (backend + frontend)
**Performance Goals**: Result page loads within 3 seconds
**Constraints**: All calculations server-side; backward compatible with existing assessment data
**Scale/Scope**: Extends existing scoring service and result page; no new endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a blank template — no project-specific gates defined. Proceeding with standard engineering practices.

**Post-Phase 1 re-check**: No violations. Design extends existing patterns (same table, same API shape, same component hierarchy).

## Project Structure

### Documentation (this feature)

```text
specs/006-risk-score-calculation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── results-api.md   # API contract changes
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── assessment_score.py    # MODIFY: add new nullable columns
│   ├── services/
│   │   ├── scoring.py             # MODIFY: replace scoring logic
│   │   └── results.py             # MODIFY: map new fields to response
│   ├── schemas/
│   │   ├── results.py             # MODIFY: add new fields
│   │   └── public.py              # MODIFY: add new fields
│   └── api/
│       └── public/assessment.py   # NO CHANGE: existing endpoint shape sufficient
├── tests/
│   └── (new test files for scoring)
└── alembic/
    └── versions/
        └── (new migration for columns)

frontend/
├── src/
│   ├── types/
│   │   └── api.ts                 # MODIFY: extend result types
│   ├── components/
│   │   ├── OverallScoreCard.tsx   # MODIFY: show grade, risk description, insurance
│   │   └── TypeScoreCard.tsx      # MODIFY: show probability, consequence, grade
│   └── pages/
│       └── Results.tsx            # MODIFY: update layout for new scoring hierarchy
└── tests/
```

**Structure Decision**: Extends existing web application structure. No new directories or architectural changes needed — all modifications within existing files and patterns.

## Complexity Tracking

No constitution violations to justify.
