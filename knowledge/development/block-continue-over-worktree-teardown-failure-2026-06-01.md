# Block Continue Over Uncleared Worktree-Teardown Failure — Dev Log

**Date:** 2026-06-01
**Plan:** `executable-block-continue-over-worktree-teardown-failure-2026-06-01.md`
**Step:** 1 (DEV)
**Blueprint:** `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md` — Gap 1(b)

---

## Guard Placement

The guard is inserted at the TOP of the `if v == "continue":` block in `_consume_verdicts` (`bellows.py`), before the final/non-final split (`step_number >= total_steps_c`). This ensures it covers both inter-step resume AND final-step continue-to-done.

### Before (lines 1338–1341):

```python
gate_result = gate_result_from_request or {"failures": [], "files_changed": []}

if v == "continue":
    is_diag = original_name.startswith("diagnostic-")
```

### After (lines 1338–1359):

```python
gate_result = gate_result_from_request or {"failures": [], "files_changed": []}

if v == "continue":
    # Guard: block continue when prior step's worktree teardown failed (Gap 1b).
    # An uncleared worktree_teardown failure means Step N's commits were never
    # cherry-picked to main — advancing would orphan them. Route to halted-
    # for manual R2 recovery instead of silently advancing.
    if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", [])):
        _log("ERROR", ...)
        verdict.log_to_ledger(..., "continue-blocked-worktree-teardown", ...)
        shutil.move(full_plan_path, halted_path)
        _cleanup_verdicts_for_slug(cleanup_slug)
        self._seen.discard(cleanup_slug)
        _delete_shadow(original_name)
        notifier.notify_plan_halted(original_name)
        break
    is_diag = original_name.startswith("diagnostic-")
```

---

## Detection Predicate

```python
any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))
```

Matches the exact dict shape `{"gate": "worktree_teardown", "evidence": str(e)}` appended by `_teardown_worktree` at three sites (bellows.py lines 556, 649, 679). "Uncleared" = simply present in `failures`; no separate clearing mechanism exists or was invented.

---

## Block-Path Housekeeping

When the predicate fires, the guard performs:

1. **`_log("ERROR", ...)`** — loud error with plan slug stating continue was rejected, commits not landed, manual R2 recovery required.
2. **`verdict.log_to_ledger(...)`** — action `"continue-blocked-worktree-teardown"`, reason string includes step number and R2 recovery instruction, passes `pause_reason_code=pause_reason_code_from_request`.
3. **`shutil.move`** — moves plan from `verdict-pending-{original_name}` to `halted-{original_name}` in `decisions_path`.
4. **`_cleanup_verdicts_for_slug(cleanup_slug)`** — removes pending verdict-request file.
5. **`self._seen.discard(cleanup_slug)`** — clears slug from seen set.
6. **`_delete_shadow(original_name)`** — removes shadow cache entry.
7. **`notifier.notify_plan_halted(original_name)`** — CEO notification via Pushover.
8. **`break`** — exits inner pname loop; `plan_matched=True` already set → outer loop breaks → verdict file moved to `processed-{fname}` by the existing `plan_matched` block.

This mirrors the existing stop/halt exit (lines 1404–1414 post-edit) but with the specific blocked-continue action and error message.

---

## Pre-Edit Verification Query Results

### Query 1: `gate_result_from_request` binding
- `gate_result_from_request = None` at line 1292
- `gate_result_from_request = json.loads(req_line.split(":**", 1)[1].strip())` at line 1315 (parsed from `**Gate Result JSON:**`)
- `gate_result = gate_result_from_request or {"failures": [], "files_changed": []}` at line 1338
- `if v == "continue":` at line 1340
- **CONFIRMED:** gate result parsed and bound before continue branch.

### Query 2: `worktree_teardown` failure shape
- Line 556: `gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})`
- Line 649: same shape
- Line 679: same shape
- **CONFIRMED:** ≥1 hit with exact dict shape the guard matches.

