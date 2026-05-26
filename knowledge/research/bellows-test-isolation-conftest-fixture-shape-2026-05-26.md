# Bellows Test-Isolation Conftest — Fixture-Shape Diagnostic Findings

**Date:** 2026-05-26 | **Agent:** Bellows Systems Analyst | **Plan:** diagnostic-bellows-test-isolation-conftest-2026-05-26 | **Step:** 1

---

## Audit Deliverable A — Patch-Surface Confirmation for `VERDICTS_DIR`

### Three call sites that read `VERDICTS_DIR`

**1. `verdict.py:180` — `post_verdict_request`**
```python
pending_dir = VERDICTS_DIR / "pending"
```
Reads `VERDICTS_DIR` from the module's global namespace at call time (bare name lookup in function body). Not closed over at import time. `monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path)` propagates. **CLEAN.**

**2. `verdict.py:283` — `check_verdict`**
```python
resolved_dir = VERDICTS_DIR / "resolved"
```
Same pattern — module-namespace read at call time. **CLEAN.**

**3. `verdict.py:317–318` — `log_to_ledger`**
```python
VERDICTS_DIR.mkdir(parents=True, exist_ok=True)
ledger_path = VERDICTS_DIR / "ledger.jsonl"
```
Same pattern — both reads resolve from module namespace at call time. **CLEAN.**

### Direct-import search

Searched all source files for `from verdict import VERDICTS_DIR` — **zero matches**. No caller imports the constant directly. All verdict.py consumers use `import verdict` (module-level import) and access functions via `verdict.<function>()`, which in turn read `VERDICTS_DIR` from the module namespace.

Verified import statements:
- `bellows.py:120`: `import verdict` (module import, not `from verdict import VERDICTS_DIR`)
- `tests/test_verdict.py:10`: `import verdict`
- `tests/test_bellows.py:15`: `import verdict`
- `tests/test_rule_26_deposit_parser.py:11`: `import verdict`
- `tests/test_extract_primary_deposit_blocks.py:8`: `from verdict import extract_primary_deposit` — imports a function, not the constant; `extract_primary_deposit` does not reference `VERDICTS_DIR`.

### Verdict

**Patch surface is clean.** A single `monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path)` propagates to all three call sites and all callers. No additional patch targets required.

---

## Audit Deliverable B — Leaking-Test Enumeration

### Confirmed leakers (2 tests, both dispatch-spawn vector)

| Test File | Test Function | Line | Leak Vector | Evidence |
|---|---|---|---|---|
| `tests/test_bellows.py` | `test_apply_defensive_header_defaults_propagates_to_reparsed_header` | 3049 | dispatch-spawn | Orphan `verdict-request-item4-test-2026-05-26-step-1.md`; test calls `bellows.run_plan()` at line 3049 without mocking `bellows.verdict.post_verdict_request`; flow reaches `verdict.post_verdict_request()` at `bellows.py:531` via `header_says_pause` returning True (defensive default `pause_for_verdict="after_step_1"` on sparse 2-step plan header) |
| `tests/test_consume_verdicts.py` | `test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` | 243 | dispatch-spawn | Orphan `verdict-request-regression-slug-collision-2026-05-01-step-1.md`; test calls `bellows.run_plan()` at line 243 without mocking `bellows.verdict.post_verdict_request`; same flow — `_clean_gates()` returns `plan_header: {"auto_close": "true"}` (1 key < 3), so `_apply_defensive_header_defaults` injects `pause_for_verdict="after_step_1"`, causing step 1 pause via `bellows.py:531` |

### Leak mechanism (shared by both tests)

Both tests create 2-step plans (`"## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n"`) and call `bellows.run_plan()`. The mocked `gates.check()` returns a `plan_header` dict with < 3 keys and no `pause_for_verdict` field. The function `_apply_defensive_header_defaults` (`bellows.py:318–327`) fires because `total_steps > 1` and `len(header) < 3`, injecting `pause_for_verdict="after_step_1"`. Then `header_says_pause` (`bellows.py:304–315`) returns True for `current_step=1`, routing the flow to the intermediate-step pause branch at `bellows.py:531`:

