# Feature Specification: Risk Assessment Survey System

**Feature Branch**: `001-risk-assessment-survey`
**Created**: 2026-01-21
**Status**: Draft
**Input**: PRD - Үнэлгээний Асуулгын Систем (Phase 1: Admin API + Public UI)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Creates Assessment Link (Priority: P1)

An internal staff member or integration system needs to generate a one-time assessment link for a respondent. They configure which questionnaire types to include, select or create the respondent, and receive a unique URL that can be shared with the respondent.

**Why this priority**: This is the foundation of the entire system. Without the ability to create assessments and generate links, no surveys can be conducted. This enables the primary business function.

**Independent Test**: Can be fully tested by calling Admin API endpoints to create types, questions, respondent, and assessment. Delivers a functional one-time link URL that can be verified for correct format and token generation.

**Acceptance Scenarios**:

1. **Given** configured questionnaire types with questions exist, **When** admin creates an assessment for a respondent with selected types, **Then** system returns a unique public URL containing an access token
2. **Given** an assessment is being created, **When** admin selects multiple questionnaire types, **Then** all questions from selected types are included in the assessment snapshot
3. **Given** an assessment creation request, **When** admin specifies an expiration date, **Then** the link becomes invalid after that date
4. **Given** questionnaire configuration changes after assessment creation, **When** respondent accesses the link, **Then** they see the original questions as snapshotted at creation time

---

### User Story 2 - Respondent Completes Assessment (Priority: P1)

A respondent (organization or individual) receives a one-time link via external communication. They open the link in a browser, see questions in Mongolian Cyrillic, answer YES/NO questions with required comments and images where applicable, and submit to receive their risk assessment results.

**Why this priority**: This is the core user-facing functionality. The public form is the only UI in Phase 1 and represents the primary value delivery to end users.

**Independent Test**: Can be fully tested by accessing a valid assessment link, completing all questions with required attachments, submitting, and verifying results are displayed correctly in Mongolian.

**Acceptance Scenarios**:

1. **Given** a valid one-time link, **When** respondent opens it, **Then** they see the assessment form with their name (if available), questions grouped by type and then by group within each type, and a progress indicator showing "X / Y асуулт"
2. **Given** a question is displayed, **When** respondent selects YES or NO, **Then** if that option requires a comment, a "Тайлбар" text field appears and becomes required
3. **Given** a question is displayed, **When** respondent selects an option that requires an image, **Then** an image upload field appears with "Зураг хавсаргах" label and becomes required
4. **Given** all required fields are completed, **When** respondent enters their contact information (Овог, Нэр, email, phone, Албан тушаал) and submits, **Then** backend calculates scores and frontend displays per-group scores, per-type scores, and overall score with risk ratings
5. **Given** a submitted assessment, **When** the same link is accessed again, **Then** system displays "Энэ линк аль хэдийн ашиглагдсан байна."

---

### User Story 3 - Admin Configures Questionnaire Types and Groups (Priority: P2)

An admin needs to create and manage questionnaire types (эрсдэлийн төрөл) that serve as top-level risk categories, and groups (бүлэг) within each type that organize related questions. Each type has thresholds for risk ratings and weight for overall calculation. Each group has a weight for type calculation.

**Why this priority**: Types and groups provide the hierarchical organizational structure for questions and enable meaningful score segmentation at multiple levels. Required before questions can be created, but less frequently performed than assessment creation.

**Independent Test**: Can be tested by creating types with groups, updating configurations, and verifying the hierarchy appears correctly in assessment configurations.

**Acceptance Scenarios**:

1. **Given** admin wants to categorize questions, **When** they create a new type with name and thresholds, **Then** the type is available for group creation
2. **Given** a type exists, **When** admin creates a group within the type with name and weight, **Then** the group is available for question assignment
3. **Given** an existing type or group, **When** admin updates its thresholds or weight, **Then** future assessments use the updated configuration
4. **Given** a type or group with existing questions, **When** admin deactivates it, **Then** it's excluded from new assessments but historical data remains intact

---

### User Story 4 - Admin Configures Questions and Options (Priority: P2)

An admin creates YES/NO questions within question groups, configuring the score for each answer and any conditional requirements (comments, images) for specific answers.

