# Failure 3 Ordering Diagnostic — Findings
**Date:** 2026-04-24 | **Agent:** Bellows Systems Analyst | **Plan:** diagnostic-failure-3-ordering-2026-04-24

---

## Q1 — Dispatch Ordering Timeline

The following timeline maps the lifecycle of a terminal (final) step in `bellows.py::run_plan()`. Line references are to `bellows.py` as of commit `5eea941`.

```
1. Bellows claims plan                        [L221-225]
   ├─ rename executable-foo.md → in-progress-executable-foo.md
   └─ write shadow copy to .bellows-cache/executable-foo.md.pristine

2. Bellows captures pre-step git diff          [L250]
   └─ _capture_git_diff(project_path)

3. Bellows launches agent subprocess           [L252-254]
   └─ runner.run_step(bootstrap_prompt, project_path, model, ...)
   └─ bootstrap prompt points agent to .bellows-cache/*.pristine (read-only)

   ┌──────── INSIDE AGENT EXECUTION (opaque to Bellows) ────────┐
   │ 3a. Agent reads plan from shadow cache                      │
   │ 3b. Agent performs step work (code, deposits, commits)      │
   │ 3c. Agent performs Rule 8 + Rule 23 housekeeping:           │
   │     ├─ feedback append → agent-prompt-feedback.md           │
   │     ├─ PROJECT_STATUS.md update                             │
   │     ├─ BACKLOG.md update (if applicable)                    │
   │     ├─ final commit                                         │
   │     └─ *** move plan to Done/ ***                           │
   │         shutil.move("in-progress-*", "Done/executable-*")  │
   │                                                             │
   │   At this point the plan file is in decisions/Done/.        │
   │   The in-progress-* file NO LONGER EXISTS on disk.          │
   └─────────────────────────────────────────────────────────────┘

4. Agent subprocess exits                      [L252 returns]
   └─ runner.run_step() returns parsed dict (receipt, cost, etc.)

5. Bellows records run to DB                   [L259-263]

6. Bellows captures post-step git diff         [L266-267]
   └─ _capture_git_diff + _parse_diff_stat

7. Bellows evaluates gates                     [L268]
   └─ gates.check(parsed, plan_text, current_step, project_path, files_changed)

8. Bellows acts on gate result (terminal step) [L332-381]
   ├─ If gates FAIL (or QA/header/auto_close pause):  [L332-358]
   │   ├─ verdict.post_verdict_request(...)            [L348]
   │   ├─ notifier.notify_verdict_request(...)         [L349-351]
   │   ├─ shutil.move(inprogress_path, verdict_pending_path)  [L353-354]
   │   │   └─ GUARD: if os.path.exists(inprogress_path)
   │   │      └─ FALSE — agent already moved to Done/ at step 3c
   │   │      └─ rename silently skipped
   │   └─ return (plan is stranded in Done/ with pending verdict)
   │
   └─ If gates PASS + auto_close:             [L363-381]
       ├─ verdict.log_to_ledger(...)
       ├─ source = inprogress_path if exists else plan_path  [L373]
       │   └─ Neither may exist (agent moved to Done/)
       ├─ shutil.move(source, done_path)       [L375-376]
       │   └─ GUARD: if os.path.exists(source) — may be False
       └─ _delete_shadow(plan_filename)
```

