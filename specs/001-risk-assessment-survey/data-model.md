# Data Model: Risk Assessment Survey System

**Date**: 2026-01-21 | **Feature**: 001-risk-assessment-survey

## Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   api_keys      │     │questionnaire_   │     │question_groups  │     │   questions     │
├─────────────────┤     │    types        │     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     ├─────────────────┤     │ id (PK)         │     │ id (PK)         │
│ key_hash        │     │ id (PK)         │◄────│ type_id (FK)    │◄────│ group_id (FK)   │──┐
│ name            │     │ name            │     │ name            │     │ text            │  │
│ is_active       │     │ threshold_high  │     │ display_order   │     │ display_order   │  │
│ created_at      │     │ threshold_medium│     │ weight          │     │ weight          │  │
│ last_used_at    │     │ weight          │     │ is_active       │     │ is_critical     │  │
└─────────────────┘     │ is_active       │     │ created_at      │     │ is_active       │  │
                        │ created_at      │     │ updated_at      │     │ created_at      │  │
                        │ updated_at      │     └─────────────────┘     └─────────────────┘  │
                        └─────────────────┘                                      │           │
                                 │                                               │           │
                                 │                             ┌─────────────────────────┐   │
                                 │                             │   question_options      │   │
                                 │                             ├─────────────────────────┤   │
                                 │                             │ id (PK)                 │   │
                                 │                             │ question_id (FK)        │───┘
                                 │                             │ option_type (YES/NO)    │
                                 │                             │ score                   │
                                 │                             │ require_comment         │
                                 │                             │ require_image           │
                                 │                             │ comment_min_len         │
                                 │                             │ max_images              │
                                 │                             │ image_max_mb            │
                                 │                             └─────────────────────────┘
                                 │
┌─────────────────┐              │         ┌─────────────────────┐   ┌───────────────────┐
│  respondents    │              │         │    assessments      │   │submission_contacts│
├─────────────────┤              │         ├─────────────────────┤   ├───────────────────┤
│ id (PK)         │◄─────────────┼─────────│ id (PK)             │──►│ id (PK)           │
│ kind (ORG/      │              │         │ respondent_id (FK)  │   │ assessment_id(FK) │
│   PERSON)       │              │         │ contact_id (FK)     │   │ last_name         │
│ name            │              └────────►│ token_hash          │   │ first_name        │
│ registration_no │                        │ selected_type_ids   │   │ email             │
│ created_at      │                        │ questions_snapshot  │   │ phone             │
│ updated_at      │                        │ expires_at          │   │ position          │
└─────────────────┘                        │ status              │   │ created_at        │
                                           │ completed_at        │   └───────────────────┘
                                           │ created_at          │
                                           └─────────────────────┘
                                                    │
                       ┌────────────────────────────┼────────────────────────────┐
                       │                            │                            │
                       ▼                            ▼                            ▼
          ┌─────────────────┐     ┌─────────────────────────┐   ┌─────────────────┐
          │    answers      │     │    assessment_scores    │   │   attachments   │
          ├─────────────────┤     ├─────────────────────────┤   ├─────────────────┤
          │ id (PK)         │     │ id (PK)                 │   │ id (PK)         │
          │ assessment_id   │     │ assessment_id (FK)      │   │ answer_id (FK)  │
          │ question_id     │     │ type_id (NULL=overall)  │   │ storage_key     │
          │ selected_option │     │ group_id (NULL=type/ovr)│   │ original_name   │
          │ comment         │     │ raw_score               │   │ size_bytes      │
          │ score_awarded   │     │ max_score               │   │ mime_type       │
          │ created_at      │     │ percentage              │   │ created_at      │
          └─────────────────┘     │ risk_rating             │   └─────────────────┘
                 │                └─────────────────────────┘
                 └──────────────────────────────────────────────────┘
