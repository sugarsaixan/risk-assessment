# Odoo 15 ERP — Admin API Integration Guide

This guide covers how to call the Risk Assessment Admin API from Odoo 15 to create assessments, query results, and manage the assessment lifecycle.

## Prerequisites

- Risk Assessment backend running (e.g. `http://localhost:8000`)
- A valid API key (stored in the `api_keys` table)
- At least one active questionnaire type with questions configured

## Authentication

All Admin API requests require the `X-API-Key` header.

```python
HEADERS = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json",
}
```

In Odoo 15, store the API key and base URL as system parameters:

```python
# In Odoo: Settings → Technical → Parameters → System Parameters
# key: risk_assessment.api_url     value: http://localhost:8000
# key: risk_assessment.api_key     value: your-api-key-here
```

Access them in code:

```python
api_url = self.env["ir.config_parameter"].sudo().get_param("risk_assessment.api_url")
api_key = self.env["ir.config_parameter"].sudo().get_param("risk_assessment.api_key")
```

---

## 1. Create Assessment

**`POST /admin/assessments`**

Creates an assessment with inline respondent data and optional employee info. The system creates or matches the respondent automatically.

### Request Body

```json
{
  "respondent": {
    "odoo_id": "res.partner_42",
    "name": "Монгол Банк ХХК",
    "kind": "ORG",
    "registration_no": "1234567"
  },
  "employee_id": "hr.employee_15",
  "employee_name": "Батболд Д.",
  "selected_type_ids": ["<questionnaire-type-uuid>"],
  "expires_in_days": 30
}
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `respondent.odoo_id` | string (max 100) | Yes | Unique respondent ID from Odoo. Use `res.partner_<id>` or the Odoo XML ID. |
| `respondent.name` | string (1-300) | Yes | Respondent display name |
| `respondent.kind` | `"ORG"` or `"PERSON"` | Yes | Respondent type |
| `respondent.registration_no` | string (max 50) | ORG: Yes, PERSON: No | Organization registration number |
| `employee_id` | string (max 100) | No | Odoo employee who initiated this assessment, e.g. `hr.employee_<id>` |
| `employee_name` | string (max 300) | No | Display name of the employee |
| `selected_type_ids` | UUID[] (min 1) | Yes | Questionnaire type IDs to include |
| `expires_in_days` | int (1-365) | No | Link expiry in days (default: 30) |

### Response (201)

```json
{
  "id": "a1b2c3d4-...",
  "respondent_id": "e5f6a7b8-...",
  "url": "https://app.example.com/a/token123abc",
  "expires_at": "2026-02-27T00:00:00Z"
}
```

- `id` — assessment UUID (use this to query results later)
- `respondent_id` — internal UUID of the created/matched respondent
- `url` — one-time link to share with the respondent

### Odoo 15 Python Example

```python
import json
import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RiskAssessmentMixin(models.AbstractModel):
    _name = "risk.assessment.mixin"
    _description = "Risk Assessment API Client"

    def _get_api_config(self):
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "url": ICP.get_param("risk_assessment.api_url", "http://localhost:8000"),
            "key": ICP.get_param("risk_assessment.api_key", ""),
        }

    def _api_headers(self):
        config = self._get_api_config()
        return {
            "X-API-Key": config["key"],
            "Content-Type": "application/json",
        }

    def _api_url(self, path):
        config = self._get_api_config()
        return f"{config['url']}{path}"


