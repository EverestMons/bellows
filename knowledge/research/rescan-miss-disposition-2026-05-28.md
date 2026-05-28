# Rescan Miss Disposition — 2026-05-28

**Diagnostic:** `diagnostic-rescan-miss-disposition-2026-05-28`
**Agent:** Bellows Systems Analyst
**Date:** 2026-05-28

---

## Section 1 — Existing rescan mechanism map

The `_rescan` method (bellows.py:1156) performs three sequential operations every 30 seconds (rescan_interval at bellows.py:1456, call site at bellows.py:1462-1464):

1. **Verdict consumption** (line 1158): `self._consume_verdicts()` — processes resolved verdict files to resume or halt paused plans.

2. **Parallel-group settle-window dispatch** (lines 1160-1171): iterates `handler._pending_groups`, and for any group whose timestamp is >5 seconds old, collects sibling plans via `handler.collect_group()`, filters out plans whose slugs are already in `_seen` (line 1167), adds the remaining slugs to `_seen` (line 1168), and dispatches via `self.handle_parallel_group()`. Deletes the group from `_pending_groups` after dispatch (line 1171).

3. **General sweep** (lines 1172-1177): iterates every watched `decisions/` directory (line 1172), calls `os.listdir()` (line 1174), filters by `is_runnable_plan(fname)` (line 1175), and calls `handler._handle(full_path, from_rescan=True)` on each match (line 1177).

**Confirmation:** The general sweep at lines 1172-1177 scans `decisions/` for ALL files matching `is_runnable_plan` regardless of filesystem events, and calls `_handle(..., from_rescan=True)` on each. This is exactly the mechanism the BACKLOG entry proposes adding.

**The BACKLOG entry's proposed fix already exists.** The general sweep has been present since the initial commit (`^4e0a755`, 2026-05-15, per `git blame`). Every daemon instance — including the one running during the session-12 incident — had this code.

---

## Section 2 — `_seen` guard trace

### Case A: slug NOT in `_seen`

When `_handle(full_path, from_rescan=True)` is called for an unclaimed `executable-*` plan whose slug is not in `_seen`:

1. **Line 1036:** `path_parent` check — passes (path is under a watched directory).
2. **Line 1039:** `is_runnable_plan(filename)` — True for `executable-*` prefix (regex at line 1009: `^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$`).
3. **Line 1046:** `verdict.slug_from_path(path) in self.orchestrator._seen` — False → continues.
4. **Line 1048:** `extract_parallel_group(filename)` — None (not a `parallel-N-` prefixed file).
5. **Lines 1066-1068:** slug added to `_seen`, plan logged as detected, `handle_new_plan(path)` dispatches the plan.

This is the expected happy path. The plan would be claimed within one rescan interval (~30s).

### Case B: slug IS in `_seen`

When `_handle(full_path, from_rescan=True)` is called and the slug IS already in `_seen`:

1. **Lines 1036, 1039:** same as Case A — both pass.
2. **Line 1046:** `verdict.slug_from_path(path) in self.orchestrator._seen` — **True → returns immediately.** No log output, no dispatch.

The plan is silently skipped. This happens on **every subsequent rescan tick** as long as the slug remains in `_seen`. There is no timeout, no retry counter, and no log line indicating a skip.

### How a slug can become stranded in `_seen`

`slug_from_path` (verdict.py:82-92) strips both `executable-` and `diagnostic-` prefixes. Therefore:
- `diagnostic-foo-2026-05-27.md` → slug `foo-2026-05-27`
- `executable-foo-2026-05-27.md` → slug `foo-2026-05-27`

**Same slug for different plan types with the same base name.**

The `_seen` set is cleaned up in four places:
- **Line 668:** auto-close path — `bellows._seen.discard(slug)` after plan moves to Done.
- **Line 1084:** `on_modified` handler — invalidates `_seen` for non-lifecycle files modified in-place.
- **Line 1313:** `continue-to-done` verdict path.
- **Line 1339:** `stop` verdict path.