**Why this priority**: Questions are the content of assessments. Must be configured before assessments can be created, but this is setup work done once per questionnaire design.

**Independent Test**: Can be tested by creating questions within groups with various option configurations, then verifying conditional fields appear correctly in the public form.

**Acceptance Scenarios**:

1. **Given** a question group exists within a type, **When** admin creates a question with YES/NO options, **Then** each option can have a score, require_comment flag, and require_image flag
2. **Given** a question option configuration, **When** admin sets require_comment=true with comment_min_len=50, **Then** respondents must enter at least 50 characters when selecting that option
3. **Given** a question option configuration, **When** admin sets require_image=true with max_images=3 and image_max_mb=5, **Then** respondents can upload 1-3 images up to 5MB each when selecting that option

---

### User Story 5 - Admin Retrieves Assessment Results (Priority: P2)

After a respondent completes an assessment, admin retrieves the detailed results including per-type scores, overall score, and optionally a breakdown of individual answers.

**Why this priority**: Accessing results is essential for the business to act on assessment data, but it's a read operation that depends on completed assessments.

**Independent Test**: Can be tested by completing an assessment and then retrieving results via API, verifying all scores and breakdowns are correctly calculated.

**Acceptance Scenarios**:

1. **Given** a completed assessment, **When** admin fetches results, **Then** they receive per-group scores, per-type scores, percentages, and risk ratings along with submission contact information
2. **Given** a completed assessment with multiple types, **When** admin fetches results, **Then** type scores are calculated from group scores, and overall score is calculated as weighted average of type percentages
3. **Given** results request with breakdown option, **When** admin fetches results, **Then** they receive individual question responses with selected options, comments, and attachment references

---

### User Story 6 - Admin Manages Respondents (Priority: P3)

Admin creates and manages respondent records representing organizations or individuals who will take assessments.

**Why this priority**: Respondent management is a prerequisite for assessment creation but is a simple CRUD operation with lower complexity.

**Independent Test**: Can be tested by creating respondents of both types (ORG, PERSON), updating their details, and verifying they can be selected for assessments.

**Acceptance Scenarios**:

1. **Given** admin needs to assess an organization, **When** they create a respondent with kind=ORG, name, and registration number, **Then** the respondent is available for assessment selection
2. **Given** admin needs to assess an individual, **When** they create a respondent with kind=PERSON, name, and optional ID, **Then** the respondent is available for assessment selection
3. **Given** an existing respondent, **When** admin updates their information, **Then** future assessments reference the updated details

---

### Edge Cases

- What happens when a respondent partially completes the form and closes the browser?
  - Form state is not preserved; respondent must restart (one-time link, one submission design)
- How does system handle expired links?
  - Display "Линкний хугацаа дууссан байна." message
- What happens when image upload fails mid-submission?
  - Display error message, allow retry without losing other form data; submission is blocked until all required images upload successfully
- How does system handle concurrent access to the same link?
  - First successful submission wins; subsequent attempts see "already used" message
- What happens when all questions in a group have max score of 0?
  - Group percentage calculation handles division by zero gracefully (0% or N/A)
- What happens when all groups in a type have max score of 0?
  - Type percentage calculation handles division by zero gracefully (0% or N/A)
- How does system handle very long comment text?
  - Allow reasonable length (up to 2000 characters) with character counter

## Requirements *(mandatory)*

### Functional Requirements

#### Admin API Requirements

