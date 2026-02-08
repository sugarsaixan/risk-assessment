# Data Model: Hide Result and Show Confirmation Page

**Feature**: 004-hide-result-confirmation
**Date**: 2026-02-08

## Overview

This feature requires **no data model changes**. The modification is purely presentational - changing where users are redirected after survey submission.

## Existing Entities (Unchanged)

### Assessment
- No changes to assessment state management
- Submission still processes normally and stores results

### SubmitResponse
- Backend continues to return full results data
- Frontend chooses to display confirmation instead of results

### Assessment Result Scores
- All scoring calculations remain unchanged
- Results are still computed and stored
- Only the display behavior changes

## New Entities

**None required.**

The confirmation page is a static view component with no data persistence needs.

## State Transitions

### Before Change
```
Survey Submission → Backend Processing → Results Display
```

### After Change
```
Survey Submission → Backend Processing → Confirmation Display
                                       ↳ Results (via direct URL only)
```

## Frontend State

### ConfirmationPage
- Stateless component
- No data fetching required
- Static message display: "Таны хүсэлтийг хүлээж авлаа"

### Results Page
- Behavior unchanged
- Still reads from `location.state` if available
- Still shows fallback if state missing
