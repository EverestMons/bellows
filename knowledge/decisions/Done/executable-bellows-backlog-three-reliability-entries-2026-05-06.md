# executable — Bellows BACKLOG: Add Three Reliability Entries from 2026-05-06 Session

**Date:** 2026-05-06
**Tier:** Documentation
**Test Scope:** targeted — markdown edits only, no code, no runtime behavior change

## Execution Map

Step 1 (Bellows Documentation Analyst — DEV) → Done

Single-step executable per the BACKLOG-edit precedent. No separate QA — markdown-only edits with self-check.

---

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan, executes Step 1, and on completion runs the housekeeping block at the end.

**Bootstrap:**

```
Read the plan at bellows/knowledge/decisions/executable-bellows-backlog-three-reliability-entries-2026-05-06.md and execute Step 1.
```

---

## Context

The 2026-05-06 IP working session surfaced three Bellows reliability issues that need BACKLOG entries. These are not duplicates of existing entries — verified by reading the current `bellows/knowledge/BACKLOG.md` Open section before drafting:

1. **Inactivity timeout did not fire on hung runner.** Two reproductions in this session: `executable-half-up-currency-rounding-2026-05-06` Step 1 ran for 41+ minutes with last output ~7 minutes earlier; the configured 300s inactivity timeout (per `bellows/config.json` `step_inactivity_timeout_seconds: 300`) did not kill the runner. Required CEO-side `kill` and Bellows restart. The 2026-05-01 BACKLOG-closed entry "activity-based timeout" claimed this shipped via `executable-activity-timeout-2026-04-17`. Either the config isn't loading, or the kill logic is broken in some condition (subprocess deadlock on output buffer? activity-canary timer reset on something that isn't actual output?).

2. **`_teardown_worktree` cherry-pick reliability gap.** During recovery from issue #1, CEO ran `git status` in the invoice-pulse repo and observed ~20 Untracked plan files in `knowledge/decisions/Done/` plus 5 `deleted` files in main checkout — these are plans whose worktree commits should have been cherry-picked back to main when the plans completed but were not. Population audit needed to determine: (a) is `_teardown_worktree` failing silently in some condition, (b) are these all from pre-2026-05-03 dispatches when worktrees didn't exist, or (c) some other mechanism. Distinct from Mode A (which was about move-to-Done before gate) — this is about cherry-pick reliability post-gate.

3. **Stranded plan and verdict files in IP `knowledge/decisions/`.** Two files observed during session-end audit that should not be there:
   - `in-progress-diagnostic-continuation-rule-rounding-2026-05-06.md` — duplicate of the parallel-1 dispatched plan (which is in Done/ as `parallel-1-diagnostic-continuation-rule-rounding-2026-05-06.md`); appears to be agent-side confusion creating a shadow file in the watched directory while the parallel-1 plan was being run
   - `verdict-pending-diagnostic-lanes-csrf-fix-verification-2026-05-06.md` — Bellows logged `verdict continue-to-done` for this plan earlier in the session, file should be in Done/. Stranded.

Today's session also surfaced 5 stale `deleted` files in invoice-pulse main checkout (legacy from prior sessions, separate cleanup):
- `knowledge/data/pending/copilot_exchanges_20260416_121355_317607.json`
- `knowledge/decisions/in-progress-executable-csv-upload-fetch-fix-2026-04-17.md`
- `knowledge/decisions/verdict-pending-diagnostic-base-rates-method-not-allowed-2026-04-21.md`
- `knowledge/decisions/verdict-pending-diagnostic-planner-governance-sweep-2026-04-20.md`
- `knowledge/decisions/verdict-pending-executable-gitattributes-crlf-2026-04-17.md`

Item #2 likely produces these as a side effect, so capturing in the same entry.

---

## Step 1 — BACKLOG Entry Additions (Bellows Documentation Analyst — DEV)

**Agent:** Bellows Documentation Analyst
**Specialist file:** `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`

