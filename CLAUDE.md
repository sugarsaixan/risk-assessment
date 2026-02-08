# risk-assessment Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-21

## Active Technologies
- PostgreSQL (primary), S3-compatible object storage (images) (001-risk-assessment-survey)
- Python 3.11+ (backend), TypeScript 5.x (frontend) - inherited from 001 + FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router, TailwindCSS (frontend) - inherited from 001 (002-submit-contact-workflow)
- PostgreSQL (primary), S3-compatible object storage (images) - inherited from 001 (002-submit-contact-workflow)
- Python 3.11+ (backend only — no frontend changes) + FastAPI, SQLAlchemy 2.0 (async), Pydantic 2.x, asyncpg (003-odoo-respondent-sync)
- PostgreSQL (existing, via asyncpg) (003-odoo-respondent-sync)
- Python 3.11+ (backend), TypeScript 5.x (frontend) + FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router v6, TailwindCSS (frontend) (004-hide-result-confirmation)
- TypeScript 5.x (frontend), Python 3.11+ (backend - minor change) + React 18, React Router, TailwindCSS (frontend); FastAPI (backend) (005-result-answers-display)
- N/A (uses existing data) (005-result-answers-display)

- Python 3.11+ (backend), TypeScript 5.x (frontend) + FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router, TailwindCSS (frontend) (001-risk-assessment-survey)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+ (backend), TypeScript 5.x (frontend): Follow standard conventions

## Recent Changes
- 005-result-answers-display: Added TypeScript 5.x (frontend), Python 3.11+ (backend - minor change) + React 18, React Router, TailwindCSS (frontend); FastAPI (backend)
- 004-hide-result-confirmation: Added Python 3.11+ (backend), TypeScript 5.x (frontend) + FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router v6, TailwindCSS (frontend)
- 003-odoo-respondent-sync: Added Python 3.11+ (backend only — no frontend changes) + FastAPI, SQLAlchemy 2.0 (async), Pydantic 2.x, asyncpg


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
