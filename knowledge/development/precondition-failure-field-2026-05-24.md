# Precondition-Failure Verdict-Request Field — Dev Log

**Date:** 2026-05-24
**Plan:** `executable-precondition-failure-field-2026-05-24`
**Step:** 1 (DEV)
**BACKLOG item:** #5 (step-counter loop after precondition-failure verdict)

---

## (a) Pre-Edit Verification

**Check (i):** `grep -n 'def post_verdict_request' verdict.py`
```
178:def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None):
```
Result: ✅ one match at line 178.

**Check (ii):** `grep -c 'precondition_failure' verdict.py bellows.py`
```
verdict.py:0
bellows.py:0
```
Result: ✅ zero references exist.

**Check (iii):** `grep -n 'Pause Reason Code' verdict.py`
```
231:        f"**Pause Reason Code:** {pause_reason}\n"
```
Result: ✅ one match at line 231 (plan estimated 2; line 230 has "Pause Reason" without "Code" — plan estimation error, not a state mismatch).

**Check (iv):** `grep -n 'pause_reason_code_from_request' bellows.py`
```
1157:            pause_reason_code_from_request = None
1175:                        pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
1219:                                                      pause_reason_code=pause_reason_code_from_request)
1231:                                                      pause_reason_code=pause_reason_code_from_request)
1240:                                                  pause_reason_code=pause_reason_code_from_request)
```
Result: ✅ 5 matches (plan said ~3; 5 is more).

**Check (v):** `grep -n 'resume_step=step_number + 1' bellows.py`
```
1237:                                self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```
Result: ✅ one match at line 1237.

**Check (vi):** `python3 -c "import bellows; import verdict"` → ✅ clean exit (only urllib3 LibreSSL warning, no import errors).

**Check (vii):** `python3 -m pytest tests/test_bellows.py tests/test_consume_verdicts.py tests/test_verdict.py -q`
```
163 passed, 1 warning in 0.99s
```
Result: ✅ all pass. Pre-existing carry-over failures are in `test_decisions.py` and `test_runner_parser.py`, not in these files.

---

## (b) Edit Sites — Before/After

### Site 1: `verdict.py:178` — Signature

**Before:**
```python
def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None):
```

**After:**
```python
def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None, precondition_failure=False):
```

### Site 2: `verdict.py:232` — Content template

**Before:**
```python
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
```

**After:**
```python
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Precondition Failure:** {'true' if precondition_failure else 'false'}\n"
        f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
```

### Site 3: `bellows.py:443-445` — Worktree-creation failure call (Site 1)

**Before:**
```python
            verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
                                         pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text)
```

**After:**
```python
            # Precondition-failure signal (item #5, 2026-05-24): worktree creation failed → step never ran → consumer must retry, not advance.
            verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
                                         pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text,
                                         precondition_failure=True)
```

### Site 4: `bellows.py:1158-1177` — Parser init + parse line

**Before:**
```python
            pause_reason_code_from_request = None
            if pending_req_file.exists():
```

**After:**
```python
            pause_reason_code_from_request = None
            precondition_failure_from_request = False
            if pending_req_file.exists():
```

And added parser line after the `pause_reason_code` parser:
```python
                    if req_line.startswith("**Precondition Failure:**"):
                        precondition_failure_from_request = req_line.split(":**", 1)[1].strip().lower() == "true"
```

### Site 5: `bellows.py:1240-1248` — Conditional dispatch

**Before:**
```python
                                _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
                                # Dispatch next step
                                self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```

**After:**
```python
                                # Precondition-failure handling (item #5, 2026-05-24): if the prior step never ran due to
                                # a precondition gate failure (e.g., worktree creation), retry the same step rather than advance.
                                if precondition_failure_from_request:
                                    next_step = step_number
                                    _log("EVENT", f"verdict continue — retrying step {step_number} (precondition failure)", slug=slug_for(original_name))
                                else:
                                    next_step = step_number + 1
                                    _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
                                self.handle_new_plan(inprogress_path, resume_step=next_step)
```

---

## (c) New Test Functions

1. **`test_consume_verdict_continue_advances_step_when_precondition_failure_absent`** (`test_consume_verdicts.py`) — Verifies backward-compat: verdict-request WITHOUT `**Precondition Failure:**` field results in `resume_step=step_number + 1` (advance).

