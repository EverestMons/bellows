# Executable — _teardown_worktree stale lock detection + orphaned directory cleanup

**Project:** bellows | **Type:** executable | **Steps:** 2 | **Priority:** 1 | **auto_close:** false | **pause_for_verdict:** after_step_1

## Context

Diagnostic at `bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md` identified ONE real failure mode in `_teardown_worktree` (BACKLOG `2026-05-07 cherry-pick fragility`):

**Stale `.git/index.lock` blocking cherry-pick.** Reproduced live during teardown of `executable-billto-type-field-mapping-fix-2026-05-07`: the lock prevented git from acquiring the index, the 60-second `subprocess.run` timeout fired, `WorktreeTeardownError` was raised, and the worktree was left alive for manual recovery. Manual cost ~10 minutes.

The diagnostic also disproved the BACKLOG's "Failure 2 single-SHA" hypothesis — the cherry-pick code at `bellows.py:629-653` already iterates ALL commits via `git log --format=%H HEAD --not main_branch` with oldest-first reversal. No multi-SHA fix needed.

This plan ships two surgical changes:
- **Candidate 3:** stale `.git/index.lock` detection and removal before cherry-pick (~10 LOC). Closes the only confirmed reliability bug.
- **Candidate 5:** orphaned worktree directory cleanup as a fallback after `git worktree remove` (~3 LOC). Cosmetic but cheap — handles the case where `git worktree remove` fails but the directory persists.

Candidate 4 (retry-with-backoff on cherry-pick timeout) deferred per diagnostic Q8 — ship Candidate 3 first, observe whether lock-related failures recur, add retry only if needed.

## Execution Map

Step 1 (DEV) → Step 2 (QA)

## STEP 1 — Bellows Developer: ship lock detection + orphan cleanup

**Agent:** Bellows Developer
**Deposits:**
- `bellows/bellows.py` (modified)
- `bellows/tests/test_bellows.py` (modified — new regression tests added)
- `bellows/knowledge/development/teardown-worktree-lock-cleanup-dev-log-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_DEVELOPER.md, then the diagnostic at bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md (Q1, Q5, Q7 Candidate 3, Q7 Candidate 5, and "Recommended Fix" sections). You are the Bellows Developer implementing two tightly-scoped fixes to `_teardown_worktree` in `bellows.py`.

OBJECTIVE
Add stale `.git/index.lock` detection and removal before the cherry-pick loop, AND add orphaned worktree directory cleanup as a fallback after `git worktree remove`. Total scope: ~13 LOC + 3 regression tests.

EXACT CHANGES (bellows.py)

VERIFY THE LINE NUMBERS in the actual file before editing — the diagnostic captured them but the file may have shifted. The diagnostic identified `_teardown_worktree` at L602-689 and the cherry-pick loop at L639-653.

### CHANGE 1 — Stale lock detection and removal (Candidate 3)

Insert BEFORE the cherry-pick `for sha in commit_shas:` loop. Imports `os`, `time` should already be present at top of file (verify; add if not).

```python
# Detect stale .git/index.lock that would block cherry-pick
lock_path = os.path.join(project_path, ".git", "index.lock")
if os.path.exists(lock_path):
    lock_age = time.time() - os.path.getmtime(lock_path)
    if lock_age > 5:
        try:
            os.remove(lock_path)
            print(f"Bellows: ⚠ removed stale .git/index.lock ({lock_age:.0f}s old) for {slug}")
        except OSError as e:
            print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")
    else:
        # Fresh lock — wait briefly, then remove if still present
        time.sleep(3)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"Bellows: ⚠ removed .git/index.lock after 3s wait for {slug}")
            except OSError as e:
                print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")
```

### CHANGE 2 — Orphaned directory fallback cleanup (Candidate 5)

Insert AFTER the `git worktree remove` subprocess block (around L689 per diagnostic, but verify). The current code prints a warning on removal failure but does not raise — the directory may persist. Add fallback `shutil.rmtree`:

```python
# Fallback: if `git worktree remove` failed and the directory still exists, force-remove it
if os.path.exists(wt_path):
    try:
        shutil.rmtree(wt_path, ignore_errors=True)
    except Exception as e:
        print(f"Bellows: ⚠ could not force-remove orphaned worktree dir {wt_path}: {e}")
