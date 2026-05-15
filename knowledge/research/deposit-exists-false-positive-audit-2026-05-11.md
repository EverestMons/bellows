# deposit_exists False-Positive Root Cause Audit

**Date:** 2026-05-11
**Author:** Systems Analyst (Bellows-dispatched)
**Plan:** diagnostic-deposit-exists-false-positive-audit-2026-05-11

---

## 1. Summary

Fourteen false-positive reproductions were found across 8 verdict requests spanning
2026-04-30 to 2026-05-08. The **dominant cause is Cause 1 — path resolution drift**
(11 of 14 reproductions): the gate evaluated deposit paths against `project_path`
while newly-created files existed only in `wt_path` (the worktree), and worktree
teardown executed AFTER gate evaluation. This cause was already fixed in commit
`2016d02` (2026-05-06) by adding Strategy 0 (worktree-first resolution), though
3 post-fix reproductions occurred because the daemon was not restarted. A secondary
cause — **Cause 5 (plan-agent evidence path convention mismatch)** — accounts for
18 individual gate-failure lines across 3 verdict requests where the plan's
`**Deposits:**` block declared bare `evidence/*.txt` paths but the agent created
files under `knowledge/qa/evidence/<slug>/`. This is NOT covered by the existing
fix and warrants a separate backlog item. Recommended fix shape: teach
`_resolve_deposit_path()` to attempt a recursive basename match under the QA
evidence tree, or — preferably — standardize plan-authored evidence paths to use
full project-relative paths.

---

## 2. Method

### Locations searched

| Location | What was checked |
|---|---|
| `bellows/verdicts/pending/` | 3 active verdict requests |
| `bellows/verdicts/pending/archived/` | 58 archived verdict requests |
| `bellows/verdicts/resolved/` | All `processed-verdict-*` files |
| `bellows/knowledge/decisions/Done/` | Completed plans with gate-5 history |
| `bellows/logs/` | JSON step logs |
| `bellows/knowledge/research/` | Prior diagnostics on this topic |

### Gate-5 implementation — verbatim

**File:** `bellows/gates.py:183-212` — `_resolve_deposit_path()`

```python
def _resolve_deposit_path(path, project_path, wt_path=None):
    # Strategy 0 (worktree-first): added 2026-05-06
    if wt_path is not None and wt_path != project_path:
        project_basename = os.path.basename(project_path)
        if path.startswith(project_basename + os.sep):
            wt_candidate = os.path.join(wt_path, path[len(project_basename) + 1:])
        else:
            wt_candidate = os.path.join(wt_path, path)
        if os.path.isfile(wt_candidate) or os.path.isdir(wt_candidate):
            return wt_candidate

    # Strategy 1: path as-is (absolute or CWD-relative)
    if os.path.isfile(path) or os.path.isdir(path):
        return os.path.abspath(path)
    # Strategy 2: project-relative
    p2 = os.path.join(project_path, path)
    if os.path.isfile(p2) or os.path.isdir(p2):
        return os.path.abspath(p2)
    # Strategy 3: parent-relative (path includes project dir name)
    p3 = os.path.join(os.path.dirname(project_path), path)
    if os.path.isfile(p3) or os.path.isdir(p3):
        return os.path.abspath(p3)
    return None
```

**Existence check function:** `os.path.isfile()` and `os.path.isdir()` (both).

**File:** `bellows/gates.py:215-240` — `_gate_deposit_exists()`

Path list sources:
1. **Agent-declared:** parses `### Files Deposited` section from `result_text` (lines 216-232).
2. **Plan-required:** calls `_extract_plan_required_deposits(step_text)` (lines 234-240),
   which prefers the `**Deposits:**` block (Rule 26) and falls back to legacy prose patterns.

**File:** `bellows/verdict.py:34-62` — `extract_primary_deposit()`

