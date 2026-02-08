# Feature Specification: Risk Score Calculation & Grading

**Feature Branch**: `006-risk-score-calculation`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Update calculation and result page; each group has its own result based on sum score of its questions; each type has its own result; probability score (МАГАДЛАЛЫН ОНОО), consequence score (ҮР ДАГАВРЫН ОНОО), risk value, risk grade, and risk description. Per-type risk values, total risk (НИЙТ ЭРСДЭЛ), total grade (НИЙТ ЗЭРЭГЛЭЛ), and insurance decision (ДААТГАХ ЭСЭХ)."

## Clarifications

### Session 2026-02-08

- Q: Per-type risk and overall aggregation? → A: Each type calculates its own ЭРСДЭЛ (probability × consequence). НИЙТ ЭРСДЭЛ = AVERAGE(type risk values) + 0.618 × STDEV(type risk values). НИЙТ ЗЭРЭГЛЭЛ uses same grade table. ДААТГАХ ЭСЭХ: if НИЙТ ЭРСДЭЛ > 16 → "Даатгахгүй", else "Даатгана".
- Q: STDEV variant (population vs sample)? → A: Sample STDEV (STDEV.S, divide by N-1), matching Excel's default STDEV() function. When N=1, STDEV is 0.
- Q: Existing scoring model migration? → A: New scoring only for new assessments; existing completed results keep old format untouched.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Group-Level Risk Classification (Priority: P1)

After completing a risk assessment, the system calculates a risk label for each question group based on the sum of scores from its questions. The group sum score maps to a Mongolian-language classification: 0 = "Хэвийн" (Normal), 1 = "Хянахуйц" (Watchable), 2 = "Анхаарах" (Attention), 3 = "Ноцтой" (Serious), 4–5 = "Аюултай" (Dangerous).

**Why this priority**: Group-level scoring is the foundation for all higher-level calculations (type scores, probability, consequence, risk grade). Without accurate group classification, nothing else works.

**Independent Test**: Can be fully tested by submitting an assessment and verifying that each group shows its sum score and the correct Mongolian classification label.

**Acceptance Scenarios**:

1. **Given** a completed assessment with a group whose questions sum to 0, **When** results are calculated, **Then** that group's classification is "Хэвийн"
2. **Given** a completed assessment with a group whose questions sum to 1, **When** results are calculated, **Then** that group's classification is "Хянахуйц"
3. **Given** a completed assessment with a group whose questions sum to 2, **When** results are calculated, **Then** that group's classification is "Анхаарах"
4. **Given** a completed assessment with a group whose questions sum to 3, **When** results are calculated, **Then** that group's classification is "Ноцтой"
5. **Given** a completed assessment with a group whose questions sum to 4, **When** results are calculated, **Then** that group's classification is "Аюултай"
6. **Given** a completed assessment with a group whose questions sum to 5, **When** results are calculated, **Then** that group's classification is "Аюултай"

---

### User Story 2 - Probability & Consequence Scores per Type (Priority: P2)

For each questionnaire type, the system calculates two derived scores from its group classifications:

- **Probability Score (МАГАДЛАЛЫН ОНОО)**: AVERAGE of group sum scores + 0.618 × STDEV of group sum scores
- **Consequence Score (ҮР ДАГАВРЫН ОНОО)**: Convert each group classification to a numeric value (Хэвийн=1, Хянахуйц=2, Анхаарах=3, Ноцтой=4, Аюултай=5), then AVERAGE of those values + 0.618 × STDEV of those values

Both scores are displayed on the result page under each type.

**Why this priority**: These two scores feed directly into the per-type risk calculation and are the core analytical outputs of each type.

**Independent Test**: Can be tested by creating an assessment with known group scores, verifying the probability and consequence scores match the expected formula output.

**Acceptance Scenarios**:

1. **Given** a type with 5 groups having sum scores [0, 1, 2, 3, 4], **When** results are calculated, **Then** the probability score equals AVERAGE(0,1,2,3,4) + 0.618 × STDEV(0,1,2,3,4) = 2.0 + 0.618 × 1.581 = 2.977 (rounded appropriately)
2. **Given** a type with 5 groups classified as [Хэвийн, Хянахуйц, Анхаарах, Ноцтой, Аюултай], **When** results are calculated, **Then** the consequence score equals AVERAGE(1,2,3,4,5) + 0.618 × STDEV(1,2,3,4,5) = 3.0 + 0.618 × 1.581 = 3.977 (rounded appropriately)
3. **Given** a type where all groups have the same sum score (e.g., all 2), **When** results are calculated, **Then** STDEV is 0 and both scores equal the AVERAGE

