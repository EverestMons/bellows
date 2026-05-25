# Rename-first ordering at all 4 pause sites — Dev Log

**Date:** 2026-05-24
**Plan:** `executable-rename-first-ordering-2026-05-24`
**Step:** 1 (DEV)

---

## (a) Pre-edit verification stdout

**Check (i):** `grep -c 'verdict.post_verdict_request' bellows.py` → `4` ✅

**Check (ii):** `grep -n 'verdict.post_verdict_request' bellows.py` →
```
438:            verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
520:                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, ...
611:            verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, ...
640:                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
```
Lines 438, 520, 611, 640 — all in expected neighborhoods. ✅

**Check (iii):** `python3 -c "import bellows"` → exits cleanly (exit 0, urllib3 NotOpenSSLWarning only). ✅

**Check (iv):** `pytest tests/test_bellows.py tests/test_consume_verdicts.py -q` → `122 passed, 1 warning in 0.64s`. ✅

---

## (b) Before/after snippets for each reordered site

### Site 1 — worktree-creation failure (~line 437)

**Before:**
```python
            gate_result = {"failures": [...], "files_changed": [], "passed": False, "is_qa_step": False}
            verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
                                         pause_reason="gate_failure", ...)
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
```

**After:**
```python
            gate_result = {"failures": [...], "files_changed": [], "passed": False, "is_qa_step": False}
            # Rename-first ordering (RV-1 closure, 2026-05-24): ...
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
                                         pause_reason="gate_failure", ...)
```

### Site 2 — intermediate-step gate_failure pause (~line 520)

**Before:**
```python
                verdict.post_verdict_request(...)
                notifier.notify_verdict_request(...)
                # Rename plan to verdict-pending
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
```

**After:**
```python
                # Rename-first ordering (RV-1 closure, 2026-05-24): ...
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                verdict.post_verdict_request(...)
                notifier.notify_verdict_request(...)
```

### Site 3 — final-step gate_failure pause (~line 611)

**Before:**
```python
            verdict.post_verdict_request(...)
            notifier.notify_verdict_request(...)
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
```

**After:**
```python
            # Rename-first ordering (RV-1 closure, 2026-05-24): ...
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            verdict.post_verdict_request(...)
            notifier.notify_verdict_request(...)
```

### Site 4 — auto-close-failure pause (~line 640)

**Before:**
```python
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
                                             pause_reason="gate_failure", ...)
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
```

**After:**
```python
                # Rename-first ordering (RV-1 closure, 2026-05-24): ...
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
                                             pause_reason="gate_failure", ...)
```

---

## (c) New test functions

1. `test_pause_site_1_worktree_creation_failure_renames_before_post` — asserts rename-first ordering at Site 1 via `WorktreeCreationError` trigger.
2. `test_pause_site_2_intermediate_step_gate_failure_renames_before_post` — asserts rename-first ordering at Site 2 via failing `gates.check` on intermediate step of a 2-step plan.
3. `test_pause_site_3_final_step_gate_failure_renames_before_post` — asserts rename-first ordering at Site 3 via failing `gates.check` on final step of a 1-step plan.
4. `test_pause_site_4_auto_close_teardown_failure_renames_before_post` — asserts rename-first ordering at Site 4 via `WorktreeTeardownError` on auto-close path with clean gates.

All 4 tests use a shared `_make_ordering_tracker()` helper that wraps `shutil.move` (filtering to `verdict-pending-*` destinations) and `verdict.post_verdict_request` to record invocation order.

---

## (d) Task E grep verification stdout

```
$ grep -c 'verdict.post_verdict_request' bellows.py
4

$ grep -n 'Rename-first ordering (RV-1 closure' bellows.py
438:            # Rename-first ordering (RV-1 closure, 2026-05-24): ...
522:                # Rename-first ordering (RV-1 closure, 2026-05-24): ...
614:            # Rename-first ordering (RV-1 closure, 2026-05-24): ...
645:                # Rename-first ordering (RV-1 closure, 2026-05-24): ...

$ grep -B 2 'verdict.post_verdict_request' bellows.py | head -40
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            verdict.post_verdict_request(...)
--
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                verdict.post_verdict_request(...)
--
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            verdict.post_verdict_request(...)
--
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                verdict.post_verdict_request(...)
```

All 4 sites confirmed: rename block immediately precedes `verdict.post_verdict_request`.

---

## (e) Task G pytest summary

```
390 collected, 385 passed, 5 failed, 1 warning in 6.84s
```

**Failures (all pre-existing carry-overs):**
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — worktree artifact (phrase file path)
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — worktree artifact
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — worktree artifact
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — worktree artifact
- `tests/test_runner_parser.py::test_run_step_timeout` — pre-existing carry-over

All 4 new `test_pause_site_*` tests: **PASSED**. No new regressions.

---

## (f) Summary

This change closes the RV-1 boundary identified in the 2026-05-24 daemon-restart-state-divergence diagnostic (Section E16). The root cause was that `verdict.post_verdict_request()` and the plan rename from `in-progress-*` to `verdict-pending-*` were non-atomic operations with the rename happening AFTER the verdict-post. A daemon restart between these operations left the verdict-request file in `verdicts/pending/` while the plan remained named `in-progress-*`, preventing `_consume_verdicts` from matching the verdict (its predicate requires the `verdict-pending-` prefix). By reordering all four pause sites to rename BEFORE posting, the gap is eliminated: if the daemon dies after rename but before verdict-post, the plan is in `verdict-pending-*` state (safe); if it dies before rename, no verdict-request exists (also safe). This closes BACKLOG items #2 (daemon-restart recovery shape) and #3 (final-step gate_failure rename-skip). BACKLOG item #5 (step-counter loop after precondition-failure verdict) is explicitly out of scope for this plan — it is an independent logic defect in `_consume_verdicts` step-advancement.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Reordered all 4 pause sites in `bellows.py` to rename plan files from `in-progress-*` to `verdict-pending-*` BEFORE posting verdict-requests, closing the RV-1 boundary. Added 4 regression tests verifying rename-first ordering at each site.

### Files Deposited
- `knowledge/development/rename-first-ordering-2026-05-24.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — reordered rename/verdict-post at 4 pause sites (Sites 1-4), added RV-1 closure comments
- `tests/test_bellows.py` — added 4 new `test_pause_site_*` regression tests + `_make_ordering_tracker` helper

### Decisions Made
- Used `shutil.move` wrapper via `patch("shutil.move")` for ordering tests rather than monkeypatching `bellows.shutil.move`, since bellows.py imports shutil at module level and the move calls go through `shutil.move` directly.

### Flags for CEO
- None

### Flags for Next Step
- None
