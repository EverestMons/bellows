# `processed-` Prefix Re-consumption Loop & Final-Step Rename-Skip

**Date:** 2026-05-24
**Agent:** Bellows Systems Analyst
**Scope:** Diagnostic — characterize the `processed-` prefix re-consumption infinite loop (BACKLOG P0, 2026-05-22) and the companion final-step `in-progress-*` → `verdict-pending-*` rename-skip (BACKLOG 2026-05-22). Determine whether they share a root cause.
**Prior art:** `knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md` (the 2026-05-21 diagnostic that characterized the original `processed-` prefix drain failure and recommended the pre-scan rename fix shipped in commit `3c9344f`).

---

## Section A — Pre-scan rename trigger (item 1)

### Q1 — Which file and function emits the `normalized write-time processed- prefix:` log line?

**File:** `bellows.py`, method `_consume_verdicts` (class `Bellows`), line 1162.

**Code (bellows.py:1129–1162):**
```python
# Pre-scan: normalize processed-verdict-* to verdict-* (Planner write-time naming mismatch).
for fname in os.listdir(resolved_dir):
    if fname.startswith("processed-verdict-") and fname.endswith(".md"):
        # Orphan check ...
        slug_match = re.match(r"^processed-verdict-(.+)-step-(\d+)\.md$", fname)
        if slug_match:
            plan_slug = slug_match.group(1)
            has_paired_plan = False
            for decisions_path in self.config.get("watched_projects", []):
                if not os.path.isdir(decisions_path):
                    continue
                for pname in os.listdir(decisions_path):
                    if pname.startswith("verdict-pending-") and plan_slug in pname:
                        has_paired_plan = True
                        break
                if has_paired_plan:
                    break
            if not has_paired_plan:
                if fname not in _prescan_orphan_logged:
                    _log("INFO", f"pre-scan: skipping orphan {fname} — no active verdict-pending plan")
                    _prescan_orphan_logged.add(fname)
                continue
        canonical = fname[len("processed-"):]
        canonical_path = os.path.join(resolved_dir, canonical)
        if os.path.exists(canonical_path):
            _log("WARN", f"cannot normalize {fname} — canonical {canonical} already exists; skipping rename")
            continue
        shutil.move(os.path.join(resolved_dir, fname), canonical_path)
        _log("WARN", f"normalized write-time processed- prefix: {fname} → {canonical}")
```

**Calling context:** `_consume_verdicts` is called from `_rescan` (bellows.py:1074) every 30 seconds. The pre-scan runs at the top of `_consume_verdicts` before the main verdict-processing loop. It scans all files in `verdicts/resolved/` matching `processed-verdict-*.md`.

### Q2 — Is this the pre-scan rename helper from commit `dc0bdd7` / `3c9344f`?

**Yes.** This is the fix introduced in commit `3c9344f` (2026-05-21) per the `consume-verdicts-drain-failure-2026-05-21.md` diagnostic's "Option B — Strip `processed-` at write-time detection and rename before processing." That diagnostic recommended this exact pre-scan rename shape.

The code was **modified** in commit `d1855ba` (2026-05-22) to add the orphan guard (bellows.py:1136–1155), which checks for a paired `verdict-pending-*` plan before allowing the rename. The orphan guard was shipped as `executable-pre-scan-orphan-guard-2026-05-22` per BACKLOG Closed entry.

The log line text changed from `"renamed write-time processed- prefix:"` (original `3c9344f`) to `"normalized write-time processed- prefix:"` (current), but the rename mechanism is the same.

### Q3 — Under what condition does the pre-scan rename `processed-verdict-*.md` → `verdict-*.md`?

The rename fires when ALL of:
1. `fname.startswith("processed-verdict-") and fname.endswith(".md")` — bellows.py:1134
2. Orphan guard passes: there exists ANY file `pname` in ANY watched decisions directory where `pname.startswith("verdict-pending-") and plan_slug in pname` — bellows.py:1146
3. Collision guard: the canonical target `verdict-{slug}-step-{N}.md` does not already exist — bellows.py:1158