---

### User Story 3 - Per-Type Risk Value and Grade (Priority: P3)

Each questionnaire type calculates its own risk value and grade:

- **Type ЭРСДЭЛ (Risk)**: Probability Score × Consequence Score (rounded to nearest integer)
- **Type ЭРСДЭЛИЙН ЗЭРЭГЛЭЛ (Grade)**: Mapped from the type's risk value using the grade lookup table
- **Type ЭРСДЭЛИЙН ТАЙЛБАР (Description)**: Mongolian description corresponding to the grade

The result page displays the risk value, grade, and description for each type.

| Risk Value | Grade | Description (ЭРСДЭЛИЙН ТАЙЛБАР)    |
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

**Why this priority**: Per-type risk values are the building blocks for the overall risk aggregation and provide granular insight per risk category.

**Independent Test**: Can be tested by providing known probability and consequence scores per type and verifying the correct risk value, grade, and description appear for each type on the result page.

**Acceptance Scenarios**:

1. **Given** a type with probability score = 2.0 and consequence score = 3.0, **When** risk is calculated, **Then** type risk value = 6, grade = "BB", description = "Авахуйц, эрсдэл доогуур"
2. **Given** a type with probability score = 4.5 and consequence score = 4.5, **When** risk is calculated, **Then** type risk value = 20 (rounded from 20.25), grade = "DD", description = "Нэн ноцтой, эрсдэл дээгүүр"
3. **Given** a type with probability score = 1.0 and consequence score = 1.0, **When** risk is calculated, **Then** type risk value = 1, grade = "AAA", description = "Эрсдэл маш бага"

---

### User Story 4 - Overall Risk Aggregation (НИЙТ ЭРСДЭЛ) and Insurance Decision (Priority: P4)

The system aggregates all per-type risk values into an overall assessment result:

- **НИЙТ ЭРСДЭЛ (Total Risk)**: AVERAGE(all type risk values) + 0.618 × STDEV(all type risk values), rounded to the nearest integer
- **НИЙТ ЗЭРЭГЛЭЛ (Total Grade)**: Determined from НИЙТ ЭРСДЭЛ using the same grade lookup table as per-type grades
- **ЭРСДЭЛИЙН ТАЙЛБАР (Risk Description)**: Mongolian description corresponding to the total grade
- **ДААТГАХ ЭСЭХ (Insurance Decision)**: If НИЙТ ЭРСДЭЛ > 16, the decision is "Даатгахгүй" (Do not insure); otherwise "Даатгана" (Insure)

The result page prominently displays НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, the Mongolian description, and the insurance decision.

**Why this priority**: This is the ultimate output of the entire assessment — the single actionable result that determines the insurance decision.

**Independent Test**: Can be tested by creating an assessment with multiple types having known risk values and verifying the overall risk, grade, description, and insurance decision are correct.

**Acceptance Scenarios**:

1. **Given** 3 types with risk values [6, 10, 14], **When** overall risk is calculated, **Then** НИЙТ ЭРСДЭЛ = AVERAGE(6,10,14) + 0.618 × STDEV(6,10,14) = 10.0 + 0.618 × 4.0 = 12.472 → rounded to 12, grade = "CC", description = "Анхаарах, эрсдэл дунд", insurance = "Даатгана"
2. **Given** 2 types with risk values [18, 20], **When** overall risk is calculated, **Then** НИЙТ ЭРСДЭЛ = AVERAGE(18,20) + 0.618 × STDEV(18,20) = 19.0 + 0.618 × 1.414 = 19.874 → rounded to 20, grade = "DD", insurance = "Даатгахгүй"
3. **Given** 2 types with risk values [1, 1], **When** overall risk is calculated, **Then** НИЙТ ЭРСДЭЛ = 1 + 0 = 1, grade = "AAA", insurance = "Даатгана"
4. **Given** НИЙТ ЭРСДЭЛ = 16, **When** insurance decision is evaluated, **Then** result is "Даатгана" (threshold is strictly greater than 16)
5. **Given** НИЙТ ЭРСДЭЛ = 17, **When** insurance decision is evaluated, **Then** result is "Даатгахгүй"

