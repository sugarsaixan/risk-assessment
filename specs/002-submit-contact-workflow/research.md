# Research: Submit-Then-Contact Workflow

**Date**: 2026-01-24 | **Feature**: 002-submit-contact-workflow

## Overview

This feature extends 001-risk-assessment-survey. Research focuses on:
1. Draft storage strategy for server-side persistence
2. Auto-save implementation patterns
3. Multi-page form state management in React

## Backend Research

### Draft Storage Strategy

**Decision**: Store drafts as JSONB in PostgreSQL alongside assessments

**Rationale**:
- Drafts are assessment-specific and token-authenticated
- JSONB provides flexible schema for evolving answer formats
- No need for separate storage system (Redis, etc.) at MVP scale
- Simplifies backup/recovery by keeping all data in one database

**Alternatives considered**:
- Redis: Faster but adds infrastructure complexity; not needed at MVP scale
- Separate draft table with normalized columns: More complex schema management
- Client-side only (localStorage): Doesn't meet cross-device requirement

**Implementation pattern**:
```python
class AssessmentDraft(Base):
    __tablename__ = "assessment_drafts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey("assessments.id"), unique=True)
    draft_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_saved_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # One draft per assessment (upsert pattern)
```

---

### Auto-Save Debouncing Strategy

**Decision**: Backend accepts saves at any rate; frontend debounces

**Rationale**:
- Backend should be stateless and accept any valid save request
- Frontend controls user experience and network efficiency
- Debouncing in frontend prevents excessive API calls during rapid typing

**Implementation pattern**:
- Frontend debounces saves by 2 seconds after last change
- 30-second interval timer as fallback for idle users
- Backend uses upsert (INSERT ON CONFLICT UPDATE) for atomic saves

---

### Draft Cleanup Admin Endpoint

**Decision**: Single admin endpoint to cleanup drafts for expired assessments

**Rationale**:
- Matches existing admin API pattern with X-API-Key authentication
- Batch operation is more efficient than per-draft deletion
- Can include optional filters (older than X days, specific respondent, etc.)

**Implementation pattern**:
```python
@router.delete("/cleanup/drafts")
async def cleanup_orphaned_drafts(
    older_than_days: int = Query(default=30),
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    # Delete drafts where assessment.expires_at < now - older_than_days
    # Also cleanup associated orphaned images
```

---

## Frontend Research

### Multi-Page Form State Management

**Decision**: React Router + React Hook Form with shared context

**Rationale**:
- React Router already in use from 001 implementation
- React Hook Form provides excellent form state management
- Context can hold form state across page navigation
- Matches existing patterns in the codebase

**Alternatives considered**:
- URL state (query params): Limited data size, exposes answers in URL
- Redux/Zustand: Adds complexity; not needed for this use case
- Session storage: Doesn't sync with server; risk of stale data

**Implementation pattern**:
```typescript
// AssessmentContext holds form state
const AssessmentContext = createContext<AssessmentState | null>(null);

// Routes
<Route path="/a/:token" element={<AssessmentForm />} />
<Route path="/a/:token/contact" element={<ContactPage />} />
<Route path="/a/:token/results" element={<ResultsPage />} />
```

---

### Auto-Save Hook Pattern

**Decision**: Custom useAutoSave hook with debounce and retry logic

**Rationale**:
- Encapsulates all auto-save logic in one reusable hook
- Handles network failures gracefully with exponential backoff
- Provides status for UI indicator ("Saving...", "Saved", "Failed")

**Implementation pattern**:
```typescript
function useAutoSave(formData: FormData, token: string) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // Debounced save on change
  const debouncedSave = useDebouncedCallback(async (data) => {
    setStatus('saving');
    try {
      await draftService.save(token, data);
      setStatus('saved');
    } catch (e) {
      setStatus('error');
      // Retry logic
    }
  }, 2000);

  // Interval save every 30s
  useInterval(() => {
    if (hasChanges) debouncedSave(formData);
  }, 30000);

  return { status, saveNow: () => debouncedSave.flush() };
}
```

**Packages**: `use-debounce` (already common in React projects)

---

### Navigation Between Questionnaire and Contact Form

**Decision**: React Router navigation with state preservation via context

**Rationale**:
- Clean URL structure (/a/{token} → /a/{token}/contact → /a/{token}/results)
- Browser back button works naturally
- Form state preserved in context, restored on back navigation

**Implementation pattern**:
```typescript
// On Submit click (questionnaire complete)
navigate(`/a/${token}/contact`);

// On Back click (contact form)
navigate(`/a/${token}`);

// On Confirm click (contact complete)
await submitAssessment(token, answers, contact);
navigate(`/a/${token}/results`);
```

---

## API Design Research

### Draft Endpoints

**Decision**: Two public endpoints under existing /a/{token} namespace

**Rationale**:
- Follows existing URL pattern from 001
- Token provides authentication (no additional auth needed)
- Separate GET/PUT aligns with REST semantics

**Endpoints**:
```
PUT  /api/public/a/{token}/draft  - Save draft
GET  /api/public/a/{token}/draft  - Load draft (or returns null if none)
```

**Draft data structure**:
```json
{
  "answers": [
    {
      "question_id": "uuid",
      "selected_option": "YES",
      "comment": "optional text",
      "attachment_ids": ["uuid", "uuid"]
    }
  ],
  "last_saved_at": "2026-01-24T10:30:00Z"
}
```

---

## Unresolved Items

None. All technical decisions have been made.

---

## Package Summary

### Backend (Python) - New dependencies
- None required; uses existing SQLAlchemy, Pydantic, FastAPI

### Frontend (TypeScript/React) - New dependencies
- `use-debounce` - For auto-save debouncing (if not already present)
- Or use lodash.debounce if lodash already in project