**There is NO guard checking whether the file was already-on-disk (legitimately post-consumption) vs newly-written-this-scan (Planner write-time mistake).** The pre-scan treats ALL `processed-verdict-*.md` files identically. A file that Bellows itself renamed to `processed-*` after successful consumption (bellows.py:1291) is indistinguishable from a file the Planner mistakenly wrote with the `processed-` prefix.

**There is NO guard checking whether the verdict's step number matches the step the plan is currently waiting on.** The orphan guard at bellows.py:1146 uses `plan_slug in pname` — a slug-only substring match with no step-N comparison.

### Q4 — After the rename, what is the resulting file?

The resulting file is `verdict-{slug}-step-{N}.md` in `verdicts/resolved/`. This matches the exact canonical shape that the main `_consume_verdicts` filter loop accepts at bellows.py:1165:

```python
if not fname.startswith("verdict-") or not fname.endswith(".md"):
    continue
```

And the regex at bellows.py:1170:
```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
```

The renamed file passes both filters and is treated as a fresh, unconsumed verdict.

---

## Section B — Loop mechanism (item 1)

### Q5 — Full trace from "Step 2 gate-PASS at 18:37" through first re-run

**State at 18:37 on 2026-05-22:**
- Plan: `verdict-pending-executable-stuck-state-color-override-2026-05-22.md` (paused after step 2 QA, awaiting CEO verdict)
- `verdicts/resolved/processed-verdict-stuck-state-color-override-2026-05-22-step-1.md` — legitimately on disk since step 1's verdict was consumed earlier (Bellows renamed it from `verdict-*` to `processed-*` at bellows.py:1291 after consumption)
- A step-2 verdict-request file exists in `verdicts/pending/`

**Next rescan (within 30s of 18:37):**

1. `_consume_verdicts` pre-scan at bellows.py:1133: iterates `os.listdir(resolved_dir)`, finds `processed-verdict-stuck-state-color-override-2026-05-22-step-1.md`
2. Orphan guard at bellows.py:1139–1151: extracts `plan_slug = "stuck-state-color-override-2026-05-22"` from regex. Searches watched decisions directories for `verdict-pending-*` plans with that slug. Finds `verdict-pending-executable-stuck-state-color-override-2026-05-22.md`. **`has_paired_plan = True`** — the step-2-pending plan is treated as a match for the step-1 verdict because the orphan guard does slug-only matching.
3. Collision guard at bellows.py:1158: checks if `verdict-stuck-state-color-override-2026-05-22-step-1.md` exists. It doesn't (it was the original pre-consumption name, consumed and renamed to `processed-*`). Guard passes.
4. **Rename fires** at bellows.py:1161: `processed-verdict-stuck-state-color-override-2026-05-22-step-1.md` → `verdict-stuck-state-color-override-2026-05-22-step-1.md`
5. Log emitted: `[WARN] normalized write-time processed- prefix: processed-verdict-...-step-1.md → verdict-...-step-1.md`

**Main loop (same invocation of `_consume_verdicts`):**

6. Second `os.listdir(resolved_dir)` at bellows.py:1164 sees the just-renamed `verdict-stuck-state-color-override-2026-05-22-step-1.md`
7. Filter 1 (bellows.py:1165): `startswith("verdict-")` → True. Passes.
8. Filter 2 (bellows.py:1167): `startswith("verdict-request-")` → False. Passes.
9. Regex match (bellows.py:1170): extracts `plan_slug = "stuck-state-color-override-2026-05-22"`, `step_number = 1`
10. `check_verdict` at bellows.py:1208: constructs path `verdict-stuck-state-color-override-2026-05-22-step-1.md` in resolved/, which exists (just renamed). Parses content → `{"found": True, "verdict": "continue", ...}`
11. Pairing at bellows.py:1222: `pname.startswith("verdict-pending-") and plan_slug in pname` → matches `verdict-pending-executable-stuck-state-color-override-2026-05-22.md`
12. Continue branch at bellows.py:1229: `step_number (1) >= total_steps_c (2)` → False → enters the "not final step, resume from next" branch
13. Plan moved from `verdict-pending-*` to `in-progress-*` (bellows.py:1265)
14. `handle_new_plan(inprogress_path, resume_step=2)` dispatched (bellows.py:1268)
15. Log: `verdict continue — resuming`
16. Verdict file renamed to `processed-verdict-...-step-1.md` again (bellows.py:1291)

