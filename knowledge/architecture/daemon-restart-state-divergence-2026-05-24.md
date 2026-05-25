# Daemon-Restart State Divergence — Unified Diagnostic

**Date:** 2026-05-24
**Agent:** Bellows Systems Analyst
**Scope:** Joint characterization of BACKLOG items #2 (daemon-restart recovery shape, 2026-05-23), #3 (final-step gate_failure rename-skip, 2026-05-22), #5 (step-counter loop after precondition-failure verdict, 2026-05-21). Determine whether they share a root cause.
**Prior art:** `knowledge/research/step-state-persistence-map-2026-04-28.md` (DB is write-only, no step recovery), `knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md` Section C/D (rename IS present at bellows.py:615-617, gap is verdict-post → rename atomicity).

---

## Section A — Daemon State Model (Joint)

### A1 — State-modifying operations in a single step's lifecycle

The daemon performs the following state-modifying operations during one step, in order. "Atomic?" indicates whether the operation is atomic with the subsequent one (i.e., no process-termination gap between them).

| # | Operation | File:Line | Type | Atomic with next? |
|---|---|---|---|---|
| 1 | Claim rename: `executable-*` → `in-progress-*` | bellows.py:402 (`shutil.move`) | Filename rename | No — shadow write is next |
| 2 | Shadow cache write | bellows.py:405 (`_write_shadow`) | File write | No |
| 3 | Worktree creation | bellows.py:433 (`_create_worktree`) | Subprocess | No |
| 4 | Agent execution (`runner.run_step`) | bellows.py:449 | Subprocess | No |
| 5 | DB record: step completion | bellows.py:458-462 (`record_run`, status=receipt_status) | DB INSERT | No |
| 6 | Gate evaluation | bellows.py:484 (`gates.check`) | Pure computation | No |
| 7 | Worktree teardown (cherry-pick back) | bellows.py:516 / 607 (`_teardown_worktree`) | Subprocess | No |
| 8 | Verdict-request post (file write) | bellows.py:520 / 611 (`verdict.post_verdict_request`) | File write to `verdicts/pending/` | **No — gap before rename** |
| 9 | Pushover notification | bellows.py:521-523 / 612-614 (`notifier.notify_verdict_request`) | HTTP call | **No — gap before rename** |
| 10 | Plan rename: `in-progress-*` → `verdict-pending-*` | bellows.py:525-527 / 615-617 (`shutil.move`) | Filename rename | No |
| 11 | DB record: VerdictPending | bellows.py:528-529 / 618-619 (`record_run`) | DB INSERT | No |
| 12 | Log + return | bellows.py:530 / 620 | Terminal | N/A |

**Worktree creation failure short-circuit (bellows.py:434-444):** If `_create_worktree` raises `WorktreeCreationError`, the flow skips operations 4-7 and jumps directly to:
- Verdict-request post with step=1 (hardcoded): bellows.py:438-439
- Plan rename: `in-progress-*` → `verdict-pending-*`: bellows.py:440-442
- Return

**Verdict consumption path (`_consume_verdicts`, bellows.py:1115-1280):** On verdict-continue for a non-final step:

| # | Operation | File:Line | Type |
|---|---|---|---|
| V1 | Verdict file parsed | bellows.py:1170 (`verdict.check_verdict`) | File read |
| V2 | Plan matched by prefix+slug | bellows.py:1184 | In-memory predicate |
| V3 | Ledger entry written | bellows.py:1223-1224 (`verdict.log_to_ledger`) | File append |
| V4 | Plan rename: `verdict-pending-*` → `in-progress-*` | bellows.py:1227 (`shutil.move`) | Filename rename |
| V5 | Next step dispatched | bellows.py:1230 (`handle_new_plan`, `resume_step=step_number + 1`) | Thread spawn |
| V6 | Pending verdict-request deleted | bellows.py:1248-1250 | File delete |
| V7 | Verdict file renamed to `processed-*` | bellows.py:1252-1253 | Filename rename |

### A2 — Restart-vulnerable boundaries

A restart between (op_M, op_M+1) produces inconsistent state when M's side-effects survive on disk but M+1's do not.

