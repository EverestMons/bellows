# Parallel-Plan scope_check Collision — Incident Timeline & Code-Path Trace

**Date:** 2026-05-03 | **Plan:** diagnostic-parallel-scope-check-collision-2026-05-03 | **Step:** 1 (combined)

---

## Phase 1A — 2026-04-30 Incident Reconstruction

### Plans Involved

| Plan | Slug | Parallel Group | Filename in Done/ |
|------|------|---------------|-------------------|
| A | `parallel-1-executable-deposit-exists-directory-paths-2026-04-30` | `parallel-1` | `parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md` |
| B | `executable-backlog-hygiene-sweep-2026-04-30` | None (sequential) | `executable-backlog-hygiene-sweep-2026-04-30.md` |
| C | `parallel-1-executable-ledger-pause-reason-code-2026-04-30` | `parallel-1` | `parallel-1-executable-ledger-pause-reason-code-2026-04-30.md` |

**Note:** The diagnostic plan text names plan B as `parallel-1-executable-backlog-hygiene-sweep-2026-04-30`, but the actual filename in `Done/` has no `parallel-1-` prefix — it was a sequential plan dispatched concurrently, not a member of the `parallel-1` group.

### Runner Log Mapping

Log filenames embed the runner's `datetime.now().strftime("%Y%m%d-%H%M%S")` at subprocess creation (`runner.py:43`). Each was identified by extracting the bootstrap prompt from `raw_output`:

| Log File | Runner Start (CDT) | Plan | Session ID |
|----------|-------------------|------|------------|
| `20260430-154422-step.json` | 15:44:22 | B — backlog-hygiene-sweep | `35fdc522-785c-4a35-af78-e3f943cabf14` |
| `20260430-154446-step.json` | 15:44:46 | A — deposit-exists-directory-paths | `942e7246-a751-4bee-b591-6c3e5e8e8bc7` |
| `20260430-154448-step.json` | 15:44:48 | C — ledger-pause-reason-code | `b449f771-2ff9-4587-9c6c-53bdf2bed87c` |

Dispatch order: B was dispatched first (non-parallel, separate plan). Plans A and C dispatched 24 seconds later as the `parallel-1` group with 2-second thread stagger (`bellows.py:593`).

### Git Commits During the Parallel Window

| SHA | Time (CDT) | Plan | Files Modified | Message |
|-----|-----------|------|---------------|---------|
| `e609ad3` | 15:46:15 | A (deposit-exists) | `gates.py`, `tests/test_gates.py`, `knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md` | `fix(gates): _resolve_deposit_path accepts directory paths (BACKLOG #11)` |
| `ebdc544` | 15:46:21 | B (backlog-hygiene) | `PROJECT_STATUS.md`, `knowledge/BACKLOG.md`, `knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md` | `docs: BACKLOG hygiene sweep — close 3 carried items reverified against live code` |
| `2354327` | 15:47:14 | C (ledger-pause) | `bellows.py`, `verdict.py`, `tests/test_verdict.py`, `knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md` | `feat(verdict): persist pause_reason_code in ledger entries (BACKLOG #12)` |

### Bellows DB Records (step-end timestamps)

Source: `bellows.db` `runs` table, `timestamp` column (recorded at `bellows.py:274` AFTER `runner.run_step()` returns).

| ID | Timestamp | Plan | Step | Status |
|----|-----------|------|------|--------|
| 505 | `15:46:21.917` | A (deposit-exists) | 1 | Complete |
| 506 | `15:46:22.358` | A (deposit-exists) | 1 | VerdictPending |
| 507 | `15:46:27.464` | B (backlog-hygiene) | 1 | Complete |
| 508 | `15:46:27.725` | B (backlog-hygiene) | 1 | VerdictPending |
| 509 | `15:47:20.126` | C (ledger-pause) | 1 | Complete |

### Chronological Timeline

