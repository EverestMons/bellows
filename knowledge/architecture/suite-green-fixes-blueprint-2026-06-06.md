# Suite-Green Fixes — Edit Map (Blueprint)
**Date:** 2026-06-06 | **Author:** Bellows Systems Analyst | **Step:** 1

---

## §1 — `resolve_governance_root()` helper in `decisions.py`

### Function spec

Add `resolve_governance_root()` between the `logger` definition (line 8) and the current `GOVERNANCE_ROOT` assignment (line 11). The function walks up from `Path(__file__).resolve().parent` through parent directories until it finds one containing `COMPANY.md`, then returns that path.

```python
def resolve_governance_root() -> Path:
    """Walk up from this file to the nearest ancestor containing COMPANY.md (governance root)."""
    current = Path(__file__).resolve().parent
    while True:
        if (current / "COMPANY.md").exists():
            return current
        parent = current.parent
        if parent == current:
            # Filesystem root reached — fall back to legacy two-parent assumption
            logger.warning("decisions: COMPANY.md marker not found; falling back to __file__.parent.parent")
            return Path(__file__).resolve().parent.parent
        current = parent
```

**Fallback:** If the walk reaches filesystem root without finding the marker, log a warning and fall back to the legacy `parent.parent` behavior. This ensures no silent breakage if the marker is ever removed.

### Rewrites to existing lines

| Line | Current | New |
|------|---------|-----|
| 11 | `GOVERNANCE_ROOT = Path(__file__).parent.parent.resolve()` | `GOVERNANCE_ROOT = resolve_governance_root()` |
| 12 | `PHRASES_FILE = GOVERNANCE_ROOT / "INTERMEDIATE_DECISION_PHRASES.md"` | *(unchanged — already correct)* |

### Verification: `PHRASES_FILE` is the sole consumer

`grep GOVERNANCE_ROOT decisions.py` returns only lines 11 and 12. No other code in `decisions.py` uses `GOVERNANCE_ROOT`. (`planner.py` hardcodes its own `GOVERNANCE_ROOT` as a string literal — unaffected, out of scope.)

### Verification: walk-up reaches governance root from both paths

Sandbox-verified parent chain:

**From worktree** (`bellows/.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/decisions.py`):
```
.bellows-worktrees/bellows-suite-green-fixes-2026-06-06/ → COMPANY.md: ✗
.bellows-worktrees/                                      → COMPANY.md: ✗
bellows/                                                 → COMPANY.md: ✗
GitHub/                                                  → COMPANY.md: ✓  ← governance root
```

**From canonical** (`bellows/decisions.py`):
```
bellows/  → COMPANY.md: ✗
GitHub/   → COMPANY.md: ✓  ← governance root
```

Both paths resolve to `/Users/marklehn/Developer/GitHub/` — the directory containing `COMPANY.md` and `INTERMEDIATE_DECISION_PHRASES.md`.

### Marker choice: `COMPANY.md` is correct

- `COMPANY.md` exists at the governance root (`GitHub/`) — confirmed.
- `COMPANY.md` does NOT exist inside `bellows/` or any worktree — confirmed.
- `PLANNER_TEMPLATE.md` does not exist at all on disk — rejected as marker.
- `COMPANY.md` is the canonical Eluvian governance marker referenced in agent specs (e.g., `BELLOWS_SYSTEMS_ANALYST.md` line 8: "Handbook Reference: COMPANY.md v2.4").

### Out-of-scope siblings

`runner.py:20` has `BELLOWS_ROOT = Path(__file__).parent.resolve()` — this resolves to the bellows checkout dir (correct for worktrees since it seeks `logs/` within the checkout). Three other `__file__`-relative siblings exist per the plan context. These are filed in BACKLOG for a separate audited follow-up, not touched here.

---

## §2 — Timeout-test rewrite in `tests/test_runner_parser.py`

### Current test (lines 54–59) — stale

```python
def test_run_step_timeout():
    with patch("runner.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 300)):
        result = runner.run_step("test prompt", "/tmp", "claude-sonnet-4-6")
    assert result["is_error"] is True
    assert result["escalate"] is True
    assert result["stop_reason"] == "timeout"
```

