# Worktree Teardown Current State Findings (OP-001 Recheck)

**Date:** 2026-05-05 | **Agent:** Bellows Developer | **Plan:** diagnostic-worktree-teardown-current-state-2026-05-05

---

## Investigation Section 1 — `.git` State

### Verbatim Command Output

```
$ git -C /Users/marklehn/Desktop/GitHub/bellows rev-parse --git-dir 2>&1
/Users/marklehn/Desktop/GitHub/.git

$ git -C /Users/marklehn/Desktop/GitHub/bellows rev-parse --show-toplevel 2>&1
/Users/marklehn/Desktop/GitHub

$ git -C /Users/marklehn/Desktop/GitHub/bellows worktree list 2>&1
/Users/marklehn/Desktop/GitHub  42e6fc6 [main]
```

### Assessment

Bellows repo root resolves to `/Users/marklehn/Desktop/GitHub` (governance-root), NOT to `/Users/marklehn/Desktop/GitHub/bellows`. Bellows has no project-local `.git` directory or file. This is the **original OP-001 precondition** — still structurally present.

**However**, this is now an **accepted and handled** condition. The 2026-05-04 detect-and-skip fix (commit `06aa938`) explicitly checks for this at `bellows.py:528`:
```python
if not os.path.exists(os.path.join(project_path, ".git")):
    ...
    return project_path
```
When no `.git` exists, `_create_worktree` returns `project_path` as-is, and `_teardown_worktree` short-circuits via `if wt_path == project_path: return` at line 562. Bellows-self plans run in-place without worktree isolation.

---

## Investigation Section 2 — Worktree Work Timeline (May 3–5)

| # | Date | Commit | Plan Filename | Purpose | Status |
|---|------|--------|---------------|---------|--------|
| 1 | 2026-05-03 | `36b2bba` | executable-bellows-worktree-impl-2026-05-03 | Per-plan git worktree implementation — `_create_worktree`, `_teardown_worktree`, cherry-pick merge-back, dirty file copy-back, startup prune, `.gitignore` update | Shipped |
| 2 | 2026-05-03 | `f14e7ce`, `abb452` | executable-bellows-worktree-tests-2026-05-03 | Unit + integration tests (6 unit in test_bellows.py, 7 integration in test_worktree.py) | Shipped |
| 3 | 2026-05-03 | `272fbe4` | fix-plan-worktree-teardown-type-mismatch-2026-05-03 | Fix type-contract violation: 4 sites in bellows.py changed from string to dict format in `gate_result["failures"]` | Shipped |
| 4 | 2026-05-03 | `9786e87` | executable-corrective-narrow-is-diagnostic-override-2026-05-03 | Fix multi-step diagnostic step-count regression (related, not worktree-specific) | Shipped |
| 5 | 2026-05-04 | `06aa938` | executable-monorepo-worktree-fix-2026-05-04 | Detect-and-skip: `_create_worktree` returns `project_path` when no `.git` exists (bellows-self monorepo trap) | Shipped |
| 6 | 2026-05-04 | `4c056db` | executable-backlog-capture-monorepo-worktree-2026-05-04 | BACKLOG entry capture for monorepo-worktree-at-governance-root | Shipped |
| 7 | 2026-05-04 | `9f04b59` | executable-close-monorepo-worktree-backlog-2026-05-04 | Close monorepo-worktree BACKLOG entry (hygiene) | Shipped |
| 8 | 2026-05-04 | `eb0e8ad` | executable-backlog-addendum-scope-check-external-vector-2026-05-04 | Broaden scope_check entry with external-vector reproduction | Shipped |
| 9 | 2026-05-05 | `9e9b77c` | diagnostic-worktree-delta-2026-05-05 | Surface map staleness check against 2026-05-03 recommendation | Shipped |
| 10 | 2026-05-05 | `56c26d4` | diagnostic-backlog-1-reproduction-audit-2026-05-05 | BACKLOG #1 close audit — 0 real-`.git` reproductions post-fix | Shipped |

### Diagnostic Plans (read-only investigations)