---

### User Story 5 - Updated Result Page Display (Priority: P5)

The result page is updated to display the full scoring hierarchy:

- **Per group**: sum score and Mongolian classification label
- **Per type**: probability score, consequence score, type risk value (ЭРСДЭЛ), type grade, and type risk description
- **Overall**: НИЙТ ЭРСДЭЛ (total risk value), НИЙТ ЗЭРЭГЛЭЛ (total grade), Mongolian risk description, and ДААТГАХ ЭСЭХ (insurance decision)
- Color-coding appropriate to the grade level (green for AAA–A, yellow for BBB–B, orange for CCC–C, red for DDD–D)

**Why this priority**: The display layer depends on all calculation logic being in place first.

**Independent Test**: Can be tested by viewing the result page for a completed assessment and verifying all new fields are visible with correct formatting and color-coding.

**Acceptance Scenarios**:

1. **Given** a completed assessment, **When** the user views the result page, **Then** each group shows its sum score and classification label in Mongolian
2. **Given** a completed assessment, **When** the user views the result page, **Then** each type section shows probability score, consequence score, type risk value, type grade, and type description
3. **Given** a completed assessment, **When** the user views the result page, **Then** the overall section prominently displays НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, Mongolian description, and ДААТГАХ ЭСЭХ
4. **Given** a risk grade of "AAA", **When** displayed on the result page, **Then** the grade is shown with a green color indicator
5. **Given** a risk grade of "D", **When** displayed on the result page, **Then** the grade is shown with a red color indicator
6. **Given** ДААТГАХ ЭСЭХ = "Даатгахгүй", **When** displayed, **Then** it is visually highlighted as a warning/negative indicator
7. **Given** ДААТГАХ ЭСЭХ = "Даатгана", **When** displayed, **Then** it is shown with a positive/neutral indicator

---

### Edge Cases

