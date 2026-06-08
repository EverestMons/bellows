# BELLOWS_ROOT Worktree-Reachability Audit

**Date:** 2026-06-08
**Agent:** Bellows Systems Analyst
**Reference:** BACKLOG Added 2026-06-06 — `__file__`-relative root resolution breaks under worktree execution

---

## Section 1 — Per-Instance Read-Site Inventory

### 1.1 bellows.py (BELLOWS_ROOT at line 23)

```python
BELLOWS_ROOT = Path(__file__).parent.resolve()   # line 23
DB_PATH = str(BELLOWS_ROOT / "bellows.db")        # line 24
SHADOW_CACHE_DIR = BELLOWS_ROOT / ".bellows-cache" # line 25
```

| Module | BELLOWS_ROOT line | Read site (file:line) | Resource resolved | Canonical-only? |
|---|---|---|---|---|
| bellows.py | 23 | bellows.py:24 | `bellows.db` (SQLite database) | Y — gitignored |
| bellows.py | 23 | bellows.py:25 | `.bellows-cache/` (shadow plan cache) | Y — gitignored |
| bellows.py | 23 | bellows.py:87 | `logs/terminal/` (daemon terminal logs) | Y — gitignored |
| bellows.py | 23 | bellows.py:94 | `logs/` (step JSON logs) | Y — gitignored |
| bellows.py | 23 | bellows.py:140 | `config.json` (operational config) | Y — gitignored |
| bellows.py | 23 | bellows.py:265 | `verdicts/pending/` (verdict cleanup) | Y — gitignored |
| bellows.py | 23 | bellows.py:445,517,608,656 | `logs/` (verdict-request log_path) | Y — gitignored |
| bellows.py | 23 | bellows.py:1020 | cwd for `git log` (source SHA) | Y — needs canonical repo |
| bellows.py | 23 | bellows.py:1038 | `os.path.dirname(os.path.abspath(__file__))` in `_module_fingerprints()` — separate `__file__` ref, not via BELLOWS_ROOT | Y — needs canonical modules |
| bellows.py | 23 | bellows.py:1271,1274,1301,1435 | `verdicts/{pending,resolved}/` (verdict consumption) | Y — gitignored |
| bellows.py | 23 | bellows.py:1496 | `verdicts/pending/` (startup sweep) | Y — gitignored |
| bellows.py | 23 | bellows.py:1592,1594 | `logs/terminal/` (session log at `__main__`) | Y — gitignored |

**Summary:** 17 read/write sites across the file. Every resource is canonical-only (gitignored or needs canonical git history). All read sites are inside functions (not at module import time), though `DB_PATH` and `SHADOW_CACHE_DIR` capture derived paths at module level.

### 1.2 planner.py (BELLOWS_ROOT at line 11)

```python
BELLOWS_ROOT = pathlib.Path(__file__).parent.resolve()  # line 11
```

| Module | BELLOWS_ROOT line | Read site (file:line) | Resource resolved | Canonical-only? |
|---|---|---|---|---|
| planner.py | 11 | planner.py:89 | `logs/planner-consultation.jsonl` | Y — gitignored |

**Summary:** 1 read site. The `_log_consultation()` function writes to `BELLOWS_ROOT / "logs" / "planner-consultation.jsonl"`. The path is computed inside the function body, not at module level. Canonical-only (logs/ is gitignored).

### 1.3 runner.py (BELLOWS_ROOT at line 20)

```python
BELLOWS_ROOT = Path(__file__).parent.resolve()  # line 20
LOGS_DIR = BELLOWS_ROOT / "logs"                 # line 21
```

| Module | BELLOWS_ROOT line | Read site (file:line) | Resource resolved | Canonical-only? |
|---|---|---|---|---|
| runner.py | 20 | runner.py:21 | `logs/` (step log directory — derived at module level) | Y — gitignored |
| runner.py | 20 | runner.py:28 | `LOGS_DIR.mkdir(exist_ok=True)` in `_write_log()` | Y — gitignored |
| runner.py | 20 | runner.py:56 | `LOGS_DIR / f"{timestamp}-step.json"` log file write | Y — gitignored |