**Goal:** Add three new Open BACKLOG entries to `bellows/knowledge/BACKLOG.md` capturing the reliability issues from the 2026-05-06 IP session. Each entry follows the existing BACKLOG entry style (date prefix, single dense paragraph, references to specific evidence, fix shape if known).

**Read first (in order):**

1. `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`
2. `bellows/knowledge/BACKLOG.md` — confirm current Open section structure, entry style, and ordering convention (newest-at-top per the file header)
3. `bellows/config.json` — confirm `step_inactivity_timeout_seconds` value for citation accuracy in entry 1

### Edit specification

**File:** `bellows/knowledge/BACKLOG.md`

**Action:** Insert three new entries at the top of the `## Open` section (immediately after the heading line, before any existing entries — newest-at-top convention).

**Entry 1 — Inactivity timeout failure:**

```
- 2026-05-06: **Inactivity timeout does not fire on hung runner — REPRODUCED.** Configured 300s threshold (per `bellows/config.json` `step_inactivity_timeout_seconds: 300`) did not kill the subprocess in two observations during today's IP session. Reproduction 1: `executable-half-up-currency-rounding-2026-05-06` Step 1 ran 41+ minutes with `last output 256s ago` advancing to `last output 910s+ ago`; runner kept emitting heartbeats but never fired the kill. Required manual `kill` of Bellows process to recover. Reproduction 2 (partial): same plan's Step 2 also showed extended quiet periods (last output 298s ago) without kill, but agent eventually produced more output and completed normally. The 2026-05-01 BACKLOG-closed entry "activity-based timeout" claims this shipped via `executable-activity-timeout-2026-04-17` with QA-verified subprocess.Popen + threading + last_output_time reset on every stdout line + proc.kill on timeout. Either the fix isn't actually loading the config value (config-load bug), the kill logic is gated by a condition that wasn't met (e.g., subprocess deadlock on stdout buffer keeps the runner technically "active" via heartbeat thread without producing process output), or the activity-canary timer is being reset on something that isn't agent output (bellows-side log writes? heartbeat thread itself?). **Operational impact:** every hung runner blocks recovery until CEO notices and manually kills Bellows, then requires plan re-dispatch + worktree cleanup. Today's recovery cost ~10 minutes including manual cherry-pick of completed-but-stranded worktree commit. **Diagnostic shape:** capture `step_inactivity_timeout_seconds` actual value at runtime via debug print in `runner.run_step`, then reproduce a hung subprocess (e.g., a step that runs a long-blocking command with no output); confirm whether kill fires at expected threshold. If it does, the bug is in the production hang path (different mechanism than test reproduction). If it doesn't, the config-load is the bug. References: today's session terminal logs (`runner — 2471s elapsed, last output 910s ago` is one of the longest gaps without kill); 2026-05-01 closed BACKLOG entry referencing `bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md`.
```

**Entry 2 — `_teardown_worktree` cherry-pick reliability gap:**

```
- 2026-05-06: **`_teardown_worktree` cherry-pick reliability gap — population audit needed.** During today's IP session recovery, CEO ran `git status` in the invoice-pulse repo and observed ~20 plan files in `knowledge/decisions/Done/` showing as **Untracked** (not in git's index despite being on disk and being moved to Done/ by completed plans). Also observed 5 files showing as **deleted** in main checkout from prior sessions (`knowledge/data/pending/copilot_exchanges_20260416_121355_317607.json`, `knowledge/decisions/in-progress-executable-csv-upload-fetch-fix-2026-04-17.md`, `knowledge/decisions/verdict-pending-diagnostic-base-rates-method-not-allowed-2026-04-21.md`, `knowledge/decisions/verdict-pending-diagnostic-planner-governance-sweep-2026-04-20.md`, `knowledge/decisions/verdict-pending-executable-gitattributes-crlf-2026-04-17.md`). Pattern suggests `_teardown_worktree` is not reliably cherry-picking all changes back to main — possibly only the agent's primary commit lands and lifecycle-related file moves (in-progress→Done renames, verdict consumption, etc.) drift onto the worktree's branch but never reach main. Distinct from Mode A (which was about move-to-Done firing before gate evaluation, structurally resolved 2026-05-06 closure executable) and from BACKLOG #1 (`deposit_exists` worktree-aware gate path, fixed today). **Diagnostic shape:** population audit of all Done/ entries in IP and bellows from 2026-05-03 onward (post-worktree-migration); for each, check whether the plan's expected commits are on main (`git log --all --oneline | grep <plan-slug>`) and whether the plan file is tracked (`git ls-files knowledge/decisions/Done/<plan-name>.md`); classify each as (a) shipped cleanly, (b) commits landed but plan file untracked, (c) plan file tracked but partial commits missing, (d) other anomaly. Findings inform whether this is a `_teardown_worktree` bug, a `git worktree add`/cherry-pick race, or operational drift. **Operational impact:** PROJECT_STATUS or BACKLOG hygiene plans run against `git status` data may produce confusing output; manual cleanup via `git add knowledge/decisions/Done/...` is required after each session unless this is fixed. References: today's IP session `git status` output showing 20+ Untracked Done/ files and 5 stale deletions; `_teardown_worktree` implementation in `bellows.py` (post-2026-05-04 detect-and-skip + cherry-pick logic from 36b2bba).
```

