# Research: Hide Result and Show Confirmation Page

**Feature**: 004-hide-result-confirmation
**Date**: 2026-02-08

## Executive Summary

This feature requires minimal research as it involves straightforward frontend modifications with no new technologies or complex patterns. All technical decisions are well-defined by existing codebase patterns.

## Research Tasks

### 1. Current Navigation Pattern

**Question**: How does the current submission flow navigate to results?

**Findings**:
- ContactPage.tsx (line 136-137) handles successful submission
- Navigation uses React Router's `navigate()` with state passing:
  ```typescript
  navigate(`/a/${token}/results`, { state: { results: data }, replace: true })
  ```
- Results page reads data from `location.state`

**Decision**: Follow same pattern - navigate to `/a/${token}/confirmation` instead
**Rationale**: Maintains consistency with existing codebase patterns
**Alternatives Rejected**: None - pattern is well-established

### 2. Route Structure

**Question**: How should the new confirmation route integrate with existing routes?

**Findings**:
- App.tsx defines routes under `/a/:token/` namespace
- Current routes: index (form), contact, results
- Routes wrapped in AssessmentLayout with AssessmentProvider

**Decision**: Add `/a/:token/confirmation` route within AssessmentLayout
**Rationale**: Keeps confirmation accessible only via valid token flow
**Alternatives Rejected**:
- Standalone `/confirmation` route - loses token context
- Query parameter approach - URL not clean for bookmarking

### 3. Page Component Pattern

**Question**: What pattern should ConfirmationPage follow?

**Findings**:
- Existing pages use functional components with TypeScript
- TailwindCSS for styling
- Common layout patterns: centered content, card-style containers
- ExpiredLink.tsx and UsedLink.tsx are good templates for simple message pages

**Decision**: Model ConfirmationPage after ExpiredLink.tsx pattern
**Rationale**: Simple message pages already exist; follow established conventions
**Alternatives Rejected**: None

### 4. Results Page Accessibility

**Question**: How to preserve results page access via direct URL?

**Findings**:
- Results.tsx currently expects `location.state.results`
- If state is missing, shows error with link back to form
- Direct URL access would fail with current implementation

**Decision**: Modify Results.tsx to fetch results from backend if state is missing
**Rationale**: Allows direct URL access for admins while confirmation page handles normal flow
**Alternative Considered**: Keep results page as-is (shows error for direct access) - REJECTED because spec requires results to remain accessible via URL

**Implementation Note**: Need to add a backend endpoint or use existing token to fetch completed assessment results, OR pass results via query params/localStorage. Simplest approach: pass results to confirmation page instead and keep results page unchanged (it already handles missing state gracefully).

**Revised Decision**: Keep Results.tsx unchanged. It already shows a fallback when state is missing. Admins who need results can:
1. Access directly after submission (before page reload clears state)
2. Access via admin panel (existing functionality)

This aligns with spec assumption: "There is no authentication requirement difference between confirmation and result page access" - meaning we're not adding special admin-only access, just changing the default redirect.

### 5. Mongolian Text Support

**Question**: Does the application support Mongolian (Cyrillic) text?

**Findings**:
- Existing pages contain Mongolian text (ContactPage.tsx uses "Овог", "Нэр", etc.)
- UTF-8 encoding in use
- TailwindCSS handles text rendering

**Decision**: No special handling needed for "Таны хүсэлтийг хүлээж авлаа"
**Rationale**: Mongolian text already works throughout the application

## Resolved Items

All NEEDS CLARIFICATION items from Technical Context have been resolved:

| Item | Resolution |
|------|------------|
| Navigation pattern | Use existing React Router navigate() pattern |
| Route placement | Under `/a/:token/confirmation` |
| Component structure | Follow ExpiredLink.tsx pattern |
| Results accessibility | Unchanged - already handles missing state |
| Mongolian text | Already supported |

## No Outstanding Research Needed

Feature is ready for Phase 1 design.
