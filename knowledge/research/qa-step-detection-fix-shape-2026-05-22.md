# QA Step Detection Fix Shape — Proposed `qa_steps` Header Field

**Date:** 2026-05-22
**Plan:** diagnostic-qa-step-detection-audit-2026-05-22
**Step:** 3
**Status:** Complete

---

## 1. Header Field Placement

**Proposed field:** `qa_steps`

**Position in header line:** After `Execution:` and before `pause_for_verdict:`. The field is logically grouped with the execution topology (which steps are QA is a property of the execution plan, not of the dispatch mechanics).

**Canonical value format:** Comma-separated integers. Example: `qa_steps: 2` or `qa_steps: 1,3`.

**Justification against existing conventions:**
- Existing header fields use simple scalar values: `Tier: Small`, `Dispatch Mode: bellows`, `pause_for_verdict: after_step_1`, `auto_close: true`.
- The `Execution:` field already names agents per step (`Step 1 (DEV) → Step 2 (QA)`), but this is prose-format display text, not machine-parsed.
- Comma-separated integers are the simplest machine-parseable format that handles multi-QA-step plans (e.g., a 4-step plan with QA at steps 2 and 4) without introducing range syntax complexity.
- Range syntax (`qa_steps: 1-3`) was considered and rejected: ranges require additional parsing logic, are harder to validate, and multi-QA-step plans rarely have contiguous QA steps (typical pattern is `DEV → QA → DEV → QA`, not `QA → QA → QA`).
- Bool-per-step syntax (`qa_steps: false,true,false`) was considered and rejected: it couples the field to total step count (must have exactly N entries for N steps), creates fragile alignment, and is harder to read.

**Population context from Step 2 audit:** The exhaustive plan-header scan found 14 class (b) leaks out of 139 QA steps (10.1% overall leak rate; 61.9% in invoice-pulse alone). Three naming variants leak: "Invoice Security & Testing Analyst" (7 occurrences), "INVOICE_SECURITY_TESTING_ANALYST" (2), "INVOICE SECURITY TESTING ANALYST" (2), "Bellows Security & Testing" (1), and one bare `## STEP 1` header on a standalone QA plan with no role name at all. The `qa_steps` field fixes all five patterns because it is role-name-independent.

**Downstream interaction:** The `pause_for_verdict: after_qa_step` header value (already in use on invoice-pulse plans like `fuel-paste-prompt-cents-as-integer-2026-05-21`) is currently inert when the QA role name lacks "qa" — the pause fires only if `is_qa_step` is True, which the keyword fallback never produces for these plans. Fixing `_gate_is_qa_step` via the `qa_steps` field also restores `after_qa_step` pause semantics for these plans.

**Example header lines:**

Single QA step (most common):
```
**Date:** 2026-05-22 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1
```

Multiple QA steps:
```
**Date:** 2026-05-22 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) → Step 3 (DEV) → Step 4 (QA) | **qa_steps:** 2,4 | **pause_for_verdict:** always
```

No QA steps (diagnostic):
```
**Date:** 2026-05-22 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none (read-only diagnostic) | **Execution:** Step 1 (SA) → Step 2 (SA) → Step 3 (SA) | **pause_for_verdict:** after_step_1
```
(Field omitted — see fallback semantics below.)

## 2. Parse Path

### Header parse change (`_parse_plan_header`)

No change needed to `_parse_plan_header()` itself. The function already extracts arbitrary bold-Markdown fields via regex:
```python
for m in re.finditer(r'\*\*([^:*]+):\*\*\s*([^|]*?)(?:\s*\||$)', header_line):
    key = m.group(1).strip().lower().replace(" ", "_")
    value = m.group(2).strip()
    result[key] = value
```

A header field `**qa_steps:** 2,4` will be parsed as `{"qa_steps": "2,4"}` automatically. The key normalization (`lower().replace(" ", "_")`) handles both `**qa_steps:**` and `**QA Steps:**` (though the former is canonical).

### Gate change (`_gate_is_qa_step`)

Replace the current function (lines 543–549) with:

```python
def _gate_is_qa_step(plan_text, step_number, plan_header=None):
    # Primary: check plan_header for qa_steps field
    if plan_header:
        qa_steps_raw = plan_header.get("qa_steps", "")
        if qa_steps_raw:
            try:
                # Handle YAML list case (e.g., [2, 4]) and string case (e.g., "2,4")
                if isinstance(qa_steps_raw, list):
                    return step_number in [int(x) for x in qa_steps_raw]
                qa_step_numbers = [int(s.strip()) for s in str(qa_steps_raw).split(",") if s.strip()]
                return step_number in qa_step_numbers
            except (ValueError, TypeError):
                logger.warning("qa_steps field malformed: %r — falling back to keyword detection", qa_steps_raw)

    # Fallback: keyword detection on step header (existing behavior)
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text, re.MULTILINE)
    if match:
        return "qa" in match.group(0).lower()
    return False
```

### Call site change (`check()`)

At line 178, pass the already-parsed header:
```python
# Before:
is_qa_step = _gate_is_qa_step(plan_text, step_number)

# After:
is_qa_step = _gate_is_qa_step(plan_text, step_number, plan_header=header)
```

The `header` variable is already available at this point (parsed at line 165).

## 3. Fallback Semantics

When a plan has no `qa_steps` field, the gate falls back to the existing keyword detection behavior (`"qa" in header_line.lower()`). This preserves correctness for:

| Case | Behavior |
|---|---|
| **Legacy plans** (pre-`qa_steps` field) | Keyword fallback fires. Same behavior as today — "BELLOWS QA" detected, "Invoice Security & Testing Analyst" not detected (existing gap). No regression. |
| **`manual_bootstrap` plans** | Keyword fallback fires. Manual plans typically have sparse headers but often include "QA" in step headers. No regression. |
| **Parallel-group plans** | Each sibling plan is parsed independently. A sibling with `qa_steps` uses the primary path; a sibling without falls back to keyword. No interaction between siblings. |
| **Diagnostics** (no QA steps) | No `qa_steps` field → keyword fallback → "qa" not in header → `False`. Correct. |
| **Malformed `qa_steps` value** | Parse fails → `logger.warning` → keyword fallback. Conservative; no silent failure. |

**No WARN on missing field.** Emitting a WARN for every plan without `qa_steps` would flood logs with noise during the transition period and for legitimately non-QA plans (diagnostics, session-wraps). The field's absence is not an error condition — it means "use keyword detection."

## 4. Governance Edit

### Insertion point

The `qa_steps` field should be documented in two places in PLANNER_TEMPLATE.md:

**Place 1: Plan File Structure section** (currently around line 349). The header example line should include the new field:

**Proposed edit — header example:**
```markdown
# [Project] — [Feature/Task Name]
**Date:** YYYY-MM-DD | **Tier:** [tier] | **Dispatch Mode:** [bellows | manual_bootstrap] | **Test Scope:** [targeted | full-suite | both] | **Execution:** Step 1 (AGENT) → Step 2 (AGENT) | **qa_steps:** [comma-separated step numbers] | **pause_for_verdict:** after_step_1
```

**Place 2: New paragraph after the Plan File Structure section**, before the "Step transitions" subsection. This is the definitional paragraph:

**Proposed paragraph wording:**

> **`qa_steps` header field.** Every executable plan with one or more QA steps MUST declare a `qa_steps` field in the plan header listing the step numbers that are QA-gated, as a comma-separated list of integers (e.g., `qa_steps: 2` or `qa_steps: 2,4`). Bellows's `_gate_is_qa_step` reads this field to determine which steps trigger Rule 20 self-check verification, Rule 22 QA-specific checks (c)+(d), and `qa_checkpoint` auto-pause. Without the field, Bellows falls back to keyword detection on the `## STEP N` header line — checking whether the header contains the substring "qa" (case-insensitive). This fallback misclassifies QA steps whose specialist role name does not contain "qa" (e.g., "Invoice Security & Testing Analyst"), causing Rule 20 and Rule 22 QA gates to emit vacuous PASS results and suppressing the Planner's mechanical verification under Rule 25. The `qa_steps` field is the authoritative source; the keyword fallback is a backward-compatibility path for legacy plans. Diagnostic plans and plans with no QA steps omit the field entirely — omission means "no QA steps" when no keyword match is found.

**This paragraph belongs near Rule 26** (Deposits field convention) because both are plan-header field specifications that affect Bellows gate behavior. Specifically, it should be placed after the Plan File Structure section's "Execution map" paragraph and before the "Every agent prompt must include the domain glossary read" paragraph, since it describes a header field (like execution map) rather than a prompt-level instruction (like the glossary read).

**Place 3: Gate 6 description in "The Eight Gates" table** (currently around line 955). The current Gate 6 row reads:

