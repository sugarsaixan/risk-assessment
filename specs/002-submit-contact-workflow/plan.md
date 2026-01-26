# Implementation Plan: Submit-Then-Contact Workflow

**Branch**: `002-submit-contact-workflow` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-submit-contact-workflow/spec.md`
**Depends On**: 001-risk-assessment-survey (extends existing implementation)

## Summary

Modify the assessment submission workflow to:
1. **Separate questionnaire from contact collection**: Users complete all questions first, then see a separate contact form page after clicking Submit
2. **Add server-side draft storage**: Enable save/resume functionality so users can complete assessments across multiple sessions and devices
3. **Auto-save with manual option**: Automatically save progress every 30 seconds and on answer changes, plus a manual Save button

This is a modification to the existing 001-risk-assessment-survey feature, not a standalone implementation.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend) - inherited from 001
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic (backend); React 18, React Router, TailwindCSS (frontend) - inherited from 001
**Storage**: PostgreSQL (primary), S3-compatible object storage (images) - inherited from 001
**Testing**: pytest (backend), Vitest + Testing Library (frontend) - inherited from 001
**Target Platform**: Linux server (backend), Modern browsers (frontend) - inherited from 001
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Auto-save <2s, draft restore <1s, same page load targets as 001
**Constraints**: Mobile-first responsive, WCAG AA compliance, Mongolian Cyrillic only - inherited from 001
**Scale/Scope**: Same as 001 - hundreds of assessments, tens of concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: Constitution not configured (template only) - proceeding without gate enforcement.

## Project Structure

### Documentation (this feature)

```text
specs/002-submit-contact-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (changes to 001 data model)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (new/modified API endpoints)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code Changes (to existing 001 structure)

```text
backend/
├── src/
│   ├── api/
│   │   ├── admin/
│   │   │   └── cleanup.py          # NEW: Admin cleanup endpoint for orphaned drafts
│   │   └── public/
│   │       └── assessment.py       # MODIFIED: Add draft save/load endpoints
│   ├── models/
│   │   └── assessment_draft.py     # NEW: Draft storage model
│   ├── schemas/
│   │   └── draft.py                # NEW: Draft request/response schemas
│   ├── services/
│   │   └── draft.py                # NEW: Draft save/load/cleanup logic
│   └── repositories/
│       └── draft.py                # NEW: Draft database operations
└── alembic/
    └── versions/
        └── xxx_add_assessment_drafts.py  # NEW: Migration for drafts table

frontend/
├── src/
│   ├── pages/
│   │   ├── AssessmentForm.tsx      # MODIFIED: Remove ContactForm, add Save button
│   │   └── ContactPage.tsx         # NEW: Separate contact form page
│   ├── components/
│   │   ├── SaveButton.tsx          # NEW: Manual save button with status
│   │   └── AutoSaveIndicator.tsx   # NEW: Auto-save status indicator
│   ├── hooks/
│   │   ├── useAssessment.ts        # MODIFIED: Add draft save/load logic
│   │   └── useAutoSave.ts          # NEW: Auto-save hook with debouncing
│   ├── services/
│   │   └── draft.ts                # NEW: Draft API service
│   └── App.tsx                     # MODIFIED: Add ContactPage route
```

**Structure Decision**: Extends existing 001-risk-assessment-survey structure. Changes are additive (new files) and modificative (updates to existing files). No structural reorganization needed.

## Complexity Tracking

> No constitution violations to justify - constitution not configured.