| # | Date | Plan Filename | Purpose | Status |
|---|------|---------------|---------|--------|
| D1 | 2026-05-03 | diagnostic-worktree-candidate-designs-2026-05-03 | Worktree vs. serialize-capture candidate designs | Shipped |
| D2 | 2026-05-03 | diagnostic-worktree-cost-coverage-recommendation-2026-05-03 | Cost-vs-coverage recommendation (SA, recommended worktree) | Shipped |
| D3 | 2026-05-03 | diagnostic-worktree-implementation-surface-2026-05-03 | Implementation surface + candidate re-evaluation | Shipped |
| D4 | 2026-05-04 | diagnostic-monorepo-worktree-fix-canary-2026-05-04 | Live canary for monorepo worktree fix | Shipped |

### QA Reports (from `knowledge/qa/`)

- `worktree-impl-qa-2026-05-03.md` — worktree implementation QA
- `worktree-tests-qa-2026-05-03.md` — worktree tests QA
- `worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md` — type-mismatch fix QA (6/6 deliverables ✅, 87 targeted tests pass)
- `monorepo-worktree-fix-qa-2026-05-04.md` — detect-and-skip QA (5/5 deliverables ✅, 90/90 targeted + 193/194 full suite)

---

## Investigation Section 3 — Current `_teardown_worktree` Source

### Full Function Body (bellows.py:556–643)

```python
def _teardown_worktree(project_path: str, wt_path: str, slug: str) -> None:
    """Tear down a worktree: cherry-pick commits back, copy dirty files, remove worktree.

    Raises WorktreeTeardownError on cherry-pick conflict (worktree left alive for manual resolution).
    No-op when wt_path == project_path (in-place execution, no worktree was created).
    """
    if wt_path == project_path:
        return

    # (a) Detect main branch
    main_branch = "main"
    try:
        result = subprocess.run(
            ["git", "--no-pager", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            detected = result.stdout.strip()
            if detected.startswith("origin/"):
                detected = detected[len("origin/"):]
            main_branch = detected
        else:
            print(f"Bellows: ⚠ could not detect main branch for {slug}, falling back to 'main'")
    except Exception:
        print(f"Bellows: ⚠ could not detect main branch for {slug}, falling back to 'main'")

    # (b) Collect commits made in worktree
    try:
        result = subprocess.run(
            ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
            cwd=wt_path, capture_output=True, text=True, timeout=30,
        )
        commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
    except Exception:
        commit_shas = []

    # (c) Cherry-pick each commit onto main checkout
    for sha in commit_shas:
        if not sha.strip():
            continue
        result = subprocess.run(
            ["git", "--no-pager", "cherry-pick", sha],
            cwd=project_path, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "--no-pager", "cherry-pick", "--abort"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
            raise WorktreeTeardownError(
                f"cherry-pick conflict on {sha} for slug {slug}: {result.stderr.strip()}"
            )

    # (d) Copy uncommitted dirty files back
    try:
        result = subprocess.run(
            ["git", "--no-pager", "status", "--porcelain"],
            cwd=wt_path, capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if len(line) < 3:
                continue
            status_code = line[:2]
            filename = line[3:].strip()
            if " -> " in filename:
                filename = filename.split(" -> ", 1)[1]
            if status_code.strip() == "D":
                continue
            src = os.path.join(wt_path, filename)
            dst = os.path.join(project_path, filename)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
    except Exception as e:
        print(f"Bellows: ⚠ dirty file copy-back failed for {slug}: {e}")

    # (e) Remove the worktree
    try:
        result = subprocess.run(
            ["git", "--no-pager", "worktree", "remove", wt_path, "--force"],
            cwd=project_path, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"Bellows: ⚠ worktree removal failed for {slug}: {result.stderr.strip()} — next startup prune will clean it")
    except Exception as e:
        print(f"Bellows: ⚠ worktree removal failed for {slug}: {e} — next startup prune will clean it")
```

### Subscript Inventory

| Line | Expression | Type of `x` | Source | Dict subscript? |
|------|-----------|-------------|--------|----------------|
| 573 | `result.stdout.strip()` | str | subprocess output | No — string method |
| 574 | `detected.startswith("origin/")` | str | result.stdout | No — string method |
| 575 | `detected[len("origin/"):]` | str | result.stdout | No — integer slice |
| 588 | `result.stdout.strip().splitlines()[::-1]` | list | subprocess output | No — list slice |
| 594 | `sha.strip()` | str | list element | No — string method |
| 618 | `line[:2]` | str | result.stdout line | No — integer slice |
| 619 | `line[3:].strip()` | str | result.stdout line | No — integer slice |
| 624 | `status_code.strip()` | str | line[:2] | No — string method |