class ResPartner(models.Model):
    _inherit = "res.partner"

    risk_assessment_url = fields.Char(
        string="Latest Assessment Link",
        readonly=True,
    )
    risk_assessment_id = fields.Char(
        string="Latest Assessment ID",
        readonly=True,
    )

    def action_create_risk_assessment(self):
        """Create a risk assessment for this partner."""
        self.ensure_one()
        mixin = self.env["risk.assessment.mixin"]

        # Build respondent data from partner
        respondent = {
            "odoo_id": f"res.partner_{self.id}",
            "name": self.name,
            "kind": "ORG" if self.is_company else "PERSON",
        }
        if self.is_company and self.company_registry:
            respondent["registration_no"] = self.company_registry

        # Get current employee
        employee = self.env.user.employee_id
        payload = {
            "respondent": respondent,
            "selected_type_ids": self._get_questionnaire_type_ids(),
            "expires_in_days": 30,
        }
        if employee:
            payload["employee_id"] = f"hr.employee_{employee.id}"
            payload["employee_name"] = employee.name

        try:
            resp = requests.post(
                mixin._api_url("/admin/assessments"),
                headers=mixin._api_headers(),
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise UserError("Risk Assessment серверт холбогдож чадсангүй.")
        except requests.exceptions.HTTPError as e:
            detail = e.response.json().get("detail", str(e))
            raise UserError(f"Алдаа: {detail}")

        data = resp.json()
        self.write({
            "risk_assessment_url": data["url"],
            "risk_assessment_id": data["id"],
        })

        return {
            "type": "ir.actions.act_url",
            "url": data["url"],
            "target": "new",
        }

    def _get_questionnaire_type_ids(self):
        """Return questionnaire type UUIDs. Override or configure as needed."""
        ICP = self.env["ir.config_parameter"].sudo()
        ids_str = ICP.get_param("risk_assessment.type_ids", "")
        if not ids_str:
            raise UserError(
                "risk_assessment.type_ids системийн параметр тохируулаагүй байна."
            )
        return [t.strip() for t in ids_str.split(",") if t.strip()]
```

---

## 2. List Assessments

**`GET /admin/assessments`**

### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `page` | int (default 1) | Page number |
| `page_size` | int (default 20, max 100) | Items per page |
| `odoo_id` | string | Filter by respondent Odoo ID (e.g. `res.partner_42`) |
| `employee_id` | string | Filter by employee who created the assessment |
| `respondent_id` | UUID | Filter by internal respondent UUID |
| `status` | `PENDING` / `COMPLETED` / `EXPIRED` | Filter by status |

### Examples

```
GET /admin/assessments?odoo_id=res.partner_42
GET /admin/assessments?employee_id=hr.employee_15
GET /admin/assessments?odoo_id=res.partner_42&status=COMPLETED
GET /admin/assessments?employee_id=hr.employee_15&status=PENDING&page=1&page_size=10
```

### Response (200)

```json
{
  "items": [
    {
      "id": "a1b2c3d4-...",
      "respondent_id": "e5f6a7b8-...",
      "respondent_odoo_id": "res.partner_42",
      "employee_id": "hr.employee_15",
      "employee_name": "Батболд Д.",
      "selected_type_ids": ["type-uuid"],
      "expires_at": "2026-02-27T00:00:00Z",
      "status": "COMPLETED",
      "completed_at": "2026-01-30T14:22:00Z",
      "created_at": "2026-01-28T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### Odoo 15 Python Example

```python
def action_view_assessments(self):
    """Fetch assessments for this partner from Risk Assessment API."""
    self.ensure_one()
    mixin = self.env["risk.assessment.mixin"]

    resp = requests.get(
        mixin._api_url("/admin/assessments"),
        headers=mixin._api_headers(),
        params={
            "odoo_id": f"res.partner_{self.id}",
            "page_size": 100,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # data["items"] contains the list of assessments
    # data["total"] is the total count
    return data
```

---

## 3. Get Single Assessment

**`GET /admin/assessments/{assessment_id}`**

### Response (200)

Same schema as list items above (single object, not paginated).

### Odoo 15 Python Example

```python
def _get_assessment(self, assessment_id):
    mixin = self.env["risk.assessment.mixin"]
    resp = requests.get(
        mixin._api_url(f"/admin/assessments/{assessment_id}"),
        headers=mixin._api_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
```

---

## 4. Get Assessment Results

**`GET /admin/assessments/{assessment_id}/results?breakdown=true`**

Returns scores, risk ratings, and optionally per-question answer breakdown.

| Parameter | Type | Description |
|---|---|---|
| `breakdown` | bool (default false) | Include individual answer details |

### Odoo 15 Python Example

```python
def action_view_results(self):
    """Fetch assessment results."""
    self.ensure_one()
    if not self.risk_assessment_id:
        raise UserError("Үнэлгээ үүсгээгүй байна.")

    mixin = self.env["risk.assessment.mixin"]
    resp = requests.get(
        mixin._api_url(
            f"/admin/assessments/{self.risk_assessment_id}/results"
        ),
        headers=mixin._api_headers(),
        params={"breakdown": "true"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
```

---

## 5. Questionnaire Types (Read-Only from Odoo)

Questionnaire types are managed via the Admin API directly (not through Odoo). Odoo only needs the type UUIDs to pass in `selected_type_ids`.

**`GET /admin/types`** — list all questionnaire types.

```python
def _fetch_questionnaire_types(self):
    """Fetch available questionnaire types for selection UI."""
    mixin = self.env["risk.assessment.mixin"]
    resp = requests.get(
        mixin._api_url("/admin/types"),
        headers=mixin._api_headers(),
        params={"page_size": 100},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["items"]
    # Each item: {"id": "uuid", "name": "ГАЛЫН АЮУЛГҮЙ БАЙДАЛ", ...}
```

---

## Error Handling

All errors return JSON with a `detail` field.

| HTTP Code | Meaning | Example `detail` |
|---|---|---|
| 400 | Validation error | `"registration_no is required for ORG respondents"` |
| 400 | Invalid types | `"Invalid or inactive questionnaire type IDs: [uuid1]"` |
| 400 | No questions | `"Selected questionnaire types have no active questions"` |
| 401 | Bad/missing API key | — |
| 404 | Not found | `"Assessment not found"` |
| 422 | Request body parse error | Pydantic validation details |

### Recommended Odoo Error Handling

```python
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
except requests.exceptions.ConnectionError:
    raise UserError("Эрсдэлийн үнэлгээний серверт холбогдож чадсангүй.")
except requests.exceptions.Timeout:
    raise UserError("Серверийн хариу хүлээх хугацаа дууссан.")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        raise UserError("API түлхүүр буруу байна.")
    detail = e.response.json().get("detail", "Тодорхойгүй алдаа")
    raise UserError(f"Алдаа: {detail}")
```

---

## Respondent Matching Logic

When creating an assessment, the system resolves the respondent in this order:

1. **By `odoo_id`** — if a respondent with this `odoo_id` exists, update its `name` and `registration_no` to the latest values and use it
2. **By `kind` + `registration_no`** (legacy linking) — if no `odoo_id` match but a respondent with matching `kind` and `registration_no` exists, link it to this `odoo_id` and use it
3. **Create new** — if no match found, create a new respondent with the provided data

This means:
- First request for a partner creates the respondent
- Subsequent requests reuse and update the same respondent
- Pre-existing respondents (created before Odoo integration) get linked automatically if `kind` + `registration_no` match

---

## Odoo ID Convention

Use a consistent format for `odoo_id` and `employee_id`:

```
odoo_id:     "res.partner_<partner.id>"     e.g. "res.partner_42"
employee_id: "hr.employee_<employee.id>"    e.g. "hr.employee_15"
```

These are strings — the Risk Assessment system does not parse them, only stores and matches them.

---

## System Parameters Summary

| Key | Example Value | Description |
|---|---|---|
| `risk_assessment.api_url` | `http://localhost:8000` | Backend base URL |
| `risk_assessment.api_key` | `sk-abc123...` | Admin API key |
| `risk_assessment.type_ids` | `uuid1,uuid2` | Comma-separated questionnaire type UUIDs |

---

## Typical Workflow

```
Odoo                              Risk Assessment API
 │                                       │
 │  POST /admin/assessments              │
 │  (respondent + employee + types)      │
 │ ─────────────────────────────────────>│
 │                                       │ upsert respondent
 │                                       │ create assessment
 │  { id, respondent_id, url, expires }  │
 │ <─────────────────────────────────────│
 │                                       │
 │  Share URL with respondent            │
 │                                       │
 │         ... respondent fills form ... │
 │                                       │
 │  GET /admin/assessments?odoo_id=X     │
 │ ─────────────────────────────────────>│
 │  { items: [...], status: COMPLETED }  │
 │ <─────────────────────────────────────│
 │                                       │
 │  GET /admin/assessments/{id}/results  │
 │ ─────────────────────────────────────>│
 │  { scores, risk_ratings, breakdown }  │
 │ <─────────────────────────────────────│
```
