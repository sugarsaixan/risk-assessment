# Feature Specification: Result Page User Answers Display

**Feature Branch**: `005-result-answers-display`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Add Result page (/a/:token/results) user answers; Keep current content just add closeable User answers"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Individual Answers on Results Page (Priority: P1)

After completing a risk assessment, administrators or users viewing the results page can see all individual question answers in addition to the score summaries. The answers section is collapsible to allow focus on either the summary or the details.

**Why this priority**: This is the core feature - providing detailed answer visibility alongside existing score displays.

**Independent Test**: Can be fully tested by navigating to a completed assessment's results page and verifying the answers section appears with all submitted answers.

**Acceptance Scenarios**:

1. **Given** a user is on the results page for a completed assessment, **When** they view the page, **Then** they see an "Answers" section in addition to the existing score summaries
2. **Given** a user is viewing the results page, **When** they look at the answers section, **Then** they see each question with its submitted answer (YES/NO), any comments, and attachment indicators
3. **Given** the answers section is visible, **When** the user looks at a question answer, **Then** they see the question text, selected option, and any associated comment

---

### User Story 2 - Collapse/Expand Answers Section (Priority: P1)

Users can collapse or expand the answers section to focus on the summary scores or drill into the details as needed.

**Why this priority**: Essential for usability - prevents information overload by allowing users to show/hide detailed answers.

**Independent Test**: Can be tested by clicking the collapse/expand control and verifying the section toggles visibility.

**Acceptance Scenarios**:

1. **Given** the answers section is expanded, **When** the user clicks the collapse control, **Then** the answers section collapses and only the section header remains visible
2. **Given** the answers section is collapsed, **When** the user clicks the expand control, **Then** the full answers section becomes visible
3. **Given** the answers section has a collapse state, **When** the page first loads, **Then** the section starts in collapsed state by default

---

### Edge Cases

- What happens when an answer has no comment? The answer displays without the comment field (clean layout)
- What happens when an answer has attachments? An indicator shows the number of attachments but attachments are not displayed inline (summary only)
- How does the system handle many answers (25+ questions)? The section scrolls within its container or uses pagination/grouping by type

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Results page MUST display a new "Хариултууд" (Answers) section below the existing score content
- **FR-002**: Answers section MUST display each question with its question text, selected answer (YES/NO), and any submitted comment
- **FR-003**: Answers section MUST be collapsible/expandable via a clickable header or toggle control
- **FR-004**: Answers section MUST start in collapsed state when the page loads
- **FR-005**: Each answer MUST show an indicator if attachments were submitted (attachment count)
- **FR-006**: Existing Results page content (scores, risk ratings, summary) MUST remain unchanged and fully functional
- **FR-007**: Answers MUST be grouped or organized by question type/group for readability
- **FR-008**: The collapsed/expanded state indicator MUST be clear (icon or text showing current state)

### Key Entities

- **Answer Display**: Shows question text, selected option (YES/NO), comment (if any), attachment count (if any)
- **Answers Section**: Collapsible container holding all answer displays, grouped by type/group

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of submitted answers are visible in the answers section when expanded
- **SC-002**: Users can collapse/expand the section in under 1 second (instant feedback)
- **SC-003**: The toggle action correctly shows/hides all answers without page reload
- **SC-004**: All existing results page functionality continues to work as before
- **SC-005**: Answers display within 2 seconds of page load (even with 50+ questions)

## Assumptions

- The results data already includes answer breakdown (verified: backend returns `answer_breakdown` in the results response)
- Comments may be empty - display should handle null/empty gracefully
- Attachments are indicated by count only, not displayed inline on the results page
- The collapsible behavior uses standard UI patterns (accordion-style)
- Default collapsed state reduces initial cognitive load for users