**Summary:** 3 read/write sites, all via the `LOGS_DIR` alias. `LOGS_DIR` is computed at module level (captured at import time). All reads are writes to the logs/ directory. Canonical-only.

### 1.4 verdict.py (BELLOWS_ROOT at line 13)

```python
BELLOWS_ROOT = Path(__file__).parent.resolve()  # line 13
VERDICTS_DIR = BELLOWS_ROOT / "verdicts"         # line 14
```

| Module | BELLOWS_ROOT line | Read site (file:line) | Resource resolved | Canonical-only? |
|---|---|---|---|---|
| verdict.py | 13 | verdict.py:14 | `verdicts/` (verdict queue root — derived at module level) | Y — partially gitignored (`ledger.jsonl` gitignored; `pending/`, `resolved/` tracked) |
| verdict.py | 13 | verdict.py:180 | `verdicts/pending/` (post verdict request) | Y — canonical daemon resource |
| verdict.py | 13 | verdict.py:283 | `verdicts/resolved/` (check for verdict) | Y — canonical daemon resource |
| verdict.py | 13 | verdict.py:317-318 | `verdicts/ledger.jsonl` (append ledger entry) | Y — gitignored |

**Summary:** 4 read/write sites, all via the `VERDICTS_DIR` alias. `VERDICTS_DIR` is computed at module level. Note: `verdicts/pending/` and `verdicts/resolved/` directories may or may not be git-tracked (depends on whether they contain tracked `.gitkeep` files), but their CONTENTS (verdict files) are runtime artifacts of the daemon. Canonical-only in all operational senses.

---

## Section 2 — Reachability Proof Per Instance

Three vectors evaluated per the BACKLOG mandate:

**(a) Daemon-process execution** — The bellows daemon (`python bellows.py`) runs from the canonical checkout. All four modules are imported from the canonical directory. `__file__` resolves to canonical paths. **NOT REACHABLE** for all four instances.

**(b) Test execution from a worktree** — The confirmed `decisions.py` vector. When the QA suite runs inside a worktree (e.g., `cd .bellows-worktrees/<wt>/ && python -m pytest`), Python imports modules from the worktree, and `__file__` resolves to `.bellows-worktrees/<wt>/<module>.py`. The test suite's `sys.path.insert(0, ...)` (e.g., test_runner.py:8) ensures imports resolve from the worktree root.

**(c) Agent/worktree-executed code path** — Agents execute via `claude -p` subprocess. The agent process does not import bellows Python modules — it reads plan files from `.bellows-cache/` and operates on the target project. **NOT REACHABLE** for all four instances.

### 2.1 bellows.py — LATENT-UNREACHABLE (convert-proactive recommended)

**Vector (a):** Not reachable. Daemon imports from canonical.

**Vector (b):** BELLOWS_ROOT, DB_PATH, and SHADOW_CACHE_DIR are captured at module load time when `import bellows` executes in any test file. This happens in: `test_bellows.py`, `test_consume_verdicts.py`, `test_cleanup_verdicts.py`, `test_misplaced_verdicts.py`, `test_worktree.py`.

However, **all tests that trigger BELLOWS_ROOT-derived filesystem operations patch `bellows.BELLOWS_ROOT` to `tmp_path`** before invoking the code. Verified: `test_bellows.py` has 17 explicit `patch("bellows.BELLOWS_ROOT", tmp_path)` calls covering every test that exercises `run_plan()`, `_consume_verdicts()`, `_perform_startup_sweep()`, `load_config()`, `_rotate_logs()`, or `migrate_db()`. `test_consume_verdicts.py` patches in all 20+ test functions. `test_cleanup_verdicts.py` passes explicit `verdicts_root=` parameter bypassing BELLOWS_ROOT. `test_misplaced_verdicts.py` patches where needed or passes explicit paths. `test_worktree.py` exercises git operations without touching BELLOWS_ROOT-derived paths.