**No dict-subscript operations (`x['key']`) exist inside `_teardown_worktree`.** The function only performs string methods and integer slicing on subprocess output. The TypeError was never inside this function.

---

## Investigation Section 4 — Call Path Inward

### Callers and Arguments

| # | Location | Arguments Passed | Context |
|---|----------|-----------------|---------|
| 1 | `bellows.py:337` | `_teardown_worktree(project_path, wt_path, plan_slug)` | Mid-step pause (gate failure / QA / verdict-request / header-pause) |
| 2 | `bellows.py:402` | `_teardown_worktree(project_path, wt_path, plan_slug)` | Final-step pause |
| 3 | `bellows.py:428` | `_teardown_worktree(project_path, wt_path, plan_slug)` | Auto-close |

### Argument Origins

- **`project_path`**: `str` — from config.json `watched_projects` array, resolved in `run_plan()` parameter. Always a directory path string.
- **`wt_path`**: `str` — return value of `_create_worktree(project_path, plan_slug)` at line 282. Either `project_path` (no `.git` → in-place) or `<project_path>/.bellows-worktrees/<slug>` (worktree created). Always a string.
- **`plan_slug`**: `str` — derived from plan filename. Always a string.

### Data Flow for Original TypeError (Pre-Fix)

1. `_teardown_worktree` raises `WorktreeTeardownError` (cherry-pick conflict at line 605–607)
2. **Caller catches** at `except WorktreeTeardownError as e:`
3. **Pre-fix (before `272fbe4`)**: caller appended `f"worktree_teardown_failed: {e}"` (a plain **string**) to `gate_result["failures"]`
4. Caller then calls `verdict.post_verdict_request(..., pause_reason="gate_failure", ...)`
5. `verdict.py:102` iterates: `for f in gate_result["failures"]: f"- **{f['gate']}**: {f['evidence']}\n"`
6. When `f` is string `"worktree_teardown_failed: ..."`, `f['gate']` raises `TypeError: string indices must be integers`
7. TypeError propagates uncaught, bypasses ALL cleanup (no verdict-pending rename, no worktree removal)

### Current State (Post-Fix)

All 3 teardown callers and 1 creation caller now append dicts:
```python
# Lines 340, 405, 433 (teardown):
gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
# Line 286 (creation):
gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], ...}
```

---

## Investigation Section 5 — Call Path Outward

### Subprocess Invocations from `_teardown_worktree`

| # | Line | Command | Purpose | Return Type |
|---|------|---------|---------|-------------|
| 1 | 568–570 | `git symbolic-ref --short refs/remotes/origin/HEAD` | Detect main branch | subprocess.CompletedProcess (stdout: string) |
| 2 | 584–586 | `git log --format=%H HEAD --not <main_branch>` | Collect commit SHAs | subprocess.CompletedProcess (stdout: string) |
| 3 | 596–598 | `git cherry-pick <sha>` | Cherry-pick commit | subprocess.CompletedProcess (returncode checked) |
| 4 | 601–603 | `git cherry-pick --abort` | Abort on conflict | subprocess.CompletedProcess (fire-and-forget) |
| 5 | 611–613 | `git status --porcelain` | List dirty files | subprocess.CompletedProcess (stdout: string) |
| 6 | 636–638 | `git worktree remove <wt_path> --force` | Remove worktree | subprocess.CompletedProcess (returncode checked) |

### Parsing Logic

- `result.stdout.strip()` → string processing (no JSON parsing)
- `result.stdout.strip().splitlines()[::-1]` → list of SHA strings
- `line[:2]` / `line[3:]` → porcelain status code / filename extraction

**No downstream function returns a dict where a string could be confused.** All subprocess calls return string output processed via string methods. No JSON parsing occurs in this function.

---

## Investigation Section 6 — Log Evidence

### Search Method

```
grep -l "string indices" bellows/logs/*.json 2>/dev/null | sort | tail -50
```