**Step 2 re-runs, completes, pauses again. Plan returns to `verdict-pending-*` state. Next rescan: cycle repeats from step 1.**

### Q6 — Does the consumer match the step-1 verdict against a step-2-pending plan?

**Yes.** The pairing at bellows.py:1222 uses only a slug substring match:

```python
if pname.startswith("verdict-pending-") and plan_slug in pname:
```

There is **no step-number comparison** in the pairing. The consumer does not check whether the verdict's step number (1) matches the step the plan is waiting on (2). It blindly pairs any verdict with slug-matching plan and processes it based on the verdict's own step number.

At bellows.py:1245, `step_number >= total_steps_c` determines whether the verdict triggers a continue-to-done or a resume-next-step. With `step_number = 1` and `total_steps_c = 2`, the code always takes the "resume from step 2" branch. This is why the plan re-runs step 2 every cycle rather than being closed.

### Q7 — Is there any code path that would terminate the loop?

**No.** There is no:
- **Idempotency check:** No tracking of "this verdict file has already been consumed N times"
- **Retry limit:** No counter for how many times a verdict has been re-processed
- **Terminal-state check:** No verification that the verdict's step has already been completed
- **Step-match guard:** No comparison of verdict step number vs plan's pending step number

The only termination mechanisms are external:
- CEO/Planner manually renames the `processed-verdict-*` file (e.g., prefixing with `_PLANNER_RECALLED_`) to break the regex match
- Agent errors out enough to produce a non-continue verdict
- The 600s inactivity-timeout kill (observed at 19:31 in the reproduction) pauses the plan temporarily, but it re-enters the loop on the next rescan when the plan returns to `verdict-pending-*`

---

## Section C — Final-step rename-skip mechanism (item 2)

### Q8 — Every site in `run_plan()` that renames `in-progress-*` → `verdict-pending-*`

There are **three** rename sites:

**Site 1 — Worktree creation failure (bellows.py:443–445):**
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```
Conditional: `WorktreeCreationError` exception. Fires for any step (step 1 only in practice since worktree is created once per plan).

**Site 2 — Intermediate-step pause (bellows.py:528–530):**
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```
Conditional: inside the `while not is_final_step(current_step, total_steps):` loop body. Gates the rename on any pause condition: `gate_failure`, `qa_checkpoint`, `agent_verdict_request`, `header_pause`.

**Site 3 — Final-step pause (bellows.py:618–620):**
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```
Conditional: after the `while` loop, in the post-loop final-step block. Gates: `not gate_result["passed"]`, `is_qa_step`, `verdict_requested`, `header_says_pause`, or `not effective_auto_close`.

**Site 4 — Auto-close worktree teardown failure (bellows.py:645–647):**
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```
Conditional: `WorktreeTeardownError` during auto-close path. Converts auto-close to gate_failure pause.

### Q9 — Final-step gate_failure path: does the rename exist?

**Yes.** The rename at Site 3 (bellows.py:618–620) is **structurally identical** to the intermediate-step rename at Site 2 (bellows.py:528–530). Both are unconditional within their respective `if` blocks (guarded only by `os.path.exists(inprogress_path)`).

The final-step gate_failure path is:

```python
# bellows.py:586-624 (post-while-loop block)
if (not gate_result["passed"]          # ← True for gate_failure
        or gate_result["is_qa_step"]
        or ...
        or not effective_auto_close):
    ...
    if not gate_result["passed"]:
        _pause_reason = "gate_failure"   # ← Set for the reproduction case
    ...
    try:
        _teardown_worktree(...)          # line 610
    except WorktreeTeardownError as e:
        ...                              # line 612-613
    verdict.post_verdict_request(...)    # line 614
    notifier.notify_verdict_request(...) # line 615-617
    verdict_pending_path = ...           # line 618
    if os.path.exists(inprogress_path):  # line 619
        shutil.move(...)                 # line 620
    record_run(...)                      # line 621-622
    _log("PAUSE", ...)                   # line 623
    return                               # line 624
```

