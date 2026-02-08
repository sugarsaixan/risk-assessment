# Data Model: Test Assessment SMS Distribution Tool

**Feature**: 004-test-assessment-sms
**Date**: 2026-02-04
**Phase**: 1 - Design & Contracts

## Overview

This document describes the data structures used in the test assessment SMS distribution tool. Since this is a standalone utility script that integrates with external APIs, the data model focuses on input validation, API request/response structures, and reporting.

## Internal Data Structures

### 1. Configuration

**Description**: Configuration loaded from config.yml and environment variables

**Fields**:
- `assessment_api_base_url`: str - Assessment API base URL
- `assessment_api_key`: str - API key for assessment service
- `assessment_session_id`: str - Session ID for assessment API
- `sms_api_base_url`: str - SMS API base URL
- `sms_api_key`: str - API key for SMS service
- `default_respondent_id`: str - UUID of default respondent
- `default_type_ids`: list[str] - List of assessment type UUIDs
- `default_expires_in_days`: int - Default expiration (default: 30)
- `message_template`: str - SMS message template with {url} placeholder
- `max_concurrent`: int - Max concurrent API requests (default: 10)
- `retry_attempts`: int - Number of retry attempts (default: 2)
- `retry_delay_seconds`: int - Delay between retries (default: 5)

**Validation**:
- All URLs must be valid HTTPS endpoints
- All UUIDs must be valid UUID format
- All numeric values must be positive integers
- Message template must contain {url} placeholder

### 2. Phone Number Input

**Description**: Phone number read from input file

**Fields**:
- `raw`: str - Raw phone number from file
- `normalized`: str - Normalized phone number (digits only, no spaces)
- `country_code`: str (optional) - Country code (e.g., "+976" for Mongolia)
- `is_valid`: bool - Whether the phone number passes validation

**Normalization Rules**:
- Strip all non-numeric characters
- Remove leading country code for Mongolian numbers
- Validate length (8 digits for Mongolian mobile)
- Validate prefix (must start with 8 or 9 for Mongolian mobile)

**Example Transformations**:
```
"89113840" → "89113840" (valid)
"+976 8911-3840" → "89113840" (valid)
"8911 38 40" → "89113840" (valid)
"123456" → None (invalid - too short)
```

### 3. Assessment Creation Request

**Description**: Request payload for assessment creation API

**Fields**:
- `respondent_id`: str (UUID) - ID of respondent taking the assessment
- `selected_type_ids`: list[str] (UUIDs) - Assessment types to include
- `expires_in_days`: int - Days until link expires

**Validation**:
- `respondent_id` must be valid UUID
- `selected_type_ids` must be non-empty array of valid UUIDs
- `expires_in_days` must be positive integer (1-365)

### 4. Assessment Creation Response

**Description**: Response from assessment creation API

**Fields**:
- `id`: str (UUID) - Unique assessment ID
- `url`: str - Full URL to assessment
- `expires_at`: str (ISO 8601 datetime) - Expiration timestamp

**Validation**:
- `id` must be valid UUID
- `url` must be valid HTTPS URL
- `expires_at` must be valid ISO 8601 datetime in future

### 5. SMS Send Request

**Description**: Request payload for SMS API

**Fields**:
- `to`: str - Phone number to send SMS to
- `message`: str - SMS message text with assessment URL

**Validation**:
- `to` must be valid phone number (8 digits for Mongolian)
- `message` must be non-empty string
- `message` length should be < 160 characters (SMS limit)

### 6. SMS Send Response

**Description**: Response from SMS API

**Fields**:
- `message`: str - Optional message from API
- `status`: str - Status message (e.g., "SMS sent successfully")

**Validation**:
- Success indicated by status containing "success" (case-insensitive)

### 7. Processing Result

**Description**: Result of processing a single phone number

**Fields**:
- `phone_number`: str - Original phone number from input
- `status`: enum - SUCCESS, FAILED_VALIDATION, FAILED_ASSESSMENT, FAILED_SMS
- `assessment_id`: str (optional) - Created assessment ID if successful
- `assessment_url`: str (optional) - Assessment URL if successful
- `error_message`: str (optional) - Error details if failed
- `retry_count`: int - Number of retry attempts made

**Status Flow**:
```
VALIDATION → ASSESSMENT_CREATION → SMS_SEND → SUCCESS
     ↓              ↓                   ↓
   FAILED_*      FAILED_*          FAILED_*
```

### 8. Processing Summary

**Description**: Aggregate summary of all processing results