- **FR-000**: System MUST authenticate Admin API requests via X-API-Key header validated against stored API keys
- **FR-001**: System MUST allow creation of questionnaire types with name, scoring_method (SUM default), risk thresholds, and weight for overall calculation
- **FR-002**: System MUST allow updating questionnaire type configurations
- **FR-003**: System MUST allow deactivating questionnaire types while preserving historical data
- **FR-004**: System MUST allow creation of question groups within types with name, display order, and weight for type calculation
- **FR-004a**: System MUST allow creation of questions with group assignment, display order, optional weight, and critical flag
- **FR-005**: System MUST allow configuration of YES/NO options per question with: score value, require_comment flag, require_image flag
- **FR-006**: System MUST allow setting validation rules per option: comment_min_len, max_images (default 3), image_max_mb (default 5)
- **FR-007**: System MUST allow creation of respondents with kind (ORG or PERSON), name, and optional registration/ID number
- **FR-008**: System MUST allow creation of assessments by selecting respondent and questionnaire types
- **FR-009**: System MUST generate a one-time access token for each assessment and return a public URL
- **FR-010**: System MUST store token as hash only for security
- **FR-011**: System MUST snapshot all groups, questions, and option configurations at assessment creation time
- **FR-012**: System MUST allow optional expiration date on assessments (default: 30 days from creation if not specified)
- **FR-013**: System MUST provide endpoint to retrieve assessment results with per-group scores, per-type scores, and overall scores
- **FR-014**: System MUST provide optional breakdown of individual answers in results
- **FR-014b**: System MUST include submission contact information (Овог, Нэр, email, phone, Албан тушаал) in assessment results
- **FR-014a**: System MUST retain completed assessment data indefinitely (no automatic purging; manual deletion only via admin action)

#### Public UI Requirements