| Time (CDT) | Event | Plan | Files | Notes |
|-------------|-------|------|-------|-------|
| 15:44:22 | `pre_diff` captured + `runner.run_step()` starts | B (backlog-hygiene) | — | Log: `20260430-154422-step.json` |
| 15:44:46 | `pre_diff` captured + `runner.run_step()` starts | A (deposit-exists) | — | Log: `20260430-154446-step.json` |
| 15:44:48 | `pre_diff` captured + `runner.run_step()` starts | C (ledger-pause) | — | Log: `20260430-154448-step.json`, 2s stagger after A |
| 15:44:48–15:47:14 | C's agent edits files in shared working tree | C (ledger-pause) | `bellows.py`, `verdict.py`, `tests/test_verdict.py` | **These files are DIRTY in the shared working tree throughout this window** |
| 15:46:15 | Git commit `e609ad3` | A (deposit-exists) | `gates.py`, `tests/test_gates.py` | A's own files leave dirty state |
| ~15:46:21 | **`post_diff` captured** | A (deposit-exists) | Sees: C's dirty files (`bellows.py`, `verdict.py`) | **CONTAMINATION POINT 1** |
| 15:46:21 | Git commit `ebdc544` | B (backlog-hygiene) | `PROJECT_STATUS.md`, `BACKLOG.md` | B's own files leave dirty state |
| 15:46:21.917 | DB: Step 1 Complete | A (deposit-exists) | `files_changed = [bellows.py, verdict.py]` | Scope_check FAILS — C's dirty files |
| ~15:46:27 | **`post_diff` captured** | B (backlog-hygiene) | Sees: C's dirty files (`bellows.py`, `tests/test_verdict.py`, `verdict.py`) | **CONTAMINATION POINT 2** |
| 15:46:27.464 | DB: Step 1 Complete | B (backlog-hygiene) | `files_changed = [bellows.py, tests/test_verdict.py, verdict.py]` | Scope_check FAILS — C's dirty files |
| 15:47:14 | Git commit `2354327` | C (ledger-pause) | `bellows.py`, `verdict.py`, `tests/test_verdict.py` | C's dirty files committed — leave working tree |
| 15:47:20.126 | DB: Step 1 Complete | C (ledger-pause) | — | No contamination (own files only) |

### Contamination Evidence from Verdict System

**Plan A (deposit-exists) Step 1 verdict request:**
- Gate failure: `scope_check: out-of-scope files: bellows.py, verdict.py`
- CEO override verdict: "The reported out-of-scope files (bellows.py, verdict.py) were committed by sibling parallel-1-executable-ledger-pause-reason-code-2026-04-30, not by this plan."
- Source: `verdicts/resolved/processed-verdict-parallel-1-executable-deposit-exists-directory-paths-2026-04-30-step-1.md`

**Plan B (backlog-hygiene) Step 1 verdict request:**
- Gate failure: `scope_check: out-of-scope files: bellows.py, tests/test_verdict.py, verdict.py`
- Files Changed: `bellows.py, tests/test_verdict.py, verdict.py`
- CEO override verdict: "The reported out-of-scope files (bellows.py, tests/test_verdict.py, verdict.py) were committed by sibling parallel-1-executable-ledger-pause-reason-code-2026-04-30"
- Source: `verdicts/pending/archived/verdict-request-backlog-hygiene-sweep-2026-04-30-step-1.md`

**Observation on file count difference:** Plan A reported 2 contaminating files (`bellows.py`, `verdict.py`); Plan B reported 3 (`bellows.py`, `tests/test_verdict.py`, `verdict.py`). Plan A's `post_diff` was captured ~6 seconds before Plan B's. The simplest explanation: the ledger agent edited `tests/test_verdict.py` in the 6-second window between the two captures (15:46:21 → 15:46:27). This is consistent with an agent editing source files first, then test files.

---

## Phase 1B — Code-Path Trace Anchored to Plan A (deposit-exists) Step 1

### Specific Contaminated Step Pair

- **Victim:** Plan A (deposit-exists), Step 1, dispatched at 15:44:46, `post_diff` captured at ~15:46:21
- **Contaminant:** Plan C (ledger-pause), editing `bellows.py`, `verdict.py`, `tests/test_verdict.py` on disk between 15:44:48 and 15:47:14

### Literal Code Path Walk-Through

**(a) Pre-diff capture — `bellows.py:265`**

```python
pre_diff = _capture_git_diff(project_path)
```

Executes at ~15:44:46 (before `runner.run_step()`). Calls `_capture_git_diff("/Users/marklehn/Desktop/GitHub/bellows")`.

At `bellows.py:414`:
```python
result = subprocess.run(
    ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."],
    cwd=project_path, capture_output=True, text=True, timeout=10,
)
```

**Working tree state at 15:44:46:** Plan C's agent has not started editing yet (runner started at 15:44:48, agent needs time to read plan and begin work). `bellows.py`, `verdict.py`, `tests/test_verdict.py` are CLEAN. Pre-diff captures whatever unrelated dirty files existed at that moment.

**(b) Runner execution — `bellows.py:267-269`**

```python
parsed = runner.run_step(bootstrap_prompt, project_path, model,
                          timeout=config.get("step_inactivity_timeout_seconds",
                                             config.get("step_timeout_seconds", 300)))
```