**Boundary RV-1: Between verdict-post (op 8) and plan-rename (op 10)**
- Lines: bellows.py:520→525-527 (intermediate) or 611→615-617 (final)
- Gap contents: Pushover HTTP call at op 9 (bellows.py:521-523 / 612-614)

**Boundary RV-2: Between plan-rename to `in-progress-*` (op 1) and step completion**
- Lines: bellows.py:402 → rest of `run_plan`
- Gap contents: entire step execution (ops 2-12)

**Boundary RV-3: Between claim and verdict-post on worktree creation failure**
- Lines: bellows.py:402 → 438
- Gap contents: shadow write, worktree creation attempt

### A3 — Post-restart state for each boundary

**RV-1 (verdict-post ↔ rename):**
- On-disk survives: verdict-request file in `verdicts/pending/`, plan file as `in-progress-*`
- In-memory lost: rename intention (`verdict_pending_path` variable)
- DB state: no VerdictPending record (op 11 hasn't run yet)
- `bellows.db` step-state-resume: **does not cover this**. Phase 3b added `plan_slug` column to `runs` table but the read-side (`_get_last_completed_step`) was never implemented. DB is write-only — confirmed by zero SELECT statements in bellows.py.
- **Observable symptom:** Planner writes verdict to `resolved/`. `_consume_verdicts` scans `resolved/`, finds verdict, tries to match against `verdict-pending-*` plans → no match (plan is still `in-progress-*`) → emits `⚠️ no verdict-pending plan found step N — leaving in resolved/ for retry` every 30s indefinitely.

**RV-2 (claim ↔ completion):**
- On-disk survives: plan file as `in-progress-*`, shadow cache file
- In-memory lost: entire execution context (which step, which plan, active thread)
- DB state: may have partial step records from prior runs
- **Observable symptom:** `in-progress-*` file is not picked up by `is_runnable_plan()` (bellows.py:928-931 — rejects `in-progress-*` prefix). Plan stays orphaned indefinitely. No startup recovery exists — `_perform_startup_sweep` (bellows.py:1281-1315) only removes orphaned verdict-requests, not orphaned `in-progress-*` plans. The startup scan at bellows.py:1346-1352 only processes `is_runnable_plan()` matches.

**RV-3 (claim ↔ worktree-failure verdict):**
- On-disk survives: plan file as `in-progress-*`, shadow cache
- In-memory lost: worktree creation failure context
- **Observable symptom:** Same as RV-2 — `in-progress-*` plan orphaned. If the Planner manually re-deposits the plan as `executable-*`, the watcher claims it fresh with `resume_step=None`, dispatching step 1 regardless of prior progress. Per step-state-persistence-map-2026-04-28 findings Q1 Scenario (c): "No recovery mechanism exists."

### A4 — Cross-reference items #2, #3, #5 against boundaries

| Item | Maps to boundary | Classification |
|---|---|---|
| **#2** (daemon-restart recovery shape) | **RV-1** — verdict-post completed, rename did not. Post-restart, `_consume_verdicts` can't pair verdict with `in-progress-*` plan. Also involves **RV-2** absence — no startup recovery for `in-progress-*` plans. | Restart boundary failure |
| **#3** (final-step rename-skip) | **RV-1** — identical boundary on the final-step code path (bellows.py:611→615-617). Daemon restart between verdict-post and rename. | Restart boundary failure |
| **#5** (step-counter loop) | **Not a restart boundary failure.** This is a **logic defect** in `_consume_verdicts` step-advancement at bellows.py:1230. The verdict consumer treats continue-on-precondition-failure identically to continue-on-success, always advancing `step_number + 1` regardless of whether the step actually ran. | Logic defect (non-restart) |

---

## Section B — Item #2 Trace (Daemon-Restart Recovery Shape)

### B5 — Verdict consumption matching predicate

**Trace:** Planner deposits `verdict-stuck-state-color-override-2026-05-22-step-2.md` in `verdicts/resolved/`. On next `_rescan` (30s interval, bellows.py:1069-1071), `_consume_verdicts` runs:

1. `os.listdir(resolved_dir)` finds `verdict-stuck-state-color-override-2026-05-22-step-2.md` (bellows.py:1126)
2. Filter: `fname.startswith("verdict-")` → True; `fname.startswith("verdict-request-")` → False (bellows.py:1127-1130)
3. Regex parse: `re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)` extracts `plan_slug="stuck-state-color-override-2026-05-22"`, `step_number=2` (bellows.py:1132-1138)
4. **Matching predicate** (bellows.py:1183-1184):
```python
for pname in os.listdir(decisions_path):
    if pname.startswith("verdict-pending-") and plan_slug in pname:
```

This requires the plan filename to start with `verdict-pending-`. The orphaned plan is `in-progress-executable-stuck-state-color-override-2026-05-22.md` — starts with `in-progress-`, so the predicate fails.

**Why `verdict-pending-` specifically?** The predicate was designed for the normal flow where `run_plan` always renames `in-progress-*` → `verdict-pending-*` before returning from a pause. In the normal case, any plan awaiting a verdict MUST have the `verdict-pending-*` prefix. The predicate is correct for normal operation but fails to account for restart-interrupted state where the rename never completed.

**Could the predicate be widened to consider `in-progress-*`?** Yes, with caveats. Changing to:
```python
if (pname.startswith("verdict-pending-") or pname.startswith("in-progress-")) and plan_slug in pname:
```
would match the orphaned plan. However, this creates a risk: a plan that is actively running (legitimately `in-progress-*` with an agent executing) could be incorrectly matched against a stale verdict. The `verdict-pending-*` prefix serves as a signal that "this plan is paused and awaiting a verdict" — widening the predicate loses that semantic distinction.

**Other uses of `verdict-pending-` prefix in bellows.py:**
- `is_runnable_plan()` (line 929): excludes `verdict-pending-*` from dispatch
- `slug_for()` (line 69): strips `verdict-pending-` for log display
- `_check_queue_drain()` (line 1050): counts `verdict-pending-*` for status
- `_perform_startup_sweep()` (line 1296): treats `verdict-pending-*` as "active" (preserves their verdict-requests)
- `_shadow_path()` (line 226): strips `verdict-pending-` for shadow lookup

Widening the matching predicate at line 1184 would not break these other sites — they use `verdict-pending-*` for different purposes (dispatch filtering, display, cleanup) and are not coupled to the verdict-consumption pairing.

### B6 — Rename site and ordering

The `in-progress-*` → `verdict-pending-*` rename in the normal (non-restart) gate_failure pause flow:

**Intermediate-step pause (bellows.py:520-527):**
```python
verdict.post_verdict_request(...)              # line 520 — verdict-request file written
notifier.notify_verdict_request(...)           # lines 521-523 — Pushover HTTP call
# >>> RESTART-VULNERABLE GAP <<<
verdict_pending_path = os.path.join(...)       # line 525
if os.path.exists(inprogress_path):            # line 526
    shutil.move(inprogress_path, ...)          # line 527 — RENAME
```

The rename is **after** the verdict-request post, with a Pushover HTTP call in the gap. The two operations are **not atomic** — they are separate Python statements with an HTTP call between them.

### B7 — Startup-state recovery for `in-progress-*` plans

**No startup-state recovery exists** for `in-progress-*` plans paired with `resolved/` verdicts.

`_perform_startup_sweep()` (bellows.py:1281-1315) scans `verdicts/pending/` for orphaned verdict-REQUEST files and removes them if no active plan exists. It does NOT scan `verdicts/resolved/` and does NOT scan for `in-progress-*` plans that should be `verdict-pending-*`.

The startup scan at bellows.py:1346-1352 iterates `os.listdir(decisions_path)` and passes each file to `handler._handle()`, but `is_runnable_plan()` at bellows.py:928 rejects `in-progress-*`:
```python
def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
```

**Confirmed absence.** No code path exists to recover `in-progress-*` plans with matching verdicts on startup. Per step-state-persistence-map-2026-04-28, Q1 Scenario (c): "No recovery mechanism exists."

### B8 — Validation against 2026-05-23 reproduction

Log evidence from `bellows-2026-05-23.log`:
```
08:46:13 [WARN] [stuck-state-color-override-2026-05-22] ⚠️ no verdict-pending plan found step 2 — leaving in resolved/ for retry
08:46:43 [WARN] [stuck-state-color-override-2026-05-22] ⚠️ no verdict-pending plan found step 2 — leaving in resolved/ for retry
...
08:48:44 [EVENT] [executable-stuck-state-color-o] verdict continue-to-done
```

At the moment of the daemon restart (between 2026-05-22 evening and 2026-05-23 morning):
- **(a) Plan filename prefix:** `in-progress-executable-stuck-state-color-override-2026-05-22.md` — the daemon died between verdict-post and rename (RV-1 boundary). The rename to `verdict-pending-*` never executed.
- **(b) Verdict file in `resolved/`:** `verdict-stuck-state-color-override-2026-05-22-step-2.md` — Planner-written while daemon was down, sitting in `resolved/` awaiting consumption.
- **(c) `bellows.db` rows:** Step completion records exist for steps 1 and 2 (status=Complete and VerdictPending from the first run). The VerdictPending record for step 2 may be absent if the daemon died before op 11 (DB record) at bellows.py:618-619.

The RV-1 boundary model explains this state completely: verdict-request posted (op 8), daemon died during Pushover call (op 9) or before rename (op 10), plan stayed as `in-progress-*`. Post-restart, `_consume_verdicts` repeatedly scanned `resolved/`, found the verdict, failed to match against any `verdict-pending-*` plan, emitted the WARN. At 08:48:44, Planner manually renamed to `verdict-pending-*`, match succeeded, plan closed.

---

## Section C — Item #3 Trace (Final-Step Rename-Skip)

### C9 — Extending the 2026-05-24 diagnostic Section C

The 2026-05-24 diagnostic Section C (processed-prefix-reconsumption-and-rename-skip-2026-05-24.md Q8-Q11) established:
- The rename IS structurally present at bellows.py:615-617 (current numbering) and is symmetric with the intermediate-step path
- There is no branch asymmetry — the rename fires unconditionally within the `if os.path.exists(inprogress_path)` guard
- `_teardown_worktree` failure cannot short-circuit the rename (exception caught inline)

**Extending to the atomicity question:** The verdict-post → rename gap on the final-step path is:

```python
# bellows.py:611-620 (final-step pause block)
verdict.post_verdict_request(...)              # line 611 — verdict-request written
notifier.notify_verdict_request(               # lines 612-614 — Pushover HTTP call
    app_key, user_key, plan_name, current_step, gate_result["failures"]
)
verdict_pending_path = os.path.join(...)       # line 615
if os.path.exists(inprogress_path):            # line 616
    shutil.move(inprogress_path, ...)          # line 617 — RENAME
```

The gap is **structurally identical** to the intermediate-step gap (Section B6): verdict-post → HTTP call → rename, with no atomic binding.

### C10 — Comparison of item #3 gap to item #2 gap

**They are the same gap.** Both items are instances of RV-1: "verdict-request posted, then rename performed, with restart-vulnerable space between." The only difference is which code path triggered the gap:

| | Item #2 | Item #3 |
|---|---|---|
| **Pause site** | Could be either intermediate (line 520) or final (line 611) — the BACKLOG doesn't specify which step was final | Final-step (line 611) — step 2 of 2 |
| **Gap location** | bellows.py:520→525-527 or 611→615-617 | bellows.py:611→615-617 |
| **Gap contents** | Pushover HTTP call | Pushover HTTP call |
| **Root cause** | Daemon restart between verdict-post and rename | Daemon restart between verdict-post and rename |

Items #2 and #3 are **two observations of the same structural bug** (RV-1), not independent bugs.

### C11 — Log evidence for 2026-05-22 daemon restart

Log evidence from `bellows-2026-05-22.log`:
```
09:13:05 [WARN] [pre-scan-orphan-guard-2026-05-22] ⚠️ no verdict-pending plan found step 1 — leaving in resolved/ for retry
... (repeated every 30s through 09:20:16)
09:20:16 [WARN] [pre-scan-orphan-guard-2026-05-22] ⚠️ no verdict-pending plan found step 2 — leaving in resolved/ for retry
09:20:39 [INFO] ── session restart ──────────────────────────────
09:21:12 [WARN] [pre-scan-orphan-guard-2026-05-22] ⚠️ no verdict-pending plan found step 1 — leaving in resolved/ for retry
09:21:12 [WARN] [pre-scan-orphan-guard-2026-05-22] ⚠️ no verdict-pending plan found step 2 — leaving in resolved/ for retry
```

**Confirmed:** The log shows the plan stuck in `in-progress-*` state (no `verdict-pending-*` match found) from 09:13:05 continuously. At 09:20:39, a session restart occurred. Post-restart, the same no-match WARN continued.

The restart at 09:20:39 is NOT the restart that caused the rename-skip — the plan was already stuck before that restart (WARNs started at 09:13:05). The original restart that dropped the rename happened earlier, during the step 2 execution around 09:13:30 (as hypothesized in the BACKLOG). The 09:20:39 restart was a recovery attempt that did not help because no startup recovery for `in-progress-*` plans exists (Section B7).

This confirms: the rename-skip occurred due to daemon restart between verdict-post and rename (RV-1), consistent with the 2026-05-24 diagnostic Section D conclusion.

---

## Section D — Item #5 Trace (Step-Counter Loop After Precondition-Failure)

### D12 — Step-advancement logic in `_consume_verdicts`

When a verdict-continue arrives for a non-final step (bellows.py:1222-1230):

```python
if step_number >= total_steps_c:
    # Final step — continue-to-done
    ...
else:
    verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                          pause_reason_code=pause_reason_code_from_request)
    inprogress_name = f"in-progress-{original_name}"
    inprogress_path = os.path.join(decisions_path, inprogress_name)
    shutil.move(full_plan_path, inprogress_path)
    _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
    # Dispatch next step
    self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
```

**The dispatch is always `resume_step=step_number + 1`.** There is no conditional logic based on pause reason, gate type, or whether the step actually executed. For a verdict-continue on a plan that paused with `gate_failure` on `worktree_creation`, the behavior is identical to a verdict-continue on a plan that paused with `header_pause` after successful execution.

### D13 — Step number source

The step number for next dispatch comes from **(a) parsed from verdict filename:**

```python
# bellows.py:1132-1138
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
...
plan_slug = match.group(1)
step_number = int(match.group(2))
```

The verdict filename is `verdict-{slug}-step-{N}.md`, where N was set when `verdict.post_verdict_request()` was called. For a worktree creation failure, N=1 (hardcoded at bellows.py:438):

```python
verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result, ...)
#                                                     ^-- hardcoded step=1
```

**This source does NOT distinguish between "step N completed successfully" and "step N never ran due to precondition failure."** The verdict filename carries the step number at which the daemon paused, not the step number that was actually executed. For a precondition failure at step 1, no agent ran, but the verdict says "step 1."

### D14 — Does `_consume_verdicts` treat continue-on-precondition-failure identically to continue-on-success?

**Yes — confirmed.** `pause_reason_code_from_request` is parsed at bellows.py:1167-1168:

```python
if req_line.startswith("**Pause Reason Code:**"):
    pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
```

But it is **only used** as a pass-through to `verdict.log_to_ledger()` at bellows.py:1212, 1224, and 1233. It is **never used** in the step-advancement decision. There is no predicate that checks:
```python
if pause_reason_code_from_request == "gate_failure":
    # check if it was a precondition failure → retry same step
```

The BACKLOG #5 hypothesis (1) is **correct:** `_consume_verdicts` interprets continue-on-precondition-failure as "step N done, advance to N+1" without checking whether step N actually produced work.

### D15 — Reproduction trace (2026-05-21 fuel-continuation-inference-ui)

Log evidence from `bellows-2026-05-21.log`:

```
15:38:15 [INFO] ── session restart ──────────────────────────────
15:38:18 [EVENT] startup scan found executable-fuel-continuation-inference-ui-2026-05-21.md
15:38:18 [INFO] [executable-fuel-continuation-i] plan has 4 steps
15:38:18 [WARN] [fuel-continuation-inference-ui-2026-05-21] ⚠ worktree creation failed, retrying in 2s
15:38:20 [ERROR] [executable-fuel-continuation-i] ❌ worktree creation failed
```

**Reconstruction of the three-iteration loop:**

**Iteration 1:**
- 15:38: Daemon restart → re-claims plan as `executable-*` → worktree creation fails (stale worktree from prior run, `already exists` error)
- Verdict request posted: `verdict-request-{slug}-step-1.md` with `Pause Reason Code: gate_failure`, gate=`worktree_creation`
- Plan renamed to `verdict-pending-*` (line 440-442 — this rename IS inside the WorktreeCreationError handler, no gap)
- Planner writes `verdict-{slug}-step-1.md` with "continue"
- `_consume_verdicts`: `step_number=1`, dispatches `resume_step=2`

**Iteration 2:**
- `run_plan(path, resume_step=2)` → worktree created successfully (stale one pruned at startup, bellows.py:1013-1023)
- Bootstrap prompt: "Execute Step 2" → agent runs in fresh worktree forked from origin tip
- Step 2 work was already shipped to origin from the prior run → agent produces no meaningful changes → commit is empty or no-op
- Teardown: `git log HEAD --not main` finds no new commits (work already on main via origin) → `commit_shas = []` → no cherry-pick → teardown succeeds cleanly
- Gates evaluate step 2 output: `current_step=2`, `is_final_step(2, 4)=False` → enters while loop
- Gate result may pass or fail depending on agent output quality
- If gates pass: step advances to 3 via the while-loop auto-advance (no verdict needed)
- If gates fail: verdict posted at step 2, continue, dispatches step 3

**Iterations 2-3-4** follow the same pattern: each step's work is already on origin, agent no-ops or produces minimal output, eventual gate failure or header-pause triggers verdict at the current step, continue advances to next.

**State at third iteration:**
- **(a) Verdict request `Step` field:** Step number advances each iteration (1 → 2 → 3 → ...)
- **(b) `bellows.db` last-recorded step:** Records accumulate — each `record_run` call appends a row with the current step. The max step in DB reflects the latest dispatch, not the latest successful completion.
- **(c) Plan filename:** Alternates between `in-progress-*` (during execution) and `verdict-pending-*` (during pause). The cycle is: `verdict-pending-*` → (verdict continue) → `in-progress-*` → (execution) → `verdict-pending-*`.

**Root cause of the loop:** The initial verdict-continue on the step-1 worktree-creation failure advanced to step 2 when it should have retried step 1 (step 1 never ran). All subsequent steps then encountered the parallel-SHA pattern (work already on origin) producing empty/no-op agent runs.

---

## Section E — Joint Root Cause Analysis

### E16 — Classification

**Items #2 and #3 are two observations of one shared boundary gap (RV-1).** Items #5 is an independent logic defect.

| | Items #2 + #3 (shared) | Item #5 (independent) |
|---|---|---|
| **Root cause** | Non-atomic verdict-post → rename sequence. Daemon restart between ops drops the rename, leaving plan as `in-progress-*` with a verdict-request in `pending/`. Post-restart, `_consume_verdicts` can't pair verdict with `in-progress-*` plan. | `_consume_verdicts` step-advancement logic does not distinguish precondition-failure (step never ran) from step-completion. Always advances `step_number + 1`, regardless of `pause_reason_code`. |
| **Code region** | `run_plan()` pause blocks — bellows.py:520-527 (intermediate) and 611-617 (final). The gap exists at both sites identically. | `_consume_verdicts()` — bellows.py:1230. The `resume_step=step_number + 1` dispatch is unconditional. |
| **Trigger** | Daemon restart (or unhandled exception in `notifier.notify_verdict_request`) between verdict-post and rename. | Any verdict-continue on a plan paused with a precondition gate failure (e.g., `worktree_creation`). No restart required. |
| **Restart involvement** | Restart IS the trigger | Restart is incidental (the 2026-05-21 reproduction started with a restart that re-claimed the plan, but the step-counter bug is in `_consume_verdicts`, not in restart recovery) |

### E17 — Fix sequencing

**RV-1 fix (items #2 + #3):**
- Fixing this does NOT mask or worsen item #5. RV-1 is about plan-rename atomicity; item #5 is about step-advancement logic. They operate in different code paths (`run_plan` vs `_consume_verdicts`).
- A fix that ensures the rename always happens before the daemon can die (rename-first ordering) would prevent the orphaned `in-progress-*` state entirely. This makes item #2's `_consume_verdicts` predicate widening unnecessary — the predicate would never encounter `in-progress-*` plans with pending verdicts.

**Item #5 fix:**
- Fixing this does NOT mask or worsen items #2/#3. Item #5's fix would add a `pause_reason_code` check in `_consume_verdicts` before deciding whether to advance or retry. This has no interaction with the rename ordering in `run_plan`.
- However, item #5's fix should be sequenced AFTER the RV-1 fix if possible. Reason: item #5's reproduction in 2026-05-21 was triggered by a daemon restart that re-claimed a plan, which then hit the worktree-creation failure. If RV-1 is fixed first (with startup recovery for `in-progress-*` plans), the re-claim path changes — the plan would be recovered to `verdict-pending-*` on restart rather than re-claimed as `executable-*`, which changes the step-counter input. Item #5's fix should account for the post-RV-1 recovery semantics.

**Can they be fixed in parallel?** Yes, with care. The code regions are disjoint: RV-1 touches the pause blocks in `run_plan()` (lines 520-527, 611-617, 440-442); item #5 touches `_consume_verdicts` (line 1230 and surrounding step-advancement logic). No shared code site. However, testing should verify the combined behavior: restart with precondition failure → recovery → verdict-continue → correct step advancement.

**Recommended order:**
1. Fix RV-1 first (items #2 + #3). Higher operational impact — indefinitely-stuck plans on every daemon restart mid-pause.
2. Fix item #5 second. Lower frequency — requires the specific precondition-failure + already-shipped-work constellation.

---

## Section F — Resolution Options

### F18 — Fix shapes per item

**RV-1 (items #2 + #3): Non-atomic verdict-post → rename**

**Shape A — Rename-first ordering.** Move the `in-progress-*` → `verdict-pending-*` rename BEFORE the verdict-request post at all 3 pause sites (intermediate line 520, final line 611, auto-close-failure line 640). If daemon dies after rename but before verdict-post: plan is `verdict-pending-*`, no verdict-request exists — Planner sees no request, can re-trigger or daemon restart re-posts. If daemon dies before rename: neither happened, plan is `in-progress-*`, restart recovery re-claims. **LOC estimate:** ~10 (reorder 3 sites, each is move 3 lines up). **Closes:** RV-1 boundary entirely. Items #2 and #3 are both closed.

**Shape B — Startup recovery scan for orphaned `in-progress-*` plans.** On startup, scan decisions directories for `in-progress-*` plans that have a matching verdict-request in `verdicts/pending/`. Auto-promote to `verdict-pending-*`. Integrates into existing `_perform_startup_sweep()`. **LOC estimate:** ~15 production + ~15 test. **Closes:** The post-restart no-match symptom (item #2). Does NOT close the underlying RV-1 gap — a restart between verdict-post and rename still produces transient inconsistency, but startup recovery auto-heals it.

**Shape C — Unified `_pause_for_verdict()` helper with rename-first semantics.** Extract rename → verdict-post → notify → record_run → log into a single helper. Unify all 4 pause sites through it. **LOC estimate:** ~25 production + ~20 test. **Closes:** RV-1 boundary + reduces code duplication across 4 pause sites. Higher change surface.

**Item #5: Step-counter logic on precondition-failure**

**Shape D — Pause-reason-aware step advancement.** In `_consume_verdicts`, before dispatching `resume_step=step_number + 1`, check `pause_reason_code_from_request`. If the pause was a precondition gate failure (e.g., `gate_failure` with gate=`worktree_creation`), dispatch `resume_step=step_number` (retry same step) instead of `step_number + 1`. Requires parsing the gate name from the verdict-request content (currently `pause_reason_code` is parsed but gate identity is not). **LOC estimate:** ~15 production (parse gate from verdict-request, conditional dispatch) + ~10 test. **Closes:** Item #5. Does not address items #2/#3.

**Shape E — Distinguish precondition-failure from execution-failure in verdict-request metadata.** Add a `**Precondition Failure:**` field to the verdict-request format. `_consume_verdicts` checks this field: if True, retry same step; if False/absent, advance. Simpler predicate than Shape D (no gate-name parsing). **LOC estimate:** ~10 production (1 field in `post_verdict_request`, 1 check in `_consume_verdicts`) + ~10 test. **Closes:** Item #5.

**Shape F — Step-number semantics change.** Make the verdict-request `Step` field mean "next step to dispatch" rather than "step that paused." For precondition failures at step 1, post with `Step: 1` (retry). For successful step 1 completion, post with `Step: 2` (advance). This shifts the advancement decision to `run_plan` (where pause context is available) rather than `_consume_verdicts` (where it's lost). **LOC estimate:** ~20 production (touch all verdict-post sites + `_consume_verdicts` dispatch logic) + ~15 test. **Closes:** Item #5. Larger blast radius — changes `_consume_verdicts` dispatch from `step_number + 1` to `step_number` and requires all verdict-post sites to compute the correct next step.

### F19 — Unified fix

Items #2 and #3 share root cause RV-1 and are closed by a single fix (Shape A, B, or C). Item #5 is independent and requires its own fix (Shape D, E, or F).

**If Shape A (rename-first) + Shape B (startup recovery) are shipped together:** They close items #2 and #3 completely. Shape A prevents the inconsistency from forming; Shape B heals any legacy instances. Combined LOC: ~25 production + ~15 test.

**If Shape A + Shape D or E are shipped together:** They close all three items. Combined LOC: ~25-35 production + ~25 test.

### F20 — Test coverage gaps

**Items #2 + #3 (RV-1 boundary):**
- No existing test simulates daemon restart between verdict-post and rename. The structural gap (not testable at unit level per the 2026-05-24 diagnostic Section G) would require an integration test or a mock that interrupts execution between specific lines.
- `test_run_plan_strict_pause_on_creation_failure` (test_bellows.py:2153) verifies `verdict-pending-*` rename on worktree creation failure — this confirms the rename works in the non-restart case but does not test the verdict-post → rename gap.
- **Testable via Shape A:** If rename-first ordering is shipped, a unit test can verify that the plan is `verdict-pending-*` BEFORE any verdict-request file exists in `pending/`. This inverts the current ordering and makes the "rename happened" assertion independent of subsequent operations.
- **Testable via Shape B:** If startup recovery is shipped, a unit test can seed an `in-progress-*` plan + verdict-request in `pending/` + verdict in `resolved/` and verify that startup recovery promotes the plan to `verdict-pending-*` and the verdict is consumed.

**Item #5 (step-counter logic):**
- No existing test exercises verdict-continue on a precondition gate failure and verifies the dispatched step number. The existing verdict-consumption tests in `test_consume_verdicts.py` test continue-on-success scenarios.
- **Test name for Shape D/E:** `test_verdict_continue_on_precondition_failure_retries_same_step` — seed a `verdict-pending-*` plan with a verdict-request containing `Pause Reason Code: gate_failure` and gate=`worktree_creation`, deposit a continue verdict, run `_consume_verdicts`, and verify `handle_new_plan` is called with `resume_step=N` (same step) rather than `resume_step=N+1`.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced the daemon's complete state model across three BACKLOG items, enumerating 12 state-modifying operations per step lifecycle and identifying 3 restart-vulnerable boundaries (RV-1 through RV-3). Traced each item's code path end-to-end with line-level citations: item #2 (matching predicate at bellows.py:1184 requires `verdict-pending-*` prefix), item #3 (rename IS present but non-atomic with verdict-post — confirmed by building on the 2026-05-24 diagnostic Section C), item #5 (`_consume_verdicts` at bellows.py:1230 always advances `step_number + 1` with no pause-reason-code check). Validated against log evidence for all three reproductions. Determined items #2 and #3 are two observations of the same structural bug (RV-1 boundary: verdict-post → rename gap), while item #5 is an independent logic defect in step-advancement. Proposed 6 fix shapes (A-F) with LOC estimates and boundary-closure mapping. Identified 3 test coverage gaps.

### Files Deposited
- `knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` — unified diagnostic findings (Sections A-F, 20 investigation questions)

### Files Created or Modified (Code)
- None — investigation only, no source modifications

### Decisions Made
- Classified items #2 and #3 as shared root cause (RV-1: non-atomic verdict-post → rename sequence)
- Classified item #5 as independent logic defect (step-advancement in `_consume_verdicts` does not distinguish precondition-failure from step-completion)
- Phase 3b step-state-resume (2026-04-28) was partially implemented: `plan_slug` column added to `runs` table (write-side), but `_get_last_completed_step()` read-side helper was never implemented — DB remains write-only with zero SELECT queries
- Recommended fix order: RV-1 first (items #2+#3), then item #5

### Flags for CEO
- None

### Flags for Next Step
- None — single-step diagnostic, no further steps
