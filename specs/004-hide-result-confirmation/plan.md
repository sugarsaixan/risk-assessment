# Implementation Plan: Hide Result and Show Confirmation Page

**Branch**: `004-hide-result-confirmation` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-hide-result-confirmation/spec.md`

## Summary

Hide risk assessment results from users after survey submission by redirecting them to a new confirmation page displaying "Таны хүсэлтийг хүлээж авлаа" instead of showing scores. The original result page remains accessible via direct URL for administrative use.

**Technical approach**: Create a new ConfirmationPage component, modify the submission flow in ContactPage to navigate to the confirmation route instead of results, and add a new route while preserving the existing results route.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router v6, TailwindCSS (frontend)
**Storage**: PostgreSQL (primary), S3-compatible object storage (images)
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Web application (browser)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Confirmation page loads within 2 seconds of submission
**Constraints**: Must preserve existing result page accessibility via direct URL
**Scale/Scope**: Existing user base, minimal new infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution file contains placeholder content only. No specific gates or constraints are defined. Proceeding with standard best practices.

**Pre-Phase 0 Status**: PASS (no defined gates)
**Post-Phase 1 Status**: PASS (design follows existing patterns, no new complexity)

## Project Structure

### Documentation (this feature)

```text
specs/004-hide-result-confirmation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── public/
│   │       └── assessment.py    # No changes needed - backend unaffected
│   ├── services/
│   │   └── submission.py        # No changes needed - still returns results
│   └── ...
└── tests/

frontend/
├── src/
│   ├── pages/
│   │   ├── AssessmentForm.tsx   # Existing - no changes
│   │   ├── ContactPage.tsx      # MODIFY - change navigation target
│   │   ├── Results.tsx          # PRESERVE - keep accessible via URL
│   │   └── ConfirmationPage.tsx # NEW - confirmation message display
│   ├── components/
│   ├── contexts/
│   └── App.tsx                  # MODIFY - add new route
└── tests/
```

**Structure Decision**: Web application structure. Changes isolated to frontend only - backend continues to return results data (for administrative URL access) but frontend redirects regular users to confirmation page.

## Complexity Tracking

No constitution violations. Feature is minimal scope:
- 1 new component (ConfirmationPage)
- 2 file modifications (ContactPage navigation, App.tsx routing)
- No new dependencies
- No data model changes
- No backend changes