```

`shutil` import should already be present (verify).

### CHANGE 3 — REGRESSION TESTS (tests/test_bellows.py)

Add THREE new tests. Find the test file's existing `_teardown_worktree` test patterns and model the new tests after them.

**Test 1 — `test_teardown_worktree_removes_stale_index_lock`**
- Create a temp project_path with a fake `.git/index.lock` file with mtime > 5s old
- Mock the cherry-pick subprocess to succeed (no actual git needed)
- Call `_teardown_worktree`
- Assert the lock file is gone after the call
- Assert no exception raised

**Test 2 — `test_teardown_worktree_waits_for_fresh_index_lock`**
- Create a temp project_path with a fake `.git/index.lock` file with current mtime (fresh)
- Mock subprocess calls
- Call `_teardown_worktree`
- Assert the lock is removed after the wait (the test can use a shorter `time.sleep` if patching is straightforward, otherwise just verify the lock is removed by end of call)
- Acceptable to skip the precise timing assertion if it complicates the mock; the key assertion is "lock removed by end of call"

**Test 3 — `test_teardown_worktree_force_removes_orphaned_directory`**
- Create a temp `wt_path` directory
- Mock `git worktree remove` to fail (e.g., subprocess returns non-zero)
- Call `_teardown_worktree`
- Assert `wt_path` directory no longer exists after the call
- Assert no exception propagates (the orphan cleanup is a "best effort" path)

If the existing test file uses pytest fixtures (tmp_path, monkeypatch), use them. If it uses unittest, match that style. Whatever the existing pattern is.

VERIFY

Run the targeted bellows test file:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_bellows.py -v 2>&1 | tail -50

Capture the result. Expected: all existing tests pass + 3 new tests pass.

Then run the full test suite:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tail -20

Expected: 245 passed (242 from yesterday + 3 new), 1 pre-existing `test_run_step_timeout` failure unchanged.

DEV LOG

Deposit `bellows/knowledge/development/teardown-worktree-lock-cleanup-dev-log-2026-05-10.md` with:
- The exact diff applied to bellows.py (CHANGE 1 + CHANGE 2)
- The exact 3 new tests added to test_bellows.py
- Pytest output (full output of test_bellows.py run + tail of full suite run)
- Confirmation: which line numbers ended up holding the changes (post-edit positions)
- Confirmation: no other functions in bellows.py were touched
- Confirmation: no other test files were touched

GIT COMMITS

ONE commit, conventional message:
    fix(teardown): detect stale index.lock + force-remove orphaned worktree dirs (BACKLOG 2026-05-07)

Include all three files: bellows.py, tests/test_bellows.py, the dev log. Push.

CONSTRAINTS
- Do NOT modify any other function in bellows.py. Surgical fix only.
- Do NOT modify the cherry-pick loop itself. The multi-SHA handling is correct per the diagnostic.
- Do NOT add retry-with-backoff (Candidate 4). It is deferred.
- Do NOT change error handling for `WorktreeTeardownError` at the call sites (L362, L448, L474). Those remain unchanged.
- Run pre-commit hooks if configured. If any hook fails, fix the failure and re-attempt.

OUTPUT RECEIPT
End with status (Complete / Blocked), summary of changes (lines added/removed), and deposit paths.
```

## STEP 2 — Bellows QA: verify the fix

**Agent:** Bellows QA
**Deposits:**
- `bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md`
- `bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt`
- `bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt`

**Prompt:**

