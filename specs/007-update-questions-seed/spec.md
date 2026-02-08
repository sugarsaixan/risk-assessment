# Feature Specification: Update Questions Seed with Custom Scoring Format

**Feature Branch**: `007-update-questions-seed`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User wants to update the questions seed format to support custom scoring per question option, with inverse scoring logic (if Үгүй/No has score 1, then Тийм/Yes has score 0)

## Clarifications

### Session 2026-02-08

- Q: Should the seed script set `require_comment=False` and `require_image=False` for all Үгүй and Тийм options globally, or preserve conditional requirements? → A: Apply globally to all questions (both Үгүй and Тийм options have no comment or image requirements)
- Q: What default values should be used for `comment_min_len`, `max_images`, and `image_max_mb` when comments and images are disabled? → A: Use minimal safe defaults: `comment_min_len=0`, `max_images=0`, `image_max_mb=1` (accurately reflects disabled functionality while satisfying database constraints)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Updates Question Format in Markdown Files (Priority: P1)

A developer needs to update question markdown files in the `questions/` folder to use a new format that specifies the option text (Үгүй/Тийм) and score for each option after each question. The format should support custom scoring per question rather than the hardcoded YES=1, NO=0 pattern.

**Why this priority**: This is the foundation of the feature. Without the ability to define custom scores in the markdown files, the seeding system cannot be updated to support variable scoring.

**Independent Test**: Can be tested by creating sample markdown files with the new format and running the seed script to verify questions are created with the correct scores.

**Acceptance Scenarios**:

1. **Given** a markdown file with questions in the new format, **When** the seed script parses a question line, **Then** it correctly extracts the question text, option text (Үгүй or Тийм), and score value
2. **Given** a question line with "Үгүй" (No) option with score 1, **When** the seed script processes the next line, **Then** it automatically sets the "Тийм" (Yes) option score to 0
3. **Given** a question line with "Тийм" (Yes) option with score 1, **When** the seed script processes the next line, **Then** it automatically sets the "Үгүй" (No) option score to 0
4. **Given** a markdown file with multiple groups under a type, **When** the seed script parses the file, **Then** it creates the correct hierarchy: type → groups → questions with custom scores
5. **Given** a malformed question line (missing option text or score), **When** the seed script encounters it, **Then** it logs an error and skips that question or uses a default value

---

### User Story 2 - Developer Runs Seed Script to Import Questions (Priority: P1)

After updating markdown files with the new format, a developer runs `python -m src.seeds.questions_seed` to import all questions into the database. The script must parse the new format and create Question records with QuestionOption records that have the correct scores.

**Why this priority**: This is the primary user action. The seed script is the mechanism that gets data from markdown files into the database. Without it working correctly, questions cannot be imported.

**Independent Test**: Can be tested by running the seed script against a test database with markdown files in the new format, then querying the database to verify questions and options were created with correct scores.

**Acceptance Scenarios**:

1. **Given** a fresh database, **When** the developer runs `python -m src.seeds.questions_seed`, **Then** all types, groups, questions, and options are created with custom scores from the markdown files
2. **Given** an existing database with questions, **When** the developer runs the seed script again, **Then** it updates existing questions or creates new ones based on the markdown content
3. **Given** a question with custom scores (e.g., Үгүй=1, Тийм=0), **When** the seed script completes, **Then** the database QuestionOption records have those exact score values
4. **Given** the seed script is running, **When** it completes successfully, **Then** it prints a summary showing counts of types, groups, questions, and options created
5. **Given** an error during parsing (e.g., invalid score format), **When** the seed script encounters the error, **Then** it logs a clear error message with the file and line number

---

### User Story 3 - Developer Verifies Imported Questions (Priority: P2)

After running the seed script, a developer needs to verify that questions were imported correctly by viewing them in the admin interface or querying the database directly.

**Why this priority**: Verification is important but secondary to the import functionality itself. Developers can verify through manual checks or automated tests.

**Independent Test**: Can be tested by running the seed script and then using admin API endpoints to retrieve question data, confirming scores match the markdown file values.

**Acceptance Scenarios**:

1. **Given** the seed script has completed, **When** a developer queries the database for a specific question, **Then** the question text, option types, and scores match the markdown file
2. **Given** a question with inverse scoring (Үгүй=1, Тийм=0), **When** the developer views the question in the admin interface, **Then** both options are displayed with their correct scores
3. **Given** multiple question types and groups, **When** the developer retrieves all questions via API, **Then** the hierarchy is correctly preserved with all custom scores

---

### User Story 4 - Developer Handles Edge Cases in Question Format (Priority: P3)

Edge cases such as missing scores, invalid option text, or inconsistent formatting need to be handled gracefully by the seed script.

**Why this priority**: Edge case handling improves robustness but is not critical for the initial implementation. Basic error handling is sufficient for MVP.

**Independent Test**: Can be tested by creating markdown files with various edge cases (missing scores, invalid option text, inconsistent scores) and running the seed script to verify appropriate error handling.

**Acceptance Scenarios**:

1. **Given** a question line missing a score value, **When** the seed script parses it, **Then** it uses a default score (0 for both options) or logs a warning
2. **Given** a question line with invalid option text (not Үгүй or Тийм), **When** the seed script parses it, **Then** it logs an error and skips that question
3. **Given** both Үгүй and Тийм options have score 1, **When** the seed script processes it, **Then** it logs a warning about inconsistent scoring but uses the values as specified
4. **Given** an empty group or type section, **When** the seed script encounters it, **Then** it skips that section without creating records

