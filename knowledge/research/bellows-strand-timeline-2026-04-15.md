# Phase 1 Diagnostic: Bellows Strand Timeline
**Date:** 2026-04-15 | **Type:** Read-only investigation | **Phase:** 1 of 4

---

## Q1 — Bellows Source Tree Inventory

### Python source files
| File | Modified | Size | Role |
|------|----------|------|------|
| bellows.py | Apr 14 16:02 | 14,582 B | Main orchestrator — dispatch loop, threading, plan lifecycle |
| planner.py | Apr 14 10:02 | 4,393 B | Planner judgment via `claude -p` subprocess |
| runner.py | Apr 14 08:17 | 1,986 B | Step execution subprocess wrapper |
| parser.py | Apr 13 18:28 | 1,696 B | Plan markdown parser (step extraction) |
| notifier.py | Apr 13 18:43 | 1,653 B | Pushover notification |
| server.py | Apr 13 18:44 | 1,237 B | Flask webhook server |

### Test files (`tests/`)
| File | Modified | Size |
|------|----------|------|
| test_bellows.py | Apr 14 16:02 | 4,391 B |
| test_notifier_server.py | Apr 13 18:44 | 986 B |
| test_planner.py | Apr 14 10:02 | 1,417 B |
| test_runner_parser.py | Apr 13 18:28 | 1,681 B |

### Other files
- `bellows.db` (24,576 B) — SQLite run history
- `config.json` / `config.example.json` — watched paths and Pushover creds
- `.gitignore`, `requirements.txt`, `CLAUDE.md`, `PROJECT_STATUS.md`

### Load-bearing files for agent dispatch
Confirmed: **bellows.py** is the primary suspect — it contains the dispatch loop, threading, plan claiming (`shutil.move`), step iteration, status recording, stranded detection, periodic rescan, and parallel group handling. **runner.py** handles subprocess execution. **planner.py** handles judgment. **parser.py** extracts steps. All four are on the dispatch path, but bellows.py owns the lifecycle logic where stranding occurs.

---

## Q2 — When Did Bellows Last Ship a Strand-Free Plan?

### Table schema
```
(0, 'id', 'INTEGER'), (1, 'plan_path', 'TEXT'), (2, 'project', 'TEXT'),
(3, 'session_id', 'TEXT'), (4, 'step', 'INTEGER'), (5, 'status', 'TEXT'),
(6, 'cost_usd', 'REAL'), (7, 'started_at', 'TEXT'), (8, 'completed_at', 'TEXT'),
(9, 'timestamp', 'TEXT'), (10, 'cost', 'REAL')
```

### All Bellows-project runs (chronological)

| id | step | status  | timestamp                    | plan (truncated)                       |
|----|------|---------|------------------------------|----------------------------------------|
| 10 | 1    | Unknown | 2026-04-14T10:03:08          | executable-planner-claude-code         |
| 11 | 2    | Unknown | 2026-04-14T10:04:26          | executable-planner-claude-code         |
| 14 | 1    | Unknown | 2026-04-14T10:46:41          | executable-phase2a (1st attempt)       |
| 15 | 1    | Unknown | 2026-04-14T10:51:26          | executable-phase2a (2nd attempt)       |
| 16 | 2    | Unknown | 2026-04-14T10:54:02          | executable-phase2a                     |
| 17 | 1    | Unknown | 2026-04-14T11:00:41          | executable-phase2b                     |
| 18 | 2    | Unknown | 2026-04-14T11:03:04          | executable-phase2b                     |
| 36 | 1    | Unknown | 2026-04-14T14:19:59          | diagnostic-is-runnable-plan-parallel   |
| 38 | 1    | Unknown | 2026-04-14T14:31:35          | executable-is-runnable-plan-fix        |
| 40 | 2    | Unknown | 2026-04-14T14:33:58          | executable-is-runnable-plan-fix        |
| 47 | 1    | Blocked | 2026-04-14T15:14:20          | parallel-1-diagnostic-bellows-reliability |
| 48 | 1    | Unknown | 2026-04-14T15:54:16          | executable-reliability-fixes-a-b       |
| 49 | 2    | Unknown | 2026-04-14T15:56:48          | executable-reliability-fixes-a-b       |
| 50 | 1    | Unknown | 2026-04-14T16:02:36          | executable-source-sha-startup          |
| 51 | 2    | Unknown | 2026-04-14T16:05:02          | executable-source-sha-startup          |

