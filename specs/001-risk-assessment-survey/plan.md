# Implementation Plan: Risk Assessment Survey System

**Branch**: `001-risk-assessment-survey` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-risk-assessment-survey/spec.md`

## Summary

Build a risk assessment survey system with:
- **Backend**: Admin API for managing questionnaire types, groups, questions, respondents, and assessments. Public API for assessment form access and submission. All score calculations performed on backend.
- **Frontend**: Public-facing assessment form in Mongolian Cyrillic with YES/NO questions, conditional comments/images, submission contact collection, and results display.

Hierarchical scoring: Questions → Groups → Types → Overall (weighted averages)

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router, TailwindCSS (frontend)
**Storage**: PostgreSQL (primary), S3-compatible object storage (images)
**Testing**: pytest (backend), Vitest + Testing Library (frontend)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <2s page load, <1s submission processing, 30 req/min rate limit
**Constraints**: Mobile-first responsive, WCAG AA compliance, Mongolian Cyrillic only
**Scale/Scope**: MVP scale - hundreds of assessments, tens of concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: Constitution not configured (template only) - proceeding without gate enforcement.

## Project Structure

### Documentation (this feature)

```text
specs/001-risk-assessment-survey/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin/           # Admin API routes
│   │   │   │   ├── types.py
│   │   │   │   ├── groups.py
│   │   │   │   ├── questions.py
│   │   │   │   ├── respondents.py
│   │   │   │   └── assessments.py
│   │   │   └── public/          # Public API routes
│   │   │       ├── assessment.py
│   │   │       └── upload.py
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── questionnaire.py # Type, Group, Question, Option
│   │   │   ├── respondent.py
│   │   │   ├── assessment.py    # Assessment, Answer, Attachment
│   │   │   └── contact.py       # SubmissionContact
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── scoring.py       # Score calculation logic
│   │   │   ├── assessment.py
│   │   │   └── storage.py       # S3 upload handling
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py      # API key validation
│   │   │   └── database.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── assessment/
    │   │   │   ├── QuestionCard.tsx
    │   │   │   ├── OptionSelector.tsx
    │   │   │   ├── CommentField.tsx
    │   │   │   ├── ImageUpload.tsx
    │   │   │   └── ProgressIndicator.tsx
    │   │   ├── contact/
    │   │   │   └── ContactForm.tsx
    │   │   ├── results/
    │   │   │   ├── ScoreDisplay.tsx
    │   │   │   └── RiskRating.tsx
    │   │   └── common/
    │   │       ├── Button.tsx
    │   │       └── Input.tsx
    │   ├── pages/
    │   │   ├── AssessmentPage.tsx
    │   │   ├── ResultsPage.tsx
    │   │   └── ErrorPage.tsx
    │   ├── services/
    │   │   └── api.ts
    │   ├── hooks/
    │   │   └── useAssessment.ts
    │   ├── types/
    │   │   └── assessment.ts
    │   ├── i18n/
    │   │   └── mn.ts            # Mongolian translations
    │   ├── App.tsx
    │   └── main.tsx
    ├── tests/
    ├── index.html
    ├── vite.config.ts
    ├── tailwind.config.js
    └── package.json
```

**Structure Decision**: Web application with separate backend (Python/FastAPI) and frontend (React/TypeScript) directories under `src/`. This separation enables independent deployment and testing while maintaining a monorepo structure.

## Complexity Tracking

> No constitution violations to justify - constitution not configured.
