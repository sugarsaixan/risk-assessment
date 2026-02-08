# Data Model: 006-risk-score-calculation

**Date**: 2026-02-08

## Schema Changes

### Modified Table: `assessment_scores`

Existing columns remain unchanged. New nullable columns added:

| Column               | Type          | Nullable | Default | Description                                          |
| -------------------- | ------------- | -------- | ------- | ---------------------------------------------------- |
| classification_label | VARCHAR(20)   | YES      | NULL    | Group-level: Mongolian classification (Хэвийн, etc.) |
| probability_score    | DECIMAL(8,4)  | YES      | NULL    | Type-level: AVERAGE + 0.618×STDEV of group sums      |
| consequence_score    | DECIMAL(8,4)  | YES      | NULL    | Type-level: AVERAGE + 0.618×STDEV of group numerics   |
| risk_value           | INTEGER       | YES      | NULL    | Type/Overall: rounded product or aggregation          |
| risk_grade           | VARCHAR(3)    | YES      | NULL    | Type/Overall: AAA through D                           |
| risk_description     | VARCHAR(100)  | YES      | NULL    | Type/Overall: Mongolian description                   |
| insurance_decision   | VARCHAR(20)   | YES      | NULL    | Overall only: "Даатгана" or "Даатгахгүй"            |

### Storage Hierarchy (enhanced)

**Group-level scores** (`type_id` + `group_id` set):
- Existing: raw_score, max_score, percentage, risk_rating
- New: `classification_label` — one of "Хэвийн", "Хянахуйц", "Анхаарах", "Ноцтой", "Аюултай"

**Type-level scores** (`type_id` set, `group_id` NULL):
- Existing: raw_score, max_score, percentage, risk_rating
- New: `probability_score`, `consequence_score`, `risk_value`, `risk_grade`, `risk_description`

**Overall score** (both `type_id` and `group_id` NULL):
- Existing: raw_score, max_score, percentage, risk_rating
- New: `risk_value` (НИЙТ ЭРСДЭЛ), `risk_grade` (НИЙТ ЗЭРЭГЛЭЛ), `risk_description`, `insurance_decision` (ДААТГАХ ЭСЭХ)

### Unchanged Tables

The following tables are **not modified**:
- `assessments` — no schema changes
- `answers` — no schema changes (score_awarded already exists)
- `questionnaire_types` — no schema changes
- `question_groups` — no schema changes
- `questions` — no schema changes

## Entity Relationships

```
Assessment (1) ──── (N) AssessmentScore
                         ├── Group scores (type_id + group_id)
                         │   └── classification_label (NEW)
                         ├── Type scores (type_id, group_id=NULL)
                         │   └── probability_score, consequence_score, risk_value, risk_grade, risk_description (NEW)
                         └── Overall score (type_id=NULL, group_id=NULL)
                             └── risk_value, risk_grade, risk_description, insurance_decision (NEW)
```

## Calculation Data Flow

```
Answers (score_awarded per question)
  ↓ SUM by group
Group Sum Scores → classification_label (0→Хэвийн, 1→Хянахуйц, 2→Анхаарах, 3→Ноцтой, 4-5→Аюултай)
  ↓ per type
Probability Score = AVG(group_sums) + 0.618 × STDEV.S(group_sums)
Consequence Score = AVG(group_numerics) + 0.618 × STDEV.S(group_numerics)
  ↓ per type
Type Risk Value = round(Probability × Consequence)
Type Risk Grade = grade_lookup(Type Risk Value)
  ↓ across all types
НИЙТ ЭРСДЭЛ = round(AVG(type_risk_values) + 0.618 × STDEV.S(type_risk_values))
НИЙТ ЗЭРЭГЛЭЛ = grade_lookup(НИЙТ ЭРСДЭЛ)
ДААТГАХ ЭСЭХ = "Даатгахгүй" if НИЙТ ЭРСДЭЛ > 16, else "Даатгана"
```

## Grade Lookup Table (Static)

| Risk Value | Grade | Description                         |
| ---------- | ----- | ----------------------------------- |
| 1          | AAA   | Эрсдэл маш бага                    |
| 2–3        | AA    | Эрсдэл бага                        |
| 4          | A     | Анхаарахгүй, эрсдэл бага           |
| 5          | BBB   | Нийцэхүйц, эрсдэл доогуур         |
| 6          | BB    | Авахуйц, эрсдэл доогуур           |
| 7–9        | B     | Хянахуйц, эрсдэл доогуур          |
| 10–11      | CCC   | Хянахуйц, эрсдэл дунд             |
| 12–14      | CC    | Анхаарах, эрсдэл дунд              |
| 15         | C     | Нэн анхаарах, эрсдэл дунд         |
| 16         | DDD   | Ноцтой, эрсдэл дээгүүр            |
| 17–20      | DD    | Нэн ноцтой, эрсдэл дээгүүр        |
| 21+        | D     | Аюултай, эрсдэл өндөр              |

## Classification Mapping (Static)

| Sum Score | Label     | Numeric Value |
| --------- | --------- | ------------- |
| 0         | Хэвийн    | 1             |
| 1         | Хянахуйц  | 2             |
| 2         | Анхаарах   | 3             |
| 3         | Ноцтой    | 4             |
| 4–5+      | Аюултай   | 5             |