**Entry 3 — Stranded plan/verdict files cleanup:**

```
- 2026-05-06: **Stranded plan/verdict files in invoice-pulse `knowledge/decisions/` — operational hygiene.** Two files observed during today's session-end audit that should not be in the watched directory: (a) `in-progress-diagnostic-continuation-rule-rounding-2026-05-06.md` — duplicate of the parallel-1 dispatched plan whose canonical version is in `Done/` as `parallel-1-diagnostic-continuation-rule-rounding-2026-05-06.md`; appears to be an agent-side shadow created during the parallel-1 run (the agent may have used `Filesystem:write_file` with a non-prefixed name during plan execution); (b) `verdict-pending-diagnostic-lanes-csrf-fix-verification-2026-05-06.md` — Bellows terminal log earlier today showed `verdict continue-to-done — diagnostic-lanes-csrf-fix-verification-2026-05-06.md`, meaning the plan transitioned to Done conceptually, but the file at `verdict-pending-` prefix was never renamed/moved. Stranded. Both files are non-blocking (Bellows's `is_runnable_plan()` filter skips them based on prefix combinations, and they don't trip `_seen` because their slug doesn't match an active plan), but they accumulate visual noise in the decisions directory and produce confusion during stranded-plan audits. **Cleanup options for next session:** (1) Direct `Filesystem:move_file` to remove the stranded `in-progress-` duplicate (the canonical Done/ version covers it) — simplest, no Bellows interaction; (2) Direct `Filesystem:move_file` to move `verdict-pending-` file to Done/ — restores expected lifecycle state; (3) Investigate why the verdict-pending rename didn't happen post-`continue-to-done` log line — may indicate a Bellows lifecycle bug worth a sub-entry. Lean: do (1) and (2) as immediate cleanup, then assess whether (3) is a recurring pattern or one-off based on whether more stranded `verdict-pending-` files appear in future sessions. **Cross-reference:** these files were skipped during today's IP session-wrap because they're orthogonal to the IP work shipped; capturing here so they're not lost.
```

### What NOT to do

- Do not modify any existing BACKLOG entries (Open or Closed sections).
- Do not change the file header text or the "How to use" instructions.
- Do not modify the `## Closed` section ordering or content.
- Do not touch any file other than `bellows/knowledge/BACKLOG.md`.
- Do not investigate or fix any of the three issues — this plan only adds tracking entries.

### Output Receipt

Append an Output Receipt at the bottom of a development log per the Documentation Analyst's standard format.

**Output location:** `bellows/knowledge/development/backlog-three-reliability-entries-2026-05-06.md`

The development log should record:
- Confirmation that 3 new entries were added at the top of `## Open`
- Line count of the new entries (sanity check that they survived the edit)
- Net Open-section bullet count delta (before vs after, expected +3)
- Test Results: `N/A — markdown-only edit, no code, no runtime behavior change.`