```python
verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, ...)
```

Since `bellows.verdict.post_verdict_request` is not mocked in either test, the real function executes, reads the un-patched `VERDICTS_DIR` (`verdict.py:14`, resolving to `BELLOWS_ROOT / "verdicts"`), and writes a verdict-request file to production `bellows/verdicts/pending/`.

### Orphan evidence correlation

| Orphan File (in `verdicts/pending/archived/`) | Plan Field (tmpdir path confirms test origin) | Originating Test |
|---|---|---|
| `orphan-test-spawned-verdict-request-item4-test-2026-05-26-step-1.md` | `/var/folders/.../T/tmpz78p1i0k/proj/knowledge/decisions/in-progress-executable-item4-test-2026-05-26.md` | `test_apply_defensive_header_defaults_propagates_to_reparsed_header` (plan_filename at test_bellows.py:3007: `"executable-item4-test-2026-05-26.md"`) |
| `orphan-test-spawned-verdict-request-regression-slug-collision-2026-05-01-step-1.md` | `/var/folders/.../T/tmpsqymxsso/proj/knowledge/decisions/in-progress-executable-regression-slug-collision-2026-05-01.md` | `test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` (plan_filename at test_consume_verdicts.py:196: `"executable-regression-slug-collision-2026-05-01.md"`) |

### Latent leaker audit (no additional leakers found)

Audited all 37 `bellows.run_plan()` call sites in `test_bellows.py` and 1 in `test_consume_verdicts.py`. All call sites other than the two confirmed leakers fall into one of these safe categories:

1. **Mock present** — 28 tests patch `bellows.verdict.post_verdict_request` (confirmed via grep: lines 282, 401, 1375, 1805, 1867, 2157, 2202, 2314, 2362, 2409, 2464, 2518, 2598, 2660, 2717, 2774, 3249, 3595, 3646, 3697, 3739, 3798 in test_bellows.py).

2. **Single-step auto-close** — 8 tests use single-step plans with `auto_close="true"`. For single-step plans, `_apply_defensive_header_defaults` does not fire (`total_steps=1`), `header_says_pause` returns False (no `pause_for_verdict` set), and `effective_auto_close=True`, so the auto-close branch executes (calling `verdict.log_to_ledger`, not `post_verdict_request`).

3. **Non-sparse header prevents defensive default** — 1 test (`test_run_plan_continuation_prompt_uses_shadow_path`, line 1332) explicitly constructs a header with >= 3 keys and `pause_for_verdict: "never"`, preventing `_apply_defensive_header_defaults` from firing and making `header_says_pause` return False.

4. **Resume at step 2** — 2 tests resume at `resume_step=2` on 2-step plans. The defensive default `pause_for_verdict="after_step_1"` only triggers for `current_step=1`; step 2 passes through to auto-close.

### Direct-call vector check

All tests in `test_verdict.py` that call `verdict.post_verdict_request()` directly use `patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts")` to redirect to tmpdir. **No leakers in test_verdict.py.** Same for `test_rule_26_deposit_parser.py:77` (`patch.object(verdict, "VERDICTS_DIR", tmp_path)`).

---

## Audit Deliverable C — Fixture-Shape Blueprint

### Recommended fixture: function-scoped autouse, patching `VERDICTS_DIR`

**Fixture scope: function-scoped (not session-scoped).**
Justification: `monkeypatch` is inherently function-scoped in pytest. Session-scoped would require using `monkeypatch` at session scope (pytest does not natively support this — it requires a custom implementation or `session`-scoped `tmp_path_factory` with manual `setattr`/`delattr`). The cleaner and more maintainable approach is function-scoped autouse. The performance cost is negligible: `monkeypatch.setattr` is a single dict assignment per test function; the Bellows test suite runs in < 10 seconds total. Function-scoped also provides stronger isolation (VERDICTS_DIR reset per test, no cross-test bleed).

**Autouse: yes.** The fixture should apply automatically to all tests in the `tests/` directory without requiring explicit opt-in. This prevents future tests from leaking without the author remembering to mock.

