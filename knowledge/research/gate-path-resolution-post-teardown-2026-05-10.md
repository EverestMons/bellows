# Gate Path-Resolution Post-Teardown — Findings

**Date:** 2026-05-10 | **Type:** Diagnostic findings | **Plan:** diagnostic-gate-path-resolution-post-teardown-2026-05-10

---

## Q1 — Current implementation of gate path-resolution functions

### (a) `_resolve_deposit_path` (gates.py:166–195)

Four resolution strategies, tried in order:

```python
def _resolve_deposit_path(path, project_path, wt_path=None):
    # Strategy 0 (worktree-first): if wt_path provided AND differs from project_path
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
    # Strategy 2: os.path.join(project_path, path)
    p2 = os.path.join(project_path, path)
    if os.path.isfile(p2) or os.path.isdir(p2):
        return os.path.abspath(p2)
    # Strategy 3: os.path.join(os.path.dirname(project_path), path)
    p3 = os.path.join(os.path.dirname(project_path), path)
    if os.path.isfile(p3) or os.path.isdir(p3):
        return os.path.abspath(p3)
    return None
```

Strategy 0 was added by the 2026-05-06 worktree-aware fix. It strips the project basename prefix if present, then checks the worktree path. Strategies 1–3 are the original resolution chain.

### (b) `_gate_deposit_exists` (gates.py:198–223)

```python
def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None, wt_path=None):
    # ...
    if path:
        agent_declared.add(path)
        if _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:  # LINE 214
            failures.append(...)
    # ...
    for path in _extract_plan_required_deposits(step_text):
        if path not in agent_declared and _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:  # LINE 222
            failures.append(...)
```

**Passes `wt_path` at both call sites (lines 214, 222).** This was the 2026-05-06 fix.

### (c) `_gate_rule_20_self_check` (gates.py:273–320)

```python
def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures):
    # ...
    for dep_path in md_paths:
        resolved = _resolve_deposit_path(dep_path, project_path)  # LINE 292 — NO wt_path!
        if resolved is None:
            failures.append({"gate": "rule_20_self_check",
                             "evidence": f"deposit file unreadable: {dep_path} (file not found)"})
            continue
        # ... reads file content, checks for banner ...
```

**Does NOT accept `wt_path` as a parameter.** The function signature at line 273 has no `wt_path` argument. The call to `_resolve_deposit_path` at line 292 passes only `(dep_path, project_path)` — Strategy 0 (worktree-first) is never attempted.

The caller at gates.py:105 also does not pass `wt_path`:
```python
_gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures)
```

Compare to the `_gate_deposit_exists` call at line 101, which does:
```python
_gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number, wt_path=wt_path)
```

**This is the primary root cause for `rule_20_self_check` false positives.** The 2026-05-06 fix updated `_gate_deposit_exists` but missed `_gate_rule_20_self_check`.

---

## Q2 — Call sequence around step completion

Actual chronological order for the first step execution (bellows.py lines 298–377):

| Order | Operation | Line(s) | Code |
|-------|-----------|---------|------|
| 1 | Pre-step diff capture | 298 | `pre_diff = _capture_git_diff(wt_path)` |
| 2 | Agent process runs and exits | 300–302 | `parsed = runner.run_step(bootstrap_prompt, wt_path, model, ...)` |
| 3 | Mode A detection check | 317–328 | `if not os.path.exists(inprogress_path): ...` |
| 4 | Post-step diff capture | 331 | `post_diff = _capture_git_diff(wt_path)` |
| 5 | File change parsing | 332 | `files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)` |
| 6 | **gates.check() invocation** | 333 | `gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)` |
| 7 | Pause condition evaluation | 347–350 | `if (not gate_result["passed"] or gate_result["is_qa_step"] or ...)` |
| 8 | **_teardown_worktree** (cherry-pick + remove) | 362 | `_teardown_worktree(project_path, wt_path, plan_slug)` |
| 9 | Verdict request file written | 366 | `verdict.post_verdict_request(...)` |
| 10 | Plan renamed to verdict-pending | 371–373 | `shutil.move(inprogress_path, verdict_pending_path)` |

