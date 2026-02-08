# Quickstart: Hide Result and Show Confirmation Page

**Feature**: 004-hide-result-confirmation
**Date**: 2026-02-08

## Prerequisites

- Node.js (for frontend development)
- Access to the frontend codebase at `frontend/`

## Files to Modify

### 1. Create ConfirmationPage Component

**File**: `frontend/src/pages/ConfirmationPage.tsx`

```typescript
// New file - confirmation page with simple message
// Pattern: Follow ExpiredLink.tsx structure
// Content: Display "Таны хүсэлтийг хүлээж авлаа" centered on page
// Styling: Match existing application design using TailwindCSS
```

### 2. Update App.tsx Routes

**File**: `frontend/src/App.tsx`

```typescript
// Add new route under AssessmentLayout:
// Path: /a/:token/confirmation
// Component: ConfirmationPage
// Position: After /contact route, before /results route
```

### 3. Update ContactPage Navigation

**File**: `frontend/src/pages/ContactPage.tsx`

```typescript
// Change line ~136-137 from:
//   navigate(`/a/${token}/results`, { state: { results: data }, replace: true })
// To:
//   navigate(`/a/${token}/confirmation`, { replace: true })
```

## Development Workflow

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev

# Run tests
npm test
```

## Testing the Feature

### Manual Testing Steps

1. **Complete Survey Flow**
   - Access a survey via `/a/{valid-token}`
   - Answer all questions
   - Submit and proceed to contact page
   - Fill contact information and submit
   - **Expected**: See confirmation page with "Таны хүсэлтийг хүлээж авлаа"

2. **Direct Results URL Access**
   - After completing a survey, manually navigate to `/a/{token}/results`
   - **Expected**: Results page still accessible (may show fallback if no state)

3. **Confirmation Page Direct Access**
   - Navigate directly to `/a/{token}/confirmation`
   - **Expected**: Confirmation message displayed

### Acceptance Criteria Verification

| Criterion | Test |
|-----------|------|
| SC-001: Survey redirects to confirmation | Complete survey, verify landing page |
| SC-002: Page loads in <2 seconds | Time from submit to confirmation display |
| SC-003: Results URL still works | Direct navigation to results route |
| SC-004: No results on confirmation | Visual inspection of confirmation page |
| SC-005: Mongolian text displays | Verify "Таны хүсэлтийг хүлээж авлаа" renders correctly |

## Rollback

If issues arise:
1. Revert ContactPage.tsx navigation target to `/results`
2. Route and ConfirmationPage can remain (unused)
3. No backend changes to revert