**No unpatched read/write of a canonical-only resource via BELLOWS_ROOT was found in the test suite.**

**Vector (c):** Not reachable.

**Classification: LATENT-UNREACHABLE.** The module-level path is captured wrong in worktree context, but no execution path triggers an unpatched filesystem operation. Current test patching discipline mitigates the risk.

### 2.2 planner.py — LATENT-UNREACHABLE

**Vector (a):** Not reachable. Daemon imports from canonical.

**Vector (b):** `test_planner.py` imports `planner` (top-level), causing BELLOWS_ROOT to be evaluated. However, the only BELLOWS_ROOT-derived read site is `_log_consultation()` (planner.py:89), and **no test in `test_planner.py` invokes `_log_consultation()`**. Tests exercise `build_consult_file()` (writes to `/tmp/`) and verify command construction, never triggering a write to `BELLOWS_ROOT / "logs"`.

**No unpatched read/write of BELLOWS_ROOT-derived path occurs in the test suite.**

**Vector (c):** Not reachable.

**Classification: LATENT-UNREACHABLE.** BELLOWS_ROOT is captured wrong but never dereferenced in test execution.

### 2.3 runner.py — REACHABLE (test vector, low severity)

**Vector (a):** Not reachable. Daemon imports from canonical.

**Vector (b):** `test_runner.py` imports `runner` (top-level), causing BELLOWS_ROOT and LOGS_DIR to be evaluated at the worktree path. Of 19 test functions:
- **4 tests patch `runner.LOGS_DIR` to `tmp_path`:** `test_timeout_writes_log_file`, `test_generic_exception_writes_log_file`, `test_success_writes_log_file`, `test_no_result_event_writes_log_with_raw_output`. These are SAFE.
- **2 tests don't call `run_step()`:** `test_runner_sets_disable_autoupdater_env_var`, `test_runner_respects_explicit_disable_autoupdater_override`. These are SAFE.
- **13 tests call `run_step()` WITHOUT patching LOGS_DIR.** These trigger `_write_log()` which calls `LOGS_DIR.mkdir(exist_ok=True)` and writes a JSON log file. When run from a worktree, this creates `<worktree>/logs/<timestamp>-step.json` — a write to the wrong location.

**Specific unpatched tests:** `test_configurable_timeout_respected`, `test_timeout_returns_cost_none`, `test_generic_exception_returns_cost_none`, `test_generic_exception_message_contains_actual_error`, `test_stderr_printed_on_success`, `test_no_result_event_returns_blocked`, `test_ndjson_parse_valid_stream`, `test_ndjson_parse_malformed_line_skipped`, `test_ndjson_parse_missing_result_event`, `test_resume_session_flag_in_command`, `test_append_system_prompt_flag_in_command`, `test_run_step_retries_on_transient_401`, `test_run_step_does_not_retry_on_non_transient_error`.

