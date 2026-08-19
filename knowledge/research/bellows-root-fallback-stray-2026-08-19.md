# bellows_root.py fallback creates stray lifecycle.db in watched projects

**Date:** 2026-08-19 | **Plan:** 455 (diagnostic) | **Target:** bellows_root.py

---

## Q1 — Trigger pinning (as far as the logs allow)

**Verdict: UNDETERMINED from current logs.** The step JSON schema (`{success, raw_output, stderr, parsed}`) has no `cwd` or `command` field, so the working directory of each step cannot be read directly.

**Correlation attempt:**

| Stray | Timestamp | Nearest step | Step window | Target project |
|---|---|---|---|---|
| `invoice-pulse/lifecycle.db` | 2026-08-18 20:13 | step_id 808, plan 446, step 1 | 20:10:39 – 20:15:56 | `/Users/marklehn/Developer/GitHub/invoice-pulse` |
| `lessons-forge/lifecycle.db` | 2026-07-16 08:12 | step_id 342, plan 203, step 1 | 08:15:00 – 08:18:22 | `/Users/marklehn/Developer/GitHub/lessons-forge` |

- **Invoice-pulse:** the stray falls WITHIN step 808's execution window (plan 446, a diagnostic running against invoice-pulse). However, the bellows daemon process itself always resolves `LIFECYCLE_DB_PATH` from `bellows_root.py`'s `__file__`, which is in the bellows tree — so the daemon's own lifecycle writes cannot have created this stray. The agent output for this step contains `sqlite3` references, but these are from the agent reading a Python file in the project (Read tool), not from executing `sqlite3.connect()`.

- **Lessons-forge:** the stray at 08:12 is 3 minutes BEFORE the first step of the day (08:15:00). No step was running. No July 16 step log files exist in `logs/`. This timing is consistent with daemon startup (bellows.py imports lifecycle.py, which evaluates `LIFECYCLE_DB_PATH` at import time) — but the import-time resolution uses `Path(__file__).resolve().parent` from `bellows_root.py`, which is in the bellows tree and WOULD find `config.json` correctly. If `init_lifecycle_db()` had fired with a project path, the file would have tables, not be 0-byte.

**0-byte / no-tables evidence (walk 2 F6):** Both strays are 0-byte with no tables. `init_lifecycle_db()` creates tables via DDL, so the stray was NOT created by `init_lifecycle_db()`. A bare `sqlite3.connect(path)` followed by `.close()` (or a failed read on a non-existent DB) produces exactly a 0-byte no-tables file. This favors a READ-path `sqlite3.connect()` (e.g., `active_plan_for_placeholder()`, `_count_plans_closed_since()`) or a non-bellows origin.

**Non-bellows hypothesis remains live:** A Claude Code agent, test, or manual invocation running `sqlite3.connect("lifecycle.db")` (relative path) with cwd set to a project root produces an identical 0-byte file. The `runner.py` runs `claude -p` with `cwd=project_path`, and a bellows-dispatched agent COULD execute `python3 -c "import sqlite3; sqlite3.connect('lifecycle.db')"` from the project root — this would create the stray. The logs cannot rule this out.

**Evidence needed to determine trigger:** Adding a `cwd` field to the step JSON schema, or wrapping `sqlite3.connect()` calls in lifecycle.py with path-origin logging, would disambiguate.

---

## Q2 — Call-site enumeration and classification

### resolve_bellows_root() call sites (5 total)

| # | File:Line | Context | Start resolves from | Can start be project-rooted? | Builds lifecycle.db path? |
|---|---|---|---|---|---|
| 1 | `lifecycle.py:21` | Module-level `LIFECYCLE_DB_PATH` | `__file__` (bellows_root.py) | No — `bellows_root.py` is always in the bellows tree | Yes |
| 2 | `reporting.py:67` | `__main__` block | `__file__` (bellows_root.py) | No — same reason | Yes |
| 3 | `status.py:232` | `main()` function | `__file__` (bellows_root.py) | No — same reason | Yes |
| 4 | `dashboard.py:328` | `CursesShell.__init__` | `__file__` (bellows_root.py) | No — same reason | Yes (via `assemble_state`, line 116) |
| 5 | `runner.py:23` | Module-level `BELLOWS_ROOT` | `__file__` (bellows_root.py) | No — same reason | No (used for `LOGS_DIR` only) |

### lifecycle.db builders — stray creator classification (4 builders)

