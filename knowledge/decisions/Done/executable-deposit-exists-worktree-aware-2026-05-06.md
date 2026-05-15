# executable — deposit_exists Worktree-Aware Path Resolution Fix

**Date:** 2026-05-06
**Tier:** Unit (Python module changes with corresponding test files)
**Test Scope:** unit — gates.py + bellows.py edits with matching test additions
**auto_close:** false (multi-step plan with QA checkpoint)

## Execution Map

Step 1 (Bellows Developer — DEV) → Step 2 (Bellows QA) → Done

Sequential. Step 2 cannot start until Step 1 completes; Step 1 produces the code changes Step 2 verifies.

---

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan and executes Step 1 ONLY. After Step 1 completes, Bellows pauses for CEO verdict before dispatching Step 2.

**Bootstrap (Step 1):**

```
Read the plan at bellows/knowledge/decisions/executable-deposit-exists-worktree-aware-2026-05-06.md and execute Step 1 ONLY. After completing Step 1, STOP and wait for verdict.
```

**Bootstrap (Step 2 — only after CEO verdict authorizes):**

```
Read the plan at bellows/knowledge/decisions/verdict-pending-executable-deposit-exists-worktree-aware-2026-05-06.md and execute Step 2.
```

---

## Context

**Diagnostic findings:** `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md` (2026-05-06, Bellows Systems Analyst).

**Root cause:** `gates.check()` evaluates `deposit_exists` against `project_path` while agent deposits exist only in `wt_path` (worktree). Worktree teardown runs AFTER gate evaluation, so newly-created deposits in worktree-isolated plans always fail the gate. Structural gap introduced by commit `36b2bba` (2026-05-03 worktree isolation); not intermittent.

**Reproductions:** 5 in one session (2026-05-06) on invoice-pulse plans, plus the 3 originally documented in BACKLOG #1 (2026-05-06). Total 8.

**Fix shape (from diagnostic Task 6):** thread `wt_path` through to `_gate_deposit_exists` → `_resolve_deposit_path`; add a worktree-first resolution strategy. ~10 LOC across `gates.py` and `bellows.py`.

**Backward compatibility:** bellows-self plans skip worktree creation per the 2026-05-04 detect-and-skip close (`wt_path == project_path` in that case). The fix uses an explicit guard `if wt_path != project_path` to avoid double-checking the same path.

**Strategy ordering decision (CEO-locked):** worktree-first. The gate's semantic intent is "find the freshly-deposited file"; the worktree IS where the agent just wrote it. Existing strategies remain as fallbacks for paths not in the worktree (e.g., paths to files that pre-existed and the agent didn't touch).

---

## Step 1 — Code Implementation (Bellows Developer — DEV)

**Agent:** Bellows Developer
**Specialist file:** `bellows/agents/BELLOWS_DEVELOPER.md`

**Goal:** Thread `wt_path` through the gate evaluation path so `_resolve_deposit_path` can find newly-created deposits in the worktree. Maintain backward compatibility with bellows-self plans where `wt_path == project_path`.

**Read first (in order):**

1. `bellows/agents/BELLOWS_DEVELOPER.md`
2. `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md` — root cause diagnostic, fix shape from Task 6
3. `bellows/gates.py` — full file, especially `gates.check()`, `_gate_deposit_exists`, `_resolve_deposit_path`
4. `bellows/bellows.py` — the two `gates.check()` call sites the diagnostic identified at lines 331 and 416 (verify line numbers; structure may have shifted since the diagnostic was written)
5. `bellows/tests/test_gates.py` — existing test patterns for `_resolve_deposit_path` and `_gate_deposit_exists` (use these as templates for the new tests)

### Implementation tasks

**Task 1.1 — Update `_resolve_deposit_path` signature and add worktree-first strategy**

In `bellows/gates.py`, modify `_resolve_deposit_path` to accept an optional `wt_path` parameter:

```python
def _resolve_deposit_path(path: str, project_path: str, wt_path: str | None = None) -> str | None:
    # Strategy 0 (worktree-first, NEW): if wt_path is provided AND differs from project_path,
    # try resolving against the worktree first — this is where the agent just wrote files
    if wt_path is not None and wt_path != project_path:
        # Form A (governance-root-relative path like "invoice-pulse/knowledge/...")
        # The wt_path is "<project_path>/.bellows-worktrees/<slug>", so we strip the project basename
        # from a leading prefix-form path before joining to wt_path.
        # Form B (project-relative path like "knowledge/...") joins directly.
        project_basename = os.path.basename(project_path)
        if path.startswith(project_basename + os.sep):
            wt_candidate = os.path.join(wt_path, path[len(project_basename) + 1:])
        else:
            wt_candidate = os.path.join(wt_path, path)
        if os.path.isfile(wt_candidate) or os.path.isdir(wt_candidate):
            return wt_candidate

    # Existing strategies (S1, S2, S3) follow unchanged
    # ... (preserve current code below this block)
```