```

## Entity Definitions

### 1. api_keys

Stores hashed API keys for admin authentication.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| key_hash | VARCHAR(128) | NOT NULL, UNIQUE | Argon2 hash of API key |
| name | VARCHAR(100) | NOT NULL | Descriptive name for the key |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether key can be used |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| last_used_at | TIMESTAMP | NULL | Last successful authentication |

**Indexes**: `key_hash` (for lookup)

---

### 2. questionnaire_types

Categories of questions with scoring configuration.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | VARCHAR(200) | NOT NULL | Type name (Mongolian) |
| scoring_method | ENUM | NOT NULL, DEFAULT 'SUM' | SUM only for Phase 1 |
| threshold_high | INTEGER | NOT NULL, DEFAULT 80 | >= this % = low risk |
| threshold_medium | INTEGER | NOT NULL, DEFAULT 50 | >= this % = medium risk |
| weight | DECIMAL(5,2) | NOT NULL, DEFAULT 1.0 | Weight for overall score |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Available for new assessments |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation rules**:
- `threshold_high` > `threshold_medium`
- `weight` > 0

**Indexes**: `is_active` (for filtering)

---

### 3. question_groups (Бүлэг)

Logical groupings of questions within a type.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| type_id | UUID | FK → questionnaire_types | Parent type |
| name | VARCHAR(200) | NOT NULL | Group name (Mongolian) |
| display_order | INTEGER | NOT NULL | Order within type |
| weight | DECIMAL(5,2) | NOT NULL, DEFAULT 1.0 | Weight for type calculation |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Available for new assessments |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation rules**:
- `display_order` >= 0
- `weight` > 0

**Indexes**: `(type_id, display_order)` for ordered retrieval, `(type_id, is_active)`

---

### 4. questions

Individual YES/NO questions within a group.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| group_id | UUID | FK → question_groups | Parent group |
| text | TEXT | NOT NULL | Question text (Mongolian) |
| display_order | INTEGER | NOT NULL | Order within group |
| weight | DECIMAL(5,2) | NOT NULL, DEFAULT 1.0 | Question weight (future use) |
| is_critical | BOOLEAN | NOT NULL, DEFAULT FALSE | Critical flag (future use) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Available for snapshots |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Validation rules**:
- `display_order` >= 0
- `text` length <= 2000 characters

**Indexes**: `(group_id, display_order)` for ordered retrieval, `(group_id, is_active)`

---

### 5. question_options

Configuration for YES and NO options per question.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| question_id | UUID | FK → questions | Parent question |
| option_type | ENUM | NOT NULL | 'YES' or 'NO' |
| score | INTEGER | NOT NULL, DEFAULT 0 | Points awarded |
| require_comment | BOOLEAN | NOT NULL, DEFAULT FALSE | Comment required |
| require_image | BOOLEAN | NOT NULL, DEFAULT FALSE | Image required |
| comment_min_len | INTEGER | NOT NULL, DEFAULT 0 | Min comment chars |
| max_images | INTEGER | NOT NULL, DEFAULT 3 | Max images allowed |
| image_max_mb | INTEGER | NOT NULL, DEFAULT 5 | Max image size MB |

**Validation rules**:
- `score` >= 0
- `comment_min_len` >= 0 and <= 2000
- `max_images` >= 1 and <= 10
- `image_max_mb` >= 1 and <= 20
- Exactly 2 options per question (YES and NO)

**Unique constraint**: `(question_id, option_type)`

---

### 6. respondents

Organizations or individuals taking assessments.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| kind | ENUM | NOT NULL | 'ORG' or 'PERSON' |
| name | VARCHAR(300) | NOT NULL | Respondent name |
| registration_no | VARCHAR(50) | NULL | Org registration or person ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**: `kind`, `name` (for search)

---

### 7. submission_contacts (Хариулагч)

Contact information for the person who fills out the assessment.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| assessment_id | UUID | FK → assessments, UNIQUE | Parent assessment (1:1) |
| last_name | VARCHAR(100) | NOT NULL | Овог (Last name) |
| first_name | VARCHAR(100) | NOT NULL | Нэр (First name) |
| email | VARCHAR(255) | NOT NULL | Email address |
| phone | VARCHAR(20) | NOT NULL | Phone number |
| position | VARCHAR(200) | NOT NULL | Албан тушаал (Position/Title) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Validation rules**:
- `email` must be valid email format
- `phone` must be valid phone format (Mongolian: 8 digits or +976...)
- All fields required

**Indexes**: `assessment_id` (unique), `email`

---

### 8. assessments

Assessment instances with question snapshots.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| respondent_id | UUID | FK → respondents | Who is being assessed |
| contact_id | UUID | FK → submission_contacts, NULL | Who filled the form (after completion) |
| token_hash | VARCHAR(64) | NOT NULL, UNIQUE | SHA-256 hash of access token |
| selected_type_ids | UUID[] | NOT NULL | Types included in assessment |
| questions_snapshot | JSONB | NOT NULL | Deep copy of questions/options |
| expires_at | TIMESTAMP | NOT NULL | Link expiration time |
| status | ENUM | NOT NULL, DEFAULT 'PENDING' | PENDING/COMPLETED/EXPIRED |
| completed_at | TIMESTAMP | NULL | When submission occurred |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Validation rules**:
- `expires_at` > `created_at`
- `selected_type_ids` not empty

**Indexes**: `token_hash` (for lookup), `respondent_id`, `status`, `expires_at`

**Snapshot JSONB structure** (with Type → Group → Question hierarchy):
```json
{
  "types": [
    {
      "id": "uuid",
      "name": "Галын аюулгүй байдал",
      "threshold_high": 80,
      "threshold_medium": 50,
      "weight": 1.0,
      "groups": [
        {
          "id": "uuid",
          "name": "Галын хор",
          "display_order": 1,
          "weight": 1.0,
          "questions": [
            {
              "id": "uuid",
              "text": "Question text",
              "display_order": 1,
              "options": {
                "YES": {
                  "score": 10,
                  "require_comment": false,
                  "require_image": false,
                  "comment_min_len": 0,
                  "max_images": 3,
                  "image_max_mb": 5
                },
                "NO": {
                  "score": 0,
                  "require_comment": true,
                  "require_image": true,
                  "comment_min_len": 50,
                  "max_images": 3,
                  "image_max_mb": 5
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

### 9. answers

Respondent's answers to assessment questions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| assessment_id | UUID | FK → assessments | Parent assessment |
| question_id | UUID | NOT NULL | Question from snapshot |
| selected_option | ENUM | NOT NULL | 'YES' or 'NO' |
| comment | TEXT | NULL | Optional/required comment |
| score_awarded | INTEGER | NOT NULL | Points received |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Answer timestamp |

**Validation rules**:
- `comment` length <= 2000 characters
- `score_awarded` >= 0

**Unique constraint**: `(assessment_id, question_id)`

**Indexes**: `assessment_id`

---

### 10. assessment_scores

Calculated scores per group, type, and overall.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| assessment_id | UUID | FK → assessments | Parent assessment |
| type_id | UUID | NULL | NULL = overall score |
| group_id | UUID | NULL | NULL = type or overall score |
| raw_score | INTEGER | NOT NULL | Sum of awarded scores |
| max_score | INTEGER | NOT NULL | Maximum possible score |
| percentage | DECIMAL(5,2) | NOT NULL | Calculated percentage |
| risk_rating | ENUM | NOT NULL | LOW/MEDIUM/HIGH |

**Score Level Logic**:
- `group_id` NOT NULL, `type_id` NOT NULL: Group-level score
- `group_id` NULL, `type_id` NOT NULL: Type-level score (weighted avg of groups)
- `group_id` NULL, `type_id` NULL: Overall score (weighted avg of types)

**Validation rules**:
- `raw_score` >= 0 and <= `max_score`
- `percentage` >= 0 and <= 100

**Unique constraint**: `(assessment_id, type_id, group_id)`

**Indexes**: `assessment_id`

---

### 11. attachments

Image files uploaded with answers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| answer_id | UUID | FK → answers | Parent answer |
| storage_key | VARCHAR(500) | NOT NULL | S3/MinIO object key |
| original_name | VARCHAR(255) | NOT NULL | Original filename |
| size_bytes | INTEGER | NOT NULL | File size |
| mime_type | VARCHAR(50) | NOT NULL | image/jpeg, image/png, etc. |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Upload timestamp |

**Validation rules**:
- `mime_type` must start with "image/"
- `size_bytes` <= configured max (default 5MB)

**Indexes**: `answer_id`, `storage_key`

---

## Enums

```sql
CREATE TYPE scoring_method AS ENUM ('SUM');
CREATE TYPE respondent_kind AS ENUM ('ORG', 'PERSON');
CREATE TYPE option_type AS ENUM ('YES', 'NO');
CREATE TYPE assessment_status AS ENUM ('PENDING', 'COMPLETED', 'EXPIRED');
CREATE TYPE risk_rating AS ENUM ('LOW', 'MEDIUM', 'HIGH');
```

---

## State Transitions

### Assessment Status

```
                  ┌──────────────────────────────────┐
                  │                                  │
                  ▼                                  │
┌─────────┐   submit   ┌───────────┐           ┌─────────┐
│ PENDING │──────────►│ COMPLETED │           │ EXPIRED │
└─────────┘            └───────────┘           └─────────┘
     │                                              ▲
     │                                              │
     └──────────────────────────────────────────────┘
                    expires_at reached
                    (background job or on-access check)
```

**Transitions**:
- PENDING → COMPLETED: On successful form submission
- PENDING → EXPIRED: When `expires_at` is reached (checked on access or via background job)
- COMPLETED and EXPIRED are terminal states

---

## Scoring Calculation Logic (Backend Only)

**Note**: All scoring calculations are performed on the backend. Frontend displays results only.

### 1. Group Score (Questions → Group)

```
group_raw = Σ(answer.score_awarded) for all questions in group
group_max = Σ(max(yes_score, no_score)) for all questions in group

if group_max == 0:
    group_percentage = 0  # Handle edge case
else:
    group_percentage = (group_raw / group_max) * 100
```

### 2. Type Score (Groups → Type)

```
# Weighted average of group percentages
type_percentage = Σ(group_percentage * group_weight) / Σ(group_weight)

if Σ(group_weight) == 0:
    type_percentage = 0  # Handle edge case
```

### 3. Overall Score (Types → Overall)

```
# Weighted average of type percentages
overall_percentage = Σ(type_percentage * type_weight) / Σ(type_weight)

if Σ(type_weight) == 0:
    overall_percentage = 0  # Handle edge case
```

### 4. Risk Rating Assignment

```
# Applied at group, type, and overall levels
if percentage >= threshold_high (default 80):
    risk_rating = LOW ("Бага эрсдэл")
elif percentage >= threshold_medium (default 50):
    risk_rating = MEDIUM ("Дунд эрсдэл")
else:
    risk_rating = HIGH ("Өндөр эрсдэл")
```

---

## Data Retention

Per FR-014a: Completed assessment data is retained indefinitely. Manual deletion only via admin action.

Attachments in object storage should have lifecycle rules matching database retention policy.
