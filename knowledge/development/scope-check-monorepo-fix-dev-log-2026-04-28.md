# Dev Log — scope_check Monorepo Fix (BACKLOG #4)
**Date:** 2026-04-28 | **Plan:** executable-scope-check-monorepo-fix-2026-04-28 | **Step:** 1

---

## Old `_capture_git_diff` Body (Verbatim)

```python
def _capture_git_diff(project_path: str) -> str:
    """Capture git diff --stat output for file change tracking."""
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

## New `_capture_git_diff` Body (Verbatim)

```python
def _capture_git_diff(project_path: str) -> str:
    """Capture git diff --stat output for file change tracking, scoped to the project subtree.

    Uses `--relative -- .` to handle the nested-repo case where project_path is a
    subdirectory of a larger repo (e.g., bellows/ inside the governance-root repo).
    Without scoping, git walks up to the parent repo's .git and reports the entire
    monorepo's diff. Universally applicable: for standalone repos (cwd = repo root)
    `-- .` is equivalent to no pathspec and `--relative` is a no-op. Closes BACKLOG #4.
    """
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

## New Test (Verbatim)

```python
def test_capture_git_diff_uses_relative_pathspec():
    """BACKLOG #4 fix: _capture_git_diff scopes diff to project subtree via --relative -- ."""
    mock_result = MagicMock()
    mock_result.stdout = ""
    with patch("bellows.subprocess.run", return_value=mock_result) as mock_run:
        bellows._capture_git_diff("/some/project")
    assert mock_run.called
    argv = mock_run.call_args[0][0]
    assert "--relative" in argv, f"Expected --relative in argv: {argv!r}"
    assert "--" in argv, f"Expected -- separator in argv: {argv!r}"
    dash_dash_idx = argv.index("--")
    assert dash_dash_idx + 1 < len(argv) and argv[dash_dash_idx + 1] == ".", \
        f"Expected '.' immediately after '--' in argv: {argv!r}"
```

## Test Results

- **Total tests passed:** 65
- **New test `test_capture_git_diff_uses_relative_pathspec`:** PASSED
- **Exit code:** 0
- Full pytest output: `knowledge/development/scope-check-monorepo-fix-step-1-pytest.txt`

## Anomalies

None. All 65 tests passed cleanly. The only pytest warning is the pre-existing LibreSSL/urllib3 notice, unrelated to this change.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Modified `_capture_git_diff` in `bellows.py` to add `--relative -- .` flags to the git diff command, scoping the diff to the project subtree. Added a unit test `test_capture_git_diff_uses_relative_pathspec` that verifies the new argv contains the scoping flags.

### Files Deposited
- `bellows/knowledge/development/scope-check-monorepo-fix-dev-log-2026-04-28.md` — this dev log
- `bellows/knowledge/development/scope-check-monorepo-fix-step-1-pytest.txt` — full pytest output

### Files Created or Modified (Code)
- `bellows/bellows.py` — updated `_capture_git_diff` argv and docstring (lines 398–415)
- `bellows/tests/test_bellows.py` — added `test_capture_git_diff_uses_relative_pathspec` test

### Decisions Made
- Did not modify `_parse_diff_stat` — its `..`-component filter is correct for standalone repos and inert under the new scoping per diagnostic Q4

### Flags for CEO
- None

### Flags for Next Step
- None