The dispatch-mode validator rejection path (bellows.py:390-395) is **NOT** one of these. When a plan is rejected:
1. The file is moved to `halted-{base_filename}` (line 392).
2. An ERROR is logged (line 393).
3. The function returns (line 395).
4. **`_seen` is never cleaned up.**

The `on_moved` event fires for the rename to `halted-*`, but `_handle(halted_dest_path)` hits `is_runnable_plan("halted-...")` → False → returns without touching `_seen`.

**Result:** a dispatch-mode-rejected plan permanently strands its slug in `_seen`, blocking any future plan with the same slug for the lifetime of the daemon process.

---

## Section 3 — Hypothesis test against the log

### Ground truth timeline (cross-referencing `bellows-2026-05-27.log` and `bellows-2026-05-28.log`)

| Time | Source | Event |
|------|--------|-------|
| 2026-05-27 22:06:24 | 27.log:421 | `diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` detected |
| 2026-05-27 22:06:24 | 27.log:423 | **Rejected** by dispatch-mode validator: "Plan header missing **Dispatch Mode:** field" → moved to `halted-diagnostic-...` |
| 2026-05-27 22:12:41 | 27.log:427 | `diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md` detected (different slug: `...-v2-...`) |
| 2026-05-27 22:16:47 | 27.log:436 | v2 diagnostic paused for verdict |
| 2026-05-28 09:10:49 | 27.log:648-649 | v2 diagnostic verdict: `continue-to-done` |
| 2026-05-28 09:14:51 | 27.log:650 | Heartbeat: idle (daemon still running) |
| 2026-05-28 09:19:51 | 27.log:651 | Heartbeat: idle (daemon still running) |
| 2026-05-28 ~09:14 | (inferred) | Planner deposits `executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` via `move_file` |
| 2026-05-28 09:23:09 | 28.log:1 | Fresh daemon start (no "session restart" marker → `log_existed=False`) |
| 2026-05-28 09:23:12 | 28.log:2 | **Startup scan found** `executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` |
| 2026-05-28 09:23:12 | 28.log:3 | Plan detected and claimed immediately |

**Key evidence:** `halted-diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` exists in `knowledge/decisions/` (confirmed via `ls`), proving the v1 diagnostic was rejected by the dispatch-mode validator and moved to halted state.

### Hypothesis evaluations

**(a) `is_runnable_plan(fname)` returned False — REFUTED**

The filename `executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` matches the regex `^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$` and does not start with any lifecycle prefix. `is_runnable_plan` returns True. Code inspection at bellows.py:1006-1009 confirms this. The file was also found by the startup scan at 09:23:12 using the same `is_runnable_plan` filter (bellows.py:1452).

**(b) Slug stuck in `_seen` — CONFIRMED**

Root cause chain:
1. The v1 diagnostic `diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` was detected at 22:06:24 on 2026-05-27.
2. `_handle` added slug `worktree-teardown-dirty-tree-precheck-2026-05-27` to `_seen` (bellows.py:1066).
3. `handle_new_plan` spawned `_run_tracked` → `run_plan` → dispatch-mode validator rejected the plan (missing Dispatch Mode header).
4. The rejection path (bellows.py:390-395) moved the file to `halted-diagnostic-...` and returned **without calling `_seen.discard()`**.
5. The slug `worktree-teardown-dirty-tree-precheck-2026-05-27` was permanently stranded in `_seen`.
6. The follow-on executable plan `executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` shares the **identical slug** (both `diagnostic-` and `executable-` prefixes are stripped by `slug_from_path` at verdict.py:85-87).
7. When deposited at ~09:14 on 2026-05-28, every 30-second rescan tick called `_handle(path, from_rescan=True)`, which hit the `_seen` guard at line 1046 and returned silently.
8. The daemon was manually killed and restarted at 09:23:09. The fresh `Bellows.__init__` created a new `self._seen = set()` (bellows.py:1098). The startup scan at 09:23:12 found and claimed the plan.

