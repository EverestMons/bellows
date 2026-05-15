# QA Report: deposit_exists Worktree-Aware Path Resolution Fix

**Date:** 2026-05-06
**Plan:** executable-deposit-exists-worktree-aware-2026-05-06
**Agent:** Bellows QA
**Step:** 2

---

## Verification Table

| # | Test | Status | Evidence | Summary |
|---|---|---|---|---|
| 2.1 | `test_resolve_deposit_path_finds_file_in_worktree` | ✅ PASS | `targeted-tests.txt` | Form B path resolves via worktree Strategy 0 when file exists only in wt_path |
| 2.2 | `test_resolve_deposit_path_finds_file_in_worktree_form_a` | ✅ PASS | `targeted-tests.txt` | Form A path (with project basename prefix) strips prefix and resolves in wt_path |
| 2.3 | `test_resolve_deposit_path_bellows_self_no_wt_path_drift` | ✅ PASS | `targeted-tests.txt` | Strategy 0 guard skips when wt_path == project_path; falls through to S2 |
| 2.4 | `test_resolve_deposit_path_no_wt_path_backward_compat` | ✅ PASS | `targeted-tests.txt` | No wt_path parameter (default None) preserves existing behavior |
| 2.5 | `test_gate_deposit_exists_threads_wt_path` | ✅ PASS | `targeted-tests.txt` | Gate passes when deposit exists only in wt_path and wt_path is threaded through |
| 2.6 | `test_gate_deposit_exists_fails_when_file_truly_missing` | ✅ PASS | `targeted-tests.txt` | Gate correctly fails when deposit missing from both wt_path and project_path |
| — | Full-suite regression check | ✅ PASS | `full-suite.txt` | 217 passed, 1 failed (pre-existing test_run_step_timeout); 0 regressions |

---

## Tests-Before / Tests-After

| Metric | Before (Step 1 dev log) | After (Step 2) |
|---|---|---|
| Collected | 212 | 218 |
| Passed | 211 | 217 |
| Failed | 1 (pre-existing: test_run_step_timeout) | 1 (same pre-existing) |
| New tests added | — | 6 |
| Regressions | — | 0 |

---

## Evidence Files

All evidence stored in `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/`:

| File | Contents |
|---|---|
| `targeted-tests.txt` | pytest output for test_gates.py + test_bellows.py (132 passed) |
| `full-suite.txt` | Full suite output (217 passed, 1 failed pre-existing) |
| `gates-diff.txt` | git diff showing wt_path threading in gates.py |
| `bellows-diff.txt` | git diff showing wt_path call-site updates in bellows.py |
| `wt-path-grep.txt` | grep confirming all wt_path occurrences across both files |
| `commit.txt` | Step 1 commit hash and message |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/
Files verified: 6
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Added 6 unit tests covering worktree-aware deposit path resolution (Form A, Form B, bellows-self compatibility, backward compatibility, gate threading, and negative case). Ran targeted and full test suites confirming all tests pass with 0 regressions. Collected 6 evidence files.

### Files Deposited
- `bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/` — 6 evidence files

### Files Created or Modified (Code)
- `bellows/tests/test_gates.py` — added 6 new tests (tests 2.1–2.6)

### Decisions Made
- Used `tmp_path` pytest fixture for all test isolation (no mocking needed for filesystem tests)
- Tested both `_resolve_deposit_path` (unit) and `_gate_deposit_exists` (integration) levels

### Flags for CEO
- None

### Flags for Next Step
- None
