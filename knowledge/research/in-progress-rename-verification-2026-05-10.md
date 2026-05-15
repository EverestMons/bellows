# In-Progress Rename Verification — Findings

**Date:** 2026-05-10
**Diagnostic:** diagnostic-in-progress-rename-verification-2026-05-10
**Agent:** Bellows Systems Analyst
**Status:** Complete

---

## Q1 — Current Code State

### Q1(a): Pause-handling rename logic in `run_plan()`

The rename from `in-progress-*` to `verdict-pending-*` is implemented at **four sites** in `run_plan()`. All four use `base_filename` (lifecycle-prefix-stripped) for path construction and share the same guard pattern:

```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```

**Site 1 — Worktree-creation-failure pause** (bellows.py:291-293):
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```

**Site 2 — While-loop mid-step pause** (bellows.py:371-373):
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```

**Site 3 — Final-step pause** (bellows.py:456-458):
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```

**Site 4 — Auto-close worktree-teardown-failure pause** (bellows.py:483-485):
```python
verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
if os.path.exists(inprogress_path):
    shutil.move(inprogress_path, verdict_pending_path)
```

### Q1(b): `base_filename` canonicalization — all 5 sites from c7f69f3 verified

The canonicalization introduced in commit `c7f69f3` (2026-04-24) at bellows.py:221-225:

```python
base_filename = plan_filename
for prefix in ("in-progress-", "verdict-pending-", "halted-"):
    if base_filename.startswith(prefix):
        base_filename = base_filename[len(prefix):]
        break
```

Five path-construction sites using `base_filename` (per the Closed 2026-04-24 BACKLOG entry):

| # | Line | Usage | Purpose |
|---|------|-------|---------|
| 1 | L226 | `inprogress_path = os.path.join(plan_dir, f"in-progress-{base_filename}")` | Claim path |
| 2 | L264 | `shutil.move(plan_path, os.path.join(plan_dir, "Done", base_filename))` | Skip-to-Done (0-step plans) |
| 3 | L371 | `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")` | Mid-step pause rename |
| 4 | L456 | `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")` | Final-step pause rename |
| 5 | L493 | `done_path = os.path.join(done_dir, base_filename)` | Auto-close Done move |

Additionally, three post-c7f69f3 sites added by subsequent features also use `base_filename`:

| # | Line | Usage | Purpose |
|---|------|-------|---------|
| 6 | L291 | `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")` | Worktree-creation-failure pause |
| 7 | L318 | `done_check = os.path.join(plan_dir, "Done", base_filename)` | Mode A detection |
| 8 | L483 | `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")` | Auto-close teardown-failure pause |

All sites are correctly canonicalized.

### Q1(c): Control flow guards

Every rename site is guarded by `if os.path.exists(inprogress_path)`. This guard causes silent skip if `inprogress_path` does not exist at rename time. The only conditions under which this guard would suppress the rename:

1. **Mode A (agent moved plan to Done/):** Detected at bellows.py:316-328 (shipped 2026-05-06, commit `1256879`). Recovery moves file back to `inprogress_path` before the rename site executes. If recovery succeeds, the rename fires normally.
2. **Agent deleted/moved file to other location:** Not detected. The `else` branch at L328 prints a warning (`in-progress file missing for {plan_name}`) but the rename is silently skipped.
3. **Daemon restart during execution:** Plan stays stranded at `in-progress-` prefix because `is_runnable_plan()` (L736) returns False for `in-progress-` files, and no rescan logic picks up `in-progress-` files.

### Q1(d): `_teardown_worktree` vs rename ordering

At both pause sites:
- **Mid-step** (while-loop): `_teardown_worktree` at L362, rename at L371-373
- **Final-step**: `_teardown_worktree` at L448, rename at L456-458

