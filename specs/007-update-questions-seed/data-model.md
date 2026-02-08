# Data Model: Questions Seed Custom Scoring Format

**Feature**: 007-update-questions-seed
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document describes the data entities involved in the questions seed script with custom scoring format. The feature updates the existing seed script to parse question data from markdown files with flexible scoring per option.

## Entity Hierarchy

```
QuestionnaireType (1)
    ├── QuestionGroup (many)
    │   ├── Question (many)
    │   │   ├── QuestionOption (Үгүй/NO)
    │   │   └── QuestionOption (Тийм/YES)
    │   └── ...
    └── ...
```

## Entities

### QuestionnaireType

**Purpose**: Top-level risk category containing groups of related questions

**Attributes**:
| Field | Type | Description | Source |
|-------|------|-------------|--------|
| id | UUID | Primary key | Auto-generated |
| name | string | Type name in Mongolian Cyrillic (e.g., "Байршил, үйл ажиллагаа") | Markdown file header |
| scoring_method | enum | Scoring method (always SUM) | Hardcoded |
| threshold_high | integer | High risk threshold percentage | Hardcoded (80) |
| threshold_medium | integer | Medium risk threshold percentage | Hardcoded (50) |
| weight | decimal | Weight in overall score calculation | Hardcoded (1.0) |
| is_active | boolean | Whether type is active for new assessments | Hardcoded (true) |
| created_at | timestamp | Creation timestamp | Auto-generated |
| updated_at | timestamp | Last update timestamp | Auto-generated |

**Relationships**:
- One-to-many with QuestionGroup (has many groups)

**Validation Rules**:
- name must be unique
- threshold_high > threshold_medium > 0
- weight > 0

**Lifecycle**:
- Created when seed script encounters a new type header in markdown
- Updated if type with same name already exists
- Never deleted (soft delete via is_active flag)

---

### QuestionGroup

**Purpose**: Groups related questions within a questionnaire type

**Attributes**:
| Field | Type | Description | Source |
|-------|------|-------------|--------|
| id | UUID | Primary key | Auto-generated |
| type_id | UUID | Foreign key to QuestionnaireType | From parent type |
| name | string | Group name in Mongolian Cyrillic (e.g., "Барилга байгууламжийн суурь, хана") | Markdown file section header |
| display_order | integer | Order within type (1, 2, 3...) | Sequence in markdown |
| weight | decimal | Weight in type score calculation | Hardcoded (1.0) |
| is_active | boolean | Whether group is active for new assessments | Hardcoded (true) |
| created_at | timestamp | Creation timestamp | Auto-generated |
| updated_at | timestamp | Last update timestamp | Auto-generated |

**Relationships**:
- Many-to-one with QuestionnaireType (belongs to a type)
- One-to-many with Question (has many questions)

**Validation Rules**:
- name must be unique within type_id
- display_order > 0
- weight > 0

**Lifecycle**:
- Created when seed script encounters a new group header (indented 4 spaces)
- Updated if group with same name exists in same type
- Never deleted (soft delete via is_active flag)

---

### Question

**Purpose**: Individual YES/NO question with Mongolian text

**Attributes**:
| Field | Type | Description | Source |
|-------|------|-------------|--------|
| id | UUID | Primary key | Auto-generated |
| group_id | UUID | Foreign key to QuestionGroup | From parent group |
| text | string | Question text in Mongolian Cyrillic | Markdown file question line (first part) |
| display_order | integer | Order within group (1, 2, 3...) | Sequence in markdown |
| weight | decimal | Weight in group score calculation | Hardcoded (1.0) |
| is_critical | boolean | Whether question is critical for assessment | Hardcoded (false) |
| is_active | boolean | Whether question is active for new assessments | Hardcoded (true) |
| created_at | timestamp | Creation timestamp | Auto-generated |
| updated_at | timestamp | Last update timestamp | Auto-generated |

**Relationships**:
- Many-to-one with QuestionGroup (belongs to a group)
- One-to-many with QuestionOption (has two options: Үгүй and Тийм)

**Validation Rules**:
- text must be unique within group_id
- display_order > 0
- weight > 0