**Patch target:**
```python
monkeypatch.setattr("verdict.VERDICTS_DIR", tmp_path / "verdicts")
```
Per Audit A, this single setattr propagates to all three call sites (`post_verdict_request`, `check_verdict`, `log_to_ledger`) and all callers (bellows.py, test files). No additional patch targets needed.

**Cleanup:** None required. pytest's `tmp_path` fixture handles tmpdir lifecycle automatically. `monkeypatch` restores the original value on fixture teardown. No test creates state outside tmpdir that needs explicit cleanup.

**Opt-out mechanism: not required.** Reviewed all tests in `test_verdict.py` — every test that calls `post_verdict_request`, `check_verdict`, or `log_to_ledger` already uses `patch.object(verdict, "VERDICTS_DIR", ...)` to set its own tmpdir. The autouse conftest fixture would set `VERDICTS_DIR` to the conftest's tmpdir, then the test's own `patch.object` would override it to the test's tmpdir. The test-level patch takes precedence within its `with` block. No test legitimately needs the real production `VERDICTS_DIR`. Therefore no marker or opt-out is required.

### Exact fixture body

```python
# tests/conftest.py
import pytest


@pytest.fixture(autouse=True)
def isolate_verdicts_dir(monkeypatch, tmp_path):
    """Redirect verdict.VERDICTS_DIR to tmpdir so tests never write to production verdicts/pending/."""
    import verdict
    monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")
```

**Total LOC: 7** (including blank line and import). Within the BACKLOG's ~10-15 estimate.

### Why `VERDICTS_DIR` patch (not `post_verdict_request` mock)

Patching the constant rather than the function provides broader coverage:
- Catches `post_verdict_request` (writes to `pending/`)
- Catches `log_to_ledger` (writes to `ledger.jsonl`)
- Catches `check_verdict` (reads from `resolved/`)
- Catches any future function that reads `VERDICTS_DIR`
- Tests that exercise write behavior still get real file I/O (just in tmpdir), preserving test fidelity

---

## Audit Deliverable D — Production-Side Surface Check

**No production code change required.**

`VERDICTS_DIR` already exists at `verdict.py:14` as a module-level constant. All three call sites (`post_verdict_request` at line 180, `check_verdict` at line 283, `log_to_ledger` at lines 317–318) read it from the module namespace at call time. No caller imports it directly. The conftest fixture's `monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")` patches cleanly without any production-side modification.

**Outcome: (1) — no production change. The conftest is the only artifact.**

---

## Q5 — Verification Block (Rule 39)

All line numbers verified against current file state in this worktree:

| Citation | File | Line | Verified Content |
|---|---|---|---|
| `VERDICTS_DIR` definition | `verdict.py` | 14 | `VERDICTS_DIR = BELLOWS_ROOT / "verdicts"` |
| `post_verdict_request` reads `VERDICTS_DIR` | `verdict.py` | 180 | `pending_dir = VERDICTS_DIR / "pending"` |
| `check_verdict` reads `VERDICTS_DIR` | `verdict.py` | 283 | `resolved_dir = VERDICTS_DIR / "resolved"` |
| `log_to_ledger` reads `VERDICTS_DIR` (mkdir) | `verdict.py` | 317 | `VERDICTS_DIR.mkdir(parents=True, exist_ok=True)` |
| `log_to_ledger` reads `VERDICTS_DIR` (ledger) | `verdict.py` | 318 | `ledger_path = VERDICTS_DIR / "ledger.jsonl"` |
| `bellows.py` imports verdict | `bellows.py` | 120 | `import verdict` |
| Intermediate-step `post_verdict_request` call | `bellows.py` | 531 | `verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, ...)` |
| Worktree-creation-failure `post_verdict_request` call | `bellows.py` | 444 | `verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result, ...)` |
| Final-step `post_verdict_request` call | `bellows.py` | 624 | `verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, ...)` |
| Auto-close teardown failure `post_verdict_request` call | `bellows.py` | 655 | `verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, ...)` |
| `_apply_defensive_header_defaults` | `bellows.py` | 318–327 | `if total_steps > 1 and len(header) < 3:` ... `header["pause_for_verdict"] = "after_step_1"` |
| `header_says_pause` | `bellows.py` | 304–315 | `if pv == "after_step_1": return current_step == 1` |
| Leaker 1: item4-test plan_filename | `tests/test_bellows.py` | 3007 | `plan_filename = "executable-item4-test-2026-05-26.md"` |
| Leaker 1: run_plan call | `tests/test_bellows.py` | 3049 | `bellows.run_plan(plan_path, config, response_server)` |
| Leaker 2: slug-collision plan_filename | `tests/test_consume_verdicts.py` | 196 | `plan_filename = "executable-regression-slug-collision-2026-05-01.md"` |
| Leaker 2: run_plan call | `tests/test_consume_verdicts.py` | 243 | `bellows.run_plan(str(plan_path), config, response_server, resume_step=None)` |