### Results: 20 log files match (2026-05-03 through 2026-05-05)

| Log Filename | Timestamp | Location of Match | Bellows Runtime Error? |
|---|---|---|---|
| 20260503-133850-step.json | 2026-05-03 13:38:50 | `raw_output` (agent transcript) | **NO** — agent discussing bug during worktree-impl step |
| 20260504-083237-step.json | 2026-05-04 08:32:37 | `raw_output` | **NO** — agent transcript |
| 20260504-083549-step.json | 2026-05-04 08:35:49 | `raw_output` | **NO** |
| 20260504-134310-step.json | 2026-05-04 13:43:10 | `raw_output` | **NO** |
| 20260504-161323-step.json | 2026-05-04 16:13:23 | `raw_output` | **NO** |
| 20260504-162702-step.json | 2026-05-04 16:27:02 | `raw_output` | **NO** |
| 20260504-171141-step.json | 2026-05-04 17:11:41 | `raw_output` | **NO** |
| 20260504-171334-step.json | 2026-05-04 17:13:34 | `raw_output` | **NO** |
| 20260504-175513-step.json | 2026-05-04 17:55:13 | `raw_output` | **NO** |
| 20260505-082614-step.json | 2026-05-05 08:26:14 | `raw_output` | **NO** |
| ... (10 more, all same pattern) | ... | `raw_output` | **NO** |

**Critical finding:** All 20 matches are inside the `raw_output` field (agent conversation transcripts where agents discuss/investigate/reference the error). Systematic scan of ALL log files for TypeError in `stderr` field: **zero matches**. Scan for `is_error=True` in `parsed` field: **zero worktree-related matches** (failures found are all unrelated inactivity timeouts from April 2026).

**The original crash was observed on Bellows terminal console output**, not captured in step JSON logs. The diagnosis at `worktree-teardown-bug-diagnosis-2026-05-03.md` reconstructed the crash sequence from console output patterns, not from log files.

### Latest Occurrence

**No Bellows runtime occurrence of `string indices must be integers` exists in step logs.** The original crash was diagnosed and fixed on 2026-05-03 (same day). No evidence of recurrence.

---

## Investigation Section 7 — Timeline Cross-Reference

