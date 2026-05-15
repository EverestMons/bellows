# Failure 3 Mode B — Static Analysis Findings

**Date:** 2026-05-05
**Agent:** Bellows Developer
**Plan Reference:** `bellows/knowledge/decisions/in-progress-diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`

---

## Investigation Section 1 — `gates.check()` Call Sites

| File | Line | Enclosing Function | Plan State When Called |
|---|---|---|---|
| `bellows.py` | 314 | `run_plan()` | Post-step (first step completed, `in-progress-*`) |
| `bellows.py` | 378 | `run_plan()` (while loop body) | Post-step (subsequent steps, `in-progress-*`) |

**Call site 1 — line 314 (first step):**
```python
        # Capture post-step file state and run gates
        post_diff = _capture_git_diff(wt_path)
        files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
        gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
        print(f"Bellows: gates for {plan_name} step {current_step}: passed={gate_result['passed']}, is_qa={gate_result['is_qa_step']}, failures={len(gate_result['failures'])}")

        header = gate_result.get("plan_header", {})
        effective_auto_close = header.get("auto_close", "false").lower() == "true"
```

**Call site 2 — line 378 (loop steps):**
```python
            # Capture post-step file state and run gates
            post_diff = _capture_git_diff(wt_path)
            files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
            gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
            print(f"Bellows: gates for {plan_name} step {current_step}: passed={gate_result['passed']}, is_qa={gate_result['is_qa_step']}, failures={len(gate_result['failures'])}")
```

No other call sites in production code (`bellows.py`). Test files (`test_gates.py`, `test_consume_verdicts.py`) call `gates.check()` directly or mock it — not relevant to Mode B analysis.

---

## Investigation Section 2 — Done/ Move Sites

| File | Line | Enclosing Function | Trigger |
|---|---|---|---|
| `bellows.py` | 264 | `run_plan()` | `total_steps == 0` skip path — plan has no `## STEP` headers |
| `bellows.py` | 451 | `run_plan()` | Auto-close: final step + all gates passed + `effective_auto_close=True` |
| `bellows.py` | 914 | `_consume_verdicts()` | Continue verdict on terminal step (`step_number >= total_steps_c`) |

**Done/ move site 1 — line 264 (0-step skip):**
```python
        if total_steps == 0:
            print(f"Bellows: ⚠️  SKIPPED — {plan_name} has no ## STEP headers — not a standard executable")
            notifier.push(app_key, user_key, "Bellows — Skipped", f"Plan {plan_name} has no STEP headers — moved to Done without executing.")
            shutil.move(plan_path, os.path.join(plan_dir, "Done", base_filename))
            _delete_shadow(plan_filename)
            return
```

**Done/ move site 2 — line 451 (auto-close):**
```python
            _cleanup_verdicts_for_slug(verdict.slug_from_path(plan_path))
            if os.path.exists(source):
                shutil.move(source, done_path)
            _delete_shadow(plan_filename)
            notifier.push(app_key, user_key, "Bellows — Plan Complete",
                          f"Plan: {plan_name}\nAll gates passed. Auto-closed to Done. Total cost: ${total_cost:.4f}")
```

**Done/ move site 3 — line 914 (verdict continue-to-done):**
```python
                            if step_number >= total_steps_c:
                                # Final step — continue verdict means proceed to Done
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                                                      "continue-to-done",
                                                      "continue verdict on final step — moving to Done",
                                                      pause_reason_code=pause_reason_code_from_request)
                                done_dir = os.path.join(decisions_path, "Done")
                                os.makedirs(done_dir, exist_ok=True)
                                done_path = os.path.join(done_dir, original_name)
                                _cleanup_verdicts_for_slug(cleanup_slug)
                                shutil.move(full_plan_path, done_path)
                                _delete_shadow(original_name)
```

No `os.rename()` calls target Done/ anywhere in `bellows.py`.

---

## Investigation Section 3 — Post-Step Flow Ordering

The orchestration loop in `run_plan()` (lines 298–456) follows this exact sequence:

**First step (lines 298–318):**
1. `runner.run_step()` — execute `claude -p` subprocess (line 298)
2. `record_run()` — log step to DB (line 305)
3. `_capture_git_diff()` / `_parse_diff_stat()` — capture file changes (lines 312–313)
4. `gates.check()` — run gate evaluation (line 314)
5. Extract `effective_auto_close` from plan header (lines 317–318)