2. **`test_consume_verdict_continue_advances_step_when_precondition_failure_false`** (`test_consume_verdicts.py`) — Verifies explicit `**Precondition Failure:** false` results in `resume_step=step_number + 1` (advance).

3. **`test_consume_verdict_continue_retries_step_when_precondition_failure_true`** (`test_consume_verdicts.py`) — Verifies `**Precondition Failure:** true` results in `resume_step=step_number` (retry same step).

4. **`test_post_verdict_request_writes_precondition_failure_field`** (`test_verdict.py`) — Verifies `post_verdict_request` writes `**Precondition Failure:** true` when `precondition_failure=True`, `false` when `precondition_failure=False`, and `false` when defaulted.

---

## (d) Post-Edit Verification (Task F)

```
$ python3 -c "import bellows; import verdict"
# Clean exit (urllib3 LibreSSL warning only)

$ grep -c 'precondition_failure' verdict.py bellows.py
verdict.py:2
bellows.py:4
# Total: 6 (comments use hyphens, not underscores — 6 is correct for underscore matches)

$ grep -n 'Precondition Failure' verdict.py
232:        f"**Precondition Failure:** {'true' if precondition_failure else 'false'}\n"
# Exactly 1 match in content template ✅

$ grep -n 'resume_step=step_number + 1' bellows.py
# ZERO matches — old unconditional advance replaced ✅

$ grep -n 'resume_step=next_step' bellows.py
1248:                                self.handle_new_plan(inprogress_path, resume_step=next_step)
# Exactly 1 match — new conditional dispatch ✅
```

---

## (e) Pytest Summary (Task H)

```
394 collected | 389 passed | 5 failed | 0 skipped | 1 warning

Failed (all pre-existing carry-over):
- tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file
- tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases
- tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives
- tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth
- tests/test_runner_parser.py::test_run_step_timeout
```

All 4 new tests pass. No new failures introduced.

---

## (f) Summary

This change closes BACKLOG item #5 (step-counter loop after precondition-failure verdict), as characterized in the 2026-05-24 daemon-restart-state-divergence diagnostic (Section D: root cause classification, Section F18 Shape E: design recommendation). The root cause was that `_consume_verdicts` at bellows.py:1237 unconditionally advanced `resume_step=step_number + 1` on verdict-continue, regardless of whether the step had actually executed. When the daemon paused on a precondition gate failure (worktree creation failure at bellows.py:434), the step never ran, but the consumer treated it as completed and advanced to the next step. Shape E adds an explicit `**Precondition Failure:**` boolean field to the verdict-request format — the producer (`run_plan` worktree-creation failure path) writes `true`, the consumer (`_consume_verdicts`) reads it and conditionally computes `resume_step`: `step_number` for retry on precondition failure, `step_number + 1` for advance otherwise. All other call sites of `post_verdict_request` retain the default `precondition_failure=False`, preserving backward-compatible advance behavior. Historical verdict-request files lacking the field default to `False` via the parser's initialization, ensuring replay/diagnostic compatibility.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented Shape E (Precondition Failure field) across 5 edit sites in `verdict.py` and `bellows.py`. Added 4 regression tests covering backward-compat (field absent), explicit false, explicit true (retry), and producer-side field writing. All tests pass; no regressions.

### Files Deposited
- `knowledge/development/precondition-failure-field-2026-05-24.md` — this dev log

### Files Created or Modified (Code)
- `verdict.py` — added `precondition_failure=False` parameter to `post_verdict_request` signature; added `**Precondition Failure:**` field to content template
- `bellows.py` — passed `precondition_failure=True` at worktree-creation failure call site; added parser for `**Precondition Failure:**` field in `_consume_verdicts`; replaced unconditional `resume_step=step_number + 1` with conditional dispatch based on `precondition_failure_from_request`
- `tests/test_consume_verdicts.py` — added 3 regression tests for consumer-side precondition-failure handling
- `tests/test_verdict.py` — added 1 regression test for producer-side field writing

### Decisions Made
- Accepted 6 `precondition_failure` substring matches (vs plan estimate of 7) — comments use hyphens not underscores; structural correctness confirmed via targeted grep checks
- Accepted 1 match on check (iii) vs plan estimate of 2 — "Pause Reason" (line 230) does not contain "Code" substring; code structure correct for edits

### Flags for CEO
- None

### Flags for Next Step
- None