Supporting evidence:
- `halted-diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` exists in `knowledge/decisions/` — the rejected v1 file.
- The 2026-05-27 log shows the daemon running continuously from 20:14:01 through past 09:19:51 on 2026-05-28, with heartbeats every 5 minutes.
- No `detected plan` event appears for the executable between deposit (~09:14) and restart (09:23:09) — consistent with silent `_seen` guard skipping.
- The module fingerprint `bellows.py @ git:af8e7f3` was constant throughout the 2026-05-27 daemon instance, confirming no hot-reload occurred.

**(c) Claim was actually from a rescan tick, not the restart — REFUTED**

The 2026-05-28 log line 1 (`09:23:09`) is the session log initialization, and line 2 (`09:23:12`) is explicitly `[EVENT] startup scan found executable-...`. The startup scan code (bellows.py:1448-1455) runs once before the heartbeat loop begins. The rescan loop (bellows.py:1460-1464) has not yet started. The claim came from the startup scan, not a rescan tick.

**(d) `_rescan` raised an exception before reaching line 1172 — REFUTED**

If `_rescan` raised an unhandled exception, it would propagate through the `while True` loop (bellows.py:1460) up to the `except KeyboardInterrupt` at line 1484, which only catches `KeyboardInterrupt`. Any other exception would crash the daemon. The heartbeats at 09:14:51 and 09:19:51 in the 2026-05-27 log prove the daemon was still alive and looping. Therefore `_rescan` was executing without raising.

**(e) Filesystem event was also missed — CONFIRMED (contributing factor, not root cause)**

The BACKLOG entry's hypothesis that `move_file` did not emit a filesystem event is likely correct (macOS kqueue/FSEvents can coalesce or drop atomic-rename events). However, this is a **secondary factor**: even if the watcher missed the event, the rescan general sweep should have caught the plan within 30 seconds. The rescan DID find the file via `os.listdir` but was blocked by the `_seen` guard. The filesystem miss is a contributing factor; the stranded `_seen` slug is the root cause.

---

## Section 4 — Disposition recommendation

**Narrow guard-fix:** Add `_seen.discard()` to the dispatch-mode validator rejection path.

### Root cause

The dispatch-mode validator rejection path at bellows.py:390-395 returns without cleaning up the slug from `_seen`. This is the only early-exit path in `run_plan` that does not call `bellows._seen.discard()`. (Contrast with: auto-close at line 668, continue-to-done at line 1313, and stop at line 1339 — all three discard from `_seen`.)

### Fix specification

**Insertion point:** bellows.py, between lines 392 and 393 (after `shutil.move`, before `_log`).

**Change shape:**
```python
if validation_result["rejected"]:
    halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
    shutil.move(plan_path, halted_path)
    if bellows is not None:
        bellows._seen.discard(verdict.slug_from_path(plan_path))
    _log("ERROR", f"plan rejected by dispatch-mode validator: {validation_result['reject_reason']}", slug=slug_for(plan_name))
    notifier.push(app_key, user_key, "Bellows — Plan Rejected", f"Plan: {plan_name}\nReason: {validation_result['reject_reason']}")
    return
```

**LOC estimate:** 2 lines (the `if bellows is not None:` guard + the discard call).

**Regression-test surface:**
- Existing `test_dispatch_mode_validator_rejection` tests (if any) should verify the plan is halted and the slug is NOT in `_seen` after rejection.
- New test: deposit a `diagnostic-foo.md` plan with invalid dispatch mode, verify it is halted, then deposit `executable-foo.md` with valid dispatch mode, verify the rescan claims it within one interval.
- Existing tests for `_seen` management (on_modified invalidation, auto-close discard, verdict discard) should be unaffected since this change only adds a new discard call site.

### BACKLOG entry re-framing