```
Read agents/BELLOWS_QA.md, then the diagnostic at bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md (Q1, Q7 Candidates 3 + 5, "Recommended Fix"), then the dev log at bellows/knowledge/development/teardown-worktree-lock-cleanup-dev-log-2026-05-10.md. You are the Bellows QA Analyst verifying the fix shipped in Step 1.

VERIFICATION CHECKS

(1) Read bellows/bellows.py and confirm:
    (a) Inside `_teardown_worktree`, BEFORE the cherry-pick `for sha in commit_shas:` loop, there is lock detection code that:
        - Checks `os.path.exists(lock_path)` where lock_path is `.git/index.lock` under project_path
        - On stale lock (>5s old): removes the lock file
        - On fresh lock: waits 3s, then removes if still present
        - Wraps `os.remove` in try/except OSError with print warning
    (b) AFTER the `git worktree remove` subprocess block, there is fallback cleanup:
        - Checks `os.path.exists(wt_path)`
        - Calls `shutil.rmtree(wt_path, ignore_errors=True)` wrapped in try/except
    (c) Cherry-pick loop itself (the for sha in commit_shas: block) is UNCHANGED
    (d) Error handling at call sites (L362, L448, L474) is UNCHANGED — verify by reading each call site

(2) Read bellows/tests/test_bellows.py and confirm:
    (a) `test_teardown_worktree_removes_stale_index_lock` exists and asserts lock removal on stale lock
    (b) `test_teardown_worktree_waits_for_fresh_index_lock` exists and asserts lock removal after wait
    (c) `test_teardown_worktree_force_removes_orphaned_directory` exists and asserts shutil.rmtree fallback
    (d) No other tests modified

(3) Run the bellows test suite fresh and capture full output:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest tests/test_bellows.py -v 2>&1 | tee bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt

    Verify: 3 new tests appear with PASSED status. Existing tests unchanged (no regressions).

(4) Run the full test suite for collateral damage check:
    cd /Users/marklehn/Desktop/GitHub/bellows
    python3 -m pytest 2>&1 | tee bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt

    Expected delta: +3 new tests passing, 0 regressions, 1 pre-existing `test_run_step_timeout` failure unchanged.

(5) Behavioral spot-check: write a small Python snippet (not committed) that exercises the lock-removal path end-to-end:
    - Creates a temp directory with `.git/index.lock` file (touch it, set mtime to 30s ago via os.utime)
    - Mock or stub the cherry-pick subprocess (use unittest.mock.patch)
    - Call `_teardown_worktree(project_path, wt_path, "test-slug")` against the temp dir
    - Assert the lock file is gone after the call
    - Print PASSED / FAILED with diagnostic info
    Capture the snippet output and include verbatim in the QA report.

(6) Behavioral spot-check 2: verify orphaned-directory cleanup fires when `git worktree remove` fails:
    - Create a fake worktree directory at a temp path
    - Mock `subprocess.run` to return non-zero for the worktree remove call
    - Call `_teardown_worktree`
    - Assert the directory is gone after the call (despite the mocked failure)
    - Print PASSED / FAILED
    Capture the snippet output verbatim.

QA REPORT FORMAT

Deposit at bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md with:
- Status table: each verification check (1a–1d, 2a–2d, 3, 4, 5, 6) with ✅/❌ and one-line evidence
- Pytest tail outputs (bellows suite + full suite) inline
- Behavioral spot-check outputs inline
- Final verdict line: ALL CHECKS PASSED or LIST OF FAILURES

RULE 20 SELF-CHECK

End the QA report with the canonical Rule 20 Python self-check block. **ACTUALLY EXECUTE THE BLOCK** — copy the output literally into the QA report file. The block must use absolute paths and print "RULE 20 SELF-CHECK PASSED" verbatim if all deposit files exist. Do NOT just include the script without running it.

```python
import os, sys
deposits = [
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/teardown-worktree-lock-cleanup-qa-2026-05-10.md",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_bellows.txt",
    "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/teardown-worktree-lock-cleanup-2026-05-10/pytest_full.txt",
]
missing = [d for d in deposits if not os.path.isfile(d)]
if missing:
    print(f"RULE 20 SELF-CHECK FAILED — missing: {missing}")
    sys.exit(1)
else:
    print("RULE 20 SELF-CHECK PASSED")
    sys.exit(0)
```

GIT COMMITS

ONE commit:
    docs(qa): teardown lock + orphan cleanup verification (BACKLOG 2026-05-07)

Include the QA report and both pytest evidence files. Push.

OUTPUT RECEIPT
End with status (Complete / Blocked), final verdict line, and deposit paths.
```

**STOP. Do NOT proceed beyond Step 2 without CEO verdict. After Step 2 completes, the Planner moves the plan to Done/ via Filesystem:move_file.**
