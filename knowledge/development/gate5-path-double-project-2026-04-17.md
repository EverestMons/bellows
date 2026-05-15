# Gate 5 Path Resolution Fix — Double Project Name

**Date:** 2026-04-17
**Plan:** executable-gate5-path-double-project-2026-04-17.md
**Step:** 1 (DEV)

## Changes

- Added `_resolve_deposit_path(path, project_path)` helper in `gates.py` that tries three path resolution strategies:
  1. `os.path.isfile(path)` — absolute or CWD-relative paths
  2. `os.path.isfile(os.path.join(project_path, path))` — paths relative to project root without project name prefix (e.g. `knowledge/development/foo.md`)
  3. `os.path.isfile(os.path.join(os.path.dirname(project_path), path))` — paths that include the project directory name (e.g. `invoice-pulse/knowledge/development/foo.md`)

- Replaced inline two-strategy checks in both agent-declared and plan-required deposit verification with calls to `_resolve_deposit_path`.

## Root Cause

`os.path.join(project_path, path)` where `project_path = /Users/.../invoice-pulse` and `path = invoice-pulse/knowledge/development/foo.md` produces `/Users/.../invoice-pulse/invoice-pulse/knowledge/development/foo.md` — double project name, always returns False. Strategy 3 (`os.path.dirname(project_path)` + path) resolves to `/Users/.../invoice-pulse/knowledge/development/foo.md` which is correct.

## Tests

- 104/104 full suite pass. Zero regressions.
- Commit: `8bdcaa0 fix: gate 5 path resolution — handle project-prefixed deposit paths`

---

### Output Receipt
- **Status:** Complete
- **Files Modified:** `gates.py`
- **Tests:** 104/104 pass
