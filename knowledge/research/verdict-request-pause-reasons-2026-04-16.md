# Bellows — Verdict Request Pause Reasons Audit
**Date:** 2026-04-16 | **Diagnostic:** diagnostic-verdict-request-pause-reasons-2026-04-16.md

## Question
What are all the conditions in bellows.py that cause a verdict request to be posted (i.e., a plan to pause for CEO verdict)?

---

## Findings

There are two pause-check sites in `run_plan`. Both share the same four conditions; the final-step site adds a fifth.

### Mid-plan pause check (`bellows.py:200–203`)
Fires when `current_step < total_steps`. Posts a verdict request if **any** of:

| # | Condition | Code |
|---|-----------|------|
| 1 | Gate failure | `not gate_result["passed"]` |
| 2 | QA checkpoint step | `gate_result["is_qa_step"]` |
| 3 | Agent-requested verdict | `gate_result.get("verdict_requested", {}).get("requested", False)` |
| 4 | Header `pause_for_verdict` fires | `header_says_pause(header, current_step, total_steps, is_qa_step)` |

### Final-step pause check (`bellows.py:247–251`)
Fires after the last step completes. Same four conditions plus one more:

| # | Condition | Code |
|---|-----------|------|
| 1–4 | Same as mid-plan | (see above) |
| 5 | Auto-close disabled | `not effective_auto_close` |

---

## `header_says_pause` — four return branches (`bellows.py:123–132`)

```python
def header_says_pause(header, current_step, total_steps, is_qa_step):
    pv = header.get("pause_for_verdict", "")
    if pv == "always":       return True            # every step pauses
    if pv == "after_step_1": return current_step == 1  # pause after step 1 only
    if pv == "after_qa_step": return is_qa_step     # pause whenever gate says QA
    return False                                     # no header pause
```

---

## `effective_auto_close` — how the fifth condition is set (`bellows.py:196`)

```python
effective_auto_close = header.get("auto_close", "true" if not is_diagnostic else "false").lower() == "true"
```

- **Diagnostics** (`diagnostic-` filename prefix): default `"false"` → final-step always pauses unless header sets `auto_close: true`.
- **Non-diagnostic plans**: default `"true"` → final-step auto-closes unless header sets `auto_close: false` or another condition fires.

---

## Complete Pause-Reason Taxonomy

| Reason | When | Condition |
|--------|------|-----------|
| Gate failure | Mid or final step | One or more gates (scope_check, commit_check, …) failed |
| QA checkpoint | Mid or final step | Step is tagged as QA in the plan |
| Agent-requested verdict | Mid or final step | Agent deposited a verdict-request file during execution |
| Header `pause_for_verdict` | Mid or final step | `always`, `after_step_1` (on step 1), or `after_qa_step` (on QA step) |
| Auto-close disabled | Final step only | `effective_auto_close` is False (diagnostics default; or `auto_close: false` in header) |

---

## Q3 — Recommended Threading Mechanism

**Recommendation: Option B — add an explicit `pause_reason` parameter to `post_verdict_request`.**

### Current signature (`verdict.py:26`)
```python
def post_verdict_request(plan_path, step_number, log_path, gate_result, planner_py_decision=None):
```

### Proposed signature
```python
def post_verdict_request(plan_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None):
```

### Justification

**Call-site ergonomics (2 sites, both in `bellows.py`):** Each call site sits directly inside an `if`-condition that already knows exactly which of the five conditions fired. Adding `pause_reason=...` to the call is natural — 1 extra argument per site, no intermediate mutation needed.

**Backward compatibility:** There is no external caller of `post_verdict_request`. Only `bellows.py` calls it (confirmed by grep). Adding the parameter as optional with a safe default (`auto_close_disabled`) means zero breakage. The existing `planner_py_decision` optional stays in place.

**Template clarity:** An explicit `pause_reason` string lets `verdict.py` branch cleanly: when `pause_reason == "gate_failure"` render the current "Gate Failures" section (list of failed gate names); for all other reasons render a `## Pause Reason` section with a plain-English label instead of the misleading `- None (QA checkpoint — all gates passed)` fallback.

### Why not Option A (add field to `gate_result`)?
`gate_result` is the output of `gates.check()` — it represents what the gates found, not why the dispatcher decided to pause. Injecting a dispatcher concept (`pause_reason`) into that dict crosses a semantic boundary. The two concerns are better kept separate.

### Proposed `pause_reason` enum values

| Condition | `pause_reason` value |
|-----------|----------------------|
| Gate failure | `gate_failure` |
| QA checkpoint step | `qa_checkpoint` |
| Agent-requested verdict | `agent_verdict_request` |
| Header `pause_for_verdict` | `header_pause` |
| Auto-close disabled | `auto_close_disabled` |