**Key finding:** Move-to-Done happens at step 3c (inside the agent's execution, invisible to Bellows). Gate evaluation happens at step 7 (after the agent returns). There is no mechanism for Bellows to prevent the move-to-Done or to undo it after a gate trips. The `os.path.exists(inprogress_path)` guard at step 8 silently absorbs the missing file, producing a stranded state: plan in Done/ + verdict request in pending/ with no corresponding verdict-pending plan file.

---

## Q2 — Gate State Exposure

| # | Gate | Type | Classification | Evidence Source | Notes |
|---|------|------|---------------|-----------------|-------|
| 1 | `receipt_status` | Blocking | **Post-hoc** | `parsed["receipt_status"]` from terminal `result` event | Only available after agent subprocess exits. No mid-step equivalent. |
| 2 | `ceo_flags` | Blocking | **Post-hoc** | `parsed["ceo_flags"]` from terminal `result` event | Flags for CEO are written into agent's Output Receipt, parsed from `result_text`. |
| 3 | `no_errors` | Blocking | **Post-hoc** | `parsed["is_error"]` from `result` event | Error state is a property of the subprocess exit / stream parse. |
| 4 | `no_permission_denials` | Blocking | **Post-hoc** | `parsed["permission_denials"]` from `result` event | Denial events accumulate during execution; only the final count is available post-hoc. Stream-json could expose per-event denials mid-step but this is not implemented. |
| 5 | `deposit_exists` | Blocking | **Split: plan-required is pre-step; agent-declared is post-hoc** | Plan-required: `_extract_plan_required_deposits(step_text)` + `_resolve_deposit_path()` on disk. Agent-declared: `parsed["result_text"]` Files Deposited section. | **`deposit_exists` for plan-required paths IS pre-step evaluable** — the `**Deposits:**` block declares paths up front and `_resolve_deposit_path()` checks disk existence. But the current implementation bundles both checks into a single post-hoc gate that also needs `parsed["result_text"]`. |
| 6 | `is_qa_step` | Informational | **Pre-step** | `plan_text` step header regex | Reads plan text only. Fully evaluable before agent runs. Already known at gate registration time. |
| 7 | `file_change_audit` | Informational | **Post-hoc** (mid-step under stream-json per-event) | `files_changed` list from diff-of-diffs | Currently computed from pre/post git diff --stat. Under stream-json per-event gating, each file write could be audited as it happens. |
| 8 | `scope_check` | Blocking | **Post-hoc** | `files_changed` + `step_text` | Requires the complete set of files changed (needs post-step diff) AND the step text (available pre-step). Cannot run until all file writes are known. Under stream-json per-event, individual files could be scope-checked as written, but false positives on housekeeping files (BACKLOG.md, feedback) would fire before the step completes. |

**On `scope_check` evaluability:** scope_check is NOT purely post-hoc in theory — the plan step text is pre-step, and individual file writes could be checked mid-step if per-event gating were active. However, the housekeeping files that trip Failure 3 (BACKLOG.md, validation-quality-summary.md, copilot debug logs) ARE legitimate writes that happen to fall outside the step text's explicit scope. Moving scope_check earlier would not prevent Failure 3 — it would detect the problem sooner but not change the outcome.

**On `deposit_exists` pre-step evaluability:** Confirmed. The plan's `**Deposits:**` block (Rule 26 convention) declares deposit paths up front. `_resolve_deposit_path()` can check disk at any time. A pre-housekeeping deposit check is architecturally feasible: Bellows could verify deposits exist on disk before the agent performs move-to-Done. This would require a signaling surface (see Q3) since the check would need to run inside the agent's execution window.

---

## Q3 — Agent-Bellows Signaling Surfaces

### Surface 1: `.bellows-cache/` directory

| Property | Value |
|----------|-------|
| **Read access** | Agent (via bootstrap prompt path reference); Bellows (`_read_shadow()`, `_shadow_path()`) |
| **Write access** | Bellows only (`_write_shadow()` at claim time, L103-105) |
| **Current use** | Pristine plan content preservation — agent reads plan from `*.pristine` instead of mutable `in-progress-*` file |
| **Persistence** | Persists across steps; deleted on Done/halt (`_delete_shadow()`, L116-120) |
| **Agent write today?** | No. Agent has filesystem access but no convention or instruction to write here. |
| **Retention policy** | Created at plan claim; deleted at terminal state (Done or halted). Survives verdict cycles. |
| **In .gitignore?** | Yes (`bellows/.gitignore` line 12) |

**Non-existence note:** No gate-result or sentinel files exist in `.bellows-cache/` today. Adding a file like `.bellows-cache/{slug}-gate-result.json` that Bellows writes (with pre-computed gate state) and the agent reads before housekeeping is architecturally trivial — the directory exists, both parties have access, and `.gitignore` covers it.

### Surface 2: Bootstrap prompt (Bellows → Agent)

| Property | Value |
|----------|-------|
| **Read access** | Agent (receives as `-p` argument) |
| **Write access** | Bellows (`run_plan()` constructs prompt string, L242-247) |
| **Current use** | Tells agent which plan to read and which step to execute |
| **Persistence** | Ephemeral — exists only for the subprocess invocation |
| **Bidirectional?** | No. One-way Bellows → Agent. |

### Surface 3: `parsed["verdict_requested"]` (Agent → Bellows)

| Property | Value |
|----------|-------|
| **Read access** | Bellows (checks in `run_plan()` at L278, L334, L366) |
| **Write access** | Agent (deposits a verdict-request file during execution; parser extracts it) |
| **Current use** | Agent can request a verdict pause by writing a specifically-formatted file |
| **Persistence** | Post-hoc — available only after agent returns and output is parsed |

### Surface 4: `runner.run_step()` subprocess (Agent → Bellows)

| Property | Value |
|----------|-------|
| **Read access** | Bellows (reads stdout stream, parses terminal `result` event) |
| **Write access** | Agent subprocess (claude -p stdout) |
| **Current use** | All gate inputs (receipt_status, ceo_flags, etc.) flow through this channel |
| **Persistence** | Ephemeral — stream is consumed once, logged to `logs/` |

### Surfaces that DO NOT exist today

| Candidate | Status | Notes |
|-----------|--------|-------|
| `bellows gate-check` CLI | **Does not exist** | No CLI subcommands exist. Bellows is a single-entry-point script (`python bellows.py`). |
| Environment variables on subprocess | **Not set** | `subprocess.Popen()` in `runner.py` L49-55 passes no `env` parameter. Agent inherits shell env. No `BELLOWS_*` vars. |
| Sentinel files | **No convention exists** | No sentinel file patterns in any source file. |
| Pre-commit hooks | **Not installed** | No Bellows-managed git hooks. `.git/hooks/` contains only sample files. |
| Agent writes to `verdicts/` | **No convention** | Verdict requests are written exclusively by Bellows (`verdict.post_verdict_request()`). Agents do not write to `verdicts/` today. |

---

## Q4 — Failure Class Attribution

### 10 Most Recent Verdict Requests (`bellows/verdicts/pending/`, sorted by modification time)

| # | Filename | Project | Gate Tripped | Step | Terminal? | Plan Location at Verdict Time | Housekeeping Commits Landed? | Failure Class |
|---|----------|---------|-------------|------|-----------|-------------------------------|------------------------------|---------------|
| 1 | `verdict-request-stream-json-minimal-switch-2026-04-23-step-3` | bellows | scope_check (BACKLOG.md) | 3/3 | Yes | **Done/** | Yes (`3ec214d`) | **Failure 3** |
| 2 | `verdict-request-stream-json-feasibility-2026-04-23-step-1` | bellows | _(none — gates passed)_ | 1/1 | Yes | Done/ | N/A (diagnostic) | Expected diagnostic pause (auto_close_disabled) |
| 3 | `verdict-request-permission-prompt-substrate-2026-04-23-step-1` | bellows | deposit_exists (prose paths) | 1/1 | Yes | Done/ | N/A (diagnostic) | Gate false positive (deposit_exists on prose directory references) |
| 4 | `verdict-request-planner-template-lessons-step-numbering-2026-04-23-step-1` | bellows | no_permission_denials (Grep) | 1/2 | No | verdict-pending/ | N/A (mid-plan) | Mid-plan gate failure (correctly paused) |
| 5 | `verdict-request-forge-cycle-12-2026-04-23-step-1` | forge | deposit_exists | 1/6 | No | Done/ (plan progressed to step 6) | N/A (stale request) | Stale request — plan continued past this step; verdict request not cleaned up |
| 6 | `verdict-request-forge-phrasing-eval-helpers-2026-04-23-step-2` | forge | _(none — QA checkpoint)_ | 2/2 | Yes | Done/ | Yes (plan completed) | **QA decorative** (same root cause as Failure 3) |
| 7 | `verdict-request-forge-backlog-cleanup-2026-04-23-step-2` | forge | _(none — QA checkpoint)_ | 2/2 | Yes | Done/ | Yes (plan completed) | **QA decorative** (same root cause as Failure 3) |
| 8 | `verdict-request-forge-backlog-state-audit-2026-04-23-step-1` | forge | _(none — gates passed)_ | 1/1 | Yes | Done/ | N/A (diagnostic) | Expected diagnostic pause (auto_close_disabled) |
| 9 | `verdict-request-scope-check-project-path-filter-2026-04-22-step-1` | bellows | scope_check | 1/2 | No | Done/ (plan progressed) | N/A (stale request) | Stale request — plan continued; verdict request not cleaned up |
| 10 | `verdict-request-scope-check-git-range-2026-04-22-step-1` | bellows | _(none — gates passed)_ | 1/1 | Yes | Done/ | N/A (diagnostic) | Expected diagnostic pause (auto_close_disabled) |

### Confirmed Failure 3 Reproductions (from BACKLOG, outside top-10 window)

| Filename | Project | Gate Tripped | Plan in Done/? | Housekeeping Landed? |
|----------|---------|-------------|----------------|---------------------|
| `verdict-request-base-rates-url-fix-2026-04-21-step-2` | invoice-pulse | scope_check (validation-quality-summary.md) | Yes | Yes (`75cbad7f`) |
| `processed-verdict-contract-pubs-route-removal-2026-04-22-step-2` | invoice-pulse | scope_check (copilot debug log) | Yes | Yes (`186c4b5f`) |

### Attribution Summary

| Failure Class | Count (in top 10) | Description |
|---------------|-------------------|-------------|
| **Failure 3 (pure)** | 1 | Gate trips after agent moved plan to Done/. Plan is fully shipped. Verdict request is stranded. |
| **QA decorative** | 2 | Same root cause — agent does housekeeping + Done before QA checkpoint evaluates. Verdict request asks permission for completed work. |
| Expected diagnostic pause | 3 | auto_close_disabled fires by design on diagnostics. Gates passed. Not a failure. |
| Gate false positive | 1 | deposit_exists trips on prose directory references (known parser gap). |
| Mid-plan gate failure | 1 | Correctly paused mid-plan. System working as designed. |
| Stale request | 2 | Plan progressed past this step via verdict consumption; the specific step's verdict request was not cleaned up. |

**BACKLOG hypothesis evaluation:** Failure 3 (gate-tripped-after-Done) is present but NOT the single dominant mechanism in this 10-file sample. However, when combined with QA-decorative (which shares the identical root cause — agent performs housekeeping + Done before Bellows evaluates), the "agent-moves-to-Done-before-gate-check" class accounts for **3 of 10** cases (30%). The remaining 7 are split between expected behavior (3 diagnostic pauses), gate precision issues (1 false positive), correct pauses (1 mid-plan), and stale requests (2 cleanup gaps). The two confirmed BACKLOG reproductions (base-rates-url-fix, contract-pubs-route-removal) both exhibit the pure Failure 3 pattern with housekeeping commits successfully landed and plans in Done/.

**Conclusion:** Failure 3 is a real, reproducible architectural issue affecting terminal steps of executable plans. It is not the majority mechanism for ALL pending verdict requests (diagnostics dominate by volume), but it is the dominant mechanism for **incorrect** verdict requests on fully-shipped executable plans. Every executable plan whose terminal step completes successfully is at risk of producing a stranded verdict if any gate trips on housekeeping side effects.

---

## Layer Impact

| Finding | Layer 1 (Bellows) | Layer 2 (Agents) | Layer 3 (Planner) |
|---------|-------------------|-------------------|--------------------|
| Q1: Move-to-Done inside agent execution | Affected — gate evaluation is structurally too late | **Root cause** — agent performs Done move per Rule 8/23 | Affected — receives stranded verdict requests for completed work |
| Q2: 5 of 6 blocking gates are post-hoc | Affected — cannot evaluate most gates before agent returns | Not affected | Not affected |
| Q2: deposit_exists plan-required is pre-step evaluable | Opportunity — could split this check out and run earlier | Could consume a pre-housekeeping gate signal | Not affected |
| Q3: No mid-execution signaling surface exists | Affected — no way to communicate gate state to agent during execution | Affected — no way to check gate state before housekeeping | Not affected |
| Q4: Failure 3 + QA decorative = 30% of recent verdicts | Affected — produces incorrect verdict queue state | Not affected (agents work correctly) | Affected — must manually override stranded verdicts |

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the Failure 3 ordering issue across four questions: mapped the bellows.py dispatch timeline showing the structural gap between agent move-to-Done (inside execution) and gate evaluation (after return); classified all 8 gates by when their state becomes computable; inventoried all agent-Bellows signaling surfaces (4 exist, 5 candidates do not); and attributed the 10 most recent verdict requests by failure class, confirming Failure 3 + QA-decorative accounts for 30% of the sample.

### Files Deposited
- `knowledge/architecture/failure-3-ordering-2026-04-24.md` — Q1-Q4 findings for Failure 3 ordering diagnostic

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Classified deposit_exists (plan-required subset) as pre-step evaluable — the Deposits block declares paths up front and disk checks are independent of agent output
- Determined that scope_check mid-step evaluation would not prevent Failure 3 because the files that trip it (BACKLOG.md, etc.) are legitimate housekeeping writes
- Confirmed `.bellows-cache/` as the most viable existing signaling surface for a future gate-state channel

### Flags for CEO
- None

### Flags for Next Step
- The three fix shapes (reorder, block, defer) identified in the BACKLOG are all architecturally viable given these findings. The key constraint: 5 of 6 blocking gates are post-hoc, so fix shape (a) "reorder — gate runs before housekeeping" can only work for deposit_exists (plan-required) and is_qa_step, not for receipt_status, ceo_flags, no_errors, or no_permission_denials. Fix shapes (b) "block — refuse Done on gate trip" and (c) "defer — always pause terminal step" are both feasible at Layer 1 without agent cooperation.