The rename IS there. There is **no branch asymmetry** between intermediate-step and final-step gate_failure paths for the rename operation.

### Q10 — `_teardown_worktree` ordering relative to the rename

`_teardown_worktree` is called at bellows.py:610, **before** the verdict post (line 614) and the rename (line 619-620). The exception handler at lines 612-613 catches `WorktreeTeardownError` and modifies `_pause_reason` and `gate_result`, but does NOT return or skip subsequent statements. Execution continues to verdict post, notify, and rename regardless of teardown success or failure.

A `_teardown_worktree` failure **cannot short-circuit the rename** — the exception is caught and handled in-line.

### Q11 — Could a daemon restart between pause-time and rename-time drop the rename?

**Yes. This is the most likely root cause for item 2.**

The rename at bellows.py:619-620 is a Python statement that executes only if the process reaches that line. Between the verdict post (line 614) and the rename (line 619), there are two intervening operations:

1. `notifier.notify_verdict_request(...)` at lines 615-617 — Pushover HTTP call
2. Path construction at line 618

If the daemon process is killed (SIGKILL, crash, `KeyboardInterrupt`, or unhandled exception in `notifier.notify_verdict_request`) between lines 614 and 619, the verdict request file is written to `verdicts/pending/` but the `in-progress-*` → `verdict-pending-*` rename never executes.

The BACKLOG entry for item 2 explicitly identifies "the daemon restart that occurred sometime between Step 2 pause (09:13:30) and the log dump at 09:21:12" as a possible cause. This is consistent with the code analysis: the rename is a non-atomic in-memory operation that is lost on process termination.

**The rename is NOT deferred or split across a persistent marker.** It is a single `shutil.move` call in the same function invocation as the verdict post. There is no recovery mechanism on restart — if the process dies between verdict post and rename, the state is permanently inconsistent (verdict request exists but plan is still `in-progress-*`).

**Secondary hypothesis:** An unhandled exception in `notifier.notify_verdict_request` (lines 615-617) would propagate to the outer `except Exception` at bellows.py:667, skipping the rename. This would produce the same symptom without a daemon restart. However, the BACKLOG does report a daemon restart in the relevant timeframe, making this the primary explanation.

---

## Section D — Reproduction verification

### Q12 — Stuck-state-color-override loop reconstruction

The BACKLOG entry describes:
- 2-step plan, step 1 authorized at 18:33, step 2 passed gates at 18:37
- Plan entered `verdict-pending-*` state after step 2 completion
- `processed-verdict-stuck-state-color-override-2026-05-22-step-1.md` was on disk in `verdicts/resolved/` — legitimately post-consumption from step 1

**The Section A/B trace explains ALL iterations, not just the first.** Each iteration follows the same cycle:
1. Pre-scan renames `processed-verdict-...-step-1.md` → `verdict-...-step-1.md` (step-1 verdict re-materialized)
2. Main loop consumes it as a fresh step-1 continue → dispatches step 2
3. Step 2 runs, completes, pauses → plan returns to `verdict-pending-*`
4. Consumed verdict file renamed back to `processed-verdict-...-step-1.md`
5. Next rescan: cycle repeats

The 14+ iterations (including the 600s timeout kill at 19:31) are all instances of the same cycle. The timeout kill temporarily breaks the cycle (step 2 fails with `receipt_status != Complete`), but the resulting gate_failure pause puts the plan back into `verdict-pending-*`, and the loop resumes on the next rescan.

**No surviving verdict files** were found for slug `stuck-state-color-override` in `verdicts/resolved/` (the plan was likely cleaned up during the BACKLOG-documented Planner intervention with `_PLANNER_RECALLED_` prefixing, and the plan is no longer in `knowledge/decisions/Done/`).

### Q13 — Pre-scan-orphan-guard rename-skip reconstruction

The BACKLOG entry describes:
- 2-step plan `executable-pre-scan-orphan-guard-2026-05-22.md`, step 2 QA
- Gates failed on `scope_check` (false positive)
- Verdict-request posted correctly
- Plan filename stayed as `in-progress-executable-pre-scan-orphan-guard-2026-05-22.md`
- Daemon restart between 09:13:30 and 09:21:12

