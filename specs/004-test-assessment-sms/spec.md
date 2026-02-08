# Feature Specification: Test Assessment SMS Distribution Tool

**Feature Branch**: `004-test-assessment-sms`
**Created**: 2026-02-04
**Status**: Draft
**Input**: User description: "I want to create simple python file for create test risk assessment and send unique links to test users via sms, i will provide you a curl commands of sms and creating assessment, and demo responses"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single Test User Invitation (Priority: P1)

A tester needs to quickly create a test risk assessment and send an SMS invitation with a unique link to a single test user to verify the assessment flow works correctly.

**Why this priority**: This is the core functionality - the ability to send individual test invitations is the minimum viable feature that delivers immediate value for testing and validation.

**Independent Test**: Can be tested by running the tool with one phone number, receiving the SMS, and confirming the link opens a valid assessment page.

**Acceptance Scenarios**:

1. **Given** a tester provides a valid phone number, **When** they execute the script, **Then** the system creates a new risk assessment and sends an SMS with a unique link to that phone number
2. **Given** a tester provides an invalid phone number, **When** they execute the script, **Then** the system displays a clear error message and does not create an assessment or send an SMS

---

### User Story 2 - Bulk Test User Invitations (Priority: P2)

A tester needs to create multiple test risk assessments and send SMS invitations to a list of test users at once (e.g., for batch testing or pilot groups).

**Why this priority**: Batch processing improves efficiency when testing with multiple users, but individual testing (P1) must work first.

**Independent Test**: Can be tested by providing a list of phone numbers, running the script, and verifying all recipients receive unique SMS links.

**Acceptance Scenarios**:

1. **Given** a tester provides a list of valid phone numbers, **When** they execute the script, **Then** the system creates unique assessments for each number and sends individual SMS messages with unique links
2. **Given** a list where some phone numbers are invalid, **When** the script executes, **Then** the system processes valid numbers, reports which numbers failed, and continues with remaining numbers

---

### User Story 3 - Verification and Reporting (Priority: P3)

A tester needs to confirm which assessments were created and which SMS messages were successfully sent, with a summary report of any failures.

**Why this priority**: Visibility into what succeeded and failed is important for debugging, but the core functionality (sending SMS) must work first.

**Independent Test**: Can be tested by running the script and checking the console output for success/failure counts and any error details.

**Acceptance Scenarios**:

1. **Given** the script completes execution, **When** assessments are created and SMS sent, **Then** the tester sees a summary showing total attempts, successful sends, and any failures with reasons
2. **Given** an SMS delivery fails, **When** the error occurs, **Then** the script displays the phone number and specific error reason without stopping the entire process

---

### Edge Cases

- What happens when the SMS service is unavailable or times out?
- How does the system handle duplicate phone numbers in the input list?
- What happens if the assessment creation API returns an error?
- How does the system handle international phone number formats?
- What happens when SMS credits are exhausted or API rate limits are reached?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept one or more phone numbers as input
- **FR-002**: System MUST create a unique risk assessment for each phone number
- **FR-003**: System MUST generate a unique, shareable link for each created assessment
- **FR-004**: System MUST send an SMS message containing the unique link to each provided phone number
- **FR-005**: System MUST display clear success or failure messages for each phone number processed
- **FR-006**: System MUST handle errors gracefully without crashing on partial failures
- **FR-007**: System MUST validate phone numbers before attempting to create assessments or send SMS
- **FR-008**: System MUST provide a summary report of total assessments created and SMS messages sent

### Key Entities

- **Test Assessment**: A risk assessment created for testing purposes, containing a unique identifier and access link
- **SMS Invitation**: A text message containing the assessment link, sent to a specific phone number
- **Test User**: An individual identified by phone number who receives an invitation to complete a test assessment
- **Processing Result**: The outcome of attempting to create an assessment and send an SMS (success/failure with details)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Testers can create and send a single test assessment invitation in under 30 seconds
- **SC-002**: 100% of valid phone numbers receive a unique, working assessment link
- **SC-003**: The script successfully processes 50 test users in under 2 minutes
- **SC-004**: Error messages clearly identify which phone numbers failed and why
- **SC-005**: The tool can be run by non-technical users without requiring programming knowledge

## Assumptions

- The user will provide working curl command examples for both the SMS API and assessment creation API
- The user will provide example API responses for both services
- SMS API credentials and assessment API credentials are already configured and accessible
- Phone numbers will be provided in a standard format (e.g., CSV, command-line arguments, or input file)
- The assessment generation API returns a URL or identifier that can be used to construct the unique link
- SMS messages have a standard template (e.g., "Complete your assessment: [link]")
- The script will be run in an environment with network access to both APIs
- Existing risk assessment system already has the capability to create assessments via API

## Dependencies

- Working API credentials for the risk assessment creation service
- Working API credentials for the SMS sending service
- Network connectivity to both API endpoints
- Input data source for test user phone numbers