| Event | Date | Relationship |
|---|---|---|
| Original crash observed | 2026-05-03 (during close of `executable-close-2026-05-03-step-count-regression-2026-05-03`) | — |
| Bug diagnosis | 2026-05-03 (`worktree-teardown-bug-diagnosis-2026-05-03.md`) | Same day |
| Type-contract fix | 2026-05-03 (commit `272fbe4`) | Same day — fix shipped hours after crash |
| Worktree implementation | 2026-05-03 (commit `36b2bba`) | Same day — full worktree code shipped |
| Detect-and-skip fix | 2026-05-04 (commit `06aa938`) | Next day — bellows-self monorepo trap handled |
| BACKLOG OP-001 closed | 2026-05-03 (BACKLOG "Closed 2026-05-03: worktree teardown crash") | — |
| Monorepo-worktree BACKLOG closed | 2026-05-04 | — |
| Latest "string indices" in logs | All are agent transcripts, not runtime errors | Bug is **NOT live** |
| Zero real-`.git` scope_check reproductions post-fix | 2026-05-05 (BACKLOG #1 audit) | Worktree isolation confirmed working for real-`.git` projects |

**The latest (and only) runtime occurrence of the TypeError predates the worktree fix. The bug is resolved.**

---

## Findings — Five Answered Questions

### Question A: Is Bellows's `.git` state correct?

**NO — Bellows still resolves to governance-root `/Users/marklehn/Desktop/GitHub`.** Bellows has no project-local `.git`. However, this is now an **accepted and handled** condition:
- `_create_worktree` (line 528) detects the missing `.git` and returns `project_path` as-is
- `_teardown_worktree` (line 562) short-circuits when `wt_path == project_path`
- Bellows-self plans run in-place without isolation
- This tradeoff was explicitly accepted at the 2026-05-04 close (documented in BACKLOG Closed section)
- The remaining exposure (concurrent activity tripping scope_check on bellows-self plans) is tracked as the 2026-05-05 Open BACKLOG entry

### Question B: What worktree work shipped May 3–5?

Ten plans shipped across three critical code changes:
1. **Type-contract fix** (`272fbe4`, 2026-05-03): 4 sites in bellows.py changed from `f"worktree_teardown_failed: {e}"` to `{"gate": "worktree_teardown", "evidence": str(e)}`. Prevents the `verdict.py:102` TypeError for ALL projects.
2. **Full worktree implementation** (`36b2bba`, 2026-05-03): `_create_worktree`, `_teardown_worktree`, cherry-pick merge-back, dirty file copy-back, startup prune. Provides per-plan isolation for all projects with their own `.git`.
3. **Detect-and-skip** (`06aa938`, 2026-05-04): `_create_worktree` returns `project_path` when no `.git` exists. Prevents bellows-self plans from creating governance-root worktrees.

The `_teardown_worktree` function was **created** by the worktree implementation (not modified from a broken prior version). The type-contract fix addressed the **caller's error-handling code**, not `_teardown_worktree` itself.

### Question C: Where exactly is the TypeError thrown?

- **File:** `verdict.py`, line 102 (at time of diagnosis)
- **Function:** `post_verdict_request`
- **Expression:** `f['gate']` inside `for f in gate_result["failures"]:`
- **Data flow:** `bellows.py` caller catches `WorktreeTeardownError` → appends to `gate_result["failures"]` → calls `post_verdict_request` → verdict.py iterates failures expecting dicts → string subscript with string key raises TypeError
- **Current state (post-fix):** All 4 sites now append dicts matching the `verdict.py` contract. Regression test `test_post_verdict_request_handles_worktree_teardown_failure_dict_format` locks this.

### Question D: Most recent occurrence?

**No Bellows runtime `string indices must be integers` TypeError exists in step logs.** All 20 log matches are inside agent conversation transcripts (agents discussing/investigating the bug). The original crash was observed on terminal console output on 2026-05-03, diagnosed the same day, and fixed the same day (commit `272fbe4`). The BACKLOG #1 population audit (2026-05-05) confirmed zero real-`.git` project scope_check failures post-fix. **The bug is RESOLVED.**

### Question E: Recommended next step

**Bug is resolved — only memory/knowledge needs updating.**

- OP-001 was already closed in BACKLOG on 2026-05-03 ("Closed 2026-05-03: worktree teardown crash")
- The monorepo-worktree follow-up was closed on 2026-05-04
- The BACKLOG #1 scope_check-collision entry was closed on 2026-05-05 after population audit
- The remaining bellows-self exposure is tracked as a known constraint (2026-05-05 Open BACKLOG entry)
- CEO memory noting "unsure of the current overall state" can be updated: **both original OP-001 issues (TypeError + governance-root worktree) are fully addressed**
- No fix is needed. No additional reproduction is needed. Static analysis is conclusive.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the current state of Bellows worktree teardown (OP-001 recheck). Confirmed `.git` state (still governance-root, but now handled by detect-and-skip). Reconstructed 10-plan worktree timeline (May 3–5). Traced `_teardown_worktree` source (no dict subscripts — TypeError was in caller's error-handling path at `verdict.py:102`). Mapped call paths inward and outward. Scanned all logs for runtime errors (zero found — all matches are agent transcripts). Cross-referenced timeline (fix shipped same day as crash, no recurrence). Answered five diagnostic questions: bug is resolved, only CEO memory needs updating.

### Files Deposited
- `bellows/knowledge/research/worktree-teardown-current-state-findings-2026-05-05.md` — this findings file

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified all 20 log file matches as agent-transcript references (not Bellows runtime errors) based on systematic field-level analysis — `raw_output` contains agent conversations, not Bellows error telemetry
- Determined no reproduction plan is needed — static analysis plus log evidence is conclusive

### Flags for CEO
- CEO memory can be updated: OP-001 is fully resolved. Both the TypeError (commit `272fbe4`) and the governance-root worktree trap (commit `06aa938`) are addressed. The remaining accepted constraint (bellows-self in-place execution without isolation) is tracked as the 2026-05-05 Open BACKLOG entry.

### Flags for Next Step
- None — this is a terminal diagnostic. No code changes needed.