The current BACKLOG entry "Watcher misses `move_file`-deposited plans — periodic `decisions/` rescan as self-heal" should be re-framed:

**Current framing (incorrect):** The rescan doesn't exist; add one.
**Correct framing:** The rescan exists (since `^4e0a755`, 2026-05-15) and runs every 30 seconds. The session-12 miss was caused by a `_seen` slug stranded by the dispatch-mode validator rejection path, not by a missing rescan. The fix is a 2-line `_seen.discard()` addition, not a new rescan mechanism.

The entry should be updated to reflect the true root cause and closed once the fix ships.

---

## Section 5 — Flags for next step

### Assumptions
- The v1 diagnostic filename was `diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` (inferred from the `halted-` file in `knowledge/decisions/` and the truncated log slug `[diagnostic-worktree-teardown-d]`).
- The executable deposit time was ~09:14 (after the diagnostic verdict at 09:10:49 + Planner response time). The exact time is unrecorded.

### Contradictions with BACKLOG framing
- The BACKLOG claims the rescan mechanism doesn't exist. It does — since the initial commit.
- The BACKLOG proposes "~15-25 LOC hooking the existing startup-scan logic into the heartbeat loop." This is already done at bellows.py:1172-1177 and 1462-1464. The actual fix is 2 LOC.
- The BACKLOG's `_seen`-aware filter proposal is ironic: `_seen` awareness is what CAUSED the miss, not what was missing.

### Edge cases for follow-on executable
1. **Settle-window interaction:** Not relevant — the executable is a non-parallel plan, so the parallel-group settle-window logic (lines 1160-1171) does not apply.
2. **`_pending_groups` state:** Not relevant — same reason as above.
3. **Concurrent claim during rescan tick:** The `_seen.add()` at line 1066 (in `_handle`) provides single-dispatch guarantees. The fix (discard on rejection) happens in a background thread (`_run_tracked`), but `_handle` is called from the main thread (rescan loop). Since `_seen` is a Python `set` protected by the GIL, and the discard happens BEFORE any re-check by the rescan loop's next tick, there is no race window of concern.
4. **Other early-exit paths in `run_plan`:** A broader audit of all `return` paths in `run_plan` should confirm that no other path strands a `_seen` slug. The known clean-exit paths (line 668 auto-close, line 1313 continue-to-done, line 1339 stop) all call `_seen.discard()`. The validator rejection at line 390-395 is the only identified gap.

### Layer Impact
This is a Layer 1 (Bellows) internal fix. No Layer 2 (agent) or Layer 3 (Planner) changes needed. The fix does not shift judgment responsibility between layers — it corrects a bookkeeping error in the dispatch lifecycle.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated why the existing periodic `_rescan` general-sweep did not claim the session-12 `move_file`-deposited plan within a rescan interval. Root cause identified: the dispatch-mode validator rejection path at bellows.py:390-395 strands the plan's slug in `_seen`, permanently blocking any future plan with the same slug (including a follow-on executable sharing the same base name as a rejected diagnostic).

### Files Deposited
- `knowledge/research/rescan-miss-disposition-2026-05-28.md` — full disposition report (Sections 1-5)

### Files Created or Modified (Code)
- None (diagnostic only — no code changes)

### Decisions Made
- Disposition: narrow guard-fix (2 LOC `_seen.discard()` at the validator rejection path), not a new rescan mechanism
- BACKLOG entry should be re-framed to reflect true root cause

### Flags for CEO
- BACKLOG entry "Watcher misses `move_file`-deposited plans" needs re-framing: the proposed fix (add a rescan) already exists; the real bug is a missing `_seen.discard()` in the dispatch-mode validator rejection path

### Flags for Next Step
- The fix is 2 LOC at bellows.py:392-393; regression test should verify slug cleanup on rejection and cross-plan-type slug collision
- Broader audit of all `return` paths in `run_plan` recommended to check for other `_seen` strand sites
