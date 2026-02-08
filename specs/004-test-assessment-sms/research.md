# Research: Test Assessment SMS Distribution Tool

**Feature**: 004-test-assessment-sms
**Date**: 2026-02-04
**Phase**: 0 - Outline & Research

## Overview

This document captures technical research and decisions for implementing a Python CLI tool that creates risk assessments and sends SMS invitations to test users.

## Key Technical Decisions

### 1. Script Architecture

**Decision**: Standalone async Python script with configuration file

**Rationale**:
- Simple, focused utility that doesn't require integration into the main FastAPI application
- Async support allows concurrent API calls for better performance
- Configuration file keeps API keys out of the script and allows flexibility
- Can be run directly: `python backend/scripts/test_assessment_sms.py`

**Alternatives Considered**:
- *Integrate into existing CLI* (backend/src/cli.py): Rejected because this is a testing utility, not a core system feature
- *Separate package/tool*: Rejected as overkill for a simple script
- *Sync implementation*: Rejected because async provides better performance for multiple API calls

### 2. HTTP Client Library

**Decision**: Use `httpx` for HTTP requests

**Rationale**:
- Async support matches existing backend patterns
- Modern, well-maintained library
- HTTP/2 support, connection pooling, timeouts
- Compatible with existing testing infrastructure

**Alternatives Considered**:
- *requests*: Rejected because it's synchronous only
- *aiohttp*: Rejected because httpx has a cleaner API and better type hints
- *urllib*: Rejected because it's too low-level and verbose

**Implementation Note**: httpx may already be available as a dependency (check in pyproject.toml), otherwise add to dev dependencies.

### 3. Phone Number Input Format

**Decision**: Plain text file with one phone number per line

