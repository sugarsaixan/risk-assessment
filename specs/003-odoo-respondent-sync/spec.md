# Feature Specification: Odoo ERP Respondent Integration

**Feature Branch**: `003-odoo-respondent-sync`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "I want to implement admin in Odoo ERP, so I don't want to create Respondents separate from our Odoo. Odoo will pass respondent id, name, kind, registration_no."
**Depends On**: 001-risk-assessment-survey (replaces local respondent management with Odoo-sourced respondents)

## Summary

Replace local respondent CRUD management (previously User Story 6 / P3 in 001-risk-assessment-survey) with Odoo ERP as the single source of truth for respondent data. Instead of admins creating respondents directly in the risk assessment system, Odoo passes respondent information (id, name, kind, registration_no) when creating assessments. The admin interface for the risk assessment system moves entirely into Odoo, eliminating the need for a standalone admin panel for respondent management.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Odoo Creates Assessment with Respondent Data (Priority: P1)

An Odoo admin user initiates a risk assessment from within the Odoo ERP interface. Odoo sends the respondent's information (id, name, kind, registration_no) and optionally the employee's information (employee_id, employee_name) along with the assessment creation request to the risk assessment system. The system either creates a new respondent record or matches an existing one using the Odoo-provided ID, stores the employee data on the assessment for audit purposes, then proceeds to create the assessment and return the one-time link.

**Why this priority**: This is the core integration point. Without accepting respondent data from Odoo, the entire feature has no value. This replaces the previous standalone respondent creation workflow.

**Independent Test**: Can be fully tested by sending an assessment creation request with respondent data (odoo_id, name, kind, registration_no) and optional employee data (employee_id, employee_name) to the Admin API and verifying that a respondent record is created/matched, employee data is stored on the assessment, and an assessment link is returned.

**Acceptance Scenarios**:

1. **Given** a respondent does not yet exist in the risk assessment system, **When** Odoo sends an assessment creation request with respondent id, name, kind=ORG, and registration_no, **Then** the system creates a new respondent record with the Odoo-provided data and creates the assessment linked to that respondent
2. **Given** a respondent with the same Odoo ID already exists, **When** Odoo sends an assessment creation request for that respondent, **Then** the system uses the existing respondent record and creates a new assessment linked to it
3. **Given** a respondent exists but Odoo sends updated name or registration_no, **When** the assessment creation request is processed, **Then** the system updates the respondent's information to match the latest Odoo data
4. **Given** a valid assessment creation request from Odoo, **When** the request is processed successfully, **Then** the system returns a unique one-time assessment link URL

---

### User Story 2 - Odoo Manages Full Assessment Lifecycle (Priority: P1)

An Odoo admin manages the complete assessment lifecycle from within Odoo: selecting questionnaire types, setting expiration, creating the assessment link, and later retrieving results. All admin operations that were previously done via direct API calls are now initiated from Odoo.

**Why this priority**: Centralizing admin operations in Odoo eliminates the need for a separate admin tool and ensures consistent data management across the organization's systems.

**Independent Test**: Can be tested by performing the full workflow from Odoo: creating an assessment with respondent data, retrieving the generated link, having a respondent complete it, and fetching results back into Odoo.

**Acceptance Scenarios**:

1. **Given** Odoo sends an assessment creation request with selected questionnaire type IDs and respondent data, **When** the request is processed, **Then** the system creates the assessment with the specified types and returns the link
2. **Given** a completed assessment exists, **When** Odoo requests the assessment results using the assessment ID, **Then** the system returns full results including scores, risk ratings, and respondent information
3. **Given** Odoo needs to view all assessments for a specific respondent, **When** Odoo queries by respondent Odoo ID, **Then** the system returns all assessments (pending, completed, expired) for that respondent, each including employee_id and employee_name if present
4. **Given** Odoo needs to view assessments created by a specific employee, **When** Odoo queries by employee_id, **Then** the system returns all assessments created by that employee

---

### User Story 3 - Respondent Data Consistency Between Odoo and Risk Assessment System (Priority: P2)

Over time, respondent information may change in Odoo (e.g., organization name changes, registration number updates). The system keeps respondent data current by accepting updates from Odoo whenever an assessment request is made, ensuring the risk assessment system always reflects the latest Odoo data.

**Why this priority**: Data consistency is important but secondary to the core integration. The update-on-access pattern ensures data stays current without requiring a separate sync mechanism.

**Independent Test**: Can be tested by creating a respondent through an assessment request, then sending a new request for the same respondent with changed name/registration_no, and verifying the respondent record is updated.

**Acceptance Scenarios**:

1. **Given** a respondent exists with name "Company A", **When** Odoo sends an assessment request with the same Odoo ID but name "Company B", **Then** the respondent's name is updated to "Company B" in the risk assessment system
2. **Given** a respondent's data is updated via a new assessment request, **When** viewing historical assessments for that respondent, **Then** the respondent's current name is shown but assessment snapshots retain the data as it was at assessment creation time

---

### Edge Cases

- What happens when Odoo sends a respondent with kind=PERSON but no registration_no?
  - System accepts the request; registration_no is optional for PERSON respondents
- What happens if Odoo sends an assessment request with an invalid or non-existent questionnaire type ID?
  - System returns a validation error listing the invalid type IDs; no respondent or assessment is created
- What happens if Odoo sends duplicate requests (e.g., network retry) for the same assessment?
  - Each request creates a new assessment; Odoo is responsible for idempotency at its layer if needed
- What happens when Odoo sends a respondent with kind not matching ORG or PERSON?
  - System returns a validation error with accepted kind values
