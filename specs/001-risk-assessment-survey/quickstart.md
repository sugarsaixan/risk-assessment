# Quickstart: Risk Assessment Survey System

**Feature**: 001-risk-assessment-survey | **Date**: 2026-01-21

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for local services)
- S3-compatible object storage (MinIO for local dev)

## Project Structure

```
risk-assessment/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── admin/          # Admin API routes
│   │   │   └── public/         # Public API routes
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── repositories/       # Database operations
│   │   └── core/               # Config, auth, deps
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/                # Database migrations
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API client
│   │   ├── schemas/            # Zod validation schemas
│   │   └── types/              # TypeScript types
│   ├── tests/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml          # Local dev services
├── specs/                      # Design artifacts
└── CLAUDE.md                   # AI agent context
```

## Backend Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

### 3. Environment configuration

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/risk_assessment

# Object Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=risk-assessment

# Security
API_KEY_PEPPER=your-secret-pepper-change-in-production

# App
PUBLIC_URL=http://localhost:5173
DEBUG=true
```

### 4. Start local services

```bash
# From project root
docker compose up -d postgres minio
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Create initial API key

```bash
python -m src.cli create-api-key --name "Development"
# Outputs: API Key: sk_...  (save this, shown only once)
```

### 7. Start development server

```bash
uvicorn src.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Environment configuration

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 3. Start development server

```bash
npm run dev
```

App available at: http://localhost:5173

## Docker Compose (Full Stack)

```bash
# From project root
docker compose up -d

# Services:
# - postgres: localhost:5432
# - minio: localhost:9000 (console at localhost:9001)
# - backend: localhost:8000
# - frontend: localhost:5173
```

## Testing

### Backend tests

```bash
cd backend

# Unit tests
pytest tests/unit -v

# Integration tests (requires running postgres)
pytest tests/integration -v

# All tests with coverage
pytest --cov=src --cov-report=html
```

### Frontend tests

```bash
cd frontend

# Unit tests
npm test

# With coverage
npm run test:coverage

# E2E tests (requires running backend)
npm run test:e2e
```

## API Quick Reference

### Admin API (requires X-API-Key header)

```bash
# Create questionnaire type
curl -X POST http://localhost:8000/api/admin/types \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_your_key" \
  -d '{"name": "Санхүүгийн эрсдэл", "threshold_high": 80, "threshold_medium": 50}'

# Create question
curl -X POST http://localhost:8000/api/admin/questions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_your_key" \
  -d '{"type_id": "uuid", "text": "Байгууллага санхүүгийн тайлан гаргадаг уу?"}'

# Set question options
curl -X PUT http://localhost:8000/api/admin/questions/{question_id}/options \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_your_key" \
  -d '{
    "options": [
      {"option_type": "YES", "score": 10, "require_comment": false, "require_image": false},
      {"option_type": "NO", "score": 0, "require_comment": true, "require_image": false, "comment_min_len": 50}
    ]
  }'

# Create respondent
curl -X POST http://localhost:8000/api/admin/respondents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_your_key" \
  -d '{"kind": "ORG", "name": "Тест Компани ХХК", "registration_no": "1234567"}'

# Create assessment (generates one-time link)
curl -X POST http://localhost:8000/api/admin/assessments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_your_key" \
  -d '{"respondent_id": "uuid", "type_ids": ["uuid1", "uuid2"]}'
# Returns: {"id": "...", "public_url": "http://localhost:5173/a/token123", "expires_at": "..."}

# Get assessment results
curl http://localhost:8000/api/admin/assessments/{id}/results?breakdown=true \
  -H "X-API-Key: sk_your_key"
```

### Public API (rate limited: 30 req/min/IP)

```bash
# Get assessment form
curl http://localhost:8000/api/public/a/{token}

# Upload image
curl -X POST http://localhost:8000/api/public/a/{token}/upload \
  -F "file=@image.jpg" \
  -F "question_id=uuid"

# Submit assessment
curl -X POST http://localhost:8000/api/public/a/{token}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": "uuid", "selected_option": "YES"},
      {"question_id": "uuid", "selected_option": "NO", "comment": "Тайлбар...", "attachment_ids": ["uuid"]}
    ]
  }'
```

## Development Workflow

1. **Make changes** to backend or frontend code
2. **Run tests** to verify changes
3. **Test manually** via API docs or frontend
4. **Create migration** if database schema changes:
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

## Troubleshooting

### Database connection failed
- Ensure PostgreSQL is running: `docker compose ps`
- Check DATABASE_URL in `.env`

### MinIO/S3 upload failed
- Ensure MinIO is running: `docker compose ps`
- Create bucket if needed: access MinIO console at localhost:9001

### API key authentication failed
- Ensure X-API-Key header is set correctly
- Verify key was created successfully

### Rate limit exceeded
- Public endpoints limited to 30 req/min/IP
- Wait or use different IP for testing