- What happens when a group has no questions answered? The group sum score defaults to 0, classified as "Хэвийн"
- What happens when a type has only one group? STDEV is 0, so probability and consequence scores equal the AVERAGE (i.e., the single group's values)
- What happens when only one type exists in the assessment? STDEV is 0 for НИЙТ ЭРСДЭЛ, so total risk equals the single type's risk value
- What happens when the risk value exceeds 25 (theoretical max of 5×5)? Values above 20 all map to grade "D"
- What happens when probability or consequence score results in a non-integer risk value? The product is rounded to the nearest integer before grade lookup
- What happens when a group's sum score exceeds 5? The classification formula only covers 0–5; scores above 5 should be capped at "Аюултай" (same as 4–5)
- What happens when НИЙТ ЭРСДЭЛ equals exactly 16? Insurance decision is "Даатгана" (threshold is strictly > 16)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate each group's sum score by adding the score_awarded values of all answers within that group
- **FR-002**: System MUST classify each group's risk level based on its sum score: 0="Хэвийн", 1="Хянахуйц", 2="Анхаарах", 3="Ноцтой", 4–5="Аюултай"
- **FR-003**: System MUST handle group sum scores above 5 by classifying them as "Аюултай"
- **FR-004**: System MUST calculate the Probability Score (МАГАДЛАЛЫН ОНОО) per type as: AVERAGE(group sum scores) + 0.618 × STDEV(group sum scores)
- **FR-005**: System MUST calculate the Consequence Score (ҮР ДАГАВРЫН ОНОО) per type by converting each group classification to a numeric value (Хэвийн=1, Хянахуйц=2, Анхаарах=3, Ноцтой=4, Аюултай=5), then computing AVERAGE + 0.618 × STDEV of those numeric values
- **FR-006**: System MUST calculate the per-type Risk Value (ЭРСДЭЛ) as the product of that type's Probability Score and Consequence Score, rounded to the nearest integer
- **FR-007**: System MUST determine the per-type Risk Grade (ЭРСДЭЛИЙН ЗЭРЭГЛЭЛ) from the type's Risk Value using the defined grade lookup table (AAA through D)
- **FR-008**: System MUST display the Mongolian risk description (ЭРСДЭЛИЙН ТАЙЛБАР) corresponding to each type's assigned grade
- **FR-009**: System MUST calculate НИЙТ ЭРСДЭЛ (Total Risk) as: AVERAGE(all per-type risk values) + 0.618 × STDEV(all per-type risk values), rounded to the nearest integer
- **FR-010**: System MUST determine НИЙТ ЗЭРЭГЛЭЛ (Total Grade) from НИЙТ ЭРСДЭЛ using the same grade lookup table
- **FR-011**: System MUST determine the insurance decision (ДААТГАХ ЭСЭХ): if НИЙТ ЭРСДЭЛ > 16 then "Даатгахгүй", otherwise "Даатгана"
- **FR-012**: System MUST store group classification, type-level scores (probability, consequence, risk value, grade), and overall results (НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, ДААТГАХ ЭСЭХ) in the assessment results
- **FR-013**: System MUST display per-group sum scores and classification labels on the result page
- **FR-014**: System MUST display per-type probability score, consequence score, risk value, grade, and description on the result page
- **FR-015**: System MUST prominently display НИЙТ ЭРСДЭЛ, НИЙТ ЗЭРЭГЛЭЛ, Mongolian description, and ДААТГАХ ЭСЭХ on the result page
- **FR-016**: System MUST apply color-coding to risk grades: green tones for AAA–A, yellow tones for BBB–B, orange tones for CCC–C, red tones for DDD–D
- **FR-017**: When STDEV cannot be computed (single group in a type, or single type in assessment), system MUST use 0 as the STDEV value
- **FR-018**: All calculations MUST be performed server-side, consistent with the existing architecture

### Key Entities

- **Group Score**: Represents a single group's calculated result — includes group reference, sum score (integer), and classification label (one of 5 Mongolian terms)
- **Type Score**: Represents a type's aggregated result — includes probability score (decimal), consequence score (decimal), risk value (integer), risk grade (letter code AAA–D), and risk description (Mongolian text)
- **Overall Result**: The final assessment outcome — includes НИЙТ ЭРСДЭЛ (total risk, integer), НИЙТ ЗЭРЭГЛЭЛ (total grade, letter code AAA–D), risk description (Mongolian text), and ДААТГАХ ЭСЭХ (insurance decision, "Даатгана" or "Даатгахгүй")

## Assumptions

- The STDEV function used is **sample standard deviation** (STDEV.S / divide by N-1), matching Excel's default `STDEV()` function. When N=1 (single group in a type, or single type in assessment), STDEV is 0.
- Group sum scores are expected to range from 0 to 5 based on the current question structure (each question contributes 0 or 1 to the sum). Scores above 5 are treated as "Аюултай".
- The new scoring model applies only to **new assessments** going forward. Existing completed assessments retain their original percentage-based and LOW/MEDIUM/HIGH results; no retroactive recalculation is performed.
- Rounding of all risk values (per-type and overall) uses standard mathematical rounding (0.5 rounds up).
- The ДААТГАХ ЭСЭХ threshold uses strict greater-than (>16), meaning НИЙТ ЭРСДЭЛ of exactly 16 results in "Даатгана".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of group scores produce the correct Mongolian classification label for all possible sum score values (0 through 5+)
- **SC-002**: Probability and consequence scores for each type match the defined formulas (AVERAGE + 0.618 × STDEV) to within 0.01 precision
- **SC-003**: Per-type risk grade and description match the grade lookup table for all possible risk values (1 through 25)
- **SC-004**: НИЙТ ЭРСДЭЛ matches the formula AVERAGE(type risks) + 0.618 × STDEV(type risks), rounded to integer
- **SC-005**: НИЙТ ЗЭРЭГЛЭЛ and ДААТГАХ ЭСЭХ are correctly derived from НИЙТ ЭРСДЭЛ
- **SC-006**: Users can view the complete risk breakdown (group classifications, type scores, type grades, overall risk, overall grade, insurance decision) on the result page within 3 seconds of page load
- **SC-007**: All result page elements display correctly in Mongolian Cyrillic with appropriate color-coding by grade level
