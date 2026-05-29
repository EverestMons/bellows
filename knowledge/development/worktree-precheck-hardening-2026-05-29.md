# Worktree & Dirty-Tree Pre-Check Hardening — Dev Log

**Date:** 2026-05-29
**Plan:** executable-worktree-precheck-hardening-2026-05-29
**Step:** 1 (DEV)

---

## Pre-edit Verification (Rule 39)

### Query 1: `_create_worktree` exists with `git worktree add`
```
grep -n "def _create_worktree" bellows.py
785:def _create_worktree(project_path: str, slug: str) -> str:
```
Confirmed: one definition at line 785; `git worktree add` at line 805; `parent_dir` mkdir at line 802. ✅

### Query 2: `Bellows.__init__` runs `git worktree prune`
```
grep -n "worktree prune" bellows.py
1136:                _log("WARN", f"⚠ worktree prune failed for {project_root}: {e}")
```
Confirmed: `subprocess.run(["git", "--no-pager", "worktree", "prune"], ...)` at lines 1131–1134 inside `__init__`. ✅

### Query 3: Pre-check with porcelain, `_is_lifecycle_artifact`, `_LIFECYCLE_IGNORE_RE`, `.strip()`
```
grep -n "porcelain" bellows.py → lines 882, 942
grep -n "_is_lifecycle_artifact" bellows.py → lines 43, 887
grep -n "_LIFECYCLE_IGNORE_RE" bellows.py → lines 36, 51
```
Confirmed: pre-check at lines 879–899 splits porcelain lines and filters via `_is_lifecycle_artifact`; `_LIFECYCLE_IGNORE_RE` at line 36; `.strip()` applied at lines 885–886 (the target for item f). ✅

---

## Change 1 (Item a) — Stranded-worktree cleanup in `_create_worktree`

**Before (lines 800–804):**
```python
    wt_path = os.path.join(project_path, ".bellows-worktrees", slug)
    parent_dir = os.path.join(project_path, ".bellows-worktrees")
    os.makedirs(parent_dir, exist_ok=True)

    try:
        cmd = ["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"]
```

**After (lines 800–822):**
```python
    wt_path = os.path.join(project_path, ".bellows-worktrees", slug)
    parent_dir = os.path.join(project_path, ".bellows-worktrees")
    os.makedirs(parent_dir, exist_ok=True)

    # Clean stranded worktree from a prior failed dispatch (mirrors __init__ prune style)
    if os.path.exists(wt_path):
        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "remove", "--force", wt_path],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass  # path may not be a registered worktree
        shutil.rmtree(wt_path, ignore_errors=True)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "prune"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass

    try:
        cmd = ["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"]
```

---

## Change 2 (Item f) — `rstrip()` + leading-space tolerance in pre-check

**Before (lines 885–886):**
```python
        if dt_result.returncode == 0 and dt_result.stdout.strip():
            dirty_lines = dt_result.stdout.strip().splitlines()
```

**After (lines 905–907):**
```python
        # rstrip (not strip): preserve leading status-code space on first porcelain line
        if dt_result.returncode == 0 and dt_result.stdout.rstrip():
            dirty_lines = dt_result.stdout.rstrip().splitlines()
```

`_is_lifecycle_artifact` already extracts the path via `porcelain_line[3:]` (skipping the `XY ` status prefix) and applies `path.strip()` on the extracted path — this is robust to all porcelain status forms including space-prefixed (` D`, ` M`). The `.rstrip()` change alone suffices to fix the bug where `.strip()` was removing the leading space from the first porcelain line of stdout.

---

## Change 3 (Item g) — `.bellows-worktrees/` lifecycle-ignore coverage

**Before (lines 36–40):**
```python
_LIFECYCLE_IGNORE_RE = re.compile(
    r'^knowledge/decisions/(in-progress-|verdict-pending-|halted-|executable-|diagnostic-).*\.md$'
    r'|^knowledge/decisions/Done/'
    r'|^verdicts/(pending|resolved)/'
)
```

**After (lines 36–41):**
```python
_LIFECYCLE_IGNORE_RE = re.compile(
    r'^knowledge/decisions/(in-progress-|verdict-pending-|halted-|executable-|diagnostic-).*\.md$'
    r'|^knowledge/decisions/Done/'
    r'|^verdicts/(pending|resolved)/'
    r'|^\.bellows-worktrees(/|$)'
)
```

The pattern `^\.bellows-worktrees(/|$)` matches both `.bellows-worktrees` (bare dir entry) and `.bellows-worktrees/anything` (child paths). The `^` anchor ensures it only matches at the path start, preventing false matches on paths containing the substring elsewhere.

---

## Regression Tests Added

### test_create_worktree_cleans_stranded_directory (item a)
Pre-creates a bare directory at `wt_path` with a marker file → calls `_create_worktree` → asserts worktree is usable, marker file is gone, and WARN was logged.