### Query 3: Two exits in continue branch
- **Final step** (line 1374 post-edit): `if step_number >= total_steps_c:` → `verdict.log_to_ledger(..., "continue-to-done", ...)`, `shutil.move` to `Done/`, `_cleanup_verdicts_for_slug`, `self._seen.discard`, `_delete_shadow`, `notifier.notify_plan_complete`.
- **Non-final resume** (line 1389 post-edit): `else:` → `verdict.log_to_ledger(..., v, ...)`, `shutil.move` to `in-progress-*`, `self.handle_new_plan(inprogress_path, resume_step=next_step)`.
- **CONFIRMED:** both exits present with expected housekeeping.

---

## Regression Tests

Three tests added to `tests/test_consume_verdicts.py`, mirroring the module's existing fixture/setup style (tempdir, resolved/ + verdicts/pending/ construction, verdict-pending plan placement, `_make_verdict_request_content` helper, patch context).

### 1. `test_continue_blocked_on_worktree_teardown_failure_interstep`
- **Setup:** multi-step plan (total_steps=2), step-1 continue verdict, gate result with `{"gate": "worktree_teardown", "evidence": "..."}`.
- **Asserts:** (a) plan file is `halted-*` (not `in-progress-*`, not `Done/`); (b) `handle_new_plan` not called (next step not dispatched); (c) ledger action = `continue-blocked-worktree-teardown`; (d) verdict file moved to `processed-*`.

### 2. `test_continue_to_done_blocked_on_worktree_teardown_failure_final_step`
- **Setup:** single-step plan (total_steps=1), step-1 continue verdict, gate result with worktree_teardown failure.
- **Asserts:** plan is `halted-*` (NOT in `Done/`), ledger action = `continue-blocked-worktree-teardown`, verdict file moved to `processed-*`. Proves guard sits before the final/non-final split.

### 3. `test_continue_advances_normally_without_teardown_failure`
- **Setup:** multi-step plan (total_steps=2), step-1 continue verdict, gate result with empty `failures` list.
- **Asserts:** plan advances to `in-progress-*` (not `halted-*`), `handle_new_plan` called with `resume_step=2`, ledger action = `continue` (not `continue-blocked-*`). Proves guard is specific and does not false-trip.

---

## Test Execution

### Pre-edit baseline
```
5 failed, 434 passed, 1 warning in 7.90s
```
Carry-over failures (all pre-existing, unrelated to _consume_verdicts):
- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `test_runner_parser.py::test_run_step_timeout`

### Post-edit
```
5 failed, 437 passed, 1 warning in 6.20s
```
- 3 new tests PASS (437 - 434 = 3)
- ZERO new failures (same 5 carry-over)

---

## Anchor Verification

### `grep -n "continue-blocked-worktree-teardown" bellows.py`
- Line 1348: the ledger action string. **CONFIRMED.**

### `grep -n 'worktree_teardown" for f in' bellows.py`
- Line 1345: the guard predicate. **CONFIRMED.**

### `git --no-pager diff -- bellows.py`
- Diff touches ONLY the `if v == "continue":` block in `_consume_verdicts` (18 lines inserted at line 1340).
- `_teardown_worktree` and `_create_worktree` are byte-unchanged. **CONFIRMED.**

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added a guard at the top of the `continue`-verdict branch in `_consume_verdicts` (`bellows.py`) that blocks advancement when the prior step's gate result carries an uncleared `worktree_teardown` failure. The guard routes the plan to `halted-` for manual R2 recovery instead of silently advancing (which would orphan un-landed commits). Three regression tests added covering inter-step block, final-step block, and clean-continue negative case.

### Files Deposited
- `knowledge/development/block-continue-over-worktree-teardown-failure-2026-06-01.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added 18-line worktree-teardown guard at top of continue branch in `_consume_verdicts`
- `tests/test_consume_verdicts.py` — added 3 regression tests

### Decisions Made
- Used `notifier.notify_plan_halted` (not `notify_plan_complete`) for the block path — the plan is halted, not completed
- Included `_delete_shadow(original_name)` in the block path to mirror the existing halt exit — a halted plan's shadow cache is no longer needed
- Guard `break`s out of the inner `pname` loop; the existing `plan_matched` block handles verdict-file move to `processed-` — no duplication needed

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the guard. The running daemon executed this plan with pre-edit code; the guard activates on the next plan dispatched after restart.

### Flags for Next Step
- QA should verify guard placement is before the final/non-final split, block path routes to `halted-` with all housekeeping, and the three new tests pass with zero new regressions.