Read the existing function body BEFORE editing — do not rewrite the existing strategies; insert the new Strategy 0 block at the top and preserve the existing logic below it.

**Task 1.2 — Thread `wt_path` through `_gate_deposit_exists`**

In `gates.py`, update `_gate_deposit_exists` to accept and forward `wt_path`:

```python
def _gate_deposit_exists(parsed, plan_text, current_step, project_path, wt_path=None, ...):
    # ... existing logic ...
    resolved = _resolve_deposit_path(path, project_path, wt_path=wt_path)
    # ... rest unchanged
```

Update every call to `_resolve_deposit_path` inside `_gate_deposit_exists` to pass `wt_path=wt_path`.

**Task 1.3 — Thread `wt_path` through `gates.check()`**

In `gates.py`, update `check()` signature:

```python
def check(parsed, plan_text, current_step, project_path, wt_path=None, ...):
    # ...
    _gate_deposit_exists(parsed, plan_text, current_step, project_path, wt_path=wt_path, failures=failures, ...)
    # ...
```

Preserve the existing parameter ordering for backward compatibility — `wt_path` is added as a new keyword argument with default `None`. Other gates (`scope_check`, `rule_20_self_check`, etc.) do NOT receive `wt_path` in this fix; they keep their current signatures.

**Task 1.4 — Update `gates.check()` call sites in `bellows.py`**

The diagnostic identified two call sites at `bellows.py:331` and `bellows.py:416`. Verify these line numbers (they may have shifted) by grepping for `gates.check(`. At each call site, add `wt_path=wt_path` to the call:

```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, wt_path=wt_path, ...)
```

`wt_path` is already in scope at both call sites (created at line ~282 by `_create_worktree`).

**Task 1.5 — Verify no regression on bellows-self plans**

For bellows-self plans, `_create_worktree` returns `project_path` unchanged (per 2026-05-04 detect-and-skip close). In that case `wt_path == project_path`, and the Strategy 0 guard `if wt_path is not None and wt_path != project_path` evaluates False, so the new code path is skipped entirely. Existing strategies (S1/S2/S3) handle bellows-self plans as before. No additional code needed for compatibility.

### What NOT to do

- Do not modify `scope_check`, `rule_20_self_check`, or any other gate function — the diagnostic ruled them out.
- Do not modify `_teardown_worktree` ordering — leaving teardown after gate evaluation is correct because gate failures should be visible BEFORE worktree state is committed back to project_path.
- Do not change the existing resolution strategies (S1/S2/S3) — only ADD Strategy 0 ahead of them.
- Do not modify `verdict.py`, `parser.py`, `runner.py`, or any other Bellows module.

### Output

**Dev log:** `bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md`

The dev log MUST include:
- Tests-before / Tests-after counts (run full bellows test suite: `cd bellows && python3 -m pytest tests/ -v`)
- Diff summary of changes (file-by-file LOC counts)
- Verification that the Strategy 0 guard prevents double-checking on bellows-self plans
- Output Receipt per `bellows/agents/BELLOWS_DEVELOPER.md`

**Deposits:**
- `bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md`
- `bellows/gates.py` (modified)
- `bellows/bellows.py` (modified)

---

## Housekeeping (Step 1 final block — Bellows Developer)

After Step 1 implementation completes, perform housekeeping in this exact order:

**A. Self-check (Rule 20 mandatory):**

