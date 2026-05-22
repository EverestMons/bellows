# QA Step Detection Mechanism — End-to-End Characterization

**Date:** 2026-05-22
**Plan:** diagnostic-qa-step-detection-audit-2026-05-22
**Step:** 1
**Status:** Complete

---

## Gate Function

- **Name:** `_gate_is_qa_step`
- **File:** `gates.py`
- **Line range:** 543–549

```python
def _gate_is_qa_step(plan_text, step_number):
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text, re.MULTILINE)
    if match:
        return "qa" in match.group(0).lower()
    return False
```

## Data Source

The gate reads `plan_text` (the full plan file content) and `step_number` (integer). It does **not** read:
- The plan header (no call to `_parse_plan_header()` output)
- The agent receipt or role name from the step body
- Any external specialist file or role registry
- Any `qa_steps` field (does not exist)

The sole data source is the `## STEP N` header line itself, matched via regex `^## STEP {step_number}\b[^\n]*` against the plan text (after stripping fenced code blocks).

## Classification Logic

**Verbatim logic:** `return "qa" in match.group(0).lower()`

This is a case-insensitive substring check for the literal two-character sequence `qa` anywhere in the matched `## STEP N ...` header line. No regex, no keyword set, no token boundary matching. Examples:

| Header line | `"qa" in ...lower()` | Result |
|---|---|---|
| `## STEP 2 — BELLOWS QA` | `"qa" in "## step 2 — bellows qa"` | `True` |
| `## STEP 2 — Invoice QA Analyst` | `"qa" in "## step 2 — invoice qa analyst"` | `True` |
| `## STEP 1 — Invoice Security & Testing Analyst` | `"qa" in "## step 1 — invoice security & testing analyst"` | `False` |
| `## STEP 3 — QA` | `"qa" in "## step 3 — qa"` | `True` |
| `## STEP 1 — Bellows Developer` | `"qa" in "## step 1 — bellows developer"` | `False` |

## Call Site

`gates.py:178` inside `check()`:

```python
# Gate 6: QA step detection (informational)
is_qa_step = _gate_is_qa_step(plan_text, step_number)
```

The `check()` function receives `plan_text` and `step_number` from `bellows.py:487` (first step) and `bellows.py:577` (subsequent steps in the while loop).

## is_qa_step Consumers (Enumerated)

### In gates.py

1. **`_gate_rule_20_self_check` (line 180, called at 414):** Early-returns with no failure if `is_qa_step` is `False` (line 416–417). When `True`, verifies QA deposits contain Rule 20 self-check banner with PASSED status.

2. **`_gate_rule_22_verification` (line 182, called at 468):** Performs (a) deposit-exists check for all steps. The (c) verification-table and (d) hedging-keyword checks are gated behind `if not is_qa_step: return` at line 485–486 — only run for QA steps.

3. **`check()` return dict (line 195):** `"is_qa_step": is_qa_step` — passed through to all consumers of the gate result.

### In bellows.py

4. **Intermediate-step pause logic (line 501–504):** `gate_result["is_qa_step"]` triggers `qa_checkpoint` pause reason — when True, the plan pauses for CEO verdict regardless of other conditions.

5. **`_pause_reason` assignment (line 511–512):** Sets `_pause_reason = "qa_checkpoint"` when `is_qa_step` is True.

6. **Final-step pause logic (line 589–593):** Same pattern as intermediate — `gate_result["is_qa_step"]` is one of the conditions that forces a verdict-pending pause on the final step.

7. **Final-step `_pause_reason` (line 600–601):** Sets `_pause_reason = "qa_checkpoint"`.

8. **`header_says_pause` (line 307–318):** Receives `is_qa_step` parameter; returns `True` when `pv == "after_qa_step"` and `is_qa_step` is True.

### In verdict.py

9. **`_build_verification_results_table` (line 122):** `is_qa = gate_result.get("is_qa_step", False)` — used to populate the `qa_step_detection` row in the Verification Results table.

10. **qa_step_detection row (line 128–130):** Emits `PASS | QA step detected (step N of M)` or `PASS | Not a QA step`.

11. **rule_20_self_check row (line 136–143):** When no failure, shows `Banner byte-exact, PASSED line present` if `is_qa`, else `N/A (not a QA step)`.

12. **rule_22_verification row (line 144–150):** When no failure, shows `Deposits present, verification table clean, no hedging` if `is_qa`, else `Plan-declared deposits present on disk`.

## Rule 20 Interaction

When `is_qa_step` is `False`:

1. `_gate_rule_20_self_check` (line 416–417) returns immediately — no failure appended, no check performed.
2. The verification table shows `rule_20_self_check | PASS | N/A (not a QA step)`.
3. The `PASS` status means the Planner's Rule 25 routing at the "mechanized check routing" section treats the gate as clean.
4. Rule 25's post-verdict-enrichment logic says: when BOTH `rule_22_verification: PASS` AND `rule_20_self_check: PASS`, the Planner performs substance check (b) ONLY — does NOT re-run mechanical checks.

The critical interaction: Rule 25's (b)-only path **actively suppresses** the Planner's manual Rule 20 verification. If `is_qa_step` is falsely `False`, the Rule 20 gate produces a vacuous `PASS | N/A`, Rule 25 sees both gates clean, and routes the Planner to substance-only review. The Planner's prior fallback behavior (manually checking Rule 20 substance when the gate said N/A) is no longer reliable because Rule 25 instructs the Planner to skip mechanical checks when gates pass.

## Failure Mode Summary

A real QA step gets classified as not-QA when the specialist role name in the `## STEP N` header does not contain the substring "qa" (case-insensitive). The canonical example is "Invoice Security & Testing Analyst" — the invoice-pulse project's QA specialist — which contains "testing" but not "qa". When this misclassification occurs, three things are suppressed: (1) the `rule_20_self_check` gate is skipped entirely, producing a vacuous `PASS | N/A` instead of verifying the Rule 20 banner and PASSED line exist in the QA deposit; (2) the `rule_22_verification` gate's QA-specific checks (c) verification-table greenness and (d) hedging-keyword absence are skipped, leaving only (a) deposit-exists; and (3) the `qa_checkpoint` auto-pause does not fire, so the step proceeds based on other pause conditions rather than forcing CEO review of QA output. The Planner historically caught these leaks via manual Rule 20 verification, but PLANNER_TEMPLATE v4.48+ Rule 25's mechanized-check routing now instructs the Planner to skip mechanical checks when both gates show PASS — making the vacuous N/A pass actively harmful rather than merely decorative.

---

### Output Receipt

**Status:** Complete
**Files Deposited:**
- `knowledge/research/qa-step-detection-mechanism-2026-05-22.md`