**Lifecycle**:
- Created when seed script parses a question line (indented 8 spaces)
- Updated if question with same text exists in same group
- Never deleted (soft delete via is_active flag)

**Parsing Logic**:
```python
# Example question line:
# "Тухайн барилга, байгууламжийн байршил нь 60м-ээс дээш алслалтай, хүн амын төвлөрөл бага        Үгүй                    1"

# Split by whitespace (right to left to preserve question text):
parts = line.rstrip().rsplit(maxsplit=2)
# parts[0] = question text
# parts[1] = option text (Үгүй or Тийм)
# parts[2] = score (0 or 1)
```

---

### QuestionOption

**Purpose**: Represents Үгүй (NO) or Тийм (YES) option for a question with associated score

**Attributes**:
| Field | Type | Description | Source |
|-------|------|-------------|--------|
| id | UUID | Primary key | Auto-generated |
| question_id | UUID | Foreign key to Question | From parent question |
| option_type | enum | Option type (YES or NO) | Mapped from Тийм→YES, Үгүй→NO |
| score | integer | Score value for this option (0 or 1) | Markdown file question line (last part) |
| require_comment | boolean | Whether comment is required for this option | Hardcoded (false) |
| require_image | boolean | Whether image attachment is required | Hardcoded (false) |
| comment_min_len | integer | Minimum comment length if required | Hardcoded (0) |
| max_images | integer | Maximum number of images allowed | Hardcoded (0) |
| image_max_mb | integer | Maximum image size in MB | Hardcoded (1) |
| created_at | timestamp | Creation timestamp | Auto-generated |
| updated_at | timestamp | Last update timestamp | Auto-generated |

**Relationships**:
- Many-to-one with Question (belongs to a question)

**Validation Rules**:
- (question_id, option_type) must be unique (each question has exactly one YES and one NO)
- score in {0, 1}
- max_images >= 0
- image_max_mb > 0
- comment_min_len >= 0

**Lifecycle**:
- Created as pair when seed script parses a question line
- Two options created per question: Үгүй (NO) and Тийм (YES)
- Updated if options already exist for question
- Never deleted (cascade deleted via parent question)

**Inverse Scoring Logic**:
```python
# If Үгүй (NO) has score 1, Тийм (YES) gets score 0
# If Тийм (YES) has score 1, Үгүй (NO) gets score 0

if parsed_option == "Үгүй" and parsed_score == 1:
    no_score = 1
    yes_score = 0
elif parsed_option == "Тийм" and parsed_score == 1:
    yes_score = 1
    no_score = 0
else:
    # Both can be 0
    no_score = yes_score = 0
```

**Option Type Mapping**:
| Mongolian | English Enum | Database Value |
|-----------|--------------|----------------|
| Үгүй | NO | "NO" |
| Тийм | YES | "YES" |

---

### Markdown File (Input Source)

**Purpose**: Text file containing hierarchical question data with custom scoring

**Format Structure**:
```text
Type Name (no indent, ends with colon)
    Group Name (4-space indent, ends with colon)
        Question text        Үгүй/Тийм    0/1 (8-space indent, whitespace-separated)
        Another question    Тийм/Үгүй    1/0 (8-space indent, whitespace-separated)
    Another Group
        Question text    Үгүй    1
```

**Parsing Rules**:
1. **Type Header**: Line with no leading whitespace, typically ends with colon
2. **Group Header**: Line with 4-space or 1-tab indent, typically ends with colon
3. **Question Line**: Line with 8-space or 2-tab indent, split into 3 parts:
   - Question text (can contain spaces)
   - Option text (Үгүй or Тийм)
   - Score (0 or 1)
4. **Empty Lines**: Separate sections, ignored
5. **Comments**: Lines starting with # are ignored

**Validation Rules**:
- File must use UTF-8 encoding
- Question lines must have exactly 3 whitespace-separated parts
- Option text must be "Үгүй" or "Тийм"
- Score must be integer 0 or 1
- Type and group names must be non-empty

**Error Handling**:
- Invalid score: Use default 0, log warning
- Invalid option text: Skip question, log error
- Missing score: Use default 0, log warning
- UTF-8 decode error: Skip file, log error with file path

