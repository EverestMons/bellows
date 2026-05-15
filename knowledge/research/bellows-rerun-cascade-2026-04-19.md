# Bellows Re-Run Cascade Characterization — 2026-04-19

**Diagnostic:** in-progress-diagnostic-bellows-rerun-cascade-2026-04-19.md
**Date:** 2026-04-19
**Investigator:** Systems Analyst (Claude Code)

---

## 1. Post-Restart Code State

**bellows.py — PlanHandler.on_moved:** Lines 486–488. Present and active.

```python
def on_moved(self, event):
    if not event.is_directory:
        self._handle(event.dest_path)
```

**Verdict: post-fix code is loaded.** (BACKLOG #4, shipped 2026-04-19.)

**verdict.py — extract_primary_deposit:** Lines 34–62. Block-aware parsing via `DEPOSITS_BLOCK_RE` at line 38, with `BLOCK_BULLET_RE` iteration at lines 40–47. Falls back to legacy regexes only when no block is present (line 50 onward).

**Verdict: post-fix code is loaded.** (BACKLOG #6, shipped 2026-04-19.)

**gates.py — _extract_plan_required_deposits:** Lines 166–199. Block-form preference at lines 173–182: searches for `[> ]*\*\*Deposits:\*\*` block, extracts backtick-quoted paths, returns early without applying legacy prose regexes.

**Verdict: post-fix code is loaded.** (BACKLOG #6, shipped 2026-04-19.)

---

## 2. Current Filesystem State

### decisions/ (non-recursive)

| Filename | Notes |
|---|---|
| in-progress-diagnostic-bellows-rerun-cascade-2026-04-19.md | This diagnostic (claimed) |
| roadmap-per-plan-step-state-tracker-2026-04-17.md | Non-executable roadmap |
| verdict-pending-diagnostic-bellows-deposit-path-formats-2026-04-18.md | Awaiting verdict |
| verdict-pending-diagnostic-bellows-verdict-file-schema-2026-04-18.md | Awaiting verdict |
| verdict-pending-diagnostic-extract-primary-deposit-shape-2026-04-19.md | Awaiting verdict |
| verdict-pending-diagnostic-gates-deposit-parser-current-state-2026-04-19.md | Awaiting verdict |
| verdict-pending-diagnostic-rule-26-gate-smoke-test-2026-04-19.md | Awaiting verdict |

### decisions/Done/ — filtered to verdict-lifecycle-coupling

| Filename | Size | Mtime |
|---|---|---|
| verdict-pending-diagnostic-verdict-lifecycle-coupling-2026-04-19.md | 7605 bytes | Apr 19 18:01:35 |

Note: The file in Done/ retains the `verdict-pending-` prefix — not the Planner's intended `diagnostic-*` name. Mtime 18:01:35 reflects the original plan content write time (shutil.move preserves mtime on macOS), not the time of the move to Done/.

### verdicts/pending/

**Empty.** Only .DS_Store present. No active verdict requests.

---

## 3. Trace the 18:14:32 Re-Run Trigger

### Available log files in the 18:xx window

| Log File | Session | Cost |
|---|---|---|
| 20260419-180141-step.json | 6ac744e6 (first run) | $0.983 |
| 20260419-181432-step.json | 8d132b45 (re-run) | $1.065 |

No other log files exist in the 18:06–18:15 window.

### DB records for verdict-lifecycle-coupling

| Row | Timestamp | plan_path | project | Session | Step | Status | Cost |
|---|---|---|---|---|---|---|---|
| 331 | 18:07:35 | decisions/in-progress-diagnostic-* | bellows | 6ac744e6 | 1 | Complete | 0.983 |
| 332 | 18:07:36 | decisions/in-progress-diagnostic-* | bellows | 6ac744e6 | 1 | VerdictPending | 0.983 |
| 333 | 18:20:41 | decisions/Done/in-progress-diagnostic-* | bellows/knowledge | 8d132b45 | 1 | Complete | 1.065 |
| 334 | 18:20:42 | decisions/Done/in-progress-diagnostic-* | bellows/knowledge | 8d132b45 | 1 | VerdictPending | 1.065 |

### What Bellows saw

The re-run (row 333) shows `plan_path = .../decisions/Done/in-progress-diagnostic-verdict-lifecycle-coupling-2026-04-19.md`. The `in-progress-` prefix was added by Bellows during the claim step (bellows.py L208–210). Before claiming, the filename was `diagnostic-verdict-lifecycle-coupling-2026-04-19.md` — the Planner's intended Done/ filename, which had the `verdict-pending-` prefix stripped.

**The file matched the `diagnostic-*` prefix pattern, which `is_runnable_plan` accepts.**

---

## 4. is_runnable_plan Audit

**bellows.py lines 424–427:**

```python
def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
    return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename))
```

**Rejection logic:**
- Rejects `in-progress-*`, `verdict-pending-*`, `halted-*` prefixes
- Requires `(parallel-N-)?(executable|diagnostic)-*.md` pattern
- Does **NOT** check the directory path — only the bare filename
- Does **NOT** reject files inside a `Done/` subdirectory

**Cross-reference with Q3:** The Planner moved the file to `Done/diagnostic-verdict-lifecycle-coupling-2026-04-19.md`. The filename starts with `diagnostic-`, which is_runnable_plan accepts. The file's location in `Done/` is invisible to this function.

---

## 5. Rename-Path Audit

### Timeline reconstruction

1. **18:07:36** — First run completes. Plan renamed to `verdict-pending-diagnostic-*` in decisions/.
2. **~18:08–18:14** — Planner reviews findings, moves file: `decisions/verdict-pending-diagnostic-*` to `decisions/Done/diagnostic-*` (stripping `verdict-pending-` prefix as intended).
3. **~18:14:30** — Watchdog `on_moved` fires. `event.dest_path = decisions/Done/diagnostic-*`. Handler calls `_handle(dest_path)`.
4. **~18:14:30** — `is_runnable_plan("diagnostic-verdict-lifecycle-coupling-2026-04-19.md")` returns True. `handle_new_plan` dispatches.
5. **18:14:32** — `run_plan` claims the file: moves `diagnostic-*` to `in-progress-diagnostic-*` (both inside Done/).
6. **18:20:41** — Re-run completes. Gates fail (2 failures). Plan renamed to `verdict-pending-diagnostic-*` in Done/.

### Hypothesis supported: (c) — sequential, not a race

The Planner's move succeeded and correctly created `Done/diagnostic-*`. But `on_moved` treated the dest_path as a new plan. Bellows's own lifecycle (claim, execute, verdict-pending) then overwrote the Planner's intended naming. The `verdict-pending-` prefix now on the file in Done/ was applied by Bellows during step 6, NOT retained from the original file.

**Key evidence:** The file in Done/ is named `verdict-pending-diagnostic-*` (not `diagnostic-*`), and DB row 333 confirms Bellows operated on `Done/in-progress-diagnostic-*` — proving it claimed the file the Planner had placed in Done/.

---

## 6. Risk Assessment — 5 Verdict-Pending Plans

| Plan | Verdict in resolved/? | Classification |
|---|---|---|
| verdict-pending-diagnostic-bellows-deposit-path-formats-2026-04-18.md | No | stuck (no verdict in queue) |
| verdict-pending-diagnostic-bellows-verdict-file-schema-2026-04-18.md | No | stuck (no verdict in queue) |
| verdict-pending-diagnostic-extract-primary-deposit-shape-2026-04-19.md | No | stuck (no verdict in queue) |
| verdict-pending-diagnostic-gates-deposit-parser-current-state-2026-04-19.md | No | stuck (no verdict in queue) |
| verdict-pending-diagnostic-rule-26-gate-smoke-test-2026-04-19.md | No | stuck (no verdict in queue) |

**None have corresponding verdict files in `verdicts/resolved/`.** All are stuck awaiting Planner verdict.

**Re-run risk:** All 5 are vulnerable to the identical re-run cascade. When the Planner issues a continue verdict and moves any of these to Done/ with a `diagnostic-*` filename, `on_moved` will fire, `is_runnable_plan` will accept the filename, and Bellows will re-execute the plan from inside Done/. The same project_path miscalculation (parents[2] off by one) and gate failures will occur.

---

## 7. Gate Failure Signature

**The verdict request file for the re-run is not available** — `verdicts/pending/` is empty and no processed-verdict file exists in `verdicts/resolved/` for this slug. Verbatim gate-failure strings cannot be quoted.

**Inferred failures from code analysis (2 failures, both gate 5 — deposit_exists):**

The re-run computed `project_path = .../bellows/knowledge` (bellows.py L185: `plan_p.parents[2]`, where plan_path had an extra `Done/` directory level). The correct value is `.../bellows`.

`_resolve_deposit_path` (gates.py L111–125) checks three strategies, all of which fail with the wrong project_path:

For deposit path `bellows/knowledge/research/verdict-lifecycle-coupling-2026-04-19.md`:
- Strategy 1 (CWD-relative): resolves to `bellows/bellows/knowledge/research/...` — not found
- Strategy 2 (`join(project_path, path)`): resolves to `bellows/knowledge/bellows/knowledge/research/...` — not found
- Strategy 3 (`join(dirname(project_path), path)`): resolves to `bellows/bellows/knowledge/research/...` — not found

**Both plan-required deposits would fail:** the primary findings file and the agent-prompt-feedback.md file. Two failures matches the reported `failures=2`.

---

## 8. Hypothesis Summary

**Causal chain:** The BACKLOG #4 fix (on_moved handler, shipped 2026-04-19) correctly handles plan files moved INTO the decisions/ directory but does not distinguish moves TO subdirectories. When the Planner moved the completed verdict-lifecycle-coupling plan to decisions/Done/ at ~18:14, on_moved fired with dest_path inside Done/. is_runnable_plan only checks the filename (diagnostic-*), not the directory, so it accepted the file. run_plan claimed it, computed project_path from parents[2] (off by one due to Done/ nesting), executed the diagnostic a second time ($1.07), and gate 5 failed twice because the wrong project_path made deposit resolution fail.

**Strongest evidence FOR:** DB row 333 records plan_path = `decisions/Done/in-progress-diagnostic-*` with project = `bellows/knowledge` — the Done/ directory and wrong project_path are both captured in the database, confirming the file was claimed and executed from inside Done/.

**Strongest evidence AGAINST:** Watchdog with `recursive=False` (bellows.py L683) should only emit events for the top-level watched directory. Whether on_moved fires for a move whose destination is in a subdirectory depends on the macOS FSEvents implementation and watchdog version. However, the DB evidence is conclusive that the re-run occurred from Done/, making this the only viable trigger path — the startup scan and _rescan both only list the top-level directory.
