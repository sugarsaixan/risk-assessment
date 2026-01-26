# Data Model Changes: Submit-Then-Contact Workflow

**Date**: 2026-01-24 | **Feature**: 002-submit-contact-workflow
**Base**: Extends data model from 001-risk-assessment-survey

## Entity Relationship Diagram (Changes Only)

```
┌─────────────────────┐
│    assessments      │
├─────────────────────┤
│ id (PK)             │◄─────────────────────────────────────┐
│ ... (existing)      │                                      │
│ status              │ ← MODIFIED: Add DRAFT status option  │
└─────────────────────┘                                      │
         │                                                   │
         │ 1:1 (optional)                                    │
         ▼                                                   │
┌─────────────────────────┐                                  │
│   assessment_drafts     │ ← NEW TABLE                      │
├─────────────────────────┤                                  │
│ id (PK)                 │                                  │
│ assessment_id (FK, UQ)  │──────────────────────────────────┘
│ draft_data (JSONB)      │
│ last_saved_at           │
│ created_at              │
└─────────────────────────┘
```

## New Entity: assessment_drafts

Server-side storage for partial questionnaire progress.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| assessment_id | UUID | FK → assessments, UNIQUE, NOT NULL | One draft per assessment |
| draft_data | JSONB | NOT NULL | Serialized form state |
| last_saved_at | TIMESTAMP | NOT NULL | When draft was last updated |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When draft was first created |

**Indexes**:
- `assessment_id` (unique) - for fast lookup by assessment

**JSONB Structure** (`draft_data`):
```json
{
  "answers": [
    {
      "question_id": "uuid",
      "selected_option": "YES" | "NO" | null,
      "comment": "string or null",
      "attachment_ids": ["uuid", ...]
    }
  ],
  "current_type_index": 0,
  "current_group_index": 0
}
```

**Validation rules**:
- `draft_data` must be valid JSON matching expected schema
- `assessment_id` must reference a valid, non-expired, pending assessment

---

## Modified Entity: assessments

### Status Enum Change

**Current** (from 001):
```sql
CREATE TYPE assessment_status AS ENUM ('PENDING', 'COMPLETED', 'EXPIRED');
```

**No change needed**: PENDING status already covers drafts. A draft is simply an assessment in PENDING status that has an associated `assessment_drafts` record.

### Workflow State Logic

| Assessment Status | Has Draft Record | Interpretation |
|-------------------|------------------|----------------|
| PENDING | No | Fresh assessment, never started |
| PENDING | Yes | In-progress, has saved answers |
| COMPLETED | Any | Submitted, draft can be deleted |
| EXPIRED | Any | Cannot be accessed, draft inaccessible |

---

## Data Lifecycle

### Draft Creation Flow
```
1. User accesses /a/{token}
2. Backend checks: assessment exists, PENDING, not expired
3. Backend checks: draft exists for this assessment?
   - Yes: Return draft_data with assessment snapshot
   - No: Return assessment snapshot only (empty answers)
4. Frontend displays form with restored/empty state
```

### Draft Save Flow
```
1. User modifies answer (or 30s interval)
2. Frontend calls PUT /a/{token}/draft with current answers
3. Backend validates: assessment PENDING, not expired
4. Backend upserts draft record (INSERT ON CONFLICT UPDATE)
5. Backend returns last_saved_at timestamp
6. Frontend shows "Хадгалагдсан" indicator
```

### Final Submission Flow
```
1. User completes questionnaire, clicks "Илгээх"
2. Frontend navigates to /a/{token}/contact
3. User fills contact info, clicks "Баталгаажуулах"
4. Frontend calls POST /a/{token}/submit with answers + contact
5. Backend:
   - Validates all answers
   - Creates SubmissionContact
   - Creates Answer records
   - Calculates scores
   - Updates assessment status to COMPLETED
   - Deletes draft record (if exists)
6. Frontend redirects to /a/{token}/results
```

### Draft Cleanup Flow
```
1. Admin calls DELETE /admin/cleanup/drafts?older_than_days=30
2. Backend finds assessments where:
   - expires_at < NOW() - older_than_days
   - status != COMPLETED
3. For each expired assessment:
   - Delete draft record
   - Optionally: Delete orphaned attachments
4. Return count of cleaned records
```

---

## Migration Plan

### New Migration: add_assessment_drafts

```sql
-- Up
CREATE TABLE assessment_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL UNIQUE REFERENCES assessments(id) ON DELETE CASCADE,
    draft_data JSONB NOT NULL,
    last_saved_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assessment_drafts_assessment_id ON assessment_drafts(assessment_id);

-- Down
DROP TABLE assessment_drafts;
```

**Note**: `ON DELETE CASCADE` ensures drafts are automatically deleted when assessments are deleted.

---

## Data Retention

Per clarifications:
- Drafts persist indefinitely until assessment is submitted or admin triggers cleanup
- Link expiration controls access, not data deletion
- Uploaded images for incomplete assessments retained until admin cleanup
