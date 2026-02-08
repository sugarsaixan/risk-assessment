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

## Risk Score Calculation

Scores are calculated hierarchically: **Question -> Group -> Type -> Overall**.

### Level 1: Group Classification

Each question group's sum score (total of `score_awarded` for all questions in the group) maps to a Mongolian classification:

| Sum Score | Classification | Numeric Value |
|-----------|---------------|---------------|
| 0         | Хэвийн (Normal)     | 1 |
| 1         | Хянахуйц (Watchable) | 2 |
| 2         | Анхаарах (Attention)  | 3 |
| 3         | Ноцтой (Serious)     | 4 |
| 4+        | Аюултай (Dangerous)  | 5 |

### Level 2: Type-Level Probability & Consequence Scores

For each questionnaire type, two scores are derived from its groups:

**Probability Score (МАГАДЛАЛЫН ОНОО)**:
```
AVERAGE(group sum scores) + 0.618 * STDEV.S(group sum scores)
```

**Consequence Score (ҮР ДАГАВРЫН ОНОО)**:
```
AVERAGE(group numeric values) + 0.618 * STDEV.S(group numeric values)
```

- `STDEV.S` = sample standard deviation (N-1 divisor), matching Excel's `STDEV()`.
- When a type has only 1 group, `STDEV.S` = 0, so the score equals the average.

### Level 3: Per-Type Risk Value & Grade

```
Type ЭРСДЭЛ (Risk) = ROUND(Probability Score * Consequence Score)
```

Rounding uses **round-half-up** (0.5 rounds to 1). The risk value maps to a letter grade:

| Risk Value | Grade | Description |
|------------|-------|-------------|
| 1          | AAA   | Эрсдэл маш бага |
| 2-3        | AA    | Эрсдэл бага |
| 4          | A     | Анхаарахгүй, эрсдэл бага |
| 5          | BBB   | Нийцэхүйц, эрсдэл доогуур |
| 6          | BB    | Авахуйц, эрсдэл доогуур |
| 7-9        | B     | Хянахуйц, эрсдэл доогуур |
| 10-11      | CCC   | Хянахуйц, эрсдэл дунд |
| 12-14      | CC    | Анхаарах, эрсдэл дунд |
| 15         | C     | Нэн анхаарах, эрсдэл дунд |
| 16         | DDD   | Ноцтой, эрсдэл дээгүүр |
| 17-20      | DD    | Нэн ноцтой, эрсдэл дээгүүр |
| 21+        | D     | Аюултай, эрсдэл өндөр |

### Level 4: Overall Risk & Insurance Decision

```
НИЙТ ЭРСДЭЛ (Total Risk) = ROUND(AVERAGE(type risk values) + 0.618 * STDEV.S(type risk values))
НИЙТ ЗЭРЭГЛЭЛ (Total Grade) = Grade lookup from the same table above
ДААТГАХ ЭСЭХ (Insurance) = "Даатгахгүй" if НИЙТ ЭРСДЭЛ > 16, else "Даатгана"
```

- When only 1 type exists, `STDEV.S` = 0, so total risk equals that type's risk value.
- The insurance threshold is **strictly greater than** 16 (risk = 16 -> "Даатгана").

### Calculation Example

```
Assessment with 1 type containing 3 groups:
  Group A: sum_score=0 -> Хэвийн (1)
  Group B: sum_score=2 -> Анхаарах (3)
  Group C: sum_score=1 -> Хянахуйц (2)

Probability Score:
  AVERAGE(0, 2, 1) + 0.618 * STDEV.S(0, 2, 1)
  = 1.0 + 0.618 * 1.0 = 1.618

Consequence Score:
  AVERAGE(1, 3, 2) + 0.618 * STDEV.S(1, 3, 2)
  = 2.0 + 0.618 * 1.0 = 2.618

Type Risk Value:
  ROUND(1.618 * 2.618) = ROUND(4.236) = 4
  Grade: A, Description: "Анхаарахгүй, эрсдэл бага"

Overall (single type):
  НИЙТ ЭРСДЭЛ = 4 (STDEV=0 with 1 type)
  НИЙТ ЗЭРЭГЛЭЛ = A
  ДААТГАХ ЭСЭХ = "Даатгана" (4 <= 16)
```

### Grade Color Coding

| Grades     | Color  |
|------------|--------|
| AAA, AA, A | Green  |
| BBB, BB, B | Yellow |
| CCC, CC, C | Orange |
| DDD, DD, D | Red    |

### Result Page Display

The result page shows the full scoring hierarchy:

1. **Overall card** (top): НИЙТ ЭРСДЭЛ value, НИЙТ ЗЭРЭГЛЭЛ grade badge, risk description, ДААТГАХ ЭСЭХ indicator
2. **Per-type cards**: Probability score, consequence score, type risk value, grade badge, description
3. **Per-group rows** (expandable within each type card): Sum score, classification label badge
4. **Summary table**: Score totals, percentage, risk level, grade, insurance decision

Old assessments (without the new scoring fields) fall back to the legacy percentage-based display.

## Backfill Risk Scores

To re-calculate and populate the new scoring fields for existing completed assessments:

```bash
cd backend
python -m scripts.backfill_risk_scores
```

This updates existing `assessment_scores` rows in place with group classifications, type probability/consequence/risk/grade, and overall risk/grade/insurance decision.