**Rationale**:
- Simplest format for users to create and edit
- Easy to generate from spreadsheets, databases, or other sources
- Supports comments (lines starting with #)
- Can handle blank lines gracefully

**Format Specification**:
```
# Test users for pilot program
89113840
89113841
89113842

# Another group
89113843
```

**Alternatives Considered**:
- *CSV file*: Rejected as overly complex for a single column
- *JSON/YAML*: Rejected as less user-friendly for non-technical users
- *Command-line arguments*: Rejected because it doesn't scale well for many phone numbers

### 4. Configuration Management

**Decision**: YAML configuration file (config.yml) with environment variable overrides

**Rationale**:
- YAML is human-readable and easy to edit
- Environment variables allow CI/CD integration
- Separates configuration from code
- Template file can be provided (config_template.yml)

**Configuration Structure**:
```yaml
# Assessment API Configuration
assessment_api:
  base_url: "https://aisys.agula.mn"
  api_key: "${ASSESSMENT_API_KEY}"
  session_id: "${ASSESSMENT_SESSION_ID}"
  respondent_id: "default-respondent-uuid"
  selected_type_ids:
    - "type-uuid-1"
    - "type-uuid-2"
  expires_in_days: 30

# SMS API Configuration
sms_api:
  base_url: "https://sms.agula.mn"
  api_key: "${SMS_API_KEY}"

# Message Template
message_template: "Sain baina uu. Ersdeliiin unelgeenii asuulga bogloh holboos: {url}"

# Processing Options
processing:
  max_concurrent: 10
  retry_attempts: 2
  retry_delay_seconds: 5
```

**Alternatives Considered**:
- *Environment variables only*: Rejected because it's harder to manage complex nested configuration
- *JSON config*: Rejected because JSON doesn't support comments
- *Command-line arguments*: Rejected because there are too many options

### 5. Phone Number Validation

**Decision**: Basic validation using phonenumbers library (if available) or simple regex

**Rationale**:
- Mongolia-specific phone numbers (8 digits, starts with 8x or 9x)
- Validate before making API calls to fail fast
- Allow international format with country code

**Validation Rules**:
- Must be 8 digits (for Mongolian numbers: 89113840)
- Optionally can start with +976 country code
- Strip spaces, dashes, and parentheses
- Display clear error messages for invalid numbers

**Alternatives Considered**:
- *No validation*: Rejected because it wastes API calls and creates confusing errors
- *Full phonenumbers library*: Optional if the project wants comprehensive validation
- *API-side validation only*: Rejected because we want to fail fast

### 6. Error Handling Strategy

**Decision**: Continue-on-error with detailed reporting

**Rationale**:
- One bad phone number shouldn't stop the entire batch
- Collect all errors and report at the end
- Retry transient failures (network issues, rate limits)
- Exit with non-zero code if any failures occurred

**Error Categories**:
1. **Validation errors**: Skip immediately, don't retry
2. **API errors (4xx)**: Skip immediately, log error
3. **API errors (5xx)**: Retry with exponential backoff
4. **Network errors**: Retry with exponential backoff

**Report Format**:
```
Processing Summary
==================
Total phone numbers: 10
Successfully processed: 8
Failed: 2

Success Details:
- 89113840: Assessment created, SMS sent
- 89113841: Assessment created, SMS sent
...

Failure Details:
- 89113899: Invalid phone number format
- 89113898: SMS API error: Insufficient credits
```

**Alternatives Considered**:
- *Fail-fast*: Rejected because one error shouldn't block all users
- *Interactive prompting*: Rejected because script should be non-interactive
- *Silent failures*: Rejected because users need to know what happened

### 7. SMS Message Template

**Decision**: Static Mongolian template with URL placeholder

**Template**: `"Sain baina uu. Ersdeliiin unelgeenii asuulga bogloh holboos: {url}"`

**Rationale**:
- Matches the example provided by the user
- Clear and concise
- Includes the assessment URL
- Mongolian language for local users

**Future Enhancement**: Could support template variables (name, custom message, etc.)

### 8. Assessment API Parameters

**Decision**: Use configurable defaults with command-line overrides

**Required Parameters**:
- `respondent_id`: UUID (can be a default test respondent)
- `selected_type_ids`: Array of UUIDs (assessment types to include)
- `expires_in_days`: Integer (default 30)

**Rationale**:
- Most test assessments use the same configuration
- Allows flexibility via command-line flags or config file
- Can be overridden per batch if needed

**Implementation**: Store in config.yml, allow --respondent-id and --type-ids flags

### 9. Reporting Format

**Decision**: Multi-format output (console + optional JSON/CSV file)

**Console Output**: Human-readable summary with tables
**JSON Output**: Machine-readable for automation/CI/CD
**CSV Output**: Spreadsheet-compatible for business users

**Flags**:
- `--output-format`: (json|csv|console) - default: console
- `--output-file`: path to output file (optional)
- `--verbose`: Show detailed per-number results

**Rationale**:
- Different users have different needs
- JSON enables automation
- CSV enables business reporting
- Console is best for ad-hoc testing

### 10. Rate Limiting

**Decision**: Implement configurable concurrency limits

**Default**: 10 concurrent requests
**Configurable**: Via `processing.max_concurrent` in config.yml

**Rationale**:
- Prevent overwhelming the SMS API
- Balances speed with API limits
- Semaphore-based limiting with asyncio

**Implementation**:
```python
async def process_with_semaphore(semaphore, phone_number):
    async with semaphore:
        # Process one phone number
```

**Alternatives Considered**:
- *No limiting*: Rejected because it could trigger API rate limits
- *Fixed delay*: Rejected because it's slower than necessary
- *Token bucket*: Rejected as overkill for this use case

## Dependencies

### New Dependencies Required
- `httpx`: Async HTTP client (may already be in dependencies)
- `pyyaml`: YAML configuration parsing (may already be in dependencies)
- `phonenumbers` (optional): Phone number validation

### Existing Dependencies to Use
- `pydantic`: Data validation and settings
- `pytest`: Testing framework

## Security Considerations

1. **API Keys**: Never commit to repository, use environment variables
2. **Session IDs**: Treat as sensitive, store in environment
3. **Phone Numbers**: PII - handle carefully, don't log in production
4. **Configuration**: Add config_template.yml to git, ignore actual config.yml
5. **Error Messages**: Don't expose API keys in error output

## Performance Targets

- Single phone number: < 5 seconds
- 10 phone numbers: < 30 seconds
- 50 phone numbers: < 2 minutes
- 1000 phone numbers: < 30 minutes

Based on spec requirements (SC-001: < 30s for single, SC-003: < 2 min for 50).

## Testing Strategy

1. **Unit Tests**: Mock API responses, test validation logic
2. **Integration Tests**: Use test API endpoints if available
3. **Contract Tests**: Verify request/response formats match APIs
4. **End-to-End Tests**: Run script with small batch of real phone numbers

## Open Questions

None - all technical decisions have been made.

## Next Steps

1. Create API contracts in OpenAPI format (contracts/)
2. Define data models (data-model.md)
3. Create quickstart guide (quickstart.md)
4. Proceed to task generation (/speckit.tasks)
