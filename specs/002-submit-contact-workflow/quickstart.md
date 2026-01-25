# Quickstart: Submit-Then-Contact Workflow

**Feature**: 002-submit-contact-workflow | **Date**: 2026-01-24
**Extends**: 001-risk-assessment-survey

## Prerequisites

- 001-risk-assessment-survey must be fully implemented and working
- Backend running with database migrations applied
- Frontend running and accessible

## Changes Overview

This feature modifies the existing assessment flow:

| Before (001) | After (002) |
|--------------|-------------|
| Contact form shown with questionnaire | Contact form on separate page after Submit |
| No draft saving | Auto-save every 30s + manual Save button |
| Browser-only form state | Server-side draft storage |
| Single-session completion | Cross-device resume support |

## Database Migration

Apply the new migration for draft storage:

```bash
cd backend
alembic upgrade head
```

This creates the `assessment_drafts` table.

## API Changes

### New Endpoints

```bash
# Save draft (auto-save or manual)
curl -X PUT http://localhost:8000/api/public/a/{token}/draft \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": "uuid", "selected_option": "YES", "comment": "text"}
    ]
  }'
# Returns: {"last_saved_at": "2026-01-24T10:30:00Z", "message": "Хадгалагдсан"}

# Load draft
curl http://localhost:8000/api/public/a/{token}/draft
# Returns: {"answers": [...], "last_saved_at": "..."}
# Returns 204 if no draft exists

# Admin: Cleanup orphaned drafts
curl -X DELETE "http://localhost:8000/api/admin/cleanup/drafts?older_than_days=30&dry_run=true" \
  -H "X-API-Key: sk_your_key"
# Returns: {"drafts_deleted": 5, "assessments_affected": 5, "dry_run": true}
```

### Modified Endpoints

**GET /api/public/a/{token}** - Now includes `draft` field if draft exists:
```json
{
  "id": "...",
  "respondent_name": "...",
  "questions_snapshot": {...},
  "draft": {
    "answers": [...],
    "last_saved_at": "2026-01-24T10:30:00Z"
  }
}
```

**POST /api/public/a/{token}/submit** - Contact now in request body (not form):
```json
{
  "contact": {
    "last_name": "Батболд",
    "first_name": "Дорж",
    "email": "dorj@company.mn",
    "phone": "99112233",
    "position": "Менежер"
  },
  "answers": [...]
}
```

## Frontend Routes

New route structure:

```
/a/{token}           → AssessmentForm (questionnaire only)
/a/{token}/contact   → ContactPage (new separate page)
/a/{token}/results   → ResultsPage (unchanged)
```

## Testing the New Flow

### 1. Start Assessment
```bash
# Create assessment via admin API (same as before)
curl -X POST http://localhost:8000/api/admin/assessments \
  -H "X-API-Key: sk_..." \
  -d '{"respondent_id": "...", "type_ids": ["..."]}'
# Returns: {"public_url": "http://localhost:5173/a/token123"}
```

### 2. Test Draft Save/Resume
```bash
# Open assessment in browser
open http://localhost:5173/a/token123

# Answer some questions, wait 30 seconds (auto-save)
# Or click "Хадгалах" button

# Close browser, reopen same link
# Verify answers are restored
```

### 3. Test Cross-Device Resume
```bash
# Open assessment on Device A, answer questions, click Save
# Open same link on Device B
# Verify answers from Device A are shown
```

### 4. Test Submit Flow
```bash
# Complete all questions
# Click "Илгээх" (Submit)
# Verify navigation to /a/{token}/contact
# Fill contact info
# Click "Баталгаажуулах" (Confirm)
# Verify navigation to /a/{token}/results
```

### 5. Test Cancel Flow
```bash
# Complete questions, click Submit
# On contact page, click "Буцах" (Back)
# Verify return to questionnaire with answers intact
```

### 6. Test Admin Cleanup
```bash
# Create assessment, let it expire
# Save draft but don't submit
# Run cleanup (dry run first)
curl -X DELETE "http://localhost:8000/api/admin/cleanup/drafts?dry_run=true" \
  -H "X-API-Key: sk_..."

# Verify expected drafts listed
# Run actual cleanup
curl -X DELETE "http://localhost:8000/api/admin/cleanup/drafts?dry_run=false" \
  -H "X-API-Key: sk_..."
```

## UI Components

### New Components

- **SaveButton** (`frontend/src/components/SaveButton.tsx`)
  - Manual save with loading state
  - Text: "Хадгалах"

- **AutoSaveIndicator** (`frontend/src/components/AutoSaveIndicator.tsx`)
  - Shows save status: idle, saving, saved, error
  - Text: "Хадгалагдсан" (saved), "Хадгалж байна..." (saving)

- **ContactPage** (`frontend/src/pages/ContactPage.tsx`)
  - Separate page for contact form
  - Fields: Овог, Нэр, email, phone, Албан тушаал
  - Buttons: "Баталгаажуулах", "Буцах"

### Modified Components

- **AssessmentForm** (`frontend/src/pages/AssessmentForm.tsx`)
  - Remove embedded ContactForm
  - Add SaveButton and AutoSaveIndicator
  - Navigate to /contact on Submit

## Error Messages (Mongolian)

| Scenario | Message |
|----------|---------|
| Save success | "Хадгалагдсан" |
| Save in progress | "Хадгалж байна..." |
| Save failed | "Хадгалж чадсангүй" |
| Network error | "Сүлжээний алдаа" |

## Troubleshooting

### Draft not saving
- Check network tab for PUT /draft request
- Verify assessment is PENDING status (not COMPLETED/EXPIRED)
- Check backend logs for validation errors

### Draft not restoring
- Verify GET /a/{token} returns `draft` field
- Check browser console for API errors
- Ensure assessment hasn't been submitted on another device

### Contact form not appearing
- Verify all required questions are answered
- Check for validation errors on questionnaire
- Ensure Submit button click is triggering navigation