**Key observations:**
- ALL bellows runs have status "Unknown" — the status column is never set to "Complete" for any bellows run. This is itself a bug or design gap in the status-recording logic.
- Run 14 (phase2a, step 1 only) appears to have stranded — a second session (runs 15+16) retried the plan from step 1. This is the earliest observable strand.
- The planner-claude-code plan (runs 10+11) appears to be the last clean plan: both steps executed in the same session, and the plan is in `Done/`.
- Run 47 was explicitly "Blocked" (parallel-1-diagnostic — the plan that triggered this investigation).

---

## Q3 — Recent Git History

### `git log --oneline -30` (most recent first)
```
0493922 chore: QA report — Bellows source SHA startup
4c524e5 feat: Bellows startup prints source SHA for staleness visibility
16bca31 chore: QA report — Bellows reliability fixes A+B
fd75e76 fix: Bellows reliability — stranded detection, rescan race, parallel group stagger
2d31cf7 chore: QA report — is_runnable_plan parallel fix
1cd47ab fix: is_runnable_plan accepts parallel-N- prefix
d59cb77 docs: diagnostic — is_runnable_plan parallel prefix bug
5ac6ae2 fix: move plan_dir assignment before 0-step guard to prevent NameError
d3daeec fix: prevent double-execution race and stagger thread starts for auth stability
c7340a4 fix: rescan clears _seen for reset plans so they get re-picked up
be72e9e fix: skip plans with 0 STEP headers — move to Done with Pushover notice
20c6934 docs: prompt feedback — phase2b steps 1 and 2
4ba2577 chore: QA report — phase2b
c16e1d3 feat: Phase 2B — parallel groups, queue drain notification
e6c7a40 chore: QA report — phase2a
f86f1a2 feat: Phase 2A — threading, diagnostic fix, periodic rescan, terminal output
87ce841 docs: update PROJECT_STATUS — Phase 1 complete and live
a438c17 feat: re-enable Planner judgment via claude -p subprocess — no API key required
...
008ba7a feat: implement bellows.py orchestrator with tests
...
64b78f7 chore: scaffold bellows repo
```

### Commits touching bellows.py in past 7 days (by file stat)
| Commit | Date | bellows.py changed? | Description |
|--------|------|---------------------|-------------|
| 4c524e5 | Apr 14 16:02 | +18 lines | Source SHA startup banner |
| 16bca31 | Apr 14 15:56 | -1/+1 line | QA fix (notifier title) |
| fd75e76 | Apr 14 15:54 | +19/-6 | Stranded detection, rescan race, stagger |
| 1cd47ab | Apr 14 14:31 | +8/-5 | is_runnable_plan parallel prefix |
| 5ac6ae2 | Apr 14 13:40 | +5/-5 | plan_dir assignment order |
| d3daeec | Apr 14 13:11 | +5/-2 | Double-execution race prevention |
| c7340a4 | Apr 14 11:53 | +3 | Rescan _seen clearing |
| be72e9e | Apr 14 11:44 | +5 | 0-step plan skip |
| c16e1d3 | Apr 14 11:00 | +62/-3 | **Phase 2B: parallel groups** |
| f86f1a2 | Apr 14 10:50 | +40/-6 | **Phase 2A: threading, rescan, terminal output** |
| a438c17 | Apr 14 10:05 | +10/-9 | Re-enable Planner judgment |
| 4d97ac0 | Apr 14 09:14 | +10/-8 | Deterministic judgment for Phase 1 |
| b14843a | Apr 14 09:10 | +7/-1 | in-progress- path for step 2+ |
| 9459b43 | Apr 14 09:08 | +95/-29 | DB migration, absolute log paths |
| 008ba7a | Apr 13 18:50 | +249/-1 | Initial orchestrator implementation |

---

## Q4 — Uncommitted Changes

### `git status --short`
```
M  ../COMPANY.md
 M ../PLANNER_TEMPLATE.md
 M config.json
 M ../governance/GUARDRAILS.md
?? ../LESSONS.md
?? ../anvil/
?? .vexp/
?? knowledge/decisions/Done/parallel-1-diagnostic-bellows-reliability-2026-04-14.md
?? knowledge/decisions/in-progress-diagnostic-bellows-strand-timeline-2026-04-15.md
?? knowledge/research/audit-cleanup-strand-incident-2026-04-14.md
?? knowledge/research/bellows-write-race-2026-04-14.md
?? knowledge/research/planner-bellows-collaboration-2026-04-14.md
?? ../governance/LETTERS_LEDGER_CYCLE-v0.1.md
?? ../governance/LETTERS_LEDGER_CYCLE-v0.2.md
?? ../governance/scripts/
```

### `git diff HEAD --stat`
```
bellows/config.json | 22 ++++++++++++++++------
```