- How does the system handle concurrent assessment creation requests for the same respondent?
  - System handles concurrent requests safely; respondent record is created or matched atomically to prevent duplicates
- What happens to existing respondents that were created before the Odoo integration?
  - Existing respondents without an Odoo ID continue to function; they can be linked to an Odoo ID when Odoo sends a matching respondent (matched by registration_no and kind, or manually linked by admin)

## Requirements *(mandatory)*

### Functional Requirements

#### Respondent Integration

- **FR-001**: System MUST accept respondent data (odoo_id, name, kind, registration_no) as part of the assessment creation request
- **FR-002**: System MUST use the Odoo-provided ID as the primary identifier for matching existing respondents
- **FR-003**: System MUST create a new respondent record when no existing respondent matches the provided Odoo ID
- **FR-004**: System MUST update respondent name and registration_no when a request provides newer data for an existing Odoo ID
- **FR-005**: System MUST validate that kind is one of the accepted values (ORG, PERSON)
- **FR-006**: System MUST require registration_no for respondents with kind=ORG
- **FR-007**: System MUST treat registration_no as optional for respondents with kind=PERSON

#### Assessment Creation via Odoo

- **FR-008**: System MUST accept assessment creation requests that include both respondent data, optional employee data (employee_id, employee_name), and assessment configuration (questionnaire type IDs, expiration date) in a single request
- **FR-008a**: System MUST store employee_id and employee_name on the assessment record when provided
- **FR-008b**: System MUST treat employee_id and employee_name as optional fields (assessments can be created without employee data)
- **FR-009**: System MUST validate all questionnaire type IDs exist and are active before creating the assessment
- **FR-010**: System MUST return the assessment ID and one-time link URL in the response to Odoo
- **FR-011**: System MUST continue to support the existing Admin API authentication (X-API-Key header)

#### Query and Results

- **FR-012**: System MUST allow querying assessments by respondent Odoo ID
- **FR-012a**: System MUST allow filtering assessments by employee_id query parameter
- **FR-013**: System MUST return assessment status (pending, completed, expired) when listing assessments for a respondent
- **FR-013a**: System MUST include employee_id and employee_name in assessment detail and list responses when the data is present
- **FR-014**: System MUST continue to provide full assessment results (scores, risk ratings, answers) through existing results endpoints

#### Deprecation

- **FR-015**: System MUST remove standalone respondent creation and update endpoints; respondents are only created or updated through Odoo-initiated assessment requests
- **FR-016**: System MUST continue to support respondents created before Odoo integration (respondents without an Odoo ID remain valid for their existing assessments)
- **FR-017**: System MUST allow linking a pre-existing respondent to an Odoo ID if Odoo sends a matching respondent (same kind and registration_no)

### Key Entities

- **Respondent (Modified)**: Extended with an Odoo-sourced identifier. Contains: odoo_id (unique string, from Odoo — supports both integer IDs and XML/external IDs), kind (ORG/PERSON), name, registration_no (required for ORG, optional for PERSON). Odoo ID becomes the primary lookup key for respondent matching.
- **Assessment (Modified)**: Extended with optional Odoo employee fields. Contains (new): employee_id (optional string, the Odoo employee who created this assessment), employee_name (optional string, display name of the employee). Creation workflow now accepts inline respondent data and optional employee data from Odoo instead of requiring a pre-existing respondent ID.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Odoo can create an assessment with respondent data in a single request and receive the assessment link within 2 seconds
- **SC-002**: 100% of respondent records created via Odoo have a valid Odoo ID stored for future matching
- **SC-003**: Respondent data updates from Odoo are reflected immediately in the system upon the next assessment creation request
- **SC-004**: All existing respondents and assessments created before the integration continue to function without modification
- **SC-005**: Administrators can query all assessments for a given respondent using the Odoo ID
- **SC-006**: No duplicate respondent records are created when Odoo sends multiple requests with the same Odoo ID

## Clarifications

### Session 2026-01-28

- Q: Should the standalone respondent CRUD endpoints be removed or kept alongside the new Odoo-integrated flow? → A: Remove standalone create/update endpoints; respondents only come from Odoo. Read-only access is not preserved separately.
- Q: What is the data type of the Odoo respondent ID? → A: String (allows flexibility for external IDs or XML IDs from Odoo)
- Q: Should Odoo also manage questionnaire configuration (types, groups, questions), or does that remain as standalone Admin API? → A: Questionnaire CRUD stays as-is via existing standalone Admin API; only respondent management moves to Odoo
- Q: Should Odoo employee data (employee_id, employee_name) be stored on the Assessment or the Respondent? → A: Store on Assessment — each assessment records which employee created it (audit trail per action)
- Q: Should employee_id data type be string or integer? → A: String (consistent with respondent odoo_id, supports external/XML IDs)
- Q: Should admin API support filtering assessments by employee_id? → A: Yes, add employee_id as a query parameter for filtering alongside existing filters (respondent, status, odoo_id)

## Assumptions

- Odoo is the authoritative source for respondent data; the risk assessment system does not create or modify respondent data independently after this integration
- The Odoo-provided respondent ID is globally unique and stable (does not change for the same respondent)
- Odoo is responsible for ensuring the correctness of respondent data it sends
- The existing Admin API authentication mechanism (X-API-Key) is sufficient for Odoo-to-system communication
- Questionnaire type and question management (CRUD) explicitly remains accessible via the existing standalone Admin API; this is confirmed out of scope for Odoo integration
- Odoo handles its own UI for admin operations; the risk assessment system provides only the API layer
- The update-on-access pattern (updating respondent data when a new assessment is created) is acceptable; a real-time bidirectional sync is not required
