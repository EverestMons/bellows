# deposit_exists False Positive Root Cause (BACKLOG #1)

**Root Cause: (b) path resolution drift — gate evaluates deposit_exists against `project_path` (main project directory) while agent deposits exist only in `wt_path` (worktree); worktree teardown copies files back AFTER gate evaluation, creating a structural false-negative window.**

**Date:** 2026-05-06
**Plan:** diagnostic-deposit-exists-false-positive-root-cause-2026-05-06
**Agent:** Bellows Systems Analyst

---

## Task 1 — Static Analysis of `_resolve_deposit_path`

### project_path Derivation

`bellows.py:215-216`:
```python
plan_p = pathlib.Path(plan_path)
project_path = str(plan_p.parents[2])
```

For all 5 reproductions, the plans reside in `invoice-pulse/knowledge/decisions/`. Therefore:
- `project_path` = `/Users/marklehn/Desktop/GitHub/invoice-pulse`

invoice-pulse has its own `.git` directory (confirmed: `/Users/marklehn/Desktop/GitHub/invoice-pulse/.git/` is a full repository with 23 entries). Therefore `_create_worktree` at `bellows.py:562` creates a detached-HEAD worktree at:
- `wt_path` = `/Users/marklehn/Desktop/GitHub/invoice-pulse/.bellows-worktrees/<slug>`

bellows/ has NO `.git` (confirmed). This distinction is critical — invoice-pulse plans get worktree isolation; bellows-self plans do not.

### Path Resolution Trace — Form A (invoice-pulse/ prefix, reproductions 1-3)

**Example: Reproduction 1** — path = `invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md`

| Strategy | Constructed path | Exists NOW | Exists at gate time |
|---|---|---|---|
| S1 (as-is, CWD-relative) | `/Users/marklehn/Desktop/GitHub/bellows/invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md` | NO | NO |
| S2 (project_path join) | `/Users/marklehn/Desktop/GitHub/invoice-pulse/invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md` | NO (double prefix) | NO |
| S3 (parent join) | `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md` | YES | NO — file was in worktree only |

S3 resolves TODAY because worktree teardown cherry-picked the agent's commits back to the main checkout. At gate-evaluation time (before teardown), the file existed only at `/Users/marklehn/Desktop/GitHub/invoice-pulse/.bellows-worktrees/<slug>/knowledge/research/backlog-hygiene-audit-2026-05-06.md`.

All Form A reproductions (R1, R2a, R2b, R3a, R3b) follow the same pattern: S3 is the matching strategy, but it returns FOUND only post-teardown.

### Path Resolution Trace — Form B (no prefix, reproductions 4-5)

**Example: Reproduction 5** — path = `knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md`

| Strategy | Constructed path | Exists NOW | Exists at gate time |
|---|---|---|---|
| S1 (as-is, CWD-relative) | `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md` | NO (wrong project) | NO |
| S2 (project_path join) | `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md` | YES | NO — file was in worktree only |
| S3 (parent join) | `/Users/marklehn/Desktop/GitHub/knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md` | NO | NO |

S2 resolves TODAY; at gate time, file was only in the worktree.

All Form B reproductions (R4a, R4b, R5) follow the same pattern: S2 is the matching strategy, but it returns FOUND only post-teardown.

### Empirical Verification

Post-teardown filesystem check (all 8 deposit paths across 5 reproductions):

```
R1  (Form A) invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md        → EXISTS (12729 bytes, mtime 13:00)
R2a (Form A) invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-2-qa-2026-05-06.md   → EXISTS (4461 bytes, mtime 14:01)
R2b (Form A) invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06b/ → DIR EXISTS
R3a (Form A) invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-3-qa-2026-05-06.md   → EXISTS (5298 bytes, mtime 14:35)
R3b (Form A) invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06c/ → DIR EXISTS
R4a (Form B) knowledge/qa/session-wrap-2026-05-06-qa.md                                  → EXISTS at invoice-pulse (4801 bytes, mtime 15:02)
R4b (Form B) knowledge/qa/evidence/executable-session-wrap-2026-05-06/                   → DIR EXISTS at invoice-pulse
R5  (Form B) knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md        → EXISTS at invoice-pulse (3193 bytes, mtime 14:47)
```

All 8 paths resolve against `project_path` NOW. All 8 failed at gate-evaluation time because the files were in the worktree, and teardown had not yet run.

---

## Task 2 — Timing Analysis (Hypothesis (a))

### Gate-Invocation Sequence in `bellows.py::run_plan()`

The execution sequence is deterministic, not racy:

1. **Line 282**: `wt_path = _create_worktree(project_path, plan_slug)` — worktree created
2. **Line 296**: `pre_diff = _capture_git_diff(wt_path)` — pre-step baseline captured
3. **Line 298-300**: `parsed = runner.run_step(bootstrap_prompt, wt_path, ...)` — agent runs in `wt_path`
4. **Line 329**: `post_diff = _capture_git_diff(wt_path)` — post-step diff captured from `wt_path`
5. **Line 331**: `gate_result = gates.check(parsed, plan_text, current_step, project_path, ...)` — **gate evaluates against `project_path`, NOT `wt_path`**
6. **Line 358-360** (while-loop pause) or **Line 444-446** (final-step pause): `_teardown_worktree(project_path, wt_path, plan_slug)` — cherry-pick + copy-back runs AFTER gate

The gap between steps 5 and 6 is not a race — it is the deterministic execution order. No amount of `flush()`, `sync()`, or `time.sleep()` would close it. The gate structurally checks the wrong directory.

### Synchronization Between Agent Exit and Gate

The agent subprocess exits (return code 0) and `runner.run_step()` returns the parsed output. There is no additional synchronization (`flush()`, `sync()`, `time.sleep()`) between agent exit and `gates.check()` — but this is irrelevant. Even with perfect synchronization, the files the agent wrote are in the worktree, and the gate checks `project_path`.

### Assessment

Hypothesis (a) — timing race — is **not the root cause**. The timing is deterministic. The issue is that gate evaluation is ordered BEFORE worktree teardown, and the gate receives `project_path` instead of `wt_path`. A race implies non-deterministic failure; this failure is guaranteed for every newly-created deposit in a worktree-isolated plan.

---

## Task 3 — Stale-Snapshot Analysis (Hypothesis (c))

### Does `gates.check()` Operate Against a Pre-Step Snapshot?

No. `gates.check()` receives `project_path` (a string) and calls `_resolve_deposit_path()` which uses live `os.path.isfile()` / `os.path.isdir()` calls. There is no filesystem snapshot, mtime cache, or pre-step state capture used by the deposit gate.

The `pre_diff` / `post_diff` mechanism at `bellows.py:296,329` captures git diff output for `files_changed` detection (used by `scope_check` gate), but `deposit_exists` does not consult this data.

### Does `bellows.py` Capture Any Pre-Step Filesystem State?

Only `_capture_git_diff(wt_path)` at line 296 (pre-step) and line 329 (post-step). These are git diff stat outputs, not filesystem snapshots. They feed into `_parse_diff_stat()` which computes `files_changed` for the `scope_check` gate. The `deposit_exists` gate ignores `files_changed` entirely.

### Assessment

Hypothesis (c) — stale snapshot — is **ruled out**. The gate uses live `os.path.isfile()` / `os.path.isdir()` calls. The issue is not that the gate sees stale data — it sees live data from the wrong directory.

---

## Task 4 — Agent-Receipt Parser Regression Check (Hypothesis (d))

### 2026-05-05 Fix Status

The fix at `gates.py:160-161` is intact:

```python
m = re.match(r'`([^`]+)`', line[2:].strip())
path = m.group(1) if m else line[2:].strip().strip("`")
```

This correctly extracts backtick-quoted paths from the `### Files Deposited` section, handling the `- \`path\` — description` format.

### Code Path for the 5 Reproductions

The error message in all 5 reproductions is `"plan-required deposit missing (not declared by agent): <path>"`. This message originates from `gates.py:173`:

```python
failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"})
```

This fires at `gates.py:172` when:
1. `path not in agent_declared` — the plan-required path is not in the agent's `### Files Deposited` set
2. `_resolve_deposit_path(path, project_path) is None` — the path cannot be found on disk

The agent-receipt parser at lines 154-165 is not the failure point — the failure occurs downstream at the plan-required check. Even if the agent-receipt parser works perfectly (and it does, post-2026-05-05 fix), the plan-required paths still fail `_resolve_deposit_path` because the files are in the worktree.

### Why `path not in agent_declared` Is True

The agent runs in the worktree and writes paths relative to its CWD. The plan declares paths in governance-root-relative form (Form A: `invoice-pulse/knowledge/...`) or project-relative form (Form B: `knowledge/...`). The agent's receipt paths are in project-relative form (matching its CWD in the worktree). For Form A, the plan path includes the `invoice-pulse/` prefix but the agent-declared path does not — different strings, so `path not in agent_declared` = True.

### Assessment

Hypothesis (d) — agent-receipt parser regression — is **ruled out**. The 2026-05-05 fix is intact. The failure occurs in the plan-required check (lines 168-173), not the agent-receipt section (lines 154-165). The agent-receipt parser is functioning correctly.

---

## Task 5 — Path-Form Variant Impact

### Form A (3 reproductions): `invoice-pulse/` prefix (governance-root-relative)

- **project_path:** `/Users/marklehn/Desktop/GitHub/invoice-pulse`
- **Resolution:** Strategy 3 (parent join) constructs the correct absolute path: `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/research/...`
- **Why it fails at gate time:** File exists only in worktree at `/Users/marklehn/Desktop/GitHub/invoice-pulse/.bellows-worktrees/<slug>/knowledge/research/...`
- **Why it succeeds post-teardown:** Teardown cherry-picks the commit, placing the file at the Strategy 3 path

### Form B (2 reproductions): no prefix (project-root-relative)

- **project_path:** `/Users/marklehn/Desktop/GitHub/invoice-pulse`
- **Resolution:** Strategy 2 (project join) constructs the correct absolute path: `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/research/...`
- **Why it fails at gate time:** File exists only in worktree at `/Users/marklehn/Desktop/GitHub/invoice-pulse/.bellows-worktrees/<slug>/knowledge/research/...`
- **Why it succeeds post-teardown:** Teardown cherry-picks the commit, placing the file at the Strategy 2 path

### Same Mechanism, Different Strategies

Both forms fail by the same mechanism: the file is in the worktree, not in `project_path`. The resolution strategies (S3 for Form A, S2 for Form B) are different but irrelevant — neither strategy tries the worktree path. The fix is the same for both forms: pass `wt_path` to the gate instead of (or in addition to) `project_path`.

---

## Task 6 — Verdict and Ranking

### Confirmed Root Cause

**(b) Path resolution drift** — specifically, the gate infrastructure has no concept of worktrees. `gates.check()` at `bellows.py:331` receives `project_path` but the agent deposited files in `wt_path`. `_resolve_deposit_path()` tries three resolution strategies against `project_path` and its parent; none try `wt_path`. Worktree teardown (`_teardown_worktree`) runs AFTER gate evaluation, so files are guaranteed to be absent from `project_path` at gate time for any newly-created deposit.

This is a structural gap introduced when worktree isolation was added (commit `36b2bba`, 2026-05-03). The gate code was not updated to receive or check the worktree path. Every worktree-isolated plan that creates a new deposit file will trigger this false positive — it is not intermittent.

### Ruled Out

- **(a) Timing race:** The ordering is deterministic (gate → teardown), not racy. No synchronization fix can close the gap because the gate checks the wrong directory entirely.
- **(c) Stale snapshot:** The gate uses live `os.path.isfile()` / `os.path.isdir()`. No snapshot, cache, or pre-step state is consulted by `deposit_exists`.
- **(d) Agent-receipt parser regression:** The 2026-05-05 fix is intact at `gates.py:160-161`. The failure occurs in the plan-required check (lines 168-173), not the agent-receipt parser (lines 154-165).

### Inconclusive

None. The evidence is sufficient to confirm (b) and rule out (a), (c), (d).

### Fix Shape (High-Level Only)

Pass `wt_path` to `gates.check()` as an additional parameter (or replace `project_path` with `wt_path` for the duration of gate evaluation). Inside `_gate_deposit_exists`, use the worktree path for `_resolve_deposit_path` calls so that newly-created deposits in the worktree are found. This requires: (1) adding a `wt_path` parameter to `gates.check()` and threading it to `_gate_deposit_exists` → `_resolve_deposit_path`, (2) updating the two `gates.check()` call sites in `bellows.py` (lines 331 and 416) to pass `wt_path`, and (3) adding a fourth resolution strategy in `_resolve_deposit_path` that tries `os.path.join(wt_path, path)`. Estimated scope: ~10 LOC across `gates.py` and `bellows.py`.

---

## Rule 20 Self-Check

```
SELF-CHECK PASSED
Findings file: bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md
Plan in-progress: bellows/knowledge/decisions/in-progress-diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md
```

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced the `deposit_exists` false positive root cause across all 5 reproductions. Confirmed hypothesis (b) — path resolution drift — as the root cause: the gate evaluates against `project_path` while deposits exist only in the worktree (`wt_path`), and worktree teardown runs after gate evaluation. Ruled out hypotheses (a), (c), (d) with evidence. Both path forms (A and B) fail by the same mechanism.

### Files Deposited
- `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md`

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified root cause as hypothesis (b) based on static analysis of code sequencing and empirical path-resolution traces
- Confirmed both path forms fail by the same mechanism (worktree vs project_path mismatch)

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic)