```python
DEPOSITS_BLOCK_RE = re.compile(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)')
BLOCK_BULLET_RE = re.compile(r'-\s+`([^`]+)`')
```

Recognizes plural `**Deposits:**` block (authoritative when present), returns first
`.md` path from bullet list. Falls back to `STRICT_DEPOSIT_RE`, `BOLD_NOUN_DEPOSIT_RE`,
and `INLINE_DEPOSIT_RE` for legacy prose forms. Singular `**Deposit:**` is handled by
the `STRICT_DEPOSIT_RE` fallback pattern. For plural-list blocks, only the first `.md`
file is returned; non-`.md` paths and directories are skipped.

---

## 3. Reproductions — Classification Table

### Group A: Cause 1 — Worktree path resolution drift (pre-fix, 2026-05-06)

| Plan slug | Step | Declared path | Cause | Evidence |
|---|---|---|---|---|
| diagnostic-backlog-hygiene-audit-2026-05-06 | 1 | `invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md` | 1 | File exists post-teardown at project_path; was in wt_path only at gate time. Strategy 3 resolves post-teardown. |
| executable-backlog-hygiene-edits-2026-05-06b | 2 | `invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-2-qa-2026-05-06.md` | 1 | Same mechanism. Form A path. |
| executable-backlog-hygiene-edits-2026-05-06b | 2 | `invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06b/` | 1 | Directory deposit, same mechanism. |
| executable-backlog-hygiene-edits-2026-05-06c | 2 | `invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-3-qa-2026-05-06.md` | 1 | Same mechanism. Form A path. |
| executable-backlog-hygiene-edits-2026-05-06c | 2 | `invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06c/` | 1 | Directory deposit, same mechanism. |
| executable-session-wrap-2026-05-06 | 2 | `knowledge/qa/session-wrap-2026-05-06-qa.md` | 1 | Form B path. Strategy 2 resolves post-teardown. |
| executable-session-wrap-2026-05-06 | 2 | `knowledge/qa/evidence/executable-session-wrap-2026-05-06/` | 1 | Directory, Form B, same mechanism. |
| diagnostic-tier-display-test-failure-2026-05-06 | 1 | `knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md` | 1 | Form B path. Strategy 2 resolves post-teardown. |

### Group B: Cause 1 recurring — daemon not restarted (post-fix, 2026-05-07/08)

| Plan slug | Step | Declared path | Cause | Evidence |
|---|---|---|---|---|
| executable-action-queue-aggregation-2026-05-07 | 3 | (main QA .md deposit) | 1 | `rule_20_self_check` also failed on .md file that exists post-teardown → confirms gate lacked wt_path. Fix commit `2016d02` at 2026-05-06T16:33; failure at 2026-05-07T16:02 → daemon running pre-fix code. |
| executable-action-queue-limit-and-contract-name-2026-05-08 | 2 | (main QA .md deposit) | 1 | Same pattern. Timestamp 2026-05-08T12:43. `rule_20_self_check` co-failure confirms. |
| executable-bellows-qa-prefix-and-skip-logging-2026-05-08 | 2 | (main QA .md deposit) | 1 | Bellows-self plan. Timestamp 2026-05-08T17:23. `rule_20_self_check` co-failure. |

### Group C: Cause 5 — Plan-agent evidence path convention mismatch (2026-05-07/08)

| Plan slug | Step | Declared path (example) | Cause | Evidence |
|---|---|---|---|---|
| executable-action-queue-aggregation-2026-05-07 | 3 | `evidence/orphan_handling.txt` (+ 5 more) | 5 | Plan `**Deposits:**` block lists bare `evidence/*.txt`. Agent created files at `knowledge/qa/evidence/action-queue-aggregation/*.txt`. Even with wt_path fix, Strategy 0 checks `wt_path/evidence/orphan_handling.txt` — doesn't exist there. 6 individual failures. |
| executable-action-queue-limit-and-contract-name-2026-05-08 | 2 | `evidence/main_route_display_name.txt` (+ 5 more) | 5 | Same pattern. 6 individual failures. |
| executable-bellows-qa-prefix-and-skip-logging-2026-05-08 | 2 | `evidence/skip_logging_dedup.txt` (+ 5 more) | 5 | Same pattern. Files at `knowledge/qa/evidence/qa-prefix-and-skip-logging/*.txt`. 6 individual failures. |

### Group D: Cause 1 variant — pre-worktree directory resolution (2026-04-30)

| Plan slug | Step | Declared path | Cause | Evidence |
|---|---|---|---|---|
| executable-planner-template-bellows-execution-model-section-2026-04-30 | 2 | `bellows/knowledge/qa/evidence/planner-template-bellows-execution-model-section-2026-04-30/` | 1 (variant) | Directory exists now. Strategy 3 should resolve. Pre-worktree era (no wt_path). Suspected: isdir() support may not have been present at gate-run time. Cannot verify retroactively. |

### Excluded — True positive (not false positive)

| Plan slug | Step | Declared path | Notes |
|---|---|---|---|
| executable-forge-cycle-12-2026-04-23 | 1 | `forge/knowledge/research/forge-cycle-12-step1-ingest-2026-04-23.md` | File genuinely missing. Forge project may have been cleaned. Gate was correct. |

---

## 4. Per-Cause Analysis

### Cause 1 — Path resolution drift (worktree vs project_path)

**Reproductions:** 11 confirmed + 1 suspected variant = 12 total (dominant)

**Mechanism:** Bellows creates a worktree at `project_path/.bellows-worktrees/<slug>/`
and dispatches the agent into it. The agent deposits files in the worktree. Gate
evaluation runs BEFORE worktree teardown. The original `_resolve_deposit_path()`
(pre-fix) tried three strategies — all against `project_path` or its parent. None
checked `wt_path`. Files were guaranteed invisible to the gate.

**Code path:**
- `bellows.py` line ~331: `gates.check(parsed, plan_text, current_step, project_path, ...)`
  — pre-fix, `wt_path` was NOT passed.
- `gates.py:215-240`: `_gate_deposit_exists()` called `_resolve_deposit_path(path, project_path)`
  — no `wt_path` parameter.
- `gates.py:183-212`: `_resolve_deposit_path()` tried S1/S2/S3 against `project_path` only.

**Fix (shipped 2026-05-06, commit `2016d02`):** Added `wt_path` parameter to
`_resolve_deposit_path()`, `_gate_deposit_exists()`, and `check()`. Added Strategy 0
(worktree-first) with guard `if wt_path is not None and wt_path != project_path`.
Threaded `wt_path=wt_path` at both call sites in `bellows.py`. Six unit tests added.

**Post-fix recurrence:** 3 verdict requests (2026-05-07/08) show the same pattern.
Co-occurring `rule_20_self_check` failures on main .md deposits confirm the daemon
was running pre-fix code — the fix existed on disk but wasn't loaded. This is an
operational gap (daemon restart), not a code gap.

### Cause 5 — Plan-agent evidence path convention mismatch (NEW)

**Reproductions:** 18 individual gate-failure lines across 3 verdict requests.

**Mechanism:** The plan's `**Deposits:**` block declares bare relative evidence paths
(e.g., `evidence/orphan_handling.txt`). The agent creates the files under
`knowledge/qa/evidence/<plan-slug>/orphan_handling.txt` — a deeper, slug-namespaced
directory. `_extract_plan_required_deposits()` (`gates.py:254-287`) faithfully
extracts the literal plan-declared path. None of the resolution strategies (S0-S3)
can bridge the gap because the declared path and the actual path differ structurally,
not just by prefix.

**Verification:**
- `evidence/orphan_handling.txt` → resolved via S0: `wt_path/evidence/orphan_handling.txt` → **does not exist**
- Actual file: `invoice-pulse/knowledge/qa/evidence/action-queue-aggregation/orphan_handling.txt` → **exists**
- The intermediate `action-queue-aggregation/` directory is not part of the declared path.

**Root cause is upstream of the gate:** the plan template (or the Planner) declares
evidence paths using a bare `evidence/` convention that doesn't match the agent's
actual directory structure. The gate correctly reports the declared path as missing.
This is a plan-authoring convention mismatch, not a gate resolution bug.

---

## 5. Recommended Fix Shape

**For Cause 1 (dominant, 12 reproductions):** Already fixed. No further action needed
beyond ensuring daemon restart after code changes. Consider adding a startup log line
that prints the `gates.py` mtime or a version hash so operators can verify the running
code matches the deployed code.

**For Cause 5 (secondary, 18 failure lines across 3 verdict requests):** The fix
belongs in the **Planner template**, not in `gates.py`. The Planner should emit
fully-qualified project-relative evidence paths in the `**Deposits:**` block (e.g.,
`knowledge/qa/evidence/<slug>/orphan_handling.txt` rather than `evidence/orphan_handling.txt`).
Alternatively, if bare `evidence/` paths are intentional shorthand, add a
**convention-aware normalization step** in `_extract_plan_required_deposits()`
(`gates.py:254-287`) that expands `evidence/<file>` to
`knowledge/qa/evidence/<plan-slug>/<file>` before resolution. The former (fix at
source) is preferred as it keeps the gate simple.

---

## 6. Open Questions

1. **Cause 1 variant (2026-04-30):** The single pre-worktree directory-deposit
   false positive (`planner-template-bellows-execution-model-section-2026-04-30`)
   cannot be fully verified. Strategy 3 should resolve the path NOW, but `isdir()`
   support may not have been present in the gate code at that date. Git blame would
   confirm but was not run to stay within scope.

2. **Daemon restart discipline:** Three post-fix reproductions (Group B) occurred
   because the daemon was not restarted after commit `2016d02`. There is no mechanism
   to detect code-vs-runtime drift. This is operational, not code-level, but recurs
   whenever `gates.py` is updated.

3. **Cause 2 (timing/fsync) status:** No reproductions attributable to fsync timing
   were found. All false positives have a structural explanation. Cause 2 is ruled
   out for this population but cannot be ruled out globally since mtime data is not
   preserved in verdict requests.

4. **Cause 4 (normalization/case) status:** No reproductions showed case or
   normalization differences between declared and actual paths. Cause 4 is ruled out
   for this population.
