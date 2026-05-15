# QA Report — Daemon Version Observability

**Plan:** `executable-daemon-version-observability-2026-05-11.md`
**Date:** 2026-05-11
**Step:** 2 (BELLOWS_QA)

## Deliverable Verification

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | `bellows.py` contains `def _module_fingerprints` | Function definition at line 770 | ✅ | `evidence/fingerprint_helper.txt` |
| 2 | `bellows.py` contains `MODULE_FINGERPRINT_HEARTBEAT_INTERVAL` constant | Module-level constant at line 19 | ✅ | `evidence/heartbeat_constant.txt` |
| 3 | `bellows.py` references all five modules inside `_module_fingerprints` | `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py` in modules list | ✅ | `evidence/fingerprint_modules.txt` |
| 4 | `bellows.py` calls `_module_fingerprints()` at startup | Called at line 1179 in startup banner block | ✅ | `evidence/startup_call.txt` |
| 5 | `bellows.py` calls `_module_fingerprints()` in heartbeat loop with modulo guard | Called at line 1212, guarded by `heartbeat_counter % MODULE_FINGERPRINT_HEARTBEAT_INTERVAL == 0` at line 1211 | ✅ | `evidence/heartbeat_call.txt` |
| 6 | `tests/test_bellows.py` contains three new tests | `test_module_fingerprints_returns_all_five_modules`, `test_module_fingerprints_handles_git_failure`, `test_module_fingerprints_fallback_to_unknown_on_unexpected_error` | ✅ | `evidence/new_tests.txt` |

## Targeted Test Run

```
104 passed, 0 failed, 1 warning in 0.77s
```

Full output deposited to `evidence/pytest_targeted.txt`.

Zero new failures. Baseline: 101 passed (pre-Step 1 subset), now 104 passed (3 new tests added).

## Behavioral Regression — Fingerprint Helper REPL

All 5 modules returned as keys. All values have `git:` prefix under normal conditions. No `unknown` values.

Transcript: `evidence/fingerprint_repl.txt`

## Behavioral Regression — Git-Failure REPL

With `subprocess.run` patched to raise `FileNotFoundError`, all 5 values fall back to `mtime:` prefix.

Transcript: `evidence/fingerprint_git_failure_repl.txt`

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/daemon-version-observability-2026-05-11/
Files verified: 9
```