**The Section C trace explains the rename-skip.** The code DOES contain the rename at bellows.py:618-620, and there is no branch that skips it. The rename was not "never attempted by the on-pause branch" — it was attempted (or would have been attempted) but the process was killed before reaching it.

The BACKLOG's two hypotheses:
- **(1) Code path skips the rename:** **Refuted.** The rename is present and structurally identical to the intermediate-step path.
- **(2) Daemon restart drops mid-pause state:** **Confirmed as the root cause.** The daemon restart between verdict post (line 614) and rename (line 619) caused the state inconsistency.

**Surviving verdict files:** `verdicts/resolved/processed-verdict-pre-scan-orphan-guard-2026-05-22-step-1.md` and `processed-verdict-pre-scan-orphan-guard-2026-05-22-step-2.md` are both present — confirming that verdicts for both steps were eventually consumed (likely after Planner-side manual rename recovery per the BACKLOG's operational mitigation).

---

## Section E — Joint root cause analysis

### Q14 — Do items 1 and 2 share a root cause?

**No. They are independent bugs in adjacent code regions.**

| | Item 1 (loop) | Item 2 (rename-skip) |
|---|---|---|
| **Code region** | `_consume_verdicts` pre-scan, bellows.py:1129-1162 | `run_plan` final-step pause path, bellows.py:614-620 |
| **Bug type** | Logic defect — missing step-number guard in orphan check | State-loss — non-atomic verdict-post + rename sequence |
| **Introduced by** | Commit `3c9344f` (pre-scan rename, 2026-05-21), modified by `d1855ba` (orphan guard, 2026-05-22) | Pre-existing — the verdict-post/rename sequence has always been non-atomic since the `verdict-pending-*` lifecycle was introduced |
| **Trigger** | Any multi-step plan that pauses for verdict after step N>1 with a prior step's `processed-verdict-*` file still in resolved/ | Daemon restart (or unhandled exception in notifier) between verdict post and rename |

They do not share a code site, a common helper, or a common ancestor commit. Item 1 is downstream of the 2026-05-21 drain fix. Item 2 is a pre-existing atomicity gap unrelated to the drain fix.

### Q15 — Fix sequencing

**Fixing item 1 first does NOT mask item 2.** Item 1's fix (preventing the pre-scan from renaming legitimately-processed verdicts) operates in `_consume_verdicts`. Item 2's fix (making verdict-post + rename atomic, or adding restart recovery) operates in `run_plan`. They are in different code paths with no interaction.

**Fixing item 2 first does NOT worsen item 1.** Ensuring the rename always happens (so the plan is always `verdict-pending-*` after a pause) would actually make item 1's loop trigger more reliably (because there's always a `verdict-pending-*` plan for the orphan guard to match). But item 1 already fires reliably without item 2's fix — it only requires a multi-step plan that pauses on a step after step 1.

**Recommended sequencing:** Fix item 1 first (P0 — actively burns resources with no natural termination). Item 2 can follow (lower priority — requires daemon restart to trigger, manual recovery is documented).

---

## Section F — Resolution options

### Q16 — Fix shapes for item 1 (the loop)