| Builder | File:Line | Connect mode | Existence guard? | Creates stray? | Why |
|---|---|---|---|---|---|
| `lifecycle.py:21` via `init_lifecycle_db()` | `lifecycle.py:27` | `sqlite3.connect(path)` (rw) | No | **No** — if it ran, it would create TABLES (DDL at lines 29–168); strays are 0-byte/no-tables, ruling this out as the stray creator |
| `lifecycle.py:21` via read-path functions | `lifecycle.py:176–177` (e.g., `active_plan_for_placeholder`) | `sqlite3.connect(path)` (rw) | No | **Yes, in principle** — a bare `sqlite3.connect()` on a non-existent path creates a 0-byte file; however, in production `LIFECYCLE_DB_PATH` resolves to the bellows tree, not a project |
| `reporting.py:67` | `reporting.py:34` | `file:{path}?mode=ro` (ro) | Implicit (`?mode=ro` fails on non-existent file) | **No** — `?mode=ro` URI flag prevents file creation |
| `status.py:233` | `status.py:237` | Path object, then `.exists()` check | **Yes** (line 237: `if not db_path.exists(): return`) | **No** — guarded; returns early when file absent |
| `dashboard.py:116` | `dashboard.py:142` | Path object, then `.exists()` check | **Yes** (line 142: `db_absent = not db_path.exists()`, guarded at line 146) | **No** — guarded; skips DB queries when absent |

**Summary:** In the current production code, ALL five call sites resolve from `bellows_root.py`'s `__file__`, which is always in the bellows tree. The fallback at `bellows_root.py:27–28` is a latent defect — it CAN produce a wrong path (demonstrated in Q4) but the production call sites don't trigger it because `__file__` always has `config.json` in an ancestor.

---

## Q3 — Worktree variant confirmation

**INTENDED case (works correctly):** Bellows' own plans run in `.bellows-worktrees/<wt>/` where `config.json` is absent (gitignored). The walk correctly continues UP to canonical `bellows/`:

```
start: bellows/.bellows-worktrees/455/
  → bellows/.bellows-worktrees/455/  — no config.json
  → bellows/.bellows-worktrees/       — no config.json
  → bellows/                          — HAS config.json → return ✓
```

Verified: `resolve_bellows_root(_start=bellows/.bellows-worktrees/455)` returns `bellows/` (canonical). The worktree resolution is correct.

**FAILING case (the defect):** A start rooted in a non-bellows tree (a watched project) with no `config.json` in any ancestor falls back to `start`:

```
start: lessons-forge/
  → lessons-forge/         — no config.json
  → Developer/GitHub/      — no config.json
  → Developer/             — no config.json
  → ...                    — no config.json
  → / (filesystem root)    — return start = lessons-forge/ ✗
```

Verified: `resolve_bellows_root(_start=lessons-forge)` returns `lessons-forge/` (wrong). Same for `invoice-pulse`.

**Stray environment:** Both strays came from watched project directories (`invoice-pulse`, `lessons-forge`). The exact mechanism that called `resolve_bellows_root()` with a project-rooted start is undetermined (see Q1), but the fallback behavior is confirmed.

---

## Q4 — Scratch reproduction

Reproduced in a temporary directory. Procedure:

1. Created `<tmpdir>/fake-project/src/` with no `config.json` anywhere in the tree.
2. Called `resolve_bellows_root(_start=<tmpdir>/fake-project/src)` — it returned `<tmpdir>/fake-project/src` (the fallback to `start`).
3. Built `lifecycle_path = str(result / "lifecycle.db")` and called `sqlite3.connect(lifecycle_path)` then `conn.close()`.
4. **Result:** a 0-byte file was created at `<tmpdir>/fake-project/src/lifecycle.db` with no tables — identical to the production strays.
5. Cleaned up tmpdir.

**Assertion confirmed:** the fallback at `bellows_root.py:27–28` + a `sqlite3.connect()` call demonstrably creates a 0-byte no-tables stray file at the wrong location.

---