### test_create_worktree_cleans_stranded_registered_worktree (item a)
Creates a real worktree first, then calls `_create_worktree` again at the same path → asserts it cleans up via `worktree remove --force` + prune and succeeds. Verifies WARN logged.

### test_pre_check_recognizes_space_prefixed_lifecycle_line (item f)
Tests `_is_lifecycle_artifact` with space-prefixed porcelain lines (` D knowledge/decisions/...`, ` M verdicts/pending/...`). Asserts these are recognized as lifecycle artifacts. Negative control: space-prefixed real files (` M README.md`, ` D src/app.py`) still return False.

### test_pre_check_ignores_bellows_worktrees_dir (item g)
Tests `_is_lifecycle_artifact` with `?? .bellows-worktrees/` and `?? .bellows-worktrees/some-slug/file.py`. Asserts both are treated as lifecycle artifacts. Negative control: `?? src/untracked.py` and `?? bellows-worktrees-imposter/foo.py` still return False.

---

## Test Execution

### Pre-edit baseline
```
425 passed, 8 failed
FAILED tests:
  - test_decisions.py: 4 failures (phrase file not found — pre-existing)
  - test_runner_parser.py::test_run_step_timeout (pre-existing)
  - test_worktree.py::test_teardown_removes_worktree_directory (item g target)
  - test_worktree.py::test_teardown_cherry_picks_commits (item g target)
  - test_worktree.py::test_teardown_copies_uncommitted_files (item g target)
```

### Post-edit
```
432 passed, 5 failed
FAILED tests:
  - test_decisions.py: 4 failures (same pre-existing)
  - test_runner_parser.py::test_run_step_timeout (same pre-existing)

Previously-failing worktree tests now PASS:
  ✅ test_teardown_removes_worktree_directory
  ✅ test_teardown_cherry_picks_commits
  ✅ test_teardown_copies_uncommitted_files

New regression tests all PASS:
  ✅ test_create_worktree_cleans_stranded_directory
  ✅ test_create_worktree_cleans_stranded_registered_worktree
  ✅ test_pre_check_recognizes_space_prefixed_lifecycle_line
  ✅ test_pre_check_ignores_bellows_worktrees_dir

Zero new failures. Pass count increased from 425 → 432 (+7: 3 flipped + 4 new).
```

---

## Anchor Verification

```
grep -n "stranded worktree found" bellows.py
807:        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)

grep -n "\.rstrip()" bellows.py
906:        if dt_result.returncode == 0 and dt_result.stdout.rstrip():
907:            dirty_lines = dt_result.stdout.rstrip().splitlines()

grep -n "bellows-worktrees" bellows.py
40:    r'|^\.bellows-worktrees(/|$)'
801:    wt_path = os.path.join(project_path, ".bellows-worktrees", slug)
802:    parent_dir = os.path.join(project_path, ".bellows-worktrees")

grep -n "def _create_worktree" bellows.py
786:def _create_worktree(project_path: str, slug: str) -> str:
```

All four anchors confirmed. ✅

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented three independent hardening changes in `bellows.py`: (a) stranded-worktree cleanup in `_create_worktree` that removes pre-existing directories/worktrees before re-creation; (f) changed `.strip()` to `.rstrip()` on the dirty-tree pre-check porcelain result to preserve leading status-code space; (g) extended `_LIFECYCLE_IGNORE_RE` to cover `.bellows-worktrees/` paths. Added four regression tests covering all three changes with positive and negative controls.

### Files Deposited
- `knowledge/development/worktree-precheck-hardening-2026-05-29.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — stranded-worktree cleanup guard in `_create_worktree` (item a), `.strip()` → `.rstrip()` in pre-check (item f), `.bellows-worktrees/` pattern in `_LIFECYCLE_IGNORE_RE` (item g)
- `tests/test_worktree.py` — 4 new regression tests (`test_create_worktree_cleans_stranded_directory`, `test_create_worktree_cleans_stranded_registered_worktree`, `test_pre_check_recognizes_space_prefixed_lifecycle_line`, `test_pre_check_ignores_bellows_worktrees_dir`)

### Decisions Made
- Item f: confirmed `_is_lifecycle_artifact` already handles space-prefixed porcelain lines robustly via `porcelain_line[3:]` extraction — the `.rstrip()` change alone suffices
- Item g regex: used `^\.bellows-worktrees(/|$)` to match both the bare directory and child paths, anchored to prevent substring false matches

### Flags for CEO
- None

### Flags for Next Step
- The three previously-failing `test_worktree.py` tests now pass — QA should verify this flip and confirm zero new regressions
- Pre-edit baseline had 8 failures (4 decisions + 1 timeout + 3 worktree); post-edit has 5 failures (same carry-over minus the 3 worktree)
- Daemon restart required to activate all three fixes