**Fields**:
- `total_count`: int - Total phone numbers processed
- `success_count`: int - Successfully sent SMS
- `failure_count`: int - Failed to process
- `validation_error_count`: int - Failed validation
- `assessment_error_count`: int - Failed assessment creation
- `sms_error_count`: int - Failed SMS send
- `results`: list[ProcessingResult] - Individual results
- `start_time`: datetime - Processing start timestamp
- `end_time`: datetime - Processing end timestamp
- `duration_seconds`: float - Total processing time

**Derived Metrics**:
- `success_rate`: float - success_count / total_count
- `average_time_per_number`: float - duration_seconds / total_count

### 9. Error Detail

**Description**: Detailed error information for reporting

**Fields**:
- `phone_number`: str - Phone number that failed
- `stage`: enum - VALIDATION, ASSESSMENT, SMS
- `error_type`: enum - VALIDATION_ERROR, API_ERROR, NETWORK_ERROR, RATE_LIMIT
- `error_message`: str - Human-readable error description
- `retry_attempt`: int - Which retry attempt this was
- `timestamp`: datetime - When the error occurred

**Error Types**:
- `VALIDATION_ERROR`: Invalid phone number format
- `API_ERROR`: HTTP 4xx error (client error, don't retry)
- `NETWORK_ERROR`: Connection error, timeout
- `RATE_LIMIT`: HTTP 429 (too many requests, retry with backoff)

### 10. Report Output Formats

#### Console Report
Human-readable text output with tables and summaries

#### JSON Report
Machine-readable JSON with all processing details

**Schema**:
```json
{
  "summary": {
    "total_count": 10,
    "success_count": 8,
    "failure_count": 2,
    "duration_seconds": 45.2
  },
  "results": [
    {
      "phone_number": "89113840",
      "status": "SUCCESS",
      "assessment_id": "uuid",
      "assessment_url": "https://..."
    },
    {
      "phone_number": "89113899",
      "status": "FAILED_VALIDATION",
      "error_message": "Invalid phone number format"
    }
  ]
}
```

#### CSV Report
Spreadsheet-compatible format with columns:
- phone_number
- status
- assessment_id
- assessment_url
- error_message
- timestamp

## State Transitions

### Phone Number Processing State Machine

```
[INPUT] → [VALIDATING] → [VALID] → [CREATING_ASSESSMENT] → [ASSESSMENT_CREATED] → [SENDING_SMS] → [SUCCESS]
            ↓                                  ↓                         ↓
         [INVALID]                         [FAILED]                  [FAILED]
         (skip)                           (retry)                   (retry)
```

### Retry Logic

```
[ATTEMPT 1] → [FAILURE] → [WAIT 5s] → [ATTEMPT 2] → [FAILURE] → [WAIT 5s] → [ATTEMPT 3] → [FAILURE] → [SKIP]
               ↓                                              ↓
           [SUCCESS]                                       [SUCCESS]
```

## Data Flow

```
[Input File]
     ↓
[Parse Phone Numbers]
     ↓
[Validate Each Number] → [Invalid Numbers] → [Log & Skip]
     ↓
[Valid Numbers]
     ↓
[Create Assessment (API)] → [Failed] → [Retry] → [Failed] → [Log Error & Skip]
     ↓
[Assessment Created]
     ↓
[Send SMS (API)] → [Failed] → [Retry] → [Failed] → [Log Error & Skip]
     ↓
[SMS Sent]
     ↓
[Collect Result]
     ↓
[Generate Summary Report]
```

## Storage Requirements

**No persistent storage required** - this is a stateless utility script. All data is held in memory during execution and written to reports/output files.

## Validation Summary

| Data Structure | Validation Rules |
|----------------|------------------|
| Phone Number | 8 digits, starts with 8/9, optional +976 country code |
| UUID | Must match RFC 4122 format |
| URL | Must be valid HTTPS URL |
| Datetime | Must be ISO 8601 format |
| Positive Integer | Must be > 0 |
| Message Template | Must contain {url} placeholder |
| SMS Message | Must be < 160 characters |

## Security Considerations

1. **API Keys**: Loaded from environment, not stored in data structures
2. **Phone Numbers**: Treated as PII, not logged in verbose mode
3. **Session IDs**: Loaded from environment, not stored in results
4. **Error Messages**: Sanitized to avoid exposing sensitive data

## Testing Data

**Test Phone Numbers**:
- Valid: "89113840", "89113841", "89113842"
- Invalid: "12345", "891138401" (too long), "abcdefgh"

**Mock API Responses**: See contracts/ directory for full API contracts