**Why it fails:** `run_step` uses `subprocess.Popen` (runner.py:61), not `subprocess.run`. The mock on `subprocess.run` never intercepts. Popen runs `claude` for real (or fails to find it), and the result has `is_error=False` or an unrelated error.

### Rewrite design

**Fake process stub:**

```python
class FakeProcess:
    """Simulates a process that produces no output and never exits on its own."""
    def __init__(self, *args, **kwargs):
        self.stdout = iter([])  # empty iterator — reader thread finishes instantly
        self.stderr = iter([])
    def poll(self):
        return None  # process appears to still be running
    def kill(self):
        pass  # accept the kill silently
```

**Behavior chain:**
1. `runner.subprocess.Popen` is patched to return `FakeProcess()`.
2. Reader threads start iterating `proc.stdout`/`proc.stderr` — both are `iter([])`, so they drain instantly and the threads end.
3. Main loop: `proc.poll()` returns `None` → loop body executes.
4. `time.sleep(1)` is patched to a no-op → no real wait.
5. `now = time.monotonic()` vs `last_output_time` (set at loop entry) — positive delta (microseconds).
6. With `timeout=0`, condition `age >= 0` is always True → inactivity timeout fires (runner.py:126–128).
7. `proc.kill()` is called, `timed_out = True`, loop breaks.
8. Result is built at runner.py:159–170 with `is_error=True`, `stop_reason="timeout"`, `escalate=True`.

**Patching strategy:**
- `patch("runner.subprocess.Popen", return_value=FakeProcess())` — intercepts the real Popen call.
- `patch("runner.time.sleep")` — skips the 1-second sleep in the polling loop, making the test instantaneous.
- `timeout=0` passed to `run_step` — ensures the inactivity condition fires on the first poll iteration.

**Assertions:**
```python
assert result["is_error"] is True
assert result["stop_reason"] == "timeout"
assert result["escalate"] is True
```

**Confirmed:** The test does NOT launch `claude`. The inactivity path (runner.py:126–128) is the one exercised. The result dict is built at runner.py:159–170.

---

## §3 — Scope confirmation

### Files requiring edits

| File | Change |
|------|--------|
| `decisions.py` | Add `resolve_governance_root()`, rewrite line 11 |
| `tests/test_runner_parser.py` | Rewrite `test_run_step_timeout` (lines 54–59) |

### Files requiring NO edits

- `tests/test_decisions.py` — its 4 failing tests (`test_loads_phrases_from_file`, `test_includes_known_phrases`, `test_splits_slash_alternatives`, `test_s_class_blocks_from_ground_truth`) all pass once `GOVERNANCE_ROOT` resolves correctly. They assert real phrase data from `INTERMEDIATE_DECISION_PHRASES.md`, which is found once the walk-up works.
- `runner.py` — production code is correct; only the test was stale.
- `planner.py` — hardcodes its own `GOVERNANCE_ROOT`; unaffected.

### Expected post-fix suite count

**448 passed, 0 failed** (currently: 443 passed, 5 failed).

### OPEN items

None — all questions resolved.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a precise edit map covering two fixes: (1) a `resolve_governance_root()` helper in `decisions.py` that walks up to the `COMPANY.md` marker, replacing the brittle `parent.parent` derivation; (2) a rewrite of `test_run_step_timeout` in `tests/test_runner_parser.py` to mock `subprocess.Popen` and exercise the real inactivity-timeout path. Sandbox-verified the walk-up from both canonical and worktree paths. Confirmed scope: 2 files edited, 0 OPEN items.

### Files Deposited
- `knowledge/architecture/suite-green-fixes-blueprint-2026-06-06.md` — edit map for both fixes

### Files Created or Modified (Code)
- None (SA step — no source changes)

### Decisions Made
- `COMPANY.md` selected as walk-up marker (present at governance root, absent in bellows/worktrees, referenced in agent specs)
- Fallback to legacy `parent.parent` on marker-not-found (with warning log) rather than hard error
- `timeout=0` + patched `time.sleep` chosen to keep the timeout test instantaneous

### Flags for CEO
- None

### Flags for Next Step
- The `FakeProcess` stub's `__init__` must accept `*args, **kwargs` since `Popen` is called with positional and keyword arguments by `run_step`
- `subprocess` is already imported in `test_runner_parser.py` (line 1) — no new import needed; the `subprocess.TimeoutExpired` reference on the old line 55 can be removed
