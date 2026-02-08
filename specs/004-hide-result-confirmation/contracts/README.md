# API Contracts: Hide Result and Show Confirmation Page

**Feature**: 004-hide-result-confirmation
**Date**: 2026-02-08

## Overview

This feature requires **no API contract changes**.

All modifications are frontend-only:
- New route: `/a/:token/confirmation`
- Modified navigation: ContactPage redirects to confirmation instead of results
- New component: ConfirmationPage

## Backend APIs (Unchanged)

### POST /a/{token}/submit
- Request: Same as before (contact + answers)
- Response: Same as before (SubmitResponse with full results)
- The backend continues to return results; frontend chooses not to display them

### GET /a/{token}/results
- Not an existing endpoint
- Results are passed via React Router state, not fetched separately
- This behavior remains unchanged

## Frontend Routes

### Existing Routes (Preserved)
| Route | Component | Purpose |
|-------|-----------|---------|
| `/a/:token` | AssessmentForm | Survey questions |
| `/a/:token/contact` | ContactPage | Respondent info |
| `/a/:token/results` | Results | Score display (admin access) |

### New Route
| Route | Component | Purpose |
|-------|-----------|---------|
| `/a/:token/confirmation` | ConfirmationPage | Submission acknowledgment |

## Navigation Flow Change

### Before
```
ContactPage submit success → navigate('/a/:token/results', { state: { results } })
```

### After
```
ContactPage submit success → navigate('/a/:token/confirmation', { replace: true })
```

Note: Results data is no longer passed to navigation state since confirmation page doesn't need it.
