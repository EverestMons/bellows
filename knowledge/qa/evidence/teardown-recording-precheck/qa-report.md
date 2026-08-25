# QA Report — 523: Teardown Recording + Precheck

**Date:** 2026-08-25
**Plan:** executable-523 (teardown failure recording + dirty-tree precheck + Gap-1c retry + per-plan evidence names)
**Step:** 2 (QA)
**Branch:** bellows-wt/523
**DEV commit:** a5ebc64

## Q1 — Full Suite

```
python3 -m pytest tests/ -q
1385 passed, 1 warning in 43.34s
```

- **Total collected:** 1385
- **New test file (`test_teardown_recording.py`):** 22 tests
- **Inherited baseline:** 1385 - 22 = 1363 (matches X11 pin exactly)
- **Failures:** 0
- **Raw output:** `pytest_full.txt` (this directory)

## Q2 — Change-Shape Check

**Diff stat (HEAD~1):**

| File | Changes |
|---|---|
| bellows.py | +174/-1 |
| lifecycle.py | +21 |
| tests/test_teardown_recording.py | +763 (new) |
| tools/clear_plan.py | +5 |
| **Total** | **962 insertions, 1 deletion** |

**Targeted count greps (bellows.py only, not repo-wide):**

| Check | Expected | Actual | Command |
|---|---|---|---|
| `❌ worktree teardown failed:` | 2 (X1+X2) | 2 | `grep -cF '❌ worktree teardown failed:' bellows.py` |
| `gate_result["passed"] = False` | 5 (3 pre-existing + 2 new) | 5 | `grep -cF 'gate_result["passed"] = False' bellows.py` |
| `record_single_gate_event(` call sites | 3 (X1, X2, X3) | 3 | `grep -cF 'record_single_gate_event(' bellows.py` |

**Structural placement:**

| Check | Result |
|---|---|
| Precheck between lock cleanup (~:1946) and merge comment (~:2059) | Confirmed — precheck block at ~:2039 |
| A8 refusal at TOP of `override_gate()` (line 138), ahead of both arms | Confirmed — `if gate == "worktree_teardown":` at :138, function def at :136 |
| A5 park catch contains `halted-` (lines 773-774) and no `record_park` | Confirmed — `record_park` appears only in the success path at :795 |

## Q3 — Consumer-Sweep Verification

`grep -rn -F "worktree_teardown" tests/` and `grep -rn -F "_teardown_worktree" tests/` — all hits classified:

| Module | Classification | Rationale |
|---|---|---|
| tests/test_teardown_recording.py | **New** (A10) | The 22-test file created by this plan |
| tests/test_consume_verdicts.py | Unaffected | Tests verdict consumption; patches `_teardown_worktree`; no contract change touches these |
| tests/test_bellows.py | Unaffected | Integration tests; all mock `_teardown_worktree`; the new recording calls sit inside the mock boundary |
| tests/test_worktree.py | Unaffected | Unit tests for `_teardown_worktree` itself; precheck is internal to the function; these call it directly with real repos |
| tests/test_verdict.py | Unaffected | Tests verdict-request formatting; uses the failure dict shape which is unchanged |
| tests/test_session_limit_park.py | Unaffected | Parks with `_teardown_worktree` mocked out |
| tests/test_gate_transaction_mechanization.py | Unaffected | Gate transaction tests; `_teardown_worktree` is mocked |

**No unclassified consumers.** All 1385 tests pass, confirming no regressions.

## Q4 — Gap-Table Coverage (G1-G11)

| Gap | Description | Coverage | Status |
|---|---|---|---|
| G1 | While-loop pause catch records ERROR log | A2 implemented; test_pause_path_failure_logs_error (parametrized) | ✅ |
| G2 | While-loop pause catch writes gate_events row | A2 implemented; test_pause_path_failure_writes_gate_event_row | ✅ |
| G3 | While-loop pause catch flips passed to False | A2 implemented; test_pause_path_failure_flips_passed_to_false | ✅ |
| G4 | Final-step pause catch (X2) same three additions | A3 implemented; parametrized in same tests as G1-G3 | ✅ |
| G5 | Auto-close catch (X3) records gate_events row | A4 implemented; record_single_gate_event call at :1300 | ✅ |
| G6 | Park catch (X4) routes to halted- | A5 implemented; test_park_path_failure_routes_to_halted | ✅ |
| G7 | Dirty-tree precheck restored (intersection-based) | A6 implemented; test_precheck_raises_on_intersecting_dirty_file + 5b/5c/7/8b | ✅ |
| G8 | Gap-1c dirty-tree retry reinstated | A7 implemented; test_gap1c_dirty_tree_retry_succeeds + content-conflict + mixed-failure | ✅ |
| G9 | Override refusal for worktree_teardown | A8 implemented; test_override_gate_refuses_worktree_teardown + no_db_write | ✅ |
| G10 | Per-plan evidence directory convention | This QA step's deposit path (`knowledge/qa/evidence/teardown-recording-precheck/`) | ✅ |
| G11 | Test file at pinned path | `tests/test_teardown_recording.py` — 22 tests collected | ✅ |

## Verification Table

| # | Verification Item | Status | Evidence |
|---|---|---|---|
| 1 | Full suite passes (1385 collected, 0 failures) | ✅ | pytest_full.txt |
| 2 | New test file collects 22 tests | ✅ | `--collect-only -q` on test_teardown_recording.py |
| 3 | Inherited baseline matches X11 (1363) | ✅ | 1385 - 22 = 1363 |
| 4 | `❌ worktree teardown failed:` count == 2 | ✅ | `grep -cF` against bellows.py |
| 5 | `gate_result["passed"] = False` count == 5 | ✅ | `grep -cF` against bellows.py |
| 6 | `record_single_gate_event(` count == 3 | ✅ | `grep -cF` against bellows.py |
| 7 | Precheck between lock cleanup and merge | ✅ | bellows.py :2039 between :1946 and :2059 |
| 8 | A8 refusal at top of override_gate, ahead of both arms | ✅ | clear_plan.py :138, function starts :136 |
| 9 | A5 halted- route, no record_park in catch | ✅ | bellows.py :773-774; record_park only at :795 |
| 10 | All consumer hits classified, no unclassified | ✅ | Q3 classification table above |
| 11 | G1-G11 all covered | ✅ | Q4 gap-table above |
| 12 | Per-plan evidence path used | ✅ | Deposited in knowledge/qa/evidence/teardown-recording-precheck/ |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/teardown-recording-precheck/
Files verified: 2
```