The same ordering applies in the final-step pause path (lines 430–462): gates.check() was already run (either line 333 or 418), then teardown at line 448, then verdict at line 452.

**Critical finding: gates.check() (step 6) runs BEFORE _teardown_worktree (step 8). The BACKLOG's "post-teardown" hypothesis is incorrect.**

---

## Q3 — Has _teardown_worktree already executed when gates.check() runs?

**NO. gates.check() runs BEFORE _teardown_worktree in all code paths.**

The code structure makes this unambiguous. In the first-step path:

```python
# Line 333 — gate check, worktree still alive
gate_result = gates.check(parsed, plan_text, current_step, project_path,
                          files_changed=files_changed, wt_path=wt_path)
# ...
# Lines 347-377 — pause block entered conditionally
if (not gate_result["passed"] or ...):
    # Line 362 — teardown happens INSIDE the pause block, AFTER gate check
    _teardown_worktree(project_path, wt_path, plan_slug)
    # Line 366 — verdict written AFTER teardown
    verdict.post_verdict_request(...)
```

When gates.check() runs:
- `wt_path` points to a **valid, existing directory** containing the agent's committed files
- The agent's commits are **still only on the worktree branch** — they have NOT been cherry-picked to main
- Files deposited by the agent exist at `wt_path/...` but do NOT exist at `project_path/...`

This means:
- `_gate_deposit_exists` (which passes `wt_path`) can find files via Strategy 0 — **correctly**
- `_gate_rule_20_self_check` (which does NOT pass `wt_path`) can only try Strategies 1–3, all of which look at the main project tree where files don't exist yet — **incorrectly fails**

---

## Q4 — Analysis of cited verdict-request files

### verdict-request-action-queue-aggregation-2026-05-07-step-3.md (8 failures)

**6 deposit_exists failures** — paths: `evidence/orphan_handling.txt`, `evidence/index_verification.txt`, `evidence/contract_detail_atoms.txt`, `evidence/pytest_full.txt`, `evidence/pytest_targeted.txt`, `evidence/aggregated_queue_correctness.txt`

(a) These are short relative paths extracted by the legacy prose regex in `_extract_plan_required_deposits` (Pattern 1: `Deposit[^\n`]*?to\s+`([^`]+)``). The plan step 3 text contains instructions like "deposit the test sequence to `evidence/orphan_handling.txt`" — the regex captures the backtick-quoted path verbatim.

(b) The files **do exist on main** but at deeper paths: `knowledge/qa/evidence/action-queue-aggregation/orphan_handling.txt` (verified via `find`). The short `evidence/foo.txt` paths don't match the actual directory structure.

(c) Resolution trace for `evidence/orphan_handling.txt` with `wt_path` passed:
- Strategy 0: `wt_path/evidence/orphan_handling.txt` → NOT FOUND (actual location: `wt_path/knowledge/qa/evidence/action-queue-aggregation/orphan_handling.txt`)
- Strategy 1: CWD-relative `evidence/orphan_handling.txt` → NOT FOUND
- Strategy 2: `project_path/evidence/orphan_handling.txt` → NOT FOUND
- Strategy 3: `dirname(project_path)/evidence/orphan_handling.txt` → NOT FOUND

**These paths can NEVER resolve under any strategy because they are contextual abbreviations in the plan prose, not actual file paths.** This is a false positive from the legacy regex, not a timing issue. The plan also uses full paths elsewhere (e.g., `invoice-pulse/knowledge/qa/evidence/action-queue-aggregation/bulk_pct_comparison.txt`) — those DO resolve via Strategy 3.

**2 rule_20_self_check failures** — paths: `invoice-pulse/knowledge/qa/qa-action-queue-aggregation-2026-05-07.md`, `invoice-pulse/knowledge/qa/qa-action-queue-aggregation-deliverable-verification-2026-05-07.md`

