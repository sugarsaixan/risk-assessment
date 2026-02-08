# Research: 006-risk-score-calculation

**Date**: 2026-02-08
**Feature**: Risk Score Calculation & Grading

## R-001: Sample Standard Deviation Implementation

**Decision**: Use Python's `statistics.stdev()` for sample STDEV (N-1 divisor), with a guard for N≤1 returning 0.

**Rationale**: Python's `statistics.stdev()` implements sample standard deviation (N-1 divisor), matching Excel's `STDEV()` function as specified. For N=1 it raises `StatisticsError`, so we guard with an N≤1 check returning 0.

**Alternatives considered**:
- `statistics.pstdev()` — population STDEV (N divisor), rejected per clarification
- `numpy.std(ddof=1)` — adds heavy dependency for a simple calculation
- Manual formula `sqrt(sum((x-mean)^2) / (n-1))` — reinvents the wheel, `statistics` module is stdlib

## R-002: Scoring Model Migration Strategy

**Decision**: Add new fields to the existing `AssessmentScore` model and response schemas. Existing records keep NULL for new fields. New assessments populate new fields. Old percentage/risk_rating fields remain but are deprecated for new assessments.

**Rationale**: The user specified no retroactive recalculation. Adding nullable columns to the existing table is the simplest migration path. The existing `AssessmentScore` model already has `type_id` and `group_id` for hierarchical storage. We add new columns for the new scoring model (classification_label, probability_score, consequence_score, risk_value, risk_grade, risk_description, insurance_decision).

**Alternatives considered**:
- New separate table for new scores — rejected: adds JOIN complexity and duplicates the type_id/group_id/assessment_id structure
- Replacing old columns — rejected: breaks existing data integrity

## R-003: Grade Lookup Table Implementation

**Decision**: Implement as a pure function using a sorted list of (threshold, grade, description) tuples, iterated to find the first matching range.

**Rationale**: The grade table has 12 entries with non-uniform ranges. A simple linear scan over sorted thresholds is clear, testable, and fast (max 12 comparisons). No database storage needed — the grade table is a fixed business rule.

**Alternatives considered**:
- Database-stored grade table — rejected: overengineered for a static 12-row lookup
- Dictionary with explicit key ranges — rejected: verbose, harder to maintain
- if/elif chain — rejected: error-prone with range boundaries

## R-004: Frontend Display Approach

**Decision**: Extend existing `TypeScoreCard` and `OverallScoreCard` components with new fields. Add new grade badge and insurance decision components. Keep existing component structure.

**Rationale**: The existing components already handle the hierarchical display (overall → types → groups). Extending them with new fields (grade, risk value, classification label) is less disruptive than replacing them. Color-coding logic already exists for LOW/MEDIUM/HIGH — we remap it to the AAA–D grade system.

**Alternatives considered**:
- New standalone result page — rejected: duplicates navigation, routing, and data fetching logic
- Separate components per new field — rejected: over-fragmented for a data display change

## R-005: Rounding Strategy

**Decision**: Use Python's built-in `round()` for rounding risk values to the nearest integer.

**Rationale**: Python's `round()` uses banker's rounding (round half to even), but for the risk value domain (products of scores ≥1), the difference from "round half up" is negligible — it only affects exact .5 values. The spec says "standard mathematical rounding (0.5 rounds up)", so we use `math.floor(x + 0.5)` or `int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))` for strict compliance.

**Alternatives considered**:
- Python `round()` — uses banker's rounding, deviates from spec at .5 boundaries
- `math.ceil` — always rounds up, not correct
- Custom rounding — unnecessary complexity for a well-defined need; `Decimal` quantize handles it cleanly