> `| 6 | is_qa_step | Info | Heuristic detection based on the step header containing "QA" (case-insensitive). When true, triggers a qa_checkpoint pause reason even if all blocking gates pass. |`

**Proposed replacement:**

> `| 6 | is_qa_step | Info | QA step detection: reads the plan header's qa_steps field (authoritative, comma-separated step numbers) or falls back to keyword detection on the ## STEP N header line (case-insensitive "qa" substring). When true, triggers qa_checkpoint pause reason, Rule 20 self-check verification, and Rule 22 QA-specific checks. |`

This update reflects the two-tier detection and makes the downstream effects (Rule 20, Rule 22) visible in the gate description.

## 5. Migration Risk Surface

| Risk | Likelihood | Mitigation |
|---|---|---|
| **In-flight plans without the field** | Certain — any plan authored before the governance edit ships will lack `qa_steps`. | Keyword fallback preserves exact current behavior. No regression for in-flight plans. Plans with "QA" in the header continue to be detected. |
| **Plans authored mid-transition by CEO from older template** | Moderate — CEO may copy an older plan as a template. | Keyword fallback covers this. Once the Planner prompt is updated, all new plans include the field. No hard cutover required. |
| **Parallel-group plans where only one sibling has the field** | Low — parallel plans are typically authored together by the same Planner invocation. | Each plan parsed independently. Missing-field sibling uses keyword fallback. No cross-sibling interaction. |
| **Planner writes invalid `qa_steps` value** (e.g., `qa_steps: step 2`) | Low — format is simple and the Planner follows template conventions. | Parse failure caught by try/except → `logger.warning` → keyword fallback. Conservative degradation. |
| **`qa_steps` lists a step that doesn't exist** (e.g., 3-step plan with `qa_steps: 4`) | Low — step numbers are validated by execution flow. | `step_number in qa_step_numbers` returns `False` for step 4 since step 4 never runs. Harmless no-op. |
| **`qa_steps` omitted for a plan where the QA role name contains "qa"** | Common during transition, harmless long-term. | Keyword fallback correctly detects "QA" in the header. The field is additive, not destructive. |
| **`qa_steps` omitted for a plan where the QA role does NOT contain "qa"** | This is the exact failure mode being fixed. | During transition, these plans remain broken (same as today). After the Planner governance edit, new plans always include the field. The transition window is exactly the window between the gates.py code change shipping and the Planner being re-prompted with the updated PLANNER_TEMPLATE. |
| **YAML frontmatter plans** | Rare — most plans use bold-Markdown headers. | `_parse_plan_header` handles YAML frontmatter as Strategy 1 (line 91–100). A YAML field `qa_steps: [2, 4]` would parse as a list, not a string. The proposed code explicitly handles both cases: `isinstance(qa_steps_raw, list)` branch for YAML lists, `str().split(",")` for bold-Markdown strings. Both paths produce correct results. |

## Recommended Next Plan

**Filename:** `executable-qa-steps-header-field-2026-05-2N.md` (date TBD by CEO)

**Expected step structure:**

- **Step 1 — Bellows Developer:** Implement the `qa_steps` field in `gates.py`. Edit `_gate_is_qa_step` to accept `plan_header` kwarg and check `qa_steps` field with keyword fallback (including YAML list handling). Update call site in `check()`. Add unit tests for: (a) `qa_steps: 2` with step 2 → True, step 1 → False; (b) `qa_steps: 1,3` with step 1 → True, step 2 → False; (c) no `qa_steps` field → keyword fallback; (d) malformed `qa_steps` → keyword fallback with warning; (e) YAML list `qa_steps: [2, 4]` → correct detection; (f) bare `## STEP 1` header with `qa_steps: 1` → True (standalone QA plan case).

- **Step 2 — Bellows QA:** Verify the gate change via test execution. Verify the keyword fallback preserves existing behavior for plans without the field. Run full test suite. Deposit QA report with Rule 20 self-check.

**Governance edit (PLANNER_TEMPLATE.md)** should ship as a separate plan or as a parallel step, since it modifies a governance document outside the bellows project tree. Three insertion points: (1) header example in Plan File Structure, (2) new definitional paragraph after "Execution map", (3) Gate 6 table description update. The Planner will automatically pick up the new field on its next prompt load.

---

### Output Receipt

**Status:** Complete
**Files Deposited:**
- `knowledge/research/qa-step-detection-fix-shape-2026-05-22.md`