```python
import os, sys, subprocess

devlog_path = "bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md"
plan_path = "bellows/knowledge/decisions/in-progress-executable-deposit-exists-worktree-aware-2026-05-06.md"
gates_path = "bellows/gates.py"
bellows_path = "bellows/bellows.py"

problems = []
for p in [devlog_path, plan_path, gates_path, bellows_path]:
    if not os.path.isfile(p):
        problems.append(f"MISSING: {p}")

# Confirm the new wt_path parameter exists in gates.py signatures
with open(gates_path) as f:
    gates_body = f.read()
required_signatures = [
    "def _resolve_deposit_path",
    "def _gate_deposit_exists",
    "def check(",
]
for sig in required_signatures:
    if sig not in gates_body:
        problems.append(f"MISSING signature in gates.py: {sig}")
if "wt_path" not in gates_body:
    problems.append("MISSING wt_path threading in gates.py")

# Confirm both call sites in bellows.py pass wt_path
with open(bellows_path) as f:
    bellows_body = f.read()
gates_check_calls = bellows_body.count("gates.check(")
wt_path_passes = bellows_body.count("wt_path=wt_path")
if gates_check_calls < 2:
    problems.append(f"FEWER THAN 2 gates.check() call sites in bellows.py (found {gates_check_calls})")
if wt_path_passes < 2:
    problems.append(f"FEWER THAN 2 wt_path=wt_path threadings in bellows.py (found {wt_path_passes})")

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
    print(f"Dev log: {devlog_path}")
    print(f"Modified files: gates.py, bellows.py")
    print(f"Plan in-progress: {plan_path}")
```

The Python block above MUST execute and its literal stdout MUST appear in the dev log file in a section titled `## Rule 20 Self-Check`.

**B. Commit:**

```bash
git add bellows/gates.py bellows/bellows.py bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md
git commit -m "fix: thread wt_path to deposit_exists gate (BACKLOG #1)"
```

**C. STOP.** Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict.

---

## Step 2 — QA Verification (Bellows QA)

**Agent:** Bellows QA
**Specialist file:** `bellows/agents/BELLOWS_QA.md`

**Goal:** Verify that Step 1's code changes correctly resolve newly-created worktree deposits, do not regress bellows-self plans, and add adequate test coverage to prevent regression.

**Read first (in order):**

1. `bellows/agents/BELLOWS_QA.md`
2. `bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md` — DEV's dev log from Step 1
3. `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md` — root cause diagnostic
4. `bellows/gates.py` — modified file
5. `bellows/bellows.py` — modified file
6. `bellows/tests/test_gates.py` — existing tests; new tests will be added here

### Test additions (Bellows QA writes these)

Add to `bellows/tests/test_gates.py`:

**Test 2.1 — `test_resolve_deposit_path_finds_file_in_worktree`**
- Setup: create a temp `project_path` directory and a temp `wt_path` directory (different paths). Create a deposit file at `wt_path/knowledge/research/foo.md` (Form B — project-relative). DO NOT create the file at `project_path`.
- Call `_resolve_deposit_path("knowledge/research/foo.md", project_path, wt_path=wt_path)`.
- Assert: returns the wt_path-joined absolute path; `os.path.isfile()` of the returned path returns True.

**Test 2.2 — `test_resolve_deposit_path_finds_file_in_worktree_form_a`**
- Same as 2.1 but with a Form A (governance-root-relative) path: declare the path as `<project_basename>/knowledge/research/foo.md` where `project_basename` is the basename of `project_path`.
- File on disk lives at `wt_path/knowledge/research/foo.md` (the basename prefix is stripped before joining to wt_path).
- Assert: returns the correct wt_path-joined path.

**Test 2.3 — `test_resolve_deposit_path_bellows_self_no_wt_path_drift`**
- Setup: `wt_path == project_path` (bellows-self pattern). Create the deposit file at `project_path/knowledge/research/foo.md`.
- Call `_resolve_deposit_path("knowledge/research/foo.md", project_path, wt_path=project_path)`.
- Assert: returns the project_path-joined path. Confirms the Strategy 0 guard `if wt_path != project_path` correctly skips and falls through to existing strategies.

**Test 2.4 — `test_resolve_deposit_path_no_wt_path_backward_compat`**
- Setup: don't pass `wt_path` at all (use the default `None`). Create the deposit file at `project_path/knowledge/research/foo.md`.
- Call `_resolve_deposit_path("knowledge/research/foo.md", project_path)`.
- Assert: returns the project_path-joined path. Confirms the function still works for callers that haven't been updated to pass `wt_path`.

**Test 2.5 — `test_gate_deposit_exists_threads_wt_path`**
- Mock parsed agent output and a plan-text fixture declaring a single deposit at `knowledge/research/foo.md`.
- Setup: create the file at `wt_path/knowledge/research/foo.md` only (NOT at project_path).
- Call `_gate_deposit_exists(parsed, plan_text, 1, project_path, wt_path=wt_path, ...)`.
- Assert: `failures` list is empty (gate passes).