## Data Flow

### Import Process

```
Markdown Files (questions/*.md)
    ↓
[Parsing]
    ↓
Extract: Type → Group → Question → {Option, Score}
    ↓
[Validation]
    ↓
Check: Required fields present, valid values
    ↓
[Database Upsert]
    ↓
For each question:
    1. Find existing by (type_name, group_name, question_text)
    2. If exists: Update text, display_order
    3. If new: Create new Question
    4. Create/update QuestionOption pair (NO and YES)
    ↓
[Summary Report]
    ↓
Print: Types created, Groups created, Questions created, Options created, Errors encountered
```

### Natural Key Lookups

**Question Lookup**:
```python
SELECT q.*
FROM questions q
JOIN question_groups g ON q.group_id = g.id
JOIN questionnaire_types t ON g.type_id = t.id
WHERE t.name = :type_name
  AND g.name = :group_name
  AND q.text = :question_text
```

**Purpose**:
- Avoids hardcoded UUIDs
- Supports idempotent seed script runs
- Enables updating questions by natural identifier

## State Transitions

### Question Creation

```
[Markdown Parsed]
    ↓
[Extract Question Data]
    ↓
[Check if Exists] (by natural key)
    ↓
    ├─→ [Exists] → [Update Question] → [Update Options]
    │
    └─→ [New] → [Create Question] → [Create Options]
```

### Question Update

```
[Existing Question Found]
    ↓
[Update Fields]
    - text (if changed)
    - display_order (if changed)
    ↓
[Update Options]
    - Update score if changed
    - Create missing option if deleted
```

## Indexes

**Database Indexes** (for efficient lookup):

```sql
-- Natural key lookup for upsert
CREATE INDEX idx_question_natural_key ON questions (text, group_id);

-- Foreign key indexes
CREATE INDEX idx_question_group_id ON questions (group_id);
CREATE INDEX idx_question_option_question_id ON question_options (question_id);

-- Unique constraint for options
CREATE UNIQUE INDEX idx_question_option_unique ON question_options (question_id, option_type);
```

## Constraints

### Natural Key Uniqueness

**Question**: (type_name, group_name, question_text) must be unique
- Ensures no duplicate questions within same group
- Enables idempotent seed script execution

**QuestionOption**: (question_id, option_type) must be unique
- Each question has exactly one YES and one NO option
- Enforced by database unique constraint

### Foreign Key Constraints

```sql
ALTER TABLE question_groups
ADD CONSTRAINT fk_question_groups_type
FOREIGN KEY (type_id) REFERENCES questionnaire_types(id);

ALTER TABLE questions
ADD CONSTRAINT fk_questions_group
FOREIGN KEY (group_id) REFERENCES question_groups(id);

ALTER TABLE question_options
ADD CONSTRAINT fk_question_options_question
FOREIGN KEY (question_id) REFERENCES questions(id);
```

### Cascade Rules

- Deleting QuestionnaireType → CASCADE DELETE all groups, questions, options
- Deleting QuestionGroup → CASCADE DELETE all questions, options
- Deleting Question → CASCADE DELETE all options
- (Soft delete preferred: set is_active=false instead of actual DELETE)

## Migration Strategy

**Existing Data**: No migration needed (seed script creates/updates data)

**Schema Changes**: None (all fields already exist)

**Backward Compatibility**: Not supported (spec: out of scope)

## Testing Data

**Sample Markdown File** (for testing):

```markdown
ГАЛЫН АЮУЛГҮЙ БАЙДАЛ
    Галын хор
        Лац түгжээ, шаланк, резин жийрэг нь бүрэн бүтэн эсэх        Үгүй    1
        Монометр нь ногоон түвшинг зааж байгаа эсэх        Үгүй    1
        Галын хорыг сүүлийн 6 сарын дотор туршиж үзсэн эсэх        Үгүй    1
```

**Expected Database State**:
- 1 QuestionnaireType: "ГАЛЫН АЮУЛГҮЙ БАЙДАЛ"
- 1 QuestionGroup: "Галын хор" (under above type)
- 3 Questions (one per line)
- 6 QuestionOptions (2 per question: NO with score=1, YES with score=0)