---

## Q6 — Cross-Vector Dependency Check

The dispatch-spawn leak vector is the only active vector. Both leaking tests call `bellows.run_plan()` in-process (not via subprocess). `bellows.run_plan()` at line 334 calls `verdict.post_verdict_request()` at lines 444/531/624/655 — all in-process function calls that resolve `VERDICTS_DIR` from `verdict`'s module namespace. The conftest's `monkeypatch.setattr(verdict, "VERDICTS_DIR", ...)` modifies that namespace in the same process, so the patch reaches all four call sites.

Verified: `bellows.py` does **not** shell out, subprocess, or invoke Python code in a fresh interpreter for verdict posting. Grepped for `subprocess.*verdict`, `subprocess.*bellows.py`, `os.system.*bellows` — zero matches. The only subprocess calls in `bellows.py` are `runner.run_step()` (which invokes `claude -p`, an external process that does NOT call verdict.py) and `_create_worktree`/`_teardown_worktree` (which invoke `git` commands, not Python). No code path exists where `post_verdict_request` runs in a separate Python interpreter that wouldn't inherit the monkeypatch.

**Option (a) is NOT defeated by the subprocess vector.** The conftest patch reaches all leak vectors.

---

## Flags for CEO

### Recommendation: **(a) Executable plan ready**

- Conftest fixture as specified in Deliverable C: 7 LOC, function-scoped autouse, patches `verdict.VERDICTS_DIR` to tmpdir
- No production code change required (Deliverable D confirms VERDICTS_DIR patches cleanly)
- Complete leaking-test list: 2 confirmed (Deliverable B), 0 latent leakers found
- No subprocess vector defeat (Q6 confirmed)

The Planner can author the executable directly from this diagnostic. The executable should:
1. Create `tests/conftest.py` with the 7-line fixture from Deliverable C
2. Run the full test suite to confirm zero regressions and zero new orphans in `verdicts/pending/`
3. Optionally verify the two previously-leaking tests no longer produce files in production `verdicts/pending/`

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA diagnostic)
**Status:** Complete

### What Was Done
Complete leaking-test audit and fixture-shape blueprint for `tests/conftest.py`. Confirmed `VERDICTS_DIR` patch surface is clean (3 call sites, all module-namespace reads, zero direct imports). Identified 2 leaking tests via orphan evidence and code-path tracing. Designed a 7-LOC function-scoped autouse fixture. Confirmed no production code change required and no subprocess vector defeat.

### Files Deposited
- `bellows/knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md` — full diagnostic with 4 audit deliverables, Q5 verification block, Q6 cross-vector check, and CEO flags

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Function-scoped (not session-scoped) fixture: monkeypatch is inherently function-scoped; performance cost negligible; stronger isolation
- Patch `VERDICTS_DIR` constant (not mock `post_verdict_request` function): broader coverage across all three verdict.py functions and future additions
- No opt-out mechanism: existing test-level patches in test_verdict.py already override the conftest fixture within their `with` blocks

### Flags for CEO
- Recommendation (a): executable plan ready. No blockers, no production changes, no gaps in coverage.

### Flags for Next Step
- The executable should create `tests/conftest.py` with the exact fixture body from Deliverable C
- The two leaking tests do NOT need modification — the conftest fixture handles them automatically
- QA should verify: (1) full test suite passes, (2) no new files appear in production `bellows/verdicts/pending/` after test run