(a) These are project-prefixed paths. `_gate_rule_20_self_check` calls `_resolve_deposit_path(dep_path, project_path)` WITHOUT `wt_path`. Strategy 3 would resolve `invoice-pulse/knowledge/qa/...` via `os.path.join(dirname(project_path), path)` — but ONLY if the file exists on disk at `project_path/knowledge/qa/...`. At gate evaluation time, the files exist in the worktree (agent committed there) but NOT in main (cherry-pick hasn't happened). Without Strategy 0 (worktree-first), the gate can't find them.

(b) Both files exist on main now (post cherry-pick, post-session).

(c) Strategy 0 is not attempted because `wt_path` is not passed. This is the root cause.

### verdict-request-qa-report-rule-20-banner-fix-2026-05-07-step-2.md (1 failure)

Same mechanism as the 2 rule_20_self_check failures above. The QA report exists in the worktree at gate evaluation time but `_gate_rule_20_self_check` can't find it because it doesn't use `wt_path`.

---

## Q5 — Lifetime of `wt_path` across one step execution

| Phase | Line | State of wt_path |
|-------|------|-------------------|
| Creation | 284 | `wt_path = _create_worktree(project_path, plan_slug)` — fresh worktree, directory exists |
| Pre-diff | 298 | `_capture_git_diff(wt_path)` — directory valid |
| Agent execution | 300 | `runner.run_step(bootstrap_prompt, wt_path, ...)` — agent commits files to worktree |
| Post-diff | 331 | `_capture_git_diff(wt_path)` — directory valid, files on disk |
| **Gate check** | 333 | `gates.check(..., wt_path=wt_path)` — directory valid, files on disk |
| Teardown | 362 | `_teardown_worktree(project_path, wt_path, plan_slug)` — cherry-picks to main, then removes worktree directory |
| Post-teardown | 366+ | `wt_path` variable still holds the old path string, but the directory no longer exists |

**The structural seam is NOT between gate check and teardown** (gates run while worktree is alive). The seam is inside `_gate_rule_20_self_check` at line 292, where `wt_path` is available in the `gates.check()` function scope (received as a parameter at line 74) but is never threaded through to `_gate_rule_20_self_check` (called at line 105 without `wt_path`).

The gap is a simple omission in the 2026-05-06 fix. The fix correctly added `wt_path` to:
- `gates.check()` signature (line 74)
- `_gate_deposit_exists` signature and call sites (lines 101, 198, 214, 222)

But did NOT add `wt_path` to:
- `_gate_rule_20_self_check` signature (line 273) — still no `wt_path` parameter
- `_gate_rule_20_self_check` call site (line 105) — still not passed
- `_resolve_deposit_path` call inside `_gate_rule_20_self_check` (line 292) — no `wt_path` kwarg

---

## Q6 — Fix shape evaluation

### Context correction

The BACKLOG's three candidates were designed around the "post-teardown timing" hypothesis. Since the actual root cause is different (missing `wt_path` threading, not timing), the candidates need reframing.

### Candidate 4 (NEW, RECOMMENDED): Thread `wt_path` into `_gate_rule_20_self_check`

**Description:** Add `wt_path=None` to `_gate_rule_20_self_check` signature. Pass it from the `gates.check()` call at line 105. Pass it to `_resolve_deposit_path` at line 292. This is the direct fix for Root Cause 1.

| Dimension | Value |
|-----------|-------|
| Estimated LOC | ~5 (1 signature change, 1 call-site update, 1 `_resolve_deposit_path` kwarg) |
| Risk level | Very low — mirrors the existing pattern in `_gate_deposit_exists` |
| Preserves 2026-05-06 fix | Yes — additive, no change to existing Strategy 0 logic |
| Resolves rule_20_self_check | **Yes** — the primary false-positive class |
| Resolves deposit_exists | No — the deposit_exists false positives have a different root cause (see below) |

### Candidate 5 (NEW): Fix legacy prose regex false positives

**Description:** The 6 deposit_exists failures stem from the legacy prose regex in `_extract_plan_required_deposits` (gates.py:258) capturing short relative paths like `evidence/orphan_handling.txt` that are contextual abbreviations, not resolvable file paths. Two sub-options:

**(5a)** Add a **Deposits:** block to Step 3 of the plan template pattern (Planner-side fix). When the block is present, `_extract_plan_required_deposits` skips legacy regexes entirely (line 246–253). This is a governance fix, not a code fix.

**(5b)** Add a minimum path-depth filter to the legacy regex: skip captured paths with fewer than 2 directory separators (e.g., `evidence/foo.txt` has only 1 separator — too ambiguous). Paths like `invoice-pulse/knowledge/qa/evidence/foo.txt` (3+ separators) pass through.

| Dimension | 5a | 5b |
|-----------|----|----|
| Estimated LOC | 0 (governance) | ~3 |
| Risk level | None | Low — only affects legacy fallback, block-form unaffected |
| Resolves deposit_exists | Yes (plans with Deposits: block) | Yes (short paths filtered) |

### Original candidates from BACKLOG (re-evaluated)

**(1) Move gate evaluation BEFORE _teardown_worktree:** Already the case. No change needed. The BACKLOG hypothesis was wrong.

**(2) After teardown, re-resolve all deposit paths via Strategy 1:** Not needed. Gates already run pre-teardown. The files are in the worktree. The fix is to USE the worktree path that's already available.

**(3) Gate check at TWO points:** Unnecessary complexity. Single pre-teardown check with correct `wt_path` threading is sufficient.

### Recommended fix

**Candidate 4** as the primary fix (thread `wt_path` into `_gate_rule_20_self_check`). ~5 LOC, very low risk, directly addresses the highest-friction false-positive class (rule_20_self_check on every QA step).

**Candidate 5a** as the secondary fix (Planner ensures all plan steps use explicit **Deposits:** blocks per Rule 26, eliminating legacy regex false positives). Zero code change, governance-only.

---

## Q7 — Cross-reference with cherry-pick fragility BACKLOG entry

The `2026-05-07: _teardown_worktree cherry-pick fragility` entry describes two failure modes:
1. Stale `.git/index.lock` causing cherry-pick timeout
2. Single-SHA cherry-pick missing the QA commit (only brings the first commit)

**Would a failed cherry-pick present the same gate failure pattern?**

No — because gates.check() runs BEFORE _teardown_worktree. Cherry-pick failures cannot affect gate evaluation because cherry-pick hasn't happened yet at gate evaluation time. The gate evaluates files in the worktree, not in main.

However, if the cherry-pick fails (Failure 1 or 2), the gate failures would be:
- `worktree_teardown` gate failure (added at bellows.py:365 when `WorktreeTeardownError` is caught)
- NOT `deposit_exists` or `rule_20_self_check`

**How to distinguish the two failure modes from a verdict-request file:**
- **Cherry-pick fragility:** verdict request contains `worktree_teardown` gate failure with cherry-pick error message
- **Path-resolution gap (this diagnostic):** verdict request contains `deposit_exists` and/or `rule_20_self_check` failures with "file not found" or "missing" evidence, and NO `worktree_teardown` failure

The 2026-05-07 verdict-request files have NO `worktree_teardown` failures — they are purely path-resolution false positives, confirming these are the bug investigated here, not cherry-pick fragility.

---

## Root Cause

**Two distinct root causes produce the 8+1 false positives observed in the reproductions:**

### Root Cause 1 — `_gate_rule_20_self_check` missing `wt_path` (HIGH confidence)

`_gate_rule_20_self_check` (gates.py:273) does not accept or pass `wt_path` to `_resolve_deposit_path` (line 292). The 2026-05-06 worktree-aware fix (executable-deposit-exists-worktree-aware-2026-05-06) updated `_gate_deposit_exists` but missed `_gate_rule_20_self_check`. Since gates.check() runs BEFORE _teardown_worktree, the worktree directory exists and contains the agent's committed files — but `_gate_rule_20_self_check` can't find them because it only tries Strategies 1–3 (all of which look at the main project tree where cherry-pick hasn't landed the files yet).

**Affected failures:** All `rule_20_self_check` failures in the reproductions (2 in action-queue-aggregation step 3, 1 in qa-report-rule-20-banner-fix step 2, plus re-affirmations on 2026-05-08).

### Root Cause 2 — Legacy prose regex captures unresolvable short paths (MEDIUM confidence)

`_extract_plan_required_deposits` (gates.py:237) falls back to legacy prose-matching regexes (lines 258–269) when no **Deposits:** block is present in the step text. These regexes capture short relative paths like `evidence/orphan_handling.txt` from plan prose instructions. The short paths are contextual abbreviations — the actual files live at deeper paths like `knowledge/qa/evidence/action-queue-aggregation/orphan_handling.txt`. No resolution strategy (including Strategy 0 with wt_path) can map the short path to the actual location.

**Affected failures:** The 6 `deposit_exists` failures in action-queue-aggregation step 3.

### Key finding contradicting BACKLOG hypothesis

The BACKLOG entry (2026-05-07) hypothesizes a post-teardown timing issue: "files exist in project_path (post-cherry-pick) and the gate may be looking at a worktree that no longer exists." **This hypothesis is incorrect.** The code shows gates.check() runs BEFORE _teardown_worktree (bellows.py:333 vs 362). The worktree exists and is valid at gate evaluation time. The actual bugs are: (a) one gate function doesn't use the worktree path at all, and (b) the legacy deposit-path regex captures paths that can't be resolved under any strategy.

---

## Recommended Fix

**Primary (Root Cause 1):** Thread `wt_path` through `_gate_rule_20_self_check`. ~5 LOC:

1. Add `wt_path=None` to `_gate_rule_20_self_check` signature (line 273)
2. Update `gates.check()` call at line 105 to pass `wt_path=wt_path`
3. Update `_resolve_deposit_path` call at line 292 to pass `wt_path=wt_path`

This directly mirrors the 2026-05-06 fix pattern already applied to `_gate_deposit_exists`.

**Secondary (Root Cause 2):** Ensure all plan steps include explicit **Deposits:** blocks per Rule 26 convention. When the block is present, `_extract_plan_required_deposits` returns only block-declared paths (line 246–253) and skips the legacy prose regexes entirely. This is a Planner-side governance fix requiring zero code changes.

---

## Confidence

**Root Cause 1 — HIGH.** The missing `wt_path` parameter on `_gate_rule_20_self_check` is visible in the source code. The call chain is unambiguous: `gates.check()` receives `wt_path`, passes it to `_gate_deposit_exists` (line 101), but does NOT pass it to `_gate_rule_20_self_check` (line 105). The timing analysis (gates before teardown) is confirmed by the linear code structure in bellows.py.

**Root Cause 2 — MEDIUM.** The legacy regex path-capture mechanism is confirmed in code. The actual evidence file locations were verified via `find`. The gap between captured short paths and actual locations is structural. Confidence is medium (not high) because I did not have access to the exact plan text at the moment of the 2026-05-07 dispatch — I read the Done/ copy, which may differ from what Bellows saw if the plan was modified between dispatch and close. However, the Done/ copy's step 3 text contains the exact `evidence/foo.txt` patterns matching the verdict-request failure paths, making this explanation highly likely.

**Evidence that would raise confidence:** Running the fix (Candidate 4) and confirming zero `rule_20_self_check` false positives on the next QA step dispatch for a worktree-isolated project.

---

## Rule 20 — QA Self-Check Results

```python
import os
deposit = "bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md"
abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), deposit) if '__file__' in dir() else os.path.abspath(deposit)
# Direct check from bellows project root
check_path = os.path.join("/Users/marklehn/Desktop/GitHub/bellows", "knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md")
if os.path.isfile(check_path):
    print("PASSED — SELF-CHECK PASSED")
else:
    print(f"SELF-CHECK FAILED — file not found at {check_path}")
```