- **FR-015**: System MUST display assessment form when valid token is accessed via `/a/<token>`
- **FR-016**: System MUST display respondent name and one-time link context on form
- **FR-017**: System MUST display questions grouped by type and then by group within each type, with progress indicator ("X / Y асуулт")
- **FR-018**: System MUST present YES/NO options for each question in Mongolian Cyrillic ("Тийм" / "Үгүй")
- **FR-019**: System MUST dynamically show "Тайлбар" text field when selected option requires comment
- **FR-020**: System MUST dynamically show "Зураг хавсаргах" upload field when selected option requires image
- **FR-021**: System MUST validate required fields with inline Mongolian error messages only
- **FR-022**: System MUST prevent submission until all required fields are completed
- **FR-022a**: System MUST collect submission contact information before allowing submission: last name (Овог), first name (Нэр), email, phone number, and position/title (Албан тушаал)
- **FR-022b**: System MUST validate submission contact fields: email format validation, phone number format validation, all fields required
- **FR-023**: System MUST accept image uploads (image/* types only) up to configured size limit
- **FR-024**: System MUST limit images per question to configured maximum
- **FR-024a**: System MUST block form submission until all required images have successfully uploaded to storage; upload failures display retry option without losing other form data
- **FR-025**: System MUST calculate and store type scores and overall score on submission
- **FR-026**: System MUST display results screen showing per-group scores, per-type scores, and overall score with risk ratings after successful submission
- **FR-027**: System MUST mark link as used after successful submission
- **FR-028**: System MUST display "Линкний хугацаа дууссан байна." for expired links
- **FR-029**: System MUST display "Энэ линк аль хэдийн ашиглагдсан байна." for already-used links
- **FR-030**: System MUST apply rate limiting on public endpoints (30 requests per minute per IP)

#### Scoring Requirements (Backend Only - Frontend performs no calculations)

- **FR-031**: Group score raw value MUST be calculated (on backend) as sum of awarded scores from questions in that group
- **FR-032**: Group score maximum MUST be calculated (on backend) as sum of maximum possible scores per question in that group
- **FR-033**: Group score percentage MUST be calculated (on backend) as (group_raw / group_max) * 100
- **FR-034**: Type score MUST be calculated (on backend) as weighted average of group percentages: Σ(group_percent * group_weight) / Σ(group_weight)
- **FR-035**: Overall score MUST be calculated (on backend) as weighted average of type percentages: Σ(type_percent * type_weight) / Σ(type_weight)
- **FR-036**: System MUST apply default risk rating thresholds: ≥80% = "Бага эрсдэл", 50-79% = "Дунд эрсдэл", <50% = "Өндөр эрсдэл"
- **FR-037**: Overall risk rating MUST be determined by applying thresholds to overall percentage
- **FR-038**: Frontend MUST NOT perform any score calculations; all calculations are performed on backend and results are returned to frontend for display only

#### Non-Functional Requirements

- **NFR-001**: Public UI MUST be mobile-first responsive
- **NFR-002**: Public UI MUST support light and dark mode
- **NFR-003**: Public UI MUST meet WCAG AA contrast requirements
- **NFR-004**: Public UI MUST use Cyrillic-safe fonts (Inter, Roboto, or Noto Sans)
- **NFR-005**: Public UI MUST be entirely in Mongolian Cyrillic (no other languages)

### Key Entities

- **Questionnaire Type (Эрсдэлийн төрөл)**: A top-level risk category containing groups. Contains: name, risk thresholds (high/medium/low boundaries), weight for overall calculation, active status. Example: "Галын аюулгүй байдал" (Fire Safety)
- **Question Group (Бүлэг)**: A logical grouping of related questions within a type. Contains: name, type reference, display order, weight for type calculation, active status. Example: "Галын хор" (Fire hazards) within Fire Safety type
- **Question**: A single YES/NO question within a group. Contains: text, display order, group reference, optional weight, critical flag
- **Option Configuration**: Settings for YES or NO answer to a question. Contains: score value, require_comment, require_image, comment_min_len, max_images, image_max_mb
- **Respondent**: An entity being assessed. Contains: kind (ORG/PERSON), name, registration number (org) or ID (person)
- **Submission Contact (Хариулагч)**: The person who fills out the assessment form. Contains: last name (Овог), first name (Нэр), email, phone number, position/title (Албан тушаал). Captured at submission time, linked to assessment
- **Assessment**: A specific assessment instance for a respondent. Contains: respondent reference, selected types, token hash, expiration date, status (pending/completed/expired), created timestamp, snapshot of questions/options/groups, submission contact reference
- **Answer**: A respondent's answer to a question. Contains: assessment reference, question reference, selected option (YES/NO), comment text, attachment references, score awarded
- **Attachment**: An uploaded image. Contains: file reference (storage key), question/answer reference, original filename, size, mime type

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators can create a complete assessment (types, questions, respondent, link) within 5 minutes using API tools
- **SC-002**: Respondents can complete a 20-question assessment in under 10 minutes on mobile devices
- **SC-003**: Public form loads and becomes interactive within 2 seconds under normal network conditions
- **SC-004**: Assessment submission and score calculation completes within 1 second
- **SC-005**: 100% of conditional field requirements (comment/image) are correctly enforced before submission
- **SC-006**: 100% of expired and used links display appropriate Mongolian error messages
- **SC-007**: Risk ratings are correctly calculated for all submitted assessments with no calculation errors
- **SC-008**: Public UI is fully usable on devices with screen width from 320px to 1920px
- **SC-009**: All UI text displays correctly in Mongolian Cyrillic with proper rendering
- **SC-010**: Image uploads are restricted to allowed types and sizes with no security bypasses

## Clarifications

### Session 2026-01-21

- Q: What authentication mechanism should the Admin API expect? → A: API key in header (X-API-Key) validated against stored keys
- Q: What rate limit should apply to public endpoints? → A: 30 requests per minute per IP
- Q: What is the default expiration for assessment links when not explicitly set? → A: 30 days
- Q: How long should completed assessment data be retained? → A: Indefinite (never auto-delete, manual purge only)
- Q: How should the system handle image storage failures during upload? → A: Block submission until required images upload successfully

### Session 2026-01-23

- Q: Should scoring hierarchy change from Type→Questions to Type→Group→Questions? → A: Yes, add Question Group (Бүлэг) as intermediate level between Type and Questions
- Q: Where should score calculations be performed? → A: All calculations on backend only; frontend displays results without computing
- Q: What submission contact information should be collected? → A: Овог (last name), Нэр (first name), email, phone, Албан тушаал (position/title)

## Assumptions

- Admin API authentication uses X-API-Key header; key management/provisioning is handled externally
- Assessment links are distributed to respondents through external channels (email, SMS, etc.) - delivery mechanism not in scope
- Default risk thresholds (80%/50%) are acceptable for MVP; custom thresholds per type are supported but optional
- Single language (Mongolian Cyrillic) is sufficient for Phase 1 - multi-language is explicitly out of scope
- Browser-based form state is not persisted - respondents understand they must complete in one session
- Object storage (S3/MinIO/Azure Blob) configuration is available for image attachments
- PostgreSQL database is available and configured