---

## Q4 — Template Design Sketch

Below are 15-line sketches for each pause condition. The key difference is the section that replaces or supplements "Gate Failures" for non-gate pauses.

### Condition 1 — Gate failure (`pause_reason=gate_failure`)
```
# Verdict Request

**Plan:** /path/to/plan.md
**Step:** 2
**Pause Reason:** Gate failure

## Gate Failures

- **scope_check**: Modified file outside declared scope
- **commit_check**: Commit hash not found

## Files Changed

- src/bellows.py
```

### Condition 2 — QA checkpoint (`pause_reason=qa_checkpoint`)
```
# Verdict Request

**Plan:** /path/to/plan.md
**Step:** 3
**Pause Reason:** QA checkpoint

## Pause Reason

This step is a QA checkpoint. All gates passed — CEO review requested before proceeding.

## Files Changed

- tests/test_gates.py
```

### Condition 3 — Agent-requested verdict (`pause_reason=agent_verdict_request`)
```
# Verdict Request

**Plan:** /path/to/plan.md
**Step:** 2
**Pause Reason:** Agent verdict request

## Pause Reason

The agent deposited a verdict-request file during execution and is requesting
CEO guidance before proceeding to the next step.

## Files Changed

- knowledge/research/findings.md
```

### Condition 4 — Header `pause_for_verdict` (`pause_reason=header_pause`)
```
# Verdict Request

**Plan:** /path/to/plan.md
**Step:** 1
**Pause Reason:** Header pause (pause_for_verdict: after_step_1)

## Pause Reason

The plan header specifies `pause_for_verdict: after_step_1`. Step 1 is complete;
CEO review is required before step 2 begins.

## Files Changed

- knowledge/decisions/plan.md
```

### Condition 5 — Auto-close disabled (`pause_reason=auto_close_disabled`)
```
# Verdict Request

**Plan:** /path/to/diagnostic-plan.md
**Step:** 1  (final step)
**Pause Reason:** Auto-close disabled

## Pause Reason

Plan completed. Auto-close is disabled for this plan (diagnostic default or
`auto_close: false` in header). CEO review required before closing.

## Files Changed

```

---

## Q5 — Caveats and Gotchas

### (a) `planner_py_decision` legacy parameter

`post_verdict_request` accepts `planner_py_decision=None` as an optional keyword argument (`verdict.py:26`). Neither call site in `bellows.py` ever passes it — it is effectively dead code. It renders a `## Planner.py Decision (legacy)` section when truthy (`verdict.py:54–55`). **This does not complicate the fix.** It is already optional and additive; inserting `pause_reason` before it in the signature (or leaving it in place as a trailing kwarg) requires no logic change.

### (b) Tests asserting on the fallback string

No test currently asserts on the literal string `"None (QA checkpoint — all gates passed)"`. Confirmed by grep across `tests/`. The single `test_verdict.py` test (`test_post_verdict_request_creates_file`) uses a populated `failures` list and asserts on `"receipt_status"`, `"Blocked"`, and `"gates.py"` — none of which touch the fallback branch. **Changing the fallback string will not break any test.**

### (c) In-flight verdict requests in `verdicts/pending/`

Two files are currently pending:

| File | Triggered by | Current text |
|------|-------------|--------------|
| `verdict-request-bellows-phase8-1-validation-smoke-2026-04-16-step-1.md` | Condition 5 (`not effective_auto_close`, diagnostic) | `- None (QA checkpoint — all gates passed)` |
| `verdict-request-verdict-request-pause-reasons-2026-04-16-step-1.md` | Condition 5 (`not effective_auto_close`, diagnostic) | `- None (QA checkpoint — all gates passed)` |

Both were written to disk before the fix. **These files will not be affected by the fix** — they are static files already on disk. Future verdict requests for these plans (if re-run) would render with the corrected template. No action needed on the pending files.

---

## Output Receipt
- **Status:** Complete (Q3/Q4/Q5 appended by completion diagnostic 2026-04-16)
- **Files read:** `bellows.py` (lines 119–284), `verdict.py` (full), `tests/test_verdict.py`, `tests/test_bellows.py`, `verdicts/pending/` (2 files)
- **Deposit:** `knowledge/research/verdict-request-pause-reasons-2026-04-16.md`
- **Files Created or Modified (Code):** `[]`
- **Decisions Made:** Option B — add explicit `pause_reason` parameter to `post_verdict_request`
- **Flags for CEO:** No test changes needed; no in-flight pending file migration needed; `planner_py_decision` is dead legacy and can be cleaned up opportunistically
- **Fixes made:** None (diagnostic — investigation only)