`runner.run_step()` spawns `claude -p` as a subprocess (`runner.py:49-56`). The subprocess runs from ~15:44:46 to ~15:46:15 (when A's agent commits `e609ad3`). During this window, Plan C's agent (running in a separate thread via `bellows.py:591-593`) is concurrently editing `bellows.py`, `verdict.py`, and `tests/test_verdict.py` in the SAME working tree at `cwd=/Users/marklehn/Desktop/GitHub/bellows`.

**(c) Post-diff capture — `bellows.py:281`**

```python
post_diff = _capture_git_diff(project_path)
```

Executes at ~15:46:21 (after `runner.run_step()` returns). Same `_capture_git_diff` function, same argv, same `cwd=/Users/marklehn/Desktop/GitHub/bellows`.

**Working tree state at ~15:46:21:**
- Plan A committed at 15:46:15 → `gates.py`, `tests/test_gates.py` are CLEAN (committed)
- Plan C has NOT committed yet (commits at 15:47:14) → `bellows.py`, `verdict.py` are DIRTY
- `tests/test_verdict.py` may or may not be dirty yet (it appeared in B's post_diff 6 seconds later but not in A's)

`git --no-pager diff --stat --relative -- .` returns stat lines for ALL dirty files, including C's uncommitted edits to `bellows.py` and `verdict.py`.

**(d) argv and cwd passed to `_capture_git_diff`**

- argv: `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]`
- cwd: `/Users/marklehn/Desktop/GitHub/bellows` (the shared project root)

The `--relative` flag and `-- .` pathspec scope the diff to the `bellows/` subtree. This correctly excludes files outside bellows/ but does NOT isolate per-thread changes — any thread's dirty files within `bellows/` appear in the output.

**(e) What `git --no-pager diff --stat --relative -- .` returns at ~15:46:21**

The command shows uncommitted working-tree changes. At this moment:
- `bellows.py` — dirty (C's edits, not yet committed) → **appears in output**
- `verdict.py` — dirty (C's edits, not yet committed) → **appears in output**
- A's own files (`gates.py`, `tests/test_gates.py`) — CLEAN (committed at 15:46:15) → **do not appear**
- B's files may or may not still be dirty (B commits at 15:46:21, nearly simultaneous)

Approximate `post_diff` output:
```
 bellows.py   | 15 +++++++++++----
 verdict.py   | 22 ++++++++++++++++------
 2 files changed, 26 insertions(+), 10 deletions(-)
```

**(f) `_parse_diff_stat(post_diff, pre_diff, project_path)` computation — `bellows.py:282`**

```python
files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
```

At `bellows.py:423-456`:
1. `parse_stat_map(pre_diff)` → `pre_map`: files dirty at step start (~15:44:46). `bellows.py` and `verdict.py` NOT present (Plan C hadn't started editing).
2. `parse_stat_map(post_diff)` → `post_map`: files dirty at step end (~15:46:21). Includes `bellows.py` and `verdict.py` from Plan C's edits.
3. `changed = [f for f, s in post_map.items() if pre_map.get(f) != s]` → `["bellows.py", "verdict.py"]`. These files are in `post_map` but not in `pre_map`, so the stat values differ (absent vs present).
4. `..` filter: neither path contains `..` components → both pass.
5. Returns: `["bellows.py", "verdict.py"]` (sorted).

**(g) `_gate_scope_check` with that list — `gates.py:233-258`**

Called via `gates.check()` at `bellows.py:283`:
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```

At `gates.py:233`:
1. `files_changed = ["bellows.py", "verdict.py"]` — not empty, so no early return.
2. `step_text = _extract_step_text(plan_text, 1)` — extracts Step 1's text from the deposit-exists plan.
3. For each file in `files_changed`:
   - `bellows.py`: not in `SCOPE_ALLOWLIST`, not starting with any `SCOPE_ALLOWLIST_PREFIXES`, not mentioned in step_text → **out_of_scope**
   - `verdict.py`: same checks → **out_of_scope**
4. `out_of_scope = ["bellows.py", "verdict.py"]` → appends gate failure:
   ```
   scope_check: out-of-scope files: bellows.py, verdict.py | plan step context: ## STEP 1 — ...
   ```
5. Gate result: `passed = False`, `failures = [scope_check]`.

This matches exactly what the archived verdict request records.

---

## Phase 1C — Canary Reproduction

**Gap documented:** The canary cannot be dispatched within this diagnostic execution context. This diagnostic is running as a Bellows-dispatched agent itself. Depositing canary plans to `knowledge/decisions/` would trigger Bellows to dispatch them in new threads while this diagnostic is still executing, but the diagnostic cannot observe Bellows's internal state (verdict request content, files_changed lists) from outside the main process. The canary design is sound but requires either (a) direct Bellows process instrumentation, or (b) a manual CEO-supervised dispatch where the CEO reads the verdict requests and reports back.

**Canary design (for future execution if needed):**
- Plan A writes `knowledge/research/canary-A-marker.txt`, sleeps 30s, then commits
- Plan B writes `knowledge/research/canary-B-marker.txt`, commits immediately, sleeps 30s
- Expected result: Plan A's `post_diff` captures `canary-B-marker.txt` as dirty (B committed it, leaving no trace, but the working tree was clean for B's file after B's commit — UNLESS B's file was still staged/dirty at the moment A captures post_diff)

**Note on canary validity:** The expected canary result depends on whether B's file appears in A's working-tree diff. If B commits its marker before A's post_diff capture, B's file would NOT be dirty — it's committed. The canary would only reproduce the contamination if B's file is in an uncommitted state during A's post_diff capture. This means the canary needs B to WRITE the file but NOT commit it until after A's post_diff captures, or B must create additional dirty files beyond the marker. The incident vector is specifically: sibling edits files that remain uncommitted at the time of the victim's post_diff capture. The 30-second sleep design handles this correctly: B writes and commits immediately, but if we need B's file to be dirty, the canary should be modified so B writes but delays its commit.

**Mitigation for the gap:** The incident evidence from Phase 1A is sufficient to anchor the Phase 2 candidate evaluation. The timeline, code trace, and verdict system records provide literal file-level evidence of the contamination vector. The canary would confirm reproducibility but would not change the structural analysis.

---

## Phase 1D — Observed Contamination Vector

1. **Literal mechanism:** When multiple plans execute concurrently (whether via `parallel-N-` group dispatch or coincidental sequential dispatch), they share a single git working tree at the project root. Each plan's `claude -p` subprocess writes to files on disk as part of its work. Bellows captures `post_diff` for plan A by running `git diff --stat --relative -- .` (at `bellows.py:281,414`) which reports ALL uncommitted working-tree changes, not just those made by plan A's agent. In the 2026-04-30 incident, Plan C (ledger-pause-reason-code) edited `bellows.py`, `verdict.py`, and `tests/test_verdict.py` between 15:44:48 and 15:47:14. Plan A's (deposit-exists) `post_diff` was captured at ~15:46:21 — 53 seconds before C committed — so C's dirty files appeared in A's working-tree diff. `_parse_diff_stat` correctly identified them as "new" relative to `pre_diff` (they were not dirty at 15:44:46 when A started). `_gate_scope_check` correctly flagged them as out-of-scope for Plan A.

2. **Canary status:** Not executed (see Phase 1C). The Phase 1A incident evidence is deterministic — the code path is fully traceable from source with line-level precision, and the verdict system records confirm the exact contaminating files.

3. **Required property of a fix:** A valid fix must ensure that plan A's `files_changed` list contains ONLY files modified by plan A's own `claude -p` subprocess. Any mechanism that reads shared state (working-tree dirty files, git log without per-plan filtering, file checksums of files on the shared disk) will be contaminated when a sibling writes to the same working tree. The fix must either (a) isolate each plan's working tree, (b) scope the observation mechanism to a specific process/agent identity, or (c) use a commit-attribution mechanism that is immune to concurrent dirty-file interference.

---

## Output Receipt
**Agent:** Bellows Developer (combined diagnostic execution)
**Step:** 1 (Phase 1)
**Status:** Complete (Phase 1C canary not dispatched — gap documented)

### What Was Done
Reconstructed the 2026-04-30 parallel-plan scope_check collision incident with a chronological timeline, mapped runner log files to plan identities, traced the literal code path through bellows.py with line numbers and specific file paths for one contaminated step pair, and documented the observed contamination vector.

### Files Deposited
- `bellows/knowledge/research/parallel-collision-incident-timeline-2026-05-03.md` — incident timeline, code-path trace, and contamination vector specification

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- Skipped live canary dispatch (Phase 1C) — cannot observe Bellows internal state from within a dispatched diagnostic. Documented the gap explicitly.
- Used runner log filenames to establish step-start times (the DB only records step-end times).

### Flags for CEO
- Phase 1C canary not executed. If the CEO requires live reproduction, a separate canary plan should be dispatched manually with CEO observation of the verdict request files.

### Flags for Next Step
- The contamination vector (Phase 1D) is the ground truth for candidate evaluation. Any candidate that reads shared working-tree state will fail the "does it return B's files for A?" test.
