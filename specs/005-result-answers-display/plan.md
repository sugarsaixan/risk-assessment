# Implementation Plan: Result Page User Answers Display

**Branch**: `005-result-answers-display` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-result-answers-display/spec.md`

## Summary

Add a collapsible "Хариултууд" (Answers) section to the Results page that displays all submitted question answers with their selected options, comments, and attachment counts. The section starts collapsed by default and can be expanded to show answers grouped by questionnaire type.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend - minor change)
**Primary Dependencies**: React 18, React Router, TailwindCSS (frontend); FastAPI (backend)
**Storage**: N/A (uses existing data)
**Testing**: Manual testing (per existing pattern)
**Target Platform**: Web browser
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Answers display within 2 seconds of page load (SC-005)
**Constraints**: Collapse/expand in under 1 second (SC-002)
**Scale/Scope**: Up to 50+ questions per assessment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ No new dependencies required
- ✅ No new database tables or migrations
- ✅ Uses existing API patterns (extends public results endpoint)
- ✅ Frontend-only collapsible component follows TypeScoreCard pattern
- ✅ Minimal backend change: add `breakdown=true` parameter to existing endpoint

## Project Structure

### Documentation (this feature)

```text
specs/005-result-answers-display/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   └── api/
│       └── public/
│           └── assessment.py    # Modify: add breakdown parameter to /results

frontend/
├── src/
│   ├── components/
│   │   └── AnswersSection.tsx   # NEW: Collapsible answers display
│   ├── constants/
│   │   └── mn.ts                # Modify: add answer display translations
│   ├── pages/
│   │   └── Results.tsx          # Modify: integrate AnswersSection
│   ├── services/
│   │   └── assessment.ts        # Modify: add breakdown parameter
│   └── types/
│       └── api.ts               # Modify: add AnswerBreakdown interface
```

**Structure Decision**: Web application with minimal backend modification. The backend already supports `answer_breakdown` data - we just need to expose it via the public endpoint.

## Complexity Tracking

No constitution violations - this is a straightforward feature addition using existing patterns.

## Implementation Overview

### Phase 0: Research (Complete)
- Backend already returns `answer_breakdown` via ResultsService with `include_breakdown=True`
- TypeScoreCard provides collapsible UI pattern to follow
- MN constants structure established for Mongolian translations

### Phase 1: Design
1. Add `AnswerBreakdown` TypeScript interface matching backend schema
2. Extend public `/a/{token}/results` endpoint to accept `?breakdown=true`
3. Design `AnswersSection` component with collapse/expand state
4. Group answers by type for organized display

### Phase 2: Implementation (via /speckit.tasks)
- Backend: One-line change to pass `breakdown=True` to ResultsService
- Frontend: New AnswersSection component + Results.tsx integration
- Translations: Add Mongolian strings for answers section
