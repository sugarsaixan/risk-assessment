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