`gates.check()` runs BEFORE `_teardown_worktree` (L333 vs L362 for mid-step; confirmed by today's earlier diagnostic). The teardown does NOT affect rename path validity because:
- `inprogress_path` resolves to `{plan_dir}/in-progress-{base_filename}` — a file in `knowledge/decisions/`
- The worktree is at `{project_path}/.bellows-worktrees/{slug}`
- Tearing down the worktree removes files from `.bellows-worktrees/`, not from `knowledge/decisions/`

No path validity issue.

---

## Q2 — Git History

```
$ git --no-pager log --since=2026-05-07 --until=2026-05-11 --oneline -- bellows.py

8eac4c3 fix(teardown): detect stale index.lock + force-remove orphaned worktree dirs (BACKLOG 2026-05-07)
dc0bdd7 fix(s3): format-tolerant check_verdict + verdict-request- prefix exclusion
afc8523 feat: PLANNER_TEMPLATE pause_for_verdict header + Bellows warning for multi-step plans without the field
e5188fa feat: dispatch qa- prefix plans and log silent skips
```

| Commit | Date | Touched rename sites? | What it touched |
|--------|------|-----------------------|-----------------|
| `e5188fa` | 2026-05-08 17:20 | **No** | `is_runnable_plan()` regex + `_handle()` skip logging |
| `afc8523` | 2026-05-08 22:09 | **No** | L265-269 warning print for multi-step plans without `pause_for_verdict` |
| `dc0bdd7` | 2026-05-09 10:47 | **No** | `_consume_verdicts()` — `verdict-request-` prefix exclusion |
| `8eac4c3` | 2026-05-10 14:31 | **No** | `_teardown_worktree()` — stale lock detection + orphan cleanup |

**Zero commits between 2026-05-07 and 2026-05-10 touched any rename site.** The rename logic has been unchanged since commit `c7f69f3` (2026-04-24).

---

## Q3 — Session 2026-05-08 Reproduction Conditions

Five plans completed on 2026-05-08 (all in `Done/`):

| Plan | Type |
|------|------|
| `diagnostic-plan-pickup-failure-2026-05-08` | Bellows-self diagnostic |
| `executable-bellows-qa-prefix-and-skip-logging-2026-05-08` | Bellows-self executable |
| `diagnostic-step2-auto-advance-2026-05-08` | Bellows-self diagnostic |
| `executable-step2-auto-advance-fix-2026-05-08` | Bellows-self executable |
| `executable-pipe-header-parser-and-comprehensive-qa-2026-05-08` | Bellows-self executable |

The `diagnostic-plan-pickup-failure-2026-05-08` plan explicitly documents the rename observation as secondary finding (S1):

> (S1) Plan filename remained `in-progress-qa-...md` after the agent paused -- Bellows normally flips to `verdict-pending-` prefix at this stage. **(Because Bellows never claimed the plan in step 1 -- consistent with non-pickup.)**

This reveals the mechanism. The CEO observed two scenarios that APPEARED to be rename failures but had distinct root causes:

**Scenario A — qa- prefix not dispatched (S1 in diagnostic-plan-pickup-failure):**
- Plan `qa-action-queue-limit-and-contract-name-2026-05-08` had `qa-` prefix
- `is_runnable_plan()` regex `^(parallel-\d+-)?(executable|diagnostic)-.*\.md$` did not include `qa-`
- Bellows never dispatched the plan
- CEO ran it manually via standalone `claude -p` (outside Bellows orchestration)
- The agent performed the `shutil.move` to `in-progress-` (claim step) but no Bellows orchestrator was running to perform the verdict-pending rename on pause
- Plan stayed at `in-progress-` prefix

**Scenario B — Step 2 auto-advance without pause (S2 in diagnostic-plan-pickup-failure, confirmed by diagnostic-step2-auto-advance):**
- Plans `executable-action-queue-limit-and-contract-name-2026-05-08` and `executable-bellows-qa-prefix-and-skip-logging-2026-05-08` lacked `pause_for_verdict` header fields
- `_parse_plan_header()` only recognized YAML frontmatter, not pipe-separated format
- `header_says_pause()` returned False for all steps
- Bellows auto-advanced from Step 1 to Step 2 without pausing
- No pause at Step 1 = no rename at Step 1
- Plans eventually DID pause (at gate failure on Step 2), at which point the rename fired correctly

**Neither scenario was a rename code bug.** The rename code at all four sites was structurally correct; it was never reached (Scenario A) or not triggered at the relevant step (Scenario B).

---

## Q4 — Session 2026-05-10 Empirical Data

Seven processed verdict files confirm 7 pause events across 5 plans:

| Plan Slug | Step | Verdict File | Verdict |
|-----------|------|-------------|---------|
| gate-path-resolution-post-teardown-2026-05-10 | 1 | `processed-verdict-gate-path-...-step-1.md` | continue |
| rule-20-self-check-wt-path-2026-05-10 | 2 | `processed-verdict-rule-20-...-step-2.md` | continue |
| teardown-worktree-reliability-2026-05-10 | 1 | `processed-verdict-teardown-...-step-1.md` | continue |
| teardown-worktree-lock-cleanup-2026-05-10 | 1 | `processed-verdict-teardown-...-step-1.md` | continue |
| teardown-worktree-lock-cleanup-2026-05-10 | 2 | `processed-verdict-teardown-...-step-2.md` | continue |
| phase-1-5-lessons-source-d-2026-05-10 | 1 | `processed-verdict-phase-1-5-...-step-1.md` | continue |
| phase-1-5-lessons-source-d-2026-05-10 | 2 | `processed-verdict-phase-1-5-...-step-2.md` | continue |

All 7 verdict files exist in `verdicts/resolved/` with `processed-` prefix. The `processed-` prefix means `_consume_verdicts` successfully:
1. Found the verdict file in `resolved/`
2. Matched it to a `verdict-pending-*` plan file (the inner loop at L962-963 matches on `pname.startswith("verdict-pending-")`)
3. Consumed the verdict and moved the verdict file to `processed-*`

The match at L963 (`if pname.startswith("verdict-pending-") and plan_slug in pname`) would **fail** if the plan were still at `in-progress-` prefix. The successful processing of all 7 verdicts is structural proof that the rename from `in-progress-*` to `verdict-pending-*` fired correctly at all 7 pause events.

---

## Q5 — Edge-Case Trigger Analysis

### Q5(a): Pre-pipe-header-parser?

Yes. The 2026-05-08 session was pre-pipe-header-parser for most of the day:
- Morning observations occurred with `_parse_plan_header()` only reading YAML frontmatter
- The pipe-header-parser fix shipped as the final commit of the day (`executable-pipe-header-parser-and-comprehensive-qa-2026-05-08`)
- Plans with pipe-separated `pause_for_verdict: after_step_1` headers were functionally equivalent to plans without the field

### Q5(b): Unusual filename shapes?

The `qa-` prefix on `qa-action-queue-limit-and-contract-name-2026-05-08` was the unusual shape. No `parallel-N-` prefixes were involved in the 2026-05-08 failures.

### Q5(c): Mid-step crashes?

No crashes observed. Plans completed steps normally but auto-advanced (Scenario B) or were never dispatched (Scenario A).

### Q5(d): Pre-2026-05-09 code?

Yes. The daemon was running pre-pipe-header-parser code during the morning/afternoon when the rename observations were made. However, the rename code itself (`base_filename` canonicalization at all sites) has been unchanged since 2026-04-24. The issue was not in the rename code but in the orchestrator's pause-decision logic (which is upstream of the rename).

### Summary

The 0/7 reproduction rate on 2026-05-10 vs the 2026-05-08 observations is explained by:
1. All 2026-05-10 plans used recognized prefixes (`diagnostic-` or `executable-`), so all were dispatched by Bellows
2. All 2026-05-10 multi-step plans had `pause_for_verdict` headers parsed by the now-fixed pipe-header-parser
3. All 2026-05-10 single-step diagnostics paused via the `not effective_auto_close` terminal-step gate (L434), which is unconditional

---

## Q6 — Recommendation

### Classification: **(i) Structurally fixed (close as superseded)**

The rename code has been structurally correct since commit `c7f69f3` (2026-04-24), which introduced `base_filename` canonicalization at all path-construction sites in `run_plan()`. The 2026-05-08 BACKLOG observation was a **symptom** of two distinct upstream bugs, both fixed on 2026-05-08:

| Root Cause | Fix Commit | Date |
|------------|------------|------|
| `qa-` prefix not in dispatch whitelist | `e5188fa` | 2026-05-08 |
| `_parse_plan_header()` did not read pipe-separated format | `afc8523` + pipe-header-parser executable | 2026-05-08 |

The rename code itself was never buggy. It was either never reached (Scenario A: plan not dispatched) or not triggered at the relevant step (Scenario B: plan didn't pause because the pause-decision input was broken).

**Close the BACKLOG entry as superseded by:**
- `executable-bellows-qa-prefix-and-skip-logging-2026-05-08` (commit `e5188fa`) — qa- prefix dispatch
- `executable-pipe-header-parser-and-comprehensive-qa-2026-05-08` (commit `afc8523`) — pipe-header-parser + pause_for_verdict header recognition
- `executable-step2-auto-advance-fix-2026-05-08` — PLANNER_TEMPLATE update for pause_for_verdict field

---

## Verdict

**Classification (i): Structurally fixed.** The BACKLOG entry "Plan filename not flipped from in-progress- to verdict-pending- on pause" is stale. The rename code has been correct since 2026-04-24 (commit `c7f69f3`). The 2026-05-08 observations were symptoms of two other bugs (dispatch whitelist gap + header parser gap), both fixed 2026-05-08. The 2026-05-10 session confirmed 7/7 correct renames with zero failures.

---

## Confidence

| Claim | Confidence | Evidence that would raise it |
|-------|------------|------------------------------|
| Rename code is structurally correct (all 4 sites use `base_filename`) | HIGH | N/A — verified by direct code reading at all sites |
| No commits between 2026-05-07 and 2026-05-10 touched rename logic | HIGH | N/A — verified by `git show` on all 4 commits |
| 2026-05-08 Scenario A (qa- prefix not dispatched) caused the observation | HIGH | Terminal log from 2026-05-08 showing "skipped" message would confirm, but the diagnostic-plan-pickup-failure findings are definitive |
| 2026-05-08 Scenario B (auto-advance without pause) caused the observation | HIGH | Terminal log showing Step 2 started without pause line between Step 1 completion and Step 2 start; confirmed by the diagnostic-step2-auto-advance findings |
| 7/7 correct renames on 2026-05-10 | HIGH | All 7 processed verdict files in `verdicts/resolved/` confirm `_consume_verdicts` matched `verdict-pending-*` plans |
| The `if os.path.exists(inprogress_path)` guard is NOT a latent bug | MEDIUM | The guard correctly handles Mode A recovery (file moved back before rename). The only unhandled case (agent deletes/moves file to non-Done/ location) has no observed reproduction. A grep of all Done/ plans for agent file-deletion patterns would raise confidence. |

---

## Rule 20 Self-Check

```
Rule 20 — QA Self-Check Results
========================================
  Evidence: in-progress-rename-verification-2026-05-10.md — FOUND
  QA report: bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md — FOUND
  Hedging keywords: none found
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Read-only investigation of the 2026-05-08 BACKLOG entry "Plan filename not flipped from in-progress- to verdict-pending- on pause." Verified the rename code is structurally correct across all 4 sites since commit c7f69f3 (2026-04-24). Determined the 2026-05-08 observations were symptoms of two upstream bugs (qa- prefix dispatch failure and pipe-header-parser gap), both fixed 2026-05-08. Confirmed 7/7 correct renames on 2026-05-10.

### Files Deposited
- `bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md` -- diagnostic findings with Q1-Q6 answers, verdict, and confidence assessment

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified BACKLOG entry as (i) Structurally fixed -- recommend close as superseded

### Flags for CEO
- BACKLOG entry "2026-05-08: Plan filename not flipped" is stale and should be closed as superseded by the 2026-05-08 qa- prefix fix and pipe-header-parser fix

### Flags for Next Step
- None (single-step diagnostic)
