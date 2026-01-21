# Implementation Plan: Risk Assessment Survey System

**Branch**: `001-risk-assessment-survey` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-risk-assessment-survey/spec.md`

## Summary

Build a risk assessment survey system with an Admin API (FastAPI) for configuring questionnaires and generating one-time assessment links, and a Public UI (React + TypeScript) for respondents to complete assessments in Mongolian Cyrillic. The system calculates per-type and overall risk scores, stores results in PostgreSQL, and handles image attachments via object storage.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router, TailwindCSS (frontend)
**Storage**: PostgreSQL (relational data), S3/MinIO (image attachments)
**Testing**: pytest + pytest-asyncio (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Linux server (Docker), modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**: Form load <2s, submission <1s, Admin API response <500ms p95
**Constraints**: Rate limit 30 req/min/IP on public endpoints, image upload max 5MB, max 3 images per question
**Scale/Scope**: Phase 1 MVP - single tenant, ~1000 assessments/month expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-Phase 0 Status**: PASS (No project-specific constitution configured)

**Post-Phase 1 Status**: PASS

The project constitution (`.specify/memory/constitution.md`) is currently in template format with no project-specific principles defined. This implementation follows industry best practices:

- **Security**: Token hashing (SHA-256), API key auth (Argon2), rate limiting (slowapi), input validation (Pydantic + Zod)
- **Testing**: Unit tests for business logic, integration tests for API endpoints, E2E tests for critical flows
- **Code Quality**: Type safety (TypeScript strict mode, Pydantic validation), linting, formatting
- **Documentation**: OpenAPI specs defined in contracts/, inline code comments for complex logic

No violations or deviations from best practices identified in the design phase.

## Project Structure

### Documentation (this feature)

```text
specs/001-risk-assessment-survey/
├── plan.md              # This file
├── research.md          # Technology decisions and rationale
├── data-model.md        # Database schema and entity definitions
├── quickstart.md        # Setup and development guide
├── contracts/
│   ├── admin-api.yaml   # OpenAPI spec for Admin API
│   └── public-api.yaml  # OpenAPI spec for Public API
└── tasks.md             # Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── admin/           # Admin API routes (types, questions, respondents, assessments)
│   │   └── public/          # Public API routes (form, upload, submit)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic (scoring, validation, snapshots)
│   ├── repositories/        # Database access layer
│   └── core/                # Config, auth, dependencies, rate limiting
├── tests/
│   ├── unit/                # Service and utility tests
│   ├── integration/         # API endpoint tests
│   └── conftest.py          # Pytest fixtures
├── alembic/                 # Database migrations
├── pyproject.toml
└── Dockerfile

frontend/
├── src/
│   ├── components/          # Reusable UI (Question, ProgressBar, FileUpload)
│   ├── pages/               # Route pages (AssessmentForm, Results, ErrorPages)
│   ├── hooks/               # Custom hooks (useForm, useUpload)
│   ├── services/            # API client
│   ├── schemas/             # Zod validation schemas
│   └── types/               # TypeScript type definitions
├── tests/
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── Dockerfile

docker-compose.yml           # PostgreSQL, MinIO, backend, frontend
```

**Structure Decision**: Web application with separate backend (FastAPI) and frontend (React SPA) directories. This structure supports independent development, testing, and deployment of each component.

## Complexity Tracking

> No constitution violations to justify.

| Decision | Rationale |
|----------|-----------|
| Separate backend/frontend | Standard web application pattern; enables independent scaling and deployment |
| Repository pattern | Abstracts database operations; simplifies testing with mock repositories |
| JSONB for question snapshots | PostgreSQL-native JSON support; avoids complex snapshot tables while preserving query capability |
