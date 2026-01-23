# Risk Assessment Survey System

Web application for running risk assessment surveys with a hierarchical structure (Type → Group → Question), file uploads, and results scoring.

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + SQLAlchemy (async)
- Database: PostgreSQL
- Reverse proxy: Traefik (production)

## Repository structure

- `frontend/` – React UI
- `backend/` – FastAPI service
- `questions/` – assessment questions and data
- `specs/` – specs and design notes
- `demo-ui/` – UI demos and references
- `docker-compose.yml` – production compose (Traefik)
- `docker-compose.local.yml` – local compose (no Traefik)
- `DEPLOYMENT.md` – deployment guide

## Quick start (local, no Traefik)

```bash
TAG=1.0.0 docker compose -f docker-compose.local.yml build
TAG=1.0.0 docker compose -f docker-compose.local.yml up -d
```

Local URLs:
- Frontend: http://localhost:8080/assessment/
- API health: http://localhost:8000/assessment/api/health

## Production build (Traefik)

```bash
TAG=1.0.0 docker compose build
TAG=1.0.0 docker compose up -d
```

## Environment variables

Set in `.env` or your deployment environment:

- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (default: `postgres`)
- `POSTGRES_DB` (default: `risk_assessment`)
- `PUBLIC_URL` (e.g. `https://aisys.agula.mn/assessment`)
- `CORS_ORIGINS` (e.g. `https://aisys.agula.mn`)

## Database migrations

```bash
docker compose exec api alembic upgrade head
```

## Tagging images

Images for API and frontend are tagged using `TAG` in compose files:

```bash
TAG=1.0.0 docker compose build
TAG=1.0.0 docker compose up -d
```

If `TAG` is not set, it defaults to `latest`.

## Notes

- The frontend build is configured for the `/assessment/` base path.
- See `DEPLOYMENT.md` for full production steps and troubleshooting.

## Seeding Questions

To populate the database with the default risk assessment questions:

1. **Ensure the database is running** (PostgreSQL via docker-compose):

   ```bash
   docker-compose up -d postgres
   ```

2. **Run migrations**:

   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Set environment variables** (if not already configured):
   - `DATABASE_URL` or appropriate database connection settings

4. **Run the seed**:

   ```bash
   cd backend
   python -m src.seeds.questions_seed
   ```

The script will output progress as it creates:
- 6 Questionnaire Types
- 30 Question Groups (5 per type)
- 150 Questions (25 per type)
- 300 Question Options (YES/NO for each question)
