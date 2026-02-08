# Feature Specification: Hide Result and Show Confirmation Page

**Feature Branch**: `004-hide-result-confirmation`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Hide risk assessment results from users, keep current result page accessible via URL, show new confirmation page with 'Таны хүсэлтийг хүлээж авлаа' message"

## Clarifications

### Session 2026-02-08

- Q: Should the confirmation page include additional elements beyond the message (navigation buttons, reference numbers, follow-up timeline)? → A: Message only, no additional navigation elements

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Survey Completion Confirmation (Priority: P1)

After completing the risk assessment survey, users see a confirmation page with the message "Таны хүсэлтийг хүлээж авлаа" (Your request has been received) instead of seeing their assessment results.

**Why this priority**: This is the core requirement - hiding the actual results from regular users while providing acknowledgment that their submission was received.

**Independent Test**: Can be fully tested by completing a survey and verifying the confirmation message appears instead of risk assessment scores/results.

**Acceptance Scenarios**:

1. **Given** a user completes all survey questions, **When** they submit the survey, **Then** they see a confirmation page displaying "Таны хүсэлтийг хүлээж авлаа"
2. **Given** a user is on the confirmation page, **When** they look at the page, **Then** they do not see any risk assessment scores, categories, or detailed results
3. **Given** a user completes the survey, **When** the confirmation page loads, **Then** the page displays within 2 seconds

---

### User Story 2 - Direct URL Access to Results (Priority: P2)

Administrators or authorized users can access the actual risk assessment results by navigating directly to the original result page URL.

**Why this priority**: Preserves existing functionality for internal users who need to review actual assessment data.

**Independent Test**: Can be tested by directly accessing the result page URL with a valid assessment ID and verifying full results are displayed.

**Acceptance Scenarios**:

1. **Given** a completed risk assessment exists, **When** a user navigates directly to the result page URL, **Then** the full risk assessment results are displayed
2. **Given** an assessment ID, **When** the result URL is constructed and accessed, **Then** all original result page functionality works as before

---

### User Story 3 - Survey Flow Redirection (Priority: P1)

The survey completion flow redirects users to the new confirmation page instead of the original results page.

**Why this priority**: Critical for ensuring users see the confirmation message as the default post-survey experience.

**Independent Test**: Can be tested by following the complete survey flow and verifying the final destination is the confirmation page.

**Acceptance Scenarios**:

1. **Given** the survey submission is successful, **When** the system processes the redirect, **Then** the user lands on the confirmation page (not the results page)
2. **Given** the survey submission fails, **When** an error occurs, **Then** the user sees an appropriate error message (confirmation page is not shown)

---

### Edge Cases

- What happens when a user bookmarks the confirmation page and revisits it later? The confirmation page should display a generic acknowledgment message without assessment-specific data
- How does the system handle attempts to navigate back to results from the confirmation page? Standard browser navigation is allowed; results page remains accessible via direct URL only
- What happens if the confirmation page URL is accessed without completing a survey? The page should display the confirmation message or redirect to the survey start

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST redirect users to the confirmation page after successful survey submission
- **FR-002**: System MUST display "Таны хүсэлтийг хүлээж авлаа" as the primary message on the confirmation page
- **FR-003**: System MUST NOT display any risk assessment scores, categories, or detailed results on the confirmation page
- **FR-004**: System MUST preserve the original result page functionality when accessed via direct URL
- **FR-005**: System MUST NOT include links to the result page from the confirmation page
- **FR-006**: Confirmation page MUST be visually consistent with the existing application design
- **FR-008**: Confirmation page MUST display only the acknowledgment message without additional navigation buttons, reference numbers, or follow-up information
- **FR-007**: System MUST still process and store assessment results as before (only the display is hidden from users)

### Key Entities

- **Assessment Result**: Existing entity containing the risk assessment scores and data - remains unchanged, only display access is modified
- **Confirmation Page**: New view/page that displays acknowledgment message without result data
- **Result Page**: Existing page displaying full assessment results - preserved and accessible via direct URL

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of survey completions redirect to confirmation page instead of results page
- **SC-002**: Confirmation page loads within 2 seconds of survey submission
- **SC-003**: 100% of direct URL accesses to result pages continue to function correctly
- **SC-004**: No risk assessment data is visible to users on the confirmation page
- **SC-005**: Users can read and understand the confirmation message (Mongolian language support verified)

## Assumptions

- The existing result page URL structure is known and stable
- Mongolian character encoding (UTF-8) is already supported by the application
- There is no authentication requirement difference between confirmation and result page access
- The confirmation page does not need to display any assessment-specific information (e.g., submission timestamp, reference number)
- Browser history manipulation to prevent back-navigation to results is not required