---

### Edge Cases

- What happens when a question line is missing the option text or score entirely?
- How does the system handle both Үгүй and Тийм having the same score (both 0 or both 1)?
- What happens if the score value is not a valid integer?
- How does the script handle malformed lines with extra whitespace or missing tabs?
- What happens when a markdown file has encoding issues with Mongolian Cyrillic text?
- How does the system handle duplicate questions (same text) within the same group?
- What happens if a group has no questions under it?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The seed script MUST parse question markdown files from the `questions/` folder using the new format where each question line includes question text, option text (Үгүй or Тийм), and score value separated by whitespace
- **FR-002**: The seed script MUST support custom scoring per question option, allowing scores to be different from the hardcoded YES=1, NO=0 pattern
- **FR-003**: When a question specifies Үгүй (No) with score 1, the system MUST automatically set Тийм (Yes) to score 0 for that question
- **FR-004**: When a question specifies Тийм (Yes) with score 1, the system MUST automatically set Үгүй (No) to score 0 for that question
- **FR-005**: The seed script MUST create Question records with text extracted from the question line
- **FR-006**: The seed script MUST create two QuestionOption records per question (one for Үгүй/NO, one for Тийм/YES) with the correct scores
- **FR-006a**: The seed script MUST set `require_comment=False` and `require_image=False` for ALL question options (both Үгүй and Тийм)
- **FR-006b**: When creating QuestionOption records, the seed script MUST set `comment_min_len=0`, `max_images=0`, and `image_max_mb=1` as default values (minimal values that satisfy database constraints while accurately reflecting disabled functionality)
- **FR-007**: The seed script MUST maintain the hierarchical structure: QuestionnaireType → QuestionGroup → Question → QuestionOption
- **FR-008**: The seed script MUST log clear error messages when parsing fails, including file name and line number
- **FR-009**: The seed script MUST handle Mongolian Cyrillic text correctly (Үгүй, Тийм) without encoding issues
- **FR-010**: The seed script MUST print a summary report after completion showing counts of created/updated entities
- **FR-011**: The seed script MUST be runnable via `python -m src.seeds.questions_seed` command
- **FR-012**: The seed script MUST handle missing or invalid scores by using default values (0) and logging warnings

### Key Entities

- **QuestionnaireType**: Represents a top-level risk category (e.g., "Байршил, үйл ажиллагаа"), contains multiple groups
- **QuestionGroup**: Represents a grouping of related questions within a type (e.g., "Барилга байгууламжийн суурь, хана"), belongs to a type
- **Question**: An individual YES/NO question with text in Mongolian Cyrillic, belongs to a group
- **QuestionOption**: Represents the Үгүй (NO) or Тийм (YES) option for a question, with an associated score value (0 or 1), belongs to a question
- **Markdown File**: Text file in `questions/` folder containing hierarchical question data with custom scoring information

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can update question markdown files with custom scores in under 5 minutes per file
- **SC-002**: The seed script completes successfully for all question files in under 30 seconds
- **SC-003**: All imported questions have 100% score accuracy matching the markdown file values
- **SC-004**: The seed script handles at least 95% of edge cases (missing scores, invalid formats) without crashing
- **SC-005**: Developers can run the seed script successfully on their first attempt without needing to debug parsing errors
- **SC-006**: Question import success rate is 100% for properly formatted markdown files
- **SC-007**: The seed script provides clear error messages for 100% of parsing failures, enabling quick fixes

## Assumptions & Dependencies

### Assumptions

- The `questions/` folder exists in the project root or backend directory
- Markdown files use a consistent format with question text, option text, and score separated by whitespace/tabs
- Question option text will always be "Үгүй" (No) or "Тийм" (Yes) in Mongolian Cyrillic
- Score values are integers (0 or 1)
- All question options have `require_comment=False` and `require_image=False` (no conditional requirements)
- Default values for disabled fields: `comment_min_len=0`, `max_images=0`, `image_max_mb=1` (minimal values satisfying database constraints)
- The existing database models (QuestionnaireType, QuestionGroup, Question, QuestionOption) support custom scoring
- Developers will use UTF-8 encoding for markdown files to properly display Mongolian Cyrillic text

### Dependencies

- Existing database models must support custom scores on QuestionOption (score field already exists)
- The `src.seeds.questions_seed` module exists and is runnable
- Database connection and SQLAlchemy models are properly configured
- Python environment has required dependencies (SQLAlchemy, asyncpg, etc.)

## Scope

### In Scope

- Updating the `questions_seed.py` script to parse the new markdown format with custom scores
- Supporting inverse scoring logic (if one option is 1, the other is 0)
- Parsing hierarchical structure: Type → Group → Question with custom scores
- Error handling and logging for malformed input
- Summary reporting after seed completion

### Out of Scope

- Creating a web interface for editing questions (this is admin functionality, not seed script)
- Backward compatibility with the old hardcoded scoring format (scripts will be updated, not maintained in dual mode)
- Validation of score values beyond checking they are integers (business logic validation is out of scope)
- Automatic detection of encoding issues (developers must ensure UTF-8 encoding)
- Migration of existing questions in the database to new scoring (seed script will create/update based on markdown files)