**Deposits:**
- `bellows/knowledge/BACKLOG.md` (modified)
- `bellows/knowledge/development/backlog-three-reliability-entries-2026-05-06.md`

---

## Housekeeping (Step 1 final block — Bellows Documentation Analyst)

After the BACKLOG additions and dev log are written, perform housekeeping in this exact order:

**A. Self-check (Rule 20 mandatory):**

```python
import os, sys

backlog_path = "bellows/knowledge/BACKLOG.md"
devlog_path = "bellows/knowledge/development/backlog-three-reliability-entries-2026-05-06.md"
plan_path = "bellows/knowledge/decisions/in-progress-executable-bellows-backlog-three-reliability-entries-2026-05-06.md"

problems = []
for p in [backlog_path, devlog_path, plan_path]:
    if not os.path.isfile(p):
        problems.append(f"MISSING: {p}")

# Confirm the 3 entries were added (each has a distinctive marker phrase)
with open(backlog_path) as f:
    backlog_body = f.read()

required_markers = [
    "Inactivity timeout does not fire on hung runner",
    "_teardown_worktree` cherry-pick reliability gap",
    "Stranded plan/verdict files in invoice-pulse",
]
for marker in required_markers:
    if marker not in backlog_body:
        problems.append(f"MISSING marker '{marker}' in BACKLOG.md")

# Confirm all 3 are in the Open section (not Closed)
open_section, _, closed_section = backlog_body.partition("## Closed")
for marker in required_markers:
    if marker in closed_section and marker not in open_section:
        problems.append(f"Marker '{marker}' is in Closed section but should be in Open")
    elif marker not in open_section:
        problems.append(f"Marker '{marker}' missing from Open section")

# Confirm Open-section bullet count grew by exactly 3
import re
open_bullets_now = len(re.findall(r"^- ", open_section, re.MULTILINE))
# We can't compute "before" inline without git, so just check minimum threshold
# Existing Open count was non-trivial (5+ entries pre-this-edit); after should be at least 8
if open_bullets_now < 8:
    problems.append(f"Open section has only {open_bullets_now} top-level bullets — expected at least 8 (pre-existing + 3 new)")

# Hedging keywords auto-invalidate per Rule 20
hedges = ["MAYBE", "PROBABLY", "LIKELY", "SHOULD BE", "I THINK", "PERHAPS"]
with open(devlog_path) as f:
    devlog_body = f.read()
for h in hedges:
    if h in devlog_body.upper():
        count = devlog_body.upper().count(h)
        if count > 1:
            problems.append(f"HEDGING KEYWORD '{h}' found {count} times in {devlog_path}")

if problems:
    print("SELF-CHECK FAILED")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
else:
    print("SELF-CHECK PASSED")
    print(f"BACKLOG.md updated: 3 new Open entries added")
    print(f"Open-section bullet count: {open_bullets_now}")
    print(f"Dev log: {devlog_path}")
    print(f"Plan in-progress: {plan_path}")
```

The Python block above MUST execute and its literal stdout MUST appear in the dev log file in a section titled `## Rule 20 Self-Check`.

**B. Commit:**

```bash
git add bellows/knowledge/BACKLOG.md bellows/knowledge/development/backlog-three-reliability-entries-2026-05-06.md
git commit -m "docs: bellows BACKLOG — 3 reliability entries from 2026-05-06 IP session"
```

**C. Move plan to Done (final action):**

```python
import shutil
shutil.move(
    "bellows/knowledge/decisions/in-progress-executable-bellows-backlog-three-reliability-entries-2026-05-06.md",
    "bellows/knowledge/decisions/Done/executable-bellows-backlog-three-reliability-entries-2026-05-06.md"
)
```

```bash
git add bellows/knowledge/decisions/Done/executable-bellows-backlog-three-reliability-entries-2026-05-06.md
git commit -m "chore: move bellows BACKLOG reliability entries plan to Done"
```

**Deposits:**
- `bellows/knowledge/BACKLOG.md`
- `bellows/knowledge/development/backlog-three-reliability-entries-2026-05-06.md`
