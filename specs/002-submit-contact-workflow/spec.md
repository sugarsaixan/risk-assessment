# Feature Specification: Submit-Then-Contact Workflow

**Feature Branch**: `002-submit-contact-workflow`
**Created**: 2026-01-24
**Status**: Draft
**Input**: User description: "I want to change workflow, i want users first fill questionnaire, then fill personal information, after submit button ask for fill personal info"
**Depends On**: 001-risk-assessment-survey (modifies existing behavior)

## Summary

Change the assessment submission workflow so respondents complete the entire questionnaire first, then are prompted for their personal contact information only when they click the Submit button. This separates question-answering from contact collection, reducing perceived friction during form completion.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Respondent Completes Questionnaire Before Contact Info (Priority: P1)

A respondent accesses their assessment link, sees and answers all YES/NO questions with any required comments and images, then clicks Submit. At that point (and only then), a contact information form appears asking for their details before final submission.

**Why this priority**: This is the core workflow change requested. It directly impacts the user experience for every respondent completing an assessment.

**Independent Test**: Can be fully tested by accessing a valid assessment link, completing all questions, clicking Submit, verifying the contact form appears, filling contact details, and verifying final submission completes successfully with results displayed.

**Acceptance Scenarios**:

1. **Given** a valid assessment link, **When** respondent opens the form, **Then** they see only the questionnaire questions without any contact information fields visible
2. **Given** respondent has answered all questions (including required comments/images), **When** they click the Submit button, **Then** the system navigates to a separate contact information page requesting their details
3. **Given** the contact form is displayed after clicking Submit, **When** respondent fills all required fields (Овог, Нэр, email, phone, Албан тушаал), **Then** they can click a "Баталгаажуулах" (Confirm) button to complete submission
4. **Given** the contact form is displayed, **When** respondent leaves any required field empty or invalid, **Then** they see inline Mongolian error messages and cannot proceed
5. **Given** respondent completes contact form and confirms, **When** submission succeeds, **Then** they see the results screen with scores and risk ratings

---

### User Story 2 - Respondent Cancels Contact Entry (Priority: P2)

A respondent completes the questionnaire and clicks Submit, but decides they need to review their answers before providing contact information. They can close/cancel the contact form and return to review their questionnaire answers.

**Why this priority**: Provides a necessary escape path if respondent realizes they need to change an answer before final submission, improving user experience.

**Independent Test**: Can be tested by completing questions, clicking Submit, then clicking Back on the contact page and verifying all questionnaire answers are preserved.

**Acceptance Scenarios**:

1. **Given** the contact form page is displayed after clicking Submit, **When** respondent clicks the back button ("Буцах"), **Then** they return to the questionnaire form with all their answers preserved
2. **Given** respondent returns to questionnaire after canceling contact form, **When** they modify any answer and click Submit again, **Then** the contact form appears again (empty or with previously entered data)

---

### User Story 3 - Respondent Saves Progress and Resumes Later (Priority: P1)

A respondent begins the questionnaire but needs to physically move to a different location to assess that area. They save their progress, close the browser, and later return (possibly on a different device) to continue and complete the assessment.

**Why this priority**: Essential for real-world risk assessment scenarios where respondents must physically inspect multiple locations. Without this, users would lose all progress when changing locations.

**Independent Test**: Can be tested by partially completing questions, clicking Save, closing browser, reopening the link on a different device, and verifying all previously saved answers are restored.

**Acceptance Scenarios**:

1. **Given** a respondent has answered some questions, **When** they click the "Хадгалах" (Save) button, **Then** their progress is saved to the server and they see a confirmation message
2. **Given** a respondent has saved progress and closed the browser, **When** they re-access the same assessment link, **Then** all their previously saved answers are automatically restored
3. **Given** a respondent accesses their link from a different device, **When** they have previously saved progress, **Then** they see their saved answers and can continue from where they left off
4. **Given** a respondent with saved progress, **When** they continue answering and save again, **Then** the new progress overwrites the previous draft

---

### Edge Cases

- What happens if respondent refreshes the page while on the contact form page?
  - Page reloads to contact form page; any entered contact data may be lost but questionnaire answers are preserved (saved as draft)
- What happens if respondent's session times out while filling contact form?
  - Same behavior as main form timeout - they must restart
- What if a partially filled contact form is abandoned and the user closes browser?
  - No submission occurs; link remains valid and unused
- How does the Submit button behave if required questions aren't answered?
  - Submit button shows validation errors for incomplete questions (existing behavior); contact form only appears when all questions are validly completed
- What happens if network fails during auto-save?
  - System retries silently; if persistent failure, shows warning "Хадгалж чадсангүй" (Could not save) with retry option; does not block form usage
- What happens if respondent opens the same link on two devices simultaneously?
  - Last-write-wins; most recent save overwrites previous; no real-time sync between devices
- What happens to draft data when assessment link expires?
  - Draft data remains in storage but is inaccessible; admin can manually delete or extend link expiration
- What happens to uploaded images for incomplete assessments?
  - Images remain in storage until admin triggers cleanup; no automatic deletion

## Requirements *(mandatory)*

### Functional Requirements

#### Workflow Changes

