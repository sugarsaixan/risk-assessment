# Research: Risk Assessment Survey System

**Date**: 2026-01-21 | **Feature**: 001-risk-assessment-survey

## Backend Technology Decisions

### API Key Authentication

**Decision**: Use FastAPI's `APIKeyHeader` with passlib+argon2 for hashing

**Rationale**:
- FastAPI's built-in `APIKeyHeader` integrates with OpenAPI documentation
- Argon2 is OWASP-recommended for key hashing (GPU-resistant)
- Dependency injection pattern enables clean, testable auth middleware

**Alternatives considered**:
- JWT tokens: Overkill for admin API with no user sessions
- Basic auth: Less secure, harder to rotate keys
- OAuth2: Too complex for internal API access

**Implementation pattern**:
```python
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

api_key_header = APIKeyHeader(name="X-API-Key")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    # Verify against stored hash using timing-safe comparison
    ...
```

**Packages**: `passlib`, `argon2-cffi`

---

### Rate Limiting

**Decision**: Use slowapi for rate limiting (30 req/min/IP on public endpoints)

**Rationale**:
- Simple integration with FastAPI
- Decorator-based limiting per endpoint
- Returns standard HTTP 429 responses

**Alternatives considered**:
- fastapi-limiter: Requires Redis, adds infrastructure complexity
- Custom middleware: More work, less battle-tested

**Packages**: `slowapi`

---

### Image Upload Handling

**Decision**: Form-based upload through FastAPI with server-side S3/MinIO push

**Rationale**:
- Images are small (max 5MB each, max 3 per question)
- Enables server-side validation before storage
- Simpler error handling and retry logic
- No CORS complexity of presigned URLs

**Alternatives considered**:
- Presigned URLs: Better for large files (>10MB), adds client complexity
- Base64 encoding: Increases payload size 33%, no streaming

**Validation strategy**:
1. Check file size (max 5MB)
2. Check MIME type header (image/*)
3. Validate magic bytes with python-magic (prevents spoofing)

**Packages**: `aioboto3`, `python-magic`

---

### Database ORM

**Decision**: SQLAlchemy 2.0 with async support

**Rationale**:
- Mature, well-documented ORM
- Native async support in 2.0+
- Works seamlessly with FastAPI's async patterns
- Alembic for migrations

**Packages**: `sqlalchemy[asyncio]`, `asyncpg`, `alembic`

---

## Frontend Technology Decisions

### Form Library

**Decision**: React Hook Form + Zod

**Rationale**:
- Smallest bundle size (12KB vs Formik's 44KB)
- Zero dependencies
- Uncontrolled components = fewer re-renders on large forms
- Zod provides TypeScript type generation from schemas
- Excellent file upload support built-in

**Alternatives considered**:
- Formik: Larger bundle, unmaintained (last update 1+ year ago)
- Native forms: Manual validation code, poor DX

**Packages**: `react-hook-form`, `zod`, `@hookform/resolvers`

---

### Conditional Field Handling

**Decision**: Use RHF's `watch()` hook to observe YES/NO selections

**Rationale**:
- Reactive field visibility without custom state management
- Schema-driven validation for conditional requirements
- Clean separation between field logic and validation

**Pattern**:
```typescript
const selectedOption = watch(`questions.${index}.selectedOption`);
const showComment = selectedOption?.require_comment;
const showImage = selectedOption?.require_image;
```

---

### Progress Indicator

**Decision**: Sticky header progress bar showing "X / Y асуулт"

**Rationale**:
- Mobile users see progress at all times
- Simple fraction display matches PRD requirements
- Groups questions by type for context

---

### Styling

**Decision**: TailwindCSS with shadcn/ui components

**Rationale**:
- Utility-first CSS scales well for mobile-first design
- shadcn/ui provides accessible, unstyled components
- Full control over responsive breakpoints
- Easy dark/light mode theming

**Packages**: `tailwindcss`, `@radix-ui/react-*` (via shadcn/ui)

---

### Typography

**Decision**: Noto Sans as primary font

**Rationale**:
- Excellent Mongolian Cyrillic support
- Available via Google Fonts / @fontsource
- Variable font reduces payload
- WCAG AA compliant weights available

**Packages**: `@fontsource/noto-sans`

---

### File Upload UI

**Decision**: Custom file input with drag-and-drop support

**Rationale**:
- react-dropzone provides accessible drag-and-drop
- Client-side validation before upload
- Progress indicators for each file
- Mobile-friendly large touch targets

**Packages**: `react-dropzone`

---

## Architecture Decisions

### Backend Structure

**Decision**: Layered architecture (API → Service → Repository)

**Rationale**:
- Clear separation of concerns
- Services contain business logic (scoring, validation)
- Repositories abstract database operations
- Easier to test each layer independently

**Rejected alternatives**:
- Direct DB access in routes: Harder to test, business logic scattered
- Full DDD: Overkill for MVP complexity

---

### Question Snapshotting

**Decision**: Deep copy questions/options into assessment at creation time

**Rationale**:
- FR-011 requires snapshot behavior
- Prevents configuration changes affecting in-progress assessments
- JSONB column stores snapshot efficiently

**Schema pattern**:
```sql
assessments.questions_snapshot JSONB NOT NULL
-- Contains full question/option data at creation time
```

---

### Token Security

**Decision**: SHA-256 hash with random token generation

**Rationale**:
- FR-010 requires storing only hash
- 32-byte random token provides sufficient entropy
- URL-safe base64 encoding for links

**Pattern**:
```python
token = secrets.token_urlsafe(32)  # 43 chars
token_hash = hashlib.sha256(token.encode()).hexdigest()
# Store hash, return token to admin
```

---

## Unresolved Items

None. All technical decisions have been made.

---

## Package Summary

### Backend (Python)
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `sqlalchemy[asyncio]` - ORM
- `asyncpg` - PostgreSQL async driver
- `alembic` - Database migrations
- `pydantic` - Data validation (included with FastAPI)
- `passlib` + `argon2-cffi` - Password/key hashing
- `slowapi` - Rate limiting
- `aioboto3` - Async S3/MinIO client
- `python-magic` - File type detection
- `pytest` + `pytest-asyncio` - Testing
- `httpx` - Test client

### Frontend (TypeScript/React)
- `react` - UI framework
- `react-dom` - DOM rendering
- `react-router-dom` - Routing
- `react-hook-form` - Form management
- `zod` - Schema validation
- `@hookform/resolvers` - Zod integration
- `tailwindcss` - Styling
- `@radix-ui/react-*` - Accessible components (via shadcn/ui)
- `react-dropzone` - File uploads
- `@fontsource/noto-sans` - Typography
- `axios` - HTTP client
- `vitest` - Testing
- `@testing-library/react` - Component testing