**Impact assessment:** These tests create orphaned log files in `<worktree>/logs/`. The worktree is cleaned up on teardown, so the files are transient. The tests themselves pass (they don't assert on log file location). This is a **test hygiene issue**, not a test-correctness issue — no test produces incorrect results. However, it IS a confirmed instance of BELLOWS_ROOT-derived filesystem I/O while `__file__` resolves inside a worktree.

**Vector (c):** Not reachable.

**Classification: REACHABLE** — 13 test functions trigger LOGS_DIR writes while `__file__` resolves inside a worktree. Low severity: orphaned log files only, no test failures, no wrong-data reads. This is the same reachability class as the `decisions.py` bug (test imports module from worktree), but with lower impact (writes to a gitignored directory vs. reading from a missing governance file that caused test failures).

### 2.4 verdict.py — LATENT-UNREACHABLE (mitigated by conftest)

**Vector (a):** Not reachable. Daemon imports from canonical.

**Vector (b):** `test_verdict.py` and many other test files import `verdict` (top-level), causing BELLOWS_ROOT and VERDICTS_DIR to be evaluated at the worktree path. However, `tests/conftest.py` contains an **autouse=True fixture** that patches `verdict.VERDICTS_DIR` to `tmp_path / "verdicts"` for EVERY test in the suite:

```python
@pytest.fixture(autouse=True)
def isolate_verdicts_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")
```

This comprehensively isolates all verdict filesystem operations. Additionally, individual test files that exercise verdict functions apply their own explicit patches (defensive redundancy).

**No unpatched read/write of VERDICTS_DIR occurs in the test suite.**

**Vector (c):** Not reachable.

**Classification: LATENT-UNREACHABLE.** BELLOWS_ROOT is captured wrong, but the conftest autouse fixture patches VERDICTS_DIR before any test runs. The module-level `BELLOWS_ROOT` variable itself is not directly read by any test.

---

## Section 3 — Conversion Spec

### 3.1 Helper design

Introduce `resolve_bellows_root()` in a shared location (e.g., a new `bellows_root.py` module or at the top of `bellows.py` with imports from the other three). The helper mirrors `decisions.py:resolve_governance_root()`:

```python
def resolve_bellows_root() -> Path:
    """Walk up from this file to the nearest ancestor containing config.json (bellows root).

    Under worktree execution (__file__ resolves inside .bellows-worktrees/<wt>/),
    config.json does not exist in the worktree (gitignored), so the walk continues
    up to the canonical bellows root where config.json lives.
    """
    current = Path(__file__).resolve().parent
    while True:
        if (current / "config.json").exists():
            return current
        parent = current.parent
        if parent == current:
            # Filesystem root — fall back to __file__.parent (legacy behavior)
            return Path(__file__).resolve().parent
        current = parent
```

**Marker file:** `config.json` — gitignored (confirmed in `.gitignore` line 14), required for daemon operation, present at canonical root, absent from worktree checkouts. Fallback to `Path(__file__).parent` preserves current behavior in CI/test environments without `config.json`.

**Alternative marker:** A dedicated `.bellows-root` marker file (gitignored, created once). Advantage: no dependency on config.json existence. Disadvantage: requires a one-time creation step and documentation.

**Alternative approach (non-marker):** Detect `.bellows-worktrees/` in the resolved path and navigate up:
```python
parts = Path(__file__).resolve().parts
for i, part in enumerate(parts):
    if part == ".bellows-worktrees":
        return Path(*parts[:i])
return Path(__file__).resolve().parent
```
Advantage: no marker file needed. Disadvantage: fragile — coupled to the `.bellows-worktrees/` directory name convention.

**Recommendation:** Use `config.json` marker with fallback, consistent with the `resolve_governance_root()` pattern established in `decisions.py`.

### 3.2 Instance: runner.py (REACHABLE — convert)

The only instance classified REACHABLE. Convert first.

**Current (runner.py:20-21):**
```python
BELLOWS_ROOT = Path(__file__).parent.resolve()
LOGS_DIR = BELLOWS_ROOT / "logs"
```

**Replacement:**
```python
from bellows_root import resolve_bellows_root
BELLOWS_ROOT = resolve_bellows_root()
LOGS_DIR = BELLOWS_ROOT / "logs"
```

No other changes needed — all read sites use `LOGS_DIR`, which is derived from BELLOWS_ROOT.

### 3.3 Instances: bellows.py, planner.py, verdict.py (LATENT-UNREACHABLE — convert-proactive)

**Recommendation: Convert proactively.** Rationale from BACKLOG: "same class that cost two real fixes — convert proactively before a third surfaces." The regression risk is LOW because:
1. The helper's fallback preserves `Path(__file__).parent` behavior when no marker is found (CI, fresh clone).
2. In the daemon (the only production consumer), `__file__` resolves to the canonical directory where `config.json` exists — the helper returns immediately on the first iteration, producing the identical path as the current code.
3. All test patching continues to work unchanged — tests patch the module-level variables (`bellows.BELLOWS_ROOT`, `verdict.VERDICTS_DIR`, etc.), which remain the same variable names.

**bellows.py (line 23):**
```python
# Current:
BELLOWS_ROOT = Path(__file__).parent.resolve()

# Replacement:
from bellows_root import resolve_bellows_root
BELLOWS_ROOT = resolve_bellows_root()
```

DB_PATH, SHADOW_CACHE_DIR, and all in-function references to BELLOWS_ROOT remain unchanged — they derive from the now-correct BELLOWS_ROOT.

**planner.py (line 11):**
```python
# Current:
BELLOWS_ROOT = pathlib.Path(__file__).parent.resolve()

# Replacement:
from bellows_root import resolve_bellows_root
BELLOWS_ROOT = resolve_bellows_root()
```

**verdict.py (line 13):**
```python
# Current:
BELLOWS_ROOT = Path(__file__).parent.resolve()

# Replacement:
from bellows_root import resolve_bellows_root
BELLOWS_ROOT = resolve_bellows_root()
```

VERDICTS_DIR derivation unchanged.

### 3.4 Helper location

Two options:

**(A) New `bellows_root.py` module** — Clean separation. All four files import from it. Avoids circular imports (bellows.py imports runner, which imports bellows — introducing a resolve function in bellows.py itself risks import-time issues). **Recommended.**

**(B) Inline in each file** — No new module. Each file gets its own copy of the helper. Disadvantage: 4x code duplication. Not recommended.

---

## Section 4 — Follow-On Executable Shape

### 4.1 Instances to convert

| Instance | Classification | Action |
|---|---|---|
| runner.py:20 | REACHABLE | Convert (proven worktree-reachable via test suite) |
| bellows.py:23 | LATENT-UNREACHABLE | Convert-proactive (same defect class, low regression risk) |
| planner.py:11 | LATENT-UNREACHABLE | Convert-proactive |
| verdict.py:13 | LATENT-UNREACHABLE | Convert-proactive |

### 4.2 Production changes

1. **Create `bellows_root.py`** (~15 LOC) — the `resolve_bellows_root()` helper function.
2. **Edit `bellows.py`** — replace line 23 with import + helper call.
3. **Edit `runner.py`** — replace line 20 with import + helper call.
4. **Edit `planner.py`** — replace line 11 with import + helper call.
5. **Edit `verdict.py`** — replace line 13 with import + helper call.
6. **Edit `bellows.py:1038`** — `_module_fingerprints()` uses a separate `os.path.dirname(os.path.abspath(__file__))`. Convert to use `BELLOWS_ROOT` for consistency (or leave — it's only called by the daemon from canonical).

### 4.3 Test changes

1. **Existing test fixtures: no updates required.** Tests patch `bellows.BELLOWS_ROOT`, `runner.LOGS_DIR`, `verdict.VERDICTS_DIR` — these module-level variables remain the same names and semantics. The conftest autouse fixture continues to work.

2. **New NEGATIVE test (REQUIRED):** For each converted instance, add a test that:
   - Proves the helper resolves to the canonical root when `__file__` is inside a worktree path.
   - Implementation: mock `__file__` or set up a temporary directory structure mirroring `.bellows-worktrees/<wt>/` with a `config.json` at the grandparent level.

3. **Runner LOGS_DIR hygiene (RECOMMENDED):** Patch `runner.LOGS_DIR` in the 13 unpatched `test_runner.py` functions listed in Section 2.3. This closes the confirmed reachability gap and prevents orphaned log file creation in worktrees. Can be done via a conftest autouse fixture for runner tests:
   ```python
   @pytest.fixture(autouse=True)
   def isolate_runner_logs_dir(monkeypatch, tmp_path):
       import runner
       monkeypatch.setattr(runner, "LOGS_DIR", tmp_path / "logs")
   ```

4. **New helper unit tests:** Test `resolve_bellows_root()` directly:
   - Returns `__file__.parent` when `config.json` exists there (daemon case).
   - Walks up when `config.json` is absent at `__file__.parent` (worktree case).
   - Falls back to `__file__.parent` when no `config.json` found anywhere (CI case).

### 4.4 LOC estimate

| Component | LOC |
|---|---|
| `bellows_root.py` (new helper module) | ~15 |
| Production edits (4 files, 2 lines each) | ~8 |
| Helper unit tests (`test_bellows_root.py`) | ~40 |
| Negative worktree-resolution tests | ~30 |
| Runner LOGS_DIR hygiene (conftest + cleanups) | ~10 |
| **Total** | **~103** |

### 4.5 Pre-flight notes for executable

1. The executable MUST add a test that fails under the old `Path(__file__).parent` and passes under the helper, for each converted instance. The test should simulate a worktree `__file__` path and verify the helper resolves to the canonical root.

2. Verify no circular import: `bellows.py` imports `runner` (line 124), `runner.py` imports from `bellows` (line 12: `from bellows import _log`). The new `bellows_root.py` must NOT import from bellows, runner, planner, or verdict — it must be standalone.

3. The `_module_fingerprints()` function (bellows.py:1038) uses a separate `os.path.dirname(os.path.abspath(__file__))` that is NOT via BELLOWS_ROOT. The executable should convert this to use `str(BELLOWS_ROOT)` for consistency, since BELLOWS_ROOT will now be correct.

4. Run the full test suite from BOTH the canonical checkout AND a worktree to confirm no regressions.

5. Add `bellows_root.py` to the `_module_fingerprints()` module list (bellows.py:1037) so heartbeat logging tracks it.

---

## Section 5 — Edge Cases and Open Questions

### 5.1 Bellows-self mode

When bellows is the target project (bellows as both engine and target), the worktree is created at `<bellows>/.bellows-worktrees/<slug>`. The daemon process still runs from the canonical checkout — all four BELLOWS_ROOT declarations resolve to canonical paths. The `claude -p` agent subprocess runs with `cwd=<worktree>` but does not import bellows Python modules. **No additional worktree-split behavior in bellows-self mode.** The `_create_worktree` detect-and-skip guard (`os.path.exists(os.path.join(project_path, ".git"))`) may fire if bellows lacks a project-local `.git` (BACKLOG entry 2026-05-04: monorepo-worktree fix), but this returns `project_path` as-is, not a worktree — so BELLOWS_ROOT is irrelevant in that path.

### 5.2 Marker file existence in worktree vs. canonical

The `config.json` marker file:
- **Canonical root:** Present (required for `load_config()` at daemon startup). Confirmed gitignored (`.gitignore` line 14).
- **Worktree checkout:** Absent. Git worktrees only contain tracked files; `config.json` is gitignored and not tracked (verified: `git ls-files --cached config.json` returns empty).
- **`.bellows-worktrees/` parent directory:** Absent (it's just a container directory, not a git checkout).

The walk-up from `<worktree>/module.py` → `<worktree>/` (no config.json) → `.bellows-worktrees/` (no config.json) → `<canonical bellows>/` (config.json present) → returns. **Correct behavior confirmed.**

**Edge case: fresh clone without config.json.** If `config.json` doesn't exist at the canonical root (e.g., CI environment, first-time setup before daemon configuration), the helper walks to filesystem root and falls back to `Path(__file__).parent`. In a non-worktree context, this is correct. In a worktree context, this gives the worktree root (wrong). Mitigation: the fallback matches current behavior (the code already has this bug in worktree context), and CI environments don't typically create worktrees.

### 5.3 Module-import-time capture

All four BELLOWS_ROOT declarations are at module scope (not inside functions):

| Module | Module-level captures |
|---|---|
| bellows.py | `BELLOWS_ROOT`, `DB_PATH`, `SHADOW_CACHE_DIR` |
| planner.py | `BELLOWS_ROOT` |
| runner.py | `BELLOWS_ROOT`, `LOGS_DIR` |
| verdict.py | `BELLOWS_ROOT`, `VERDICTS_DIR` |

This means the path is **frozen at first import**. If `__file__` resolves wrong at import time, the wrong path persists for the entire process lifetime. The helper adoption fixes this because `resolve_bellows_root()` executes the walk-up at import time and resolves to the correct canonical root regardless of `__file__` location.

**No instance reads a canonical-only resource at import time** (no file I/O at module level). The path values are captured but not dereferenced until functions are called. This is relevant because it means import-time failures (FileNotFoundError) are not a risk — only function-call-time reads could hit wrong paths.

### 5.4 Additional `__file__` reference

`bellows.py:1038` in `_module_fingerprints()` uses `os.path.dirname(os.path.abspath(__file__))` independently of BELLOWS_ROOT. This is a 5th `__file__` usage that should be converted to `str(BELLOWS_ROOT)` for consistency once BELLOWS_ROOT is correct. It's in the same latent-unreachable class (only called by daemon from canonical), but converting it to use the already-correct BELLOWS_ROOT is zero-risk cleanup.

### 5.5 `_source_sha()` git context

`bellows.py:1020` passes `cwd=str(BELLOWS_ROOT)` to `git log`. If BELLOWS_ROOT pointed to a worktree, `git log` would still work (worktrees share the same git database), but the path `--` filter `"bellows.py"` would match the worktree's copy. In practice this is fine (same file content), but the helper conversion makes it unambiguously correct.

### 5.6 Test-suite isolation gap (runner.py)

The 13 unpatched LOGS_DIR writes in `test_runner.py` (Section 2.3) are the only confirmed instance of worktree-reachable filesystem I/O. While low-severity (orphaned log files, no test failures), this represents a hygiene gap that the executable should close with a conftest autouse fixture for `runner.LOGS_DIR`, mirroring the existing `isolate_verdicts_dir` pattern.

### 5.7 Circular import risk

The current import graph includes `bellows.py` → `runner.py` (line 124) and `runner.py` → `bellows.py` (line 12: `from bellows import _log`). The new `bellows_root.py` module MUST be import-free (no bellows-internal imports) to avoid introducing a circular dependency. The helper function should use only `pathlib.Path` and optionally `logging`.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA)
**Status:** Complete

### What Was Done
Produced a comprehensive worktree-reachability audit for the four latent `BELLOWS_ROOT = Path(__file__).parent` instances across bellows.py, planner.py, runner.py, and verdict.py. Evaluated three reachability vectors (daemon, test suite, agent execution) for each instance with code-path citations. Provided a conversion spec with helper design, per-file diff shape, and test surface.

### Files Deposited
- `bellows/knowledge/research/bellows-root-worktree-reachability-audit-2026-06-08.md` — full audit (Sections 1-5)

### Files Created or Modified (Code)
- None (diagnostic — ships no code)

### Decisions Made
- Classified runner.py as REACHABLE (13 unpatched test writes to LOGS_DIR from worktree context)
- Classified bellows.py, planner.py, verdict.py as LATENT-UNREACHABLE
- Recommended convert-proactive for all four instances (BACKLOG mandate: "before a third surfaces")
- Recommended `config.json` as marker file for `resolve_bellows_root()` helper, with fallback
- Recommended new `bellows_root.py` module to avoid circular imports

### Flags for CEO
- None

### Flags for Next Step
- The executable should convert all four instances, not just runner.py — proactive conversion is justified by the three-instance pattern and low regression risk
- The runner.py LOGS_DIR test hygiene gap (Section 2.3) should be closed in the same executable
- Verify circular import safety: `bellows_root.py` must not import from any bellows module