## Q5 — Gap Assessment (Rule 27)

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| **(a) `bellows_root.py:27–28` fallback** | When no ancestor contains `config.json`, silently `return start` — treats any directory as a valid bellows root. | Anchor on a TRACKED bellows sentinel (`bellows.py` — present in both canonical and worktrees, gittracked). Walk up looking for `config.json` first (existing behavior), then fall back to checking for `bellows.py` as secondary sentinel. If NEITHER is found in any ancestor, raise `ValueError("not in a bellows tree")` instead of silently returning `start`. | Edit `bellows_root.py:23–29`: after the `config.json` check fails at filesystem root, do a second walk looking for `bellows.py`. If found, return that directory. If neither sentinel found, raise. |
| **(b) CI / fresh-clone preservation** | The `return start` fallback exists to handle CI/fresh-clone environments where `config.json` (gitignored) has not yet been created. The proposed fix MUST NOT break this. | The `bellows.py` secondary sentinel handles this: `bellows.py` is a tracked file present in fresh clones and CI checkouts. A fresh clone of bellows will have `bellows.py` in the repo root but no `config.json` — the secondary sentinel resolves correctly. Only truly non-bellows trees (watched projects) will raise. | No additional change — the `bellows.py` sentinel inherently handles CI/fresh-clone. |
| **(c) Call-site hardening** | No call site passes an explicit `_start` in production — all rely on the default `Path(__file__).resolve().parent`. This makes the fallback a latent defect rather than an active one. | No call-site changes needed for the immediate fix. The `_start` parameter remains available for testing. | None — the fix is entirely within `bellows_root.py`. |

**Reference:** `1ecf898` introduced `config.json` as the anchor for worktree-safe resolution. The proposed fix EXTENDS this intent by adding a tracked secondary sentinel for when `config.json` is absent (CI/fresh-clone), rather than reverting to the pre-`1ecf898` `Path(__file__).parent` behavior.

---

## Q6 — Fix scope + guard-test design

### Files and lines touched

| File | Lines | Change |
|---|---|---|
| `bellows_root.py` | 22–29 | After `config.json` walk reaches filesystem root: do a second walk up from `start` looking for `bellows.py`. If found, return that directory. If neither sentinel found, raise `ValueError("resolve_bellows_root: no bellows sentinel (config.json or bellows.py) found in any ancestor of <start>")`. |

**Single file, ~10 lines changed.** No other files require modification.

### Guard test design

Add to `tests/test_bellows_root.py`:

```python
import pytest

def test_non_bellows_tree_raises(tmp_path):
    """Resolving from a non-bellows tree must raise, not return a path.
    
    Regression guard for the stray lifecycle.db defect: the old fallback
    silently returned `start` when no sentinel was found, causing
    sqlite3.connect() calls to create files in the wrong directory.
    """
    deep = tmp_path / "fake-project" / "src"
    deep.mkdir(parents=True)
    with pytest.raises(ValueError, match="no bellows sentinel"):
        resolve_bellows_root(_start=deep)


def test_worktree_resolution_still_works(tmp_path):
    """Existing worktree resolution must still pass.
    
    bellows/.bellows-worktrees/<wt>/ has bellows.py (tracked) but no
    config.json (gitignored). The walk must find bellows.py and return
    the canonical directory.
    """
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "bellows.py").write_text("# sentinel")
    wt_dir = canonical / ".bellows-worktrees" / "wt1"
    wt_dir.mkdir(parents=True)
    
    result = resolve_bellows_root(_start=wt_dir)
    assert result == canonical


def test_config_json_takes_precedence(tmp_path):
    """When both config.json and bellows.py exist, config.json wins
    (preserves existing behavior).
    """
    root = tmp_path / "bellows"
    root.mkdir()
    (root / "config.json").write_text("{}")
    (root / "bellows.py").write_text("# sentinel")
    
    assert resolve_bellows_root(_start=root) == root
```

**Note:** The existing `test_falls_back_when_no_config` test will need to be updated — it currently asserts that the fallback returns `start`, but the fixed behavior should raise `ValueError`.

### Blast radius and tier

- **Blast radius:** `bellows_root.py` is execution-engine core path-resolution used by 5 call sites (`lifecycle.py`, `reporting.py`, `status.py`, `dashboard.py`, `runner.py`). All production calls resolve from `__file__` and will find either `config.json` (canonical) or `bellows.py` (worktree/CI), so the behavioral change only affects the error case (non-bellows trees), which currently silently produces wrong results.
- **Tier:** T1 (T-1 blast radius + T-8 novel). The core-infra blast radius is grounds for OPTIONAL self-escalation to T2 at the fix author's discretion, not automatic.

---

## Stray cleanup

`lessons-forge/lifecycle.db` is confirmed 0 bytes with no tables. **Safe to delete.** `invoice-pulse/lifecycle.db` was already deleted (2026-08-18).

---

## Output Receipt

- **Status:** Complete
- **Deposits:** `knowledge/research/bellows-root-fallback-stray-2026-08-19.md` (this file)
- **Code changes:** None (read-only diagnostic)
- **Cleanup:** Scratch temp dir created and removed during Q4 reproduction
