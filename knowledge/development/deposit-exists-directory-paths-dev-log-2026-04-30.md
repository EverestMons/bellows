# Dev Log: deposit_exists Gate Accepts Directory Paths
**Date:** 2026-04-30 | **Plan:** parallel-1-executable-deposit-exists-directory-paths-2026-04-30 | **BACKLOG:** #11

---

## 1. Before/After: `_resolve_deposit_path`

### Before
```python
def _resolve_deposit_path(path, project_path):
    """Check if a deposit file exists, trying multiple path resolution strategies.

    Returns True if the file exists at any of:
      1. path as-is (absolute or CWD-relative)
      2. os.path.join(project_path, path) — relative to project root
      3. os.path.join(os.path.dirname(project_path), path) — path includes project dir name
    """
    if os.path.isfile(path):
        return True
    if os.path.isfile(os.path.join(project_path, path)):
        return True
    if os.path.isfile(os.path.join(os.path.dirname(project_path), path)):
        return True
    return False
```

### After
```python
def _resolve_deposit_path(path, project_path):
    """Check if a deposit path exists, trying multiple path resolution strategies.

    Returns True if the path exists (as a file or directory) at any of:
      1. path as-is (absolute or CWD-relative)
      2. os.path.join(project_path, path) — relative to project root
      3. os.path.join(os.path.dirname(project_path), path) — path includes project dir name
    """
    if os.path.isfile(path) or os.path.isdir(path):
        return True
    p2 = os.path.join(project_path, path)
    if os.path.isfile(p2) or os.path.isdir(p2):
        return True
    p3 = os.path.join(os.path.dirname(project_path), path)
    if os.path.isfile(p3) or os.path.isdir(p3):
        return True
    return False
```

---

## 2. Test Additions

Five new tests added to `tests/test_gates.py`:

```python
# --- _resolve_deposit_path directory support (BACKLOG #11) ---

def test_resolve_deposit_path_directory_as_is(tmp_path):
    d = tmp_path / "evidence"
    d.mkdir()
    assert gates._resolve_deposit_path(str(d), "/nonexistent") is True


def test_resolve_deposit_path_directory_project_relative(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    assert gates._resolve_deposit_path("subdir", str(tmp_path)) is True


def test_resolve_deposit_path_directory_parent_relative(tmp_path):
    parent = tmp_path / "project"
    parent.mkdir()
    d = tmp_path / "bellows" / "evidence"
    d.mkdir(parents=True)
    assert gates._resolve_deposit_path("bellows/evidence", str(parent)) is True


@patch("os.path.isfile", return_value=False)
@patch("os.path.isdir", return_value=False)
def test_resolve_deposit_path_nonexistent(mock_isdir, mock_isfile):
    assert gates._resolve_deposit_path("/no/such/path", "/tmp") is False


def test_gate_deposit_exists_directory_in_deposits_block(tmp_path):
    d = tmp_path / "evidence"
    d.mkdir()
    plan_text = (
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n>\n"
        "> **Deposits:**\n"
        f"> - `{d}/`\n"
    )
    parsed = _clean_parsed()
    parsed["result_text"] = f"### Files Deposited\n- {d}/\n\n### Next"
    failures = []
    gates._gate_deposit_exists(parsed, failures, str(tmp_path), plan_text=plan_text, step_number=1)
    assert failures == []
```

---

## 3. Test Run Output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/marklehn/Desktop/GitHub/bellows
plugins: anyio-4.12.1, cov-7.0.0
collected 34 items

tests/test_gates.py ..................................                   [100%]

============================== 34 passed in 0.04s ==============================
```

34 tests collected, 34 passed. (29 existing + 5 new.)

---

## 4. Deviations from Plan

None. The fix was applied exactly as specified.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Fixed `_resolve_deposit_path` in `gates.py` to accept paths that exist as either files or directories, resolving BACKLOG #11's false-positive gate_failure on Rule 26 plans declaring evidence directories. Added 5 unit tests covering all three resolution strategies for directories, a nonexistent-path regression guard, and an end-to-end `_gate_deposit_exists` test with a directory deposit.

### Files Deposited
- `bellows/knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md` — this dev log

### Files Created or Modified (Code)
- `bellows/gates.py` — `_resolve_deposit_path`: added `os.path.isdir()` checks alongside existing `os.path.isfile()` at all three resolution strategies
- `bellows/tests/test_gates.py` — added 5 new tests for directory path support

### Decisions Made
- Used `tmp_path` pytest fixture for directory tests (a, b, c, e) to create real directories on disk rather than mocking — more reliable for path resolution tests

### Flags for CEO
- None

### Flags for Next Step
- None