**While loop — non-final steps (lines 320–379):**
6. Check gate results — if failed/QA/pause → post verdict request → rename to `verdict-pending-*` → **return** (lines 322–352)
7. If all gates pass → run next step via `runner.run_step()` (line 360)
8. Increment step, `record_run()` (lines 366–373)
9. `_capture_git_diff()` / `_parse_diff_stat()` (lines 376–377)
10. `gates.check()` — gate evaluation for new step (line 378)
11. Loop back to step 6

**Final step exit (lines 381–456):**
12. Check gate results — if failed/QA/pause/verdict-requested OR `not effective_auto_close` → post verdict request → rename to `verdict-pending-*` → **return** (lines 384–416)
13. If all gates pass AND `effective_auto_close=True` → auto-close to Done/ (lines 421–456)

**Critical ordering answers:**
- (a) FIRST operation after step completion: `record_run()` (DB logging)
- (b) Gate evaluation: ALWAYS the next operation after DB logging + diff capture — lines 314 and 378
- (c) Done/ move: only at line 451, which is AFTER the gate check at line 314/378 AND guarded by `gate_result["passed"]` at line 421
- (d) NO path reaches Done/ without going through gate evaluation first — the auto-close Done/ move at line 451 is structurally impossible to reach without `gate_result` being set by a preceding `gates.check()` call

---

## Investigation Section 4 — Verdict Consumption Flow

**`_consume_verdicts()`** at lines 820–968:

**(a) Non-terminal step (`step_number < total_steps_c`):**
```python
                            else:
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                                                      pause_reason_code=pause_reason_code_from_request)
                                inprogress_name = f"in-progress-{original_name}"
                                inprogress_path = os.path.join(decisions_path, inprogress_name)
                                shutil.move(full_plan_path, inprogress_path)
                                print(f"Bellows: verdict continue — resuming {original_name}")
                                # Dispatch next step
                                self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```
Renames `verdict-pending-*` back to `in-progress-*`, dispatches next step via `handle_new_plan()`. **No gates.check() call.** Gates will run when the dispatched step completes (back in `run_plan()`).

**(b) Terminal step (`step_number >= total_steps_c`):**
```python
                            if step_number >= total_steps_c:
                                # Final step — continue verdict means proceed to Done
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                                                      "continue-to-done",
                                                      "continue verdict on final step — moving to Done",
                                                      pause_reason_code=pause_reason_code_from_request)
                                done_dir = os.path.join(decisions_path, "Done")
                                os.makedirs(done_dir, exist_ok=True)
                                done_path = os.path.join(done_dir, original_name)
                                _cleanup_verdicts_for_slug(cleanup_slug)
                                shutil.move(full_plan_path, done_path)
                                _delete_shadow(original_name)
```
Moves directly from `verdict-pending-*` to `Done/`. **No gates.check() re-evaluation.** The `gate_result` used in the ledger log is a stub constructed at line 886: `gate_result = {"failures": [], "files_changed": []}`. Gates were already evaluated when the step originally completed (in `run_plan()` at line 314/378), and the verdict request that paused the plan already captured those results. The continue verdict is the CEO's explicit approval to proceed.

---

## Investigation Section 5 — Auto-Close Path (`effective_auto_close=True`)

Lines 418–456:

```python
        # Auto-close: clean gates, no QA checkpoint, no header/verdict-request pause, and
        # effective_auto_close is True. Diagnostics default to NOT auto-close (pause for
        # verdict) unless auto_close: true is set in the plan header.
        if (gate_result["passed"]
                and not gate_result["is_qa_step"]
                and not header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
                and not gate_result.get("verdict_requested", {}).get("requested", False)
                and effective_auto_close):
            # Tear down worktree before auto-close
            try:
                _teardown_worktree(project_path, wt_path, plan_slug)
            except WorktreeTeardownError as e:
                # Cherry-pick conflict on auto-close — convert to gate_failure pause
                print(f"Bellows: ❌ worktree teardown failed on auto-close for {plan_slug}: {e}")
                log_path = str(BELLOWS_ROOT / "logs")
                gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
                gate_result["passed"] = False
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
                                             pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text)
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                print(f"Bellows: ⏸️  PAUSED — {plan_name} — worktree teardown failed, awaiting CEO verdict")
                return
            verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",
                                  "all gates passed, auto_close enabled — auto-closing",
                                  pause_reason_code="auto_close")
            done_dir = os.path.join(plan_dir, "Done")
            os.makedirs(done_dir, exist_ok=True)
            done_path = os.path.join(done_dir, base_filename)
            source = inprogress_path if os.path.exists(inprogress_path) else plan_path
            _cleanup_verdicts_for_slug(verdict.slug_from_path(plan_path))
            if os.path.exists(source):
                shutil.move(source, done_path)
```

**Gate check relative to Done/ move:** The `if` guard at line 421 requires `gate_result["passed"]` — the same `gate_result` variable that was set by `gates.check()` at line 314/378. The gate check is structurally upstream. No code path reaches line 451 without `gate_result` being populated by a real `gates.check()` call.

**Worktree teardown failure safety:** If worktree teardown fails, the auto-close path converts to a verdict-pending pause (lines 430–441) — it does NOT proceed to Done/.

---

## Investigation Section 6 — Disable-Auto-Close Path (Default)

When `effective_auto_close=False` (the default), the flow is:

1. Final step completes
2. `gates.check()` runs (line 314/378) — `gate_result` populated
3. The conditional at line 384 fires because `not effective_auto_close` is True → enters the verdict-request pause block
4. `verdict.post_verdict_request()` posts the verdict request (line 406) — gate results are included
5. Plan renamed to `verdict-pending-*` (line 412)
6. `run_plan()` returns
7. *...time passes...CEO or Planner deposits continue verdict...*
8. `_consume_verdicts()` reads the verdict (line 867)
9. `step_number >= total_steps_c` check passes (line 904)
10. Plan moved to Done/ (line 914) — **NO gates.check() re-evaluation**

**Confirmed:** Bellows does NOT re-run gates when consuming the terminal-step continue verdict. It trusts that:
- Gates were already run when the step completed (step 2 above)
- The verdict request captured those gate results
- The continue verdict is the CEO/Planner's explicit approval

This is by design, not a bug: the verdict IS the gate override mechanism.

---

## Investigation Section 7 — Race Conditions and Skip Paths

**(a) Error-handling branches that move plans to Done/ on exceptions:**
```python
    except Exception as e:
        print(f"Bellows: ❌ FAILED — {plan_name}: {e}")
        notifier.notify_failure(app_key, user_key, plan_name, current_step if 'current_step' in dir() else 0, str(e))
```
(Line 458–460) — The top-level exception handler does **NOT** move the plan to Done/. It only prints the error and notifies. The plan remains in `in-progress-*` state (stale but not falsely completed).

**(b) Timeout handlers that close plans:**
Runner timeouts are handled in `runner.py` and surface as `is_error=True` in `parsed`. This flows through `gates.check()` which fails the `no_errors` gate → plan enters verdict-pending, never auto-closes. **No bypass.**

**(c) Manual override flags or environment variables that disable gates:**
Grep for `os.environ`, `getenv`, `DISABLE`, `SKIP.*GATE`, `NO.*GATE` returned **zero matches** in `bellows.py`. There are no environment variables or flags that disable gate evaluation.

**(d) `try/except` that swallows gate evaluation failures:**
`gates.check()` calls are not wrapped in `try/except` blocks. If `gates.check()` throws an uncaught exception, it would bubble up to the top-level handler at line 458, which does NOT move to Done/. **No swallowed gate failures can lead to Done/.**

**(e) Any condition where a plan reaches Done/ via a path that does not flow through `gates.check()`:**
- **Line 264 (0-step skip):** Moves to Done/ without `gates.check()`. However, this fires ONLY when `total_steps == 0` — the plan has no `## STEP` headers and is not a standard executable. This is a cleanup path, not an execution path. No step was dispatched, so there are no gates to evaluate. **Not a Mode B concern.**
- **Line 914 (verdict continue-to-done):** Moves to Done/ without *re-running* `gates.check()`. Gates WERE run when the step originally completed (line 314/378). The Done/ move is gated by the CEO's continue verdict, not by a second gate evaluation. **Not a Mode B concern — gates ran before the verdict request was posted.**

