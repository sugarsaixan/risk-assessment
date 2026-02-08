# Implementation Plan: Test Assessment SMS Distribution Tool

**Branch**: `004-test-assessment-sms` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-test-assessment-sms/spec.md`

## Summary

Create a Python CLI script that reads phone numbers from a file, creates risk assessments via the existing assessment API, sends SMS invitations with unique links via the SMS API, and generates a summary report of processing results. The tool will integrate with existing backend services and follow established patterns.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing backend)
**Primary Dependencies**:
- `httpx` - Async HTTP client for API calls
- `pydantic` - Data validation (already in project)
- Existing backend services and models

**Storage**: N/A (standalone script, no database changes)
**Testing**: `pytest` (matches existing backend test setup)
**Target Platform**: Linux/macOS CLI (standalone script)
**Project Type**: Single (utility script in backend/)
**Performance Goals**: Process 50 phone numbers in under 2 minutes
**Constraints**:
- Must handle SMS API rate limits gracefully
- Must continue processing on individual failures
- Must validate phone numbers before API calls
**Scale/Scope**: Support 1-1000 phone numbers per run

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASSED - No constitution file defined, following existing project patterns

**Compliance**:
- Following existing CLI patterns in `backend/src/cli.py`
- Using existing async patterns and dependencies
- No new frameworks or architectural changes
- Simple, focused utility script

## Project Structure

### Documentation (this feature)

```text
specs/004-test-assessment-sms/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── assessment-api.yaml
│   └── sms-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── scripts/
│   ├── __init__.py
│   ├── test_assessment_sms.py  # New standalone script
│   └── config_template.yml      # Configuration template
├── tests/
│   ├── test_scripts/
│   │   ├── __init__.py
│   │   ├── test_test_assessment_sms.py
│   │   └── fixtures/
│   │       └── phone_numbers.txt
└── pyproject.toml  # Update with httpx dependency if needed
```

**Structure Decision**: Creating a new `backend/scripts/` directory for utility scripts. This follows Python project conventions and keeps utility scripts separate from the main API code while maintaining discoverability. The script will be standalone (not part of the installed package) and invoked directly via Python.

## API Contracts

### External APIs to Integrate

#### 1. Assessment Creation API
- **Endpoint**: `https://aisys.agula.mn/assessment/api/admin/assessments`
- **Method**: POST
- **Headers**:
  - `X-API-Key`: {ASSESSMENT_API_KEY}
  - `Content-Type`: application/json
  - `Cookie`: session_id={SESSION_ID}
- **Request Body**:
  ```json
  {
    "respondent_id": "uuid",
    "selected_type_ids": ["uuid", "uuid"],
    "expires_in_days": 30
  }
  ```
- **Response**:
  ```json
  {
    "id": "uuid",
    "url": "https://aisys.agula.mn/assessment/a/...",
    "expires_at": "2026-03-06T04:26:22Z"
  }
  ```

#### 2. SMS API
- **Endpoint**: `https://sms.agula.mn/api/v1/sms`
- **Method**: POST
- **Headers**:
  - `x-api-key`: {SMS_API_KEY}
  - `Content-Type`: application/json
- **Request Body**:
  ```json
  {
    "to": "89113840",
    "message": "Sain baina uu. Ersdeliiin unelgeenii asuulga bogloh holboos: {url}"
  }
  ```
- **Response**:
  ```json
  {
    "message": "",
    "status": "SMS sent successfully"
  }
  ```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations | N/A |