**Test 2.6 — `test_gate_deposit_exists_fails_when_file_truly_missing`**
- Negative-case regression: declare a deposit that doesn't exist anywhere (not in wt_path, not in project_path).
- Assert: `failures` list contains a `deposit_exists` failure with the expected error message format.

### Targeted test execution

Run the targeted test suite for the two modified files plus the new tests:

```bash
cd bellows && python3 -m pytest tests/test_gates.py tests/test_bellows.py -v
```

Capture stdout/stderr to evidence directory (see Evidence section below).

### Full test suite execution

Run the full Bellows test suite to confirm no regressions:

```bash
cd bellows && python3 -m pytest tests/ -v
```

Capture pass/fail counts; compare against the dev log's tests-before count.

### Evidence

**Evidence directory:** `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/`

Required evidence files:
- `targeted-tests.txt` — output of `pytest tests/test_gates.py tests/test_bellows.py -v`
- `full-suite.txt` — output of `pytest tests/ -v` (last 50 lines minimum showing summary)
- `gates-diff.txt` — output of `git diff HEAD~1 HEAD -- bellows/gates.py` (or equivalent showing the wt_path threading)
- `bellows-diff.txt` — output of `git diff HEAD~1 HEAD -- bellows/bellows.py` (call-site updates)
- `wt-path-grep.txt` — output of `grep -n "wt_path" bellows/gates.py bellows/bellows.py` confirming all expected occurrences
- `commit.txt` — output of `git log -1 --oneline` showing the Step 1 commit

### QA report

**Output:** `bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md`

The QA report MUST include:

- A verification table with at least 7 rows: 6 unit tests (one per test 2.1 through 2.6) + 1 row for full-suite regression check. Each row includes Status (PASS/FAIL with checkmark emoji for PASS), Evidence file path, and one-line result summary.
- Tests-before / Tests-after counts.
- The Rule 20 mandatory QA self-check Python block executed verbatim with stdout pasted into a `## Rule 20 Self-Check` section.

### Rule 20 Self-Check (Bellows QA)

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-deposit-exists-worktree-aware-2026-05-06"
qa_report_path = "bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md"
evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "targeted-tests.txt", "full-suite.txt", "gates-diff.txt",
    "bellows-diff.txt", "wt-path-grep.txt", "commit.txt",
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
    return False

failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")

print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

The literal stdout from this block MUST appear in the QA report.

**Deposits:**
- `bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md`
- `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/`
- `bellows/tests/test_gates.py` (modified — 6 new tests added)

---

## Housekeeping (Step 2 final block — Bellows QA)

If QA self-check PASSES, perform housekeeping in this exact order:

**A. Commit:**

```bash
git add bellows/tests/test_gates.py bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/
git commit -m "test: deposit_exists worktree-aware path resolution coverage"
```

**B. BACKLOG close:**

Use `Filesystem:edit_file` to update `bellows/knowledge/BACKLOG.md`:

- Move the BACKLOG #1 entry (the long entry starting with `2026-05-06: deposit_exists gate reports plan-required deposits as missing`) from the `## Open` section to the top of the `## Closed` section.
- Append a hygiene-close annotation: `**Closed 2026-05-06:** Root cause confirmed as path resolution drift (worktree-vs-project_path mismatch) via diagnostic at \`bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md\`. Fix shipped via executable-deposit-exists-worktree-aware-2026-05-06: \`_resolve_deposit_path\` now accepts \`wt_path\` and tries worktree-first resolution; \`gates.check()\` and \`_gate_deposit_exists\` thread \`wt_path\` through; both \`gates.check()\` call sites in \`bellows.py\` pass \`wt_path\`. Strategy 0 guard \`if wt_path != project_path\` preserves bellows-self compatibility. 6 new unit tests; 0 regressions.`

Commit:

```bash
git add bellows/knowledge/BACKLOG.md
git commit -m "docs: close BACKLOG #1 (deposit_exists worktree-aware fix shipped)"
```

**C. Move plan to Done (final action):**

```python
import shutil
shutil.move(
    "bellows/knowledge/decisions/in-progress-executable-deposit-exists-worktree-aware-2026-05-06.md",
    "bellows/knowledge/decisions/Done/executable-deposit-exists-worktree-aware-2026-05-06.md"
)
```

```bash
git add bellows/knowledge/decisions/Done/executable-deposit-exists-worktree-aware-2026-05-06.md
git commit -m "chore: move deposit_exists worktree-aware fix plan to Done"
```

**Deposits:**
- `bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md`
- `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/`
- `bellows/tests/test_gates.py`
- `bellows/knowledge/BACKLOG.md`