**(f) Race conditions between gate evaluation and state transitions:**
All operations in `run_plan()` are sequential within a single thread/coroutine. The `gate_result` variable is assigned before any conditional that reads it. There is no async or threaded execution within `run_plan()` that could cause a race between gate evaluation and the Done/ move. **No race condition.**

---

## Findings

### Question A: Where does `gates.check()` get called in the post-step flow, and where does the Done/ move happen — are gates ALWAYS evaluated before any Done/ move?

Gates are evaluated at lines 314 and 378, immediately after each step's subprocess returns and diff is captured. The auto-close Done/ move at line 451 is guarded by `gate_result["passed"]` at line 421 — structurally impossible to reach without a preceding `gates.check()` call. The verdict continue-to-done Done/ move at line 914 does not re-run gates, but gates were already evaluated before the verdict request was posted. The 0-step skip Done/ move at line 264 bypasses gates intentionally (no step was executed). **Answer: Yes, gates are always evaluated before any Done/ move for plans that execute steps.**

### Question B: In the disable-auto-close terminal-step path (the default), does Bellows re-run gates when consuming the continue verdict, or trust the original evaluation?

**Trust the original evaluation.** `_consume_verdicts()` constructs a stub `gate_result = {"failures": [], "files_changed": []}` at line 886 — used only for ledger logging, not for any gate evaluation. The continue verdict is treated as the CEO's explicit approval to proceed, implicitly endorsing the gate results from the original step completion.

### Question C: In the auto-close terminal-step path, where does the gate check fit relative to the Done/ move?

Gates are evaluated at line 314/378 (after step completion). The auto-close Done/ move at line 451 is inside a conditional block (line 421) that requires `gate_result["passed"]` to be `True`. **Gate check is always upstream of the Done/ move in the auto-close path.** Additionally, if worktree teardown fails during auto-close, the path converts to a verdict-pending pause (line 430–441) rather than proceeding to Done/.

### Question D: Are there any race conditions, error paths, or skip paths that could let a plan reach Done/ without complete gate evaluation?

**No.** Specifically:
- The top-level exception handler (line 458) does NOT move to Done/
- No environment variables or flags disable gates
- No `try/except` swallows gate evaluation failures before the Done/ move
- All operations in `run_plan()` are sequential — no threading races
- The 0-step skip path (line 264) bypasses gates intentionally for non-executable plans (no steps dispatched)

### Question E: Based on (A)–(D), is Mode B structurally possible in current code?

**No.** Mode B (Bellows moves a plan to Done/ before its own gate evaluation completes for the relevant step) is **not structurally possible** in the current code. Every path to Done/ for plans that execute steps flows through `gates.check()` before reaching the Done/ transition:

1. **Auto-close path** (line 451): guarded by `gate_result["passed"]` at line 421, which requires `gates.check()` to have been called at line 314/378.
2. **Verdict continue-to-done path** (line 914): gates were evaluated at line 314/378 before the verdict request was posted. The continue verdict is the CEO's explicit override — it does not bypass gates, it approves despite/after them.
3. **0-step skip path** (line 264): no step was executed, so no gates are applicable. Intentional cleanup, not Mode B.

There are no race conditions, error paths, skip flags, or exception handlers that could move a plan to Done/ without gate evaluation having completed for the relevant step.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Static analysis of all code paths in `bellows.py` that lead to a Done/ move, mapped against all `gates.check()` call sites. Confirmed that Mode B (Bellows moves to Done/ before gate evaluation) is structurally impossible in current code.

### Files Deposited
- `bellows/knowledge/research/failure-3-mode-b-static-analysis-findings-2026-05-05.md` — Full investigation with verbatim code, flow maps, and five answered questions

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified the 0-step skip path (line 264) as intentional cleanup, not a Mode B concern
- Classified the verdict continue-to-done path (line 914) as trust-original-evaluation by design, not a gate bypass

### Flags for CEO
- None — Mode B is not a bug. All three Done/ paths are structurally sound.

### Flags for Next Step
- None