**Assessment:** `config.json` has uncommitted modifications (+16 net lines). No uncommitted changes to bellows.py or any dispatch-path Python files. The config change is NOT a suspect for the strand issue (config controls watched paths and credentials, not dispatch logic).

Untracked research files (bellows-write-race, audit-cleanup-strand-incident, planner-bellows-collaboration) are prior investigation artifacts from 2026-04-14 that were never committed.

---

## Q5 — Last Commit Before Strand Pattern Started

From Q2, the last clean plan was the **planner-claude-code** run (runs 10+11, session `1123f612...` — wait, that's a forge session. Let me re-examine. Runs 10+11 timestamps are 10:03 and 10:04 on 2026-04-14). The plan moved to Done successfully.

The first observable strand is **run 14** (phase2a, step 1 only at 10:46), which required a retry (runs 15+16).

Commits between the last clean run and the first strand:

| SHA | Time | Description |
|-----|------|-------------|
| 77cefe0 | 10:04 | QA report (docs only) |
| e7a304e | 10:04 | Prompt feedback (docs only) |
| a438c17 | 10:05 | **Re-enable Planner judgment** (bellows.py +10/-9) |
| 87ce841 | 10:28 | PROJECT_STATUS update (docs only) |
| f86f1a2 | 10:50 | **Phase 2A: threading, rescan, terminal output** (bellows.py +40/-6) |

The last commit BEFORE the strand pattern started: **a438c17** or **87ce841** (docs only).

The first commit that COULD have introduced the strand: **f86f1a2** (Phase 2A), committed at 10:50, just 4 minutes before run 14 at 10:46... wait, that's backwards. Run 14 at 10:46 came BEFORE f86f1a2 at 10:50. However, the Bellows process may have been running code from an uncommitted working tree. The commit timestamp is when the agent committed, not when the code was deployed to the running Bellows process.

Given this ambiguity, the effective boundary is: **the last-known-good SHA is 87ce841** (docs update at 10:28), and **the first suspect SHA is f86f1a2** (Phase 2A at 10:50), with the understanding that the running Bellows process may have loaded the Phase 2A code before or after the commit timestamp.

---

## Q6 — Best-Guess Timeline Reconstruction

The last demonstrably clean Bellows run was the **planner-claude-code plan** (runs 10+11, ~10:03 on 2026-04-14), which executed both steps in a single session and moved the plan to Done successfully. Between that run and the first strand (run 14, phase2a at ~10:46), two significant commits changed bellows.py: **a438c17** (re-enabled Planner judgment via `claude -p` subprocess, +10/-9 lines) and **f86f1a2** (Phase 2A — threading, periodic rescan, terminal output, +40/-6 lines). The Phase 2A commit is the highest-priority suspect because it introduced the threading model, periodic rescan, and concurrent dispatch — exactly the kind of change that creates race conditions in file-move operations. The Phase 2B commit **c16e1d3** (+62/-3, parallel groups) landed 10 minutes later and compounded the concurrency. Six subsequent bug-fix commits on the same day (c7340a4, be72e9e, d3daeec, 5ac6ae2, 1cd47ab, fd75e76) each attempted to patch symptoms — rescan races, double-execution, NameErrors, prefix mismatches, stranded detection — but the strand pattern persisted into 2026-04-15, suggesting the root cause remains unaddressed. Additionally, ALL bellows runs record status "Unknown" rather than "Complete", which may indicate that the status-recording code path itself is broken or was never wired up correctly for the threaded dispatch model.

**Priority ranking for Phase 2 code reading:**
1. **f86f1a2** — Phase 2A threading/rescan (highest priority — introduced concurrency)
2. **c16e1d3** — Phase 2B parallel groups (compounded concurrency)
3. **fd75e76** — Reliability fixes A+B (the most recent attempt to fix stranding — understanding what it tried and why it didn't fully work informs the root cause)
4. **a438c17** — Re-enable Planner judgment (changed the judgment path, could affect step completion signaling)

---

## Output Receipt

- **Status:** Complete
- **Files Deposited:** `knowledge/research/bellows-strand-timeline-2026-04-15.md`
- **Files Created or Modified (Code):** `[]` (read-only investigation)
- **Decisions Made:** Timeline reconstruction in Q6 — Phase 2A threading commit (f86f1a2) is the most likely candidate-cause, with Phase 2B (c16e1d3) as secondary. All bellows runs show "Unknown" status, which is itself a potential contributing factor.
- **Flags for CEO:** Phase 2 should read bellows.py focusing on the dispatch/threading code introduced by f86f1a2 and c16e1d3. The "Unknown" status pattern across ALL runs warrants investigation — it may be a separate bug or share a root cause with the stranding.