**Shape 1a — Add step-number guard to the orphan check.** Currently, the orphan check at bellows.py:1146 only matches slug. Extend it to verify the verdict's step number corresponds to the plan's current pending step. This requires parsing the verdict-request file in `verdicts/pending/` to extract the step number the plan is waiting on. **LOC estimate:** ~10 production lines (extract step from verdict-request filename, compare with pre-scan verdict's step number). **Risk:** Moderate — requires the verdict-request file to exist and be correctly named; if the request file was already cleaned up, the guard would not fire.

**Shape 1b — Guard the pre-scan rename on file-mtime (only rename files written this scan or recently).** Check `os.path.getmtime(fname)` and only rename files modified within the last N seconds (e.g., 120s — two rescan intervals). Legitimately-processed files will have old mtimes. **LOC estimate:** ~5 production lines. **Risk:** Low but brittle — the mtime threshold is a heuristic. A Planner-written `processed-verdict-*` file that sat unprocessed for >120s (e.g., Planner deposited it during a long daemon outage) would be missed. The original intent (fixing Planner write-time mistakes) is rare now that PLANNER_TEMPLATE v4.49 Rule 25 prohibits the `processed-` prefix at write time.

**Shape 1c — Remove the pre-scan rename entirely.** The pre-scan was a belt-and-suspenders fix; the authoritative fix is the governance rule in PLANNER_TEMPLATE v4.49 Rule 25 that prohibits `processed-` prefix at write time. Since the governance rule is in place and no new write-time `processed-` violations have occurred since 2026-05-21, the pre-scan can be removed. If a future Planner mistake writes a `processed-` file, the no-match WARN at bellows.py:1317 surfaces it for manual intervention. **LOC estimate:** -30 production lines (remove the entire pre-scan block + the `_prescan_orphan_logged` set + 4 orphan-guard regression tests). **Risk:** Low — removes the self-healing for a failure mode that governance already prevents. If a write-time `processed-` file appears in the future, manual rename is trivial. Eliminates the entire loop class permanently.

### Q17 — Fix shapes for item 2 (the rename-skip)

**Shape 2a — Swap verdict-post and rename order.** Move the rename (lines 618-620) to BEFORE the verdict post (line 614). This way, if the daemon dies after the rename, the plan is already `verdict-pending-*` and the verdict request exists or doesn't (the Planner can re-request). If the daemon dies before the rename, neither rename nor verdict post happened, and the plan stays `in-progress-*` (restart rescan picks it up). **LOC estimate:** ~5 production lines (reorder + duplicate at all 3 pause sites). **Risk:** Low — the only behavioral change is that the verdict-request file is written after the plan is already `verdict-pending-*`, which is the expected state for `_consume_verdicts` to pair them.

**Shape 2b — Add startup recovery scan for orphaned `in-progress-*` plans with pending verdicts.** On startup, scan decisions directories for `in-progress-*` plans that have a matching verdict-request in `verdicts/pending/`. Promote them to `verdict-pending-*`. This is BACKLOG entry 2026-05-23 option (a). **LOC estimate:** ~15 production lines (startup scan, slug matching, rename) + ~15 test lines. **Risk:** Low — the startup scan runs once and handles the exact state left by a daemon restart.

**Shape 2c — Make the verdict-post + rename a single helper with rename-first semantics.** Extract a `_pause_for_verdict(plan_path, ...)` helper that does rename → verdict-post → notify → record_run → log as an atomic sequence. Rename-first ensures the plan is always in `verdict-pending-*` state before the verdict request is written. Unify all 3 pause sites (intermediate, final, auto-close-failure) through this helper. **LOC estimate:** ~25 production lines (new helper + refactor 3 call sites) + ~20 test lines. **Risk:** Medium — refactoring 3 sites increases change surface; requires careful testing that all pause conditions are preserved.

### Q18 — Unified fix?

Items 1 and 2 do **not** share a root cause, so no unified fix applies. They should be fixed as separate executables.

**Recommended sequencing:**
1. Fix item 1 first (P0). Shape 1c (remove the pre-scan entirely) is the cleanest — it eliminates the loop class permanently with negative LOC. Shape 1a (step-number guard) is a reasonable alternative if the self-healing behavior is valued.
2. Fix item 2 second. Shape 2a (swap rename and verdict-post order) is the simplest. Shape 2b (startup recovery) is a good companion if daemon-restart recovery is desired as a separate BACKLOG item.

---

## Section G — Test coverage

### Q19 — Tests exercising the pre-scan rename on already-on-disk `processed-verdict-*` files

**File:** `tests/test_consume_verdicts.py`

Four tests exercise the pre-scan rename:

1. **`test_pre_scan_renames_processed_verdict_to_canonical`** (line 310): Tests that a `processed-verdict-*` file is renamed to `verdict-*` and consumed. Uses a `verdict-pending-*` plan that IS the correct pairing target. **Does NOT test a step mismatch scenario** (step-1 verdict paired with step-2-pending plan).

2. **`test_pre_scan_collision_guard_does_not_overwrite`** (line 373): Tests that the rename is skipped when the canonical target already exists. Exercises the collision guard, not the orphan guard.

3. **`test_pre_scan_skips_rename_when_no_paired_plan`** (line 515): Tests the orphan guard — rename skipped when no `verdict-pending-*` plan exists. Exercises the orphan check's slug match.

4. **`test_pre_scan_renames_when_verdict_pending_plan_exists`** (line 572): Tests that a `verdict-pending-*` plan enables the rename. **Does NOT verify step-number alignment.**

**Gap:** No test exercises the scenario where a `processed-verdict-*-step-1.md` file is on disk AND a `verdict-pending-*` plan is waiting on step 2 (not step 1). This is the exact failure mode of item 1. A test with this fixture would have caught the bug.

### Q20 — Tests for the final-step gate_failure → rename path

**File:** `tests/test_bellows.py`

Relevant tests:

1. **`test_run_plan_tears_down_worktree_after_final_gate`** (line 2104): Tests the auto-close path (gates pass), not the gate_failure path. Verifies teardown ordering, not rename.

2. **`test_run_plan_strict_pause_on_creation_failure`** (line 2153): Tests worktree creation failure (step 1). Verifies `verdict-pending-*` rename happens. Not a final-step test.

3. **`test_run_plan_pauses_on_cherry_pick_conflict`** (line 2193): Tests auto-close path with teardown failure. Verifies `verdict-pending-*` rename happens. Single-step plan, not final-step of multi-step.

4. **`test_mode_a_detected_and_recovered`** (line 2297): Tests Mode A recovery. Verifies plan is at `in-progress-*` or `verdict-pending-*`. Does not isolate the final-step gate_failure rename.

**Gap:** No test exercises a multi-step plan where the final step has a gate_failure and verifies the `in-progress-*` → `verdict-pending-*` rename occurs. All existing gate_failure/pause tests use single-step plans. The single-step tests confirm the rename works (same code path), but a multi-step final-step test would verify the execution path through the `while` loop exit followed by the post-loop pause block.

**Gap (not testable at unit level):** No test simulates daemon restart between verdict post and rename. This is the actual root cause of item 2, and it's an integration/recovery scenario, not a unit test target. Shape 2b (startup recovery scan) would be the testable mitigation.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced both code paths end-to-end per the diagnostic's 20-question investigation framework. For item 1 (the loop): identified the pre-scan rename at bellows.py:1129-1162 as the defective code path — it renames legitimately-processed `processed-verdict-*-step-N` files to canonical form whenever a `verdict-pending-*` plan exists for the same slug, regardless of step number. The main loop then consumes the renamed file as a fresh verdict, dispatching the plan for a step re-run. No natural termination mechanism exists. For item 2 (the rename-skip): confirmed the rename IS present in the final-step gate_failure path (bellows.py:618-620) and is structurally identical to the intermediate-step path. The rename-skip is caused by daemon restart (or exception) between verdict post (line 614) and rename (line 619), not by a branch asymmetry or missing code. Verified that items 1 and 2 are independent bugs in adjacent code regions with no shared root cause. Read BACKLOG entries, prior diagnostic and findings deposit, bellows.py, gates.py, verdict.py, architecture documents, reproduction verdict files, and test suites per the prescribed read order.

### Files Deposited
- `knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md` — diagnostic findings for Q1-Q20

### Files Created or Modified (Code)
- None — investigation only, no source modifications

### Decisions Made
- Classified item 1 root cause: pre-scan orphan guard at bellows.py:1146 matches slug without step-number comparison, causing re-consumption of legitimately-processed verdicts from prior steps
- Classified item 2 root cause: daemon-restart state loss (NOT a code branch asymmetry — the rename code IS present at bellows.py:618-620)
- Determined items are independent — no shared root cause, no shared code site
- Recommended fix sequencing: item 1 first (P0, active resource burn), item 2 second (lower priority, requires daemon restart to trigger)

### Flags for CEO
- None — single-step diagnostic, findings deposited for Planner review

### Flags for Next Step
- None — single-step diagnostic, no further steps