- **FR-WF-001**: System MUST NOT display contact information fields in the initial questionnaire form view
- **FR-WF-002**: System MUST present the Submit button ("Илгээх") at the bottom of the questionnaire after all questions
- **FR-WF-003**: System MUST validate all questionnaire answers (required comments, required images) when Submit is clicked, before showing contact form
- **FR-WF-004**: System MUST navigate to a separate contact information page (not a modal) after Submit button is clicked and questionnaire validation passes
- **FR-WF-005**: System MUST collect the same contact fields as before: Овог (last name), Нэр (first name), email, phone, Албан тушаал (position/title)
- **FR-WF-006**: System MUST validate contact fields with existing validation rules: email format, phone format, all fields required
- **FR-WF-007**: System MUST provide a "Баталгаажуулах" (Confirm) button in the contact form to trigger final submission
- **FR-WF-008**: System MUST provide a cancel/back option in the contact form to return to questionnaire review
- **FR-WF-009**: System MUST preserve all questionnaire answers when respondent returns from contact form to questionnaire
- **FR-WF-010**: System MUST perform final submission (save answers, calculate scores) only after contact form is completed and confirmed

#### Save and Resume Requirements

- **FR-SR-001**: System MUST store draft questionnaire progress on the server, linked to the assessment token
- **FR-SR-002**: System MUST allow respondent to save progress and continue later from any device using the same assessment link
- **FR-SR-003**: System MUST automatically restore saved draft when respondent re-accesses the assessment link
- **FR-SR-004**: System MUST provide a visible "Хадгалах" (Save) button for manual save
- **FR-SR-005**: System MUST display confirmation when draft is successfully saved
- **FR-SR-006**: System MUST overwrite previous draft when new progress is saved (single draft per assessment)
- **FR-SR-007**: System MUST auto-save draft progress every 30 seconds while respondent is active on the form
- **FR-SR-008**: System MUST auto-save draft immediately when respondent changes an answer (debounced to avoid excessive saves)
- **FR-SR-009**: System MUST display a subtle "Хадгалагдсан" (Saved) indicator when auto-save completes successfully
- **FR-SR-010**: System MUST handle offline/network failure gracefully during auto-save, retrying when connection restores
- **FR-SR-011**: System MUST NOT auto-delete draft data; drafts persist until assessment is submitted or manually deleted by admin
- **FR-SR-012**: System MUST prevent access to drafts when the assessment link has expired (link expiration controls access, not draft deletion)
- **FR-SR-013**: System MUST upload images immediately to permanent storage when respondent attaches them (not deferred to final submit)
- **FR-SR-014**: System MUST store image references in draft data so uploaded images are visible when resuming
- **FR-SR-015**: System MUST display previously uploaded images when respondent resumes a saved draft
- **FR-SR-016**: System MUST retain uploaded images for incomplete/expired assessments until admin triggers cleanup
- **FR-SR-017**: System MUST provide admin capability to cleanup orphaned drafts and images for expired assessments

#### UI Text Requirements (Mongolian)

- **FR-UI-001**: Submit button text MUST be "Илгээх" (Send/Submit)
- **FR-UI-002**: Contact form title MUST be "Хариулагчийн мэдээлэл" (Respondent Information)
- **FR-UI-003**: Confirm button text MUST be "Баталгаажуулах" (Confirm)
- **FR-UI-004**: Cancel/back button text MUST be "Буцах" (Back)
- **FR-UI-005**: Save button text MUST be "Хадгалах" (Save)
- **FR-UI-006**: Auto-save confirmation indicator MUST show "Хадгалагдсан" (Saved)

### Key Entities

- **Assessment Draft**: Server-side storage of partial questionnaire progress. Contains: assessment reference, answers in progress, last saved timestamp. Linked to assessment token for retrieval.
- **Assessment**: Modified to support draft state; submission flow timing changes
- **Submission Contact**: No schema changes; collected at a different point in the user flow

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Contact information fields are not visible until Submit button is clicked on the questionnaire
- **SC-002**: 100% of questionnaire validation errors are caught before contact form is displayed
- **SC-003**: Respondents can cancel contact entry and return to questionnaire with all answers preserved
- **SC-004**: Final submission only occurs after both questionnaire completion and contact form confirmation
- **SC-005**: Total assessment completion time remains comparable (within 10% variance) to previous workflow
- **SC-006**: Saved drafts are restored with 100% accuracy when respondent resumes (all answers, comments, and image references intact)
- **SC-007**: Auto-save completes within 2 seconds under normal network conditions
- **SC-008**: Respondents can resume saved progress from any device using the same assessment link

## Assumptions

- The contact information form is displayed as a separate page, not a modal (full page navigation from questionnaire to contact form)
- The existing contact validation logic (email format, phone format) can be reused in the new location
- Backend API changes ARE required to support draft save/load endpoints (updates previous assumption)
- Assessment token is sufficient authentication for saving/loading drafts (no additional auth required)

## Clarifications

### Session 2026-01-24

- Q: Where should draft/partial questionnaire progress be stored? → A: Server-side draft storage (can resume from any device with same link)
- Q: Should the system auto-save progress or only save on manual action? → A: Auto-save (every 30 seconds or on answer change) plus manual save button
- Q: When should saved draft data be deleted? → A: Never auto-expire; draft persists until assessment submitted or admin deletes; link expiration controls access
- Q: What happens to uploaded images when saving draft progress? → A: Images uploaded immediately to permanent storage; draft stores references to uploaded images
- Q: What happens to images uploaded for assessments that are never completed? → A: Admin-triggered cleanup; images remain until admin manually cleans up expired assessments
- Q: Should the contact form be displayed as a modal overlay or separate page? → A: Separate page (not a modal)
