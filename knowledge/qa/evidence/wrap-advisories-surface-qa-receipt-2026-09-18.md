# QA Receipt — wrap-advisories-surface-2026-09-18

**Plan:** 100129 — thread 427
**Step:** 2 (QA)
**Date:** 2026-09-19

## Verification

| # | Item | Status | Reading |
|---|------|--------|---------|
| 1 | Prior-step deposits and commits | ✅ | Three commits by [100129]: red efc2fb9d, green 8b442718, auto-stage b2eb6b2b; consecutive and in red-first order; A0 from dev-log: 2537 passed, 0 failed, 2 with-marks |
| 2 | Deliverable shape | ✅ | Diff touches 7 files, not wrap_check.py; each hook's existing import line count 1; 12 test functions; 21 mutants; dev-log carries 6 contents; tests diff empty |
| 3 | Full suite | ✅ | 2549 passed, 0 failed, 2 with-marks; delta from A0 (2537 passed) is exactly 12 new tests |
| 4 | Twelve nodes alone | ✅ | All 12 pass alone; node outputs for 3, 4, 6, 7, 8, 10 and 12 pasted below |
| 5 | Live run | ✅ | Both checkers and both hooks exit 0; two non-OK lines in each hook's output (fenced block below); OK lines absent from both outputs; stop key set is `{systemMessage}`, sentinel count 0; log: `SessionStart\tclean sid=qa-live-run` and `Stop\tarmed-pass-disarm sid=qa-live-run` |
| 6 | Mutation run | ✅ | 21 killed, 0 survived, 0 error; LIVE-TREE UNCHANGED for all three hook files |

---

### Item 4 — node outputs for 3, 4, 6, 7, 8, 10 and 12

**Node 3: test_debt_hook_clean_pass_emits_nothing**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_debt_hook_clean_pass_emits_nothing PASSED [100%]

============================== 1 passed in 0.16s ===============================
```

**Node 4: test_debt_hook_debt_path_unchanged**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_debt_hook_debt_path_unchanged PASSED [100%]

============================== 1 passed in 0.16s ===============================
```

**Node 6: test_stop_hook_armed_clean_pass_unchanged**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_stop_hook_armed_clean_pass_unchanged PASSED [100%]

============================== 1 passed in 0.16s ===============================
```

**Node 7: test_stop_hook_block_path_unchanged**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_stop_hook_block_path_unchanged PASSED [100%]

============================== 1 passed in 0.16s ===============================
```

**Node 8: test_stop_hook_unarmed_never_runs_checker**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_stop_hook_unarmed_never_runs_checker PASSED [100%]

============================== 1 passed in 0.18s ===============================
```

**Node 10: test_hooks_surface_under_harness_interpreter**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_hooks_surface_under_harness_interpreter PASSED [100%]

============================== 1 passed in 0.38s ===============================
```

**Node 12: test_hooks_load_beside_a_stale_common**

```
============================= test session starts ==============================
platform darwin -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0 -- /Users/marklehn/Developer/bellows/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_wrap_advisory_surface.py::test_hooks_load_beside_a_stale_common PASSED [100%]

============================== 1 passed in 0.11s ===============================
```

---

### Item 5 — live run surfaced lines

Non-OK lines from each checker run (identical on both debt and stop runs), and each hook's corresponding output — pasted side by side:

```
=== debt hook additionalContext ===
[4/memory] WARN (advisory): 1 entr(ies) not referenced from MEMORY.md or any section file: planted-orphan.md
[2r/receipts] SKIPPED — lifecycle.db not readable for clearance cross-check.

=== stop hook systemMessage ===
[4/memory] WARN (advisory): 1 entr(ies) not referenced from MEMORY.md or any section file: planted-orphan.md
[2r/receipts] SKIPPED — lifecycle.db not readable for clearance cross-check.
```

OK lines present in each checker run and absent from both hook outputs:

```
[2r/receipts] OK — no deposits in this session (session qa-live-run).
wrap_check: OK — all four repos wrapped.
```

---

### Item 6 — mutation run file (pasted whole)

```
PYTHON: /Users/marklehn/Developer/bellows/.venv/bin/python
HEAD: 8b442718cd377b6e7010dd31bd9a7d5640482f81
TARGET: hooks/eluvian/_common.py sha256=5d8303e1a5e6
TARGET: hooks/eluvian/wrap_debt_hook.py sha256=a68dd7ba19df
TARGET: hooks/eluvian/wrap_stop_hook.py sha256=d1a7f7e20b50

MUTANT debt-pass-discards: KILLED — suite caught the defect
MUTANT advisory-pass-logs-twice: KILLED — suite caught the defect
MUTANT stderr-selected: KILLED — suite caught the defect
MUTANT debt-pass-branch-raises: KILLED — suite caught the defect
MUTANT debt-path-composed-as-advisory: KILLED — suite caught the defect
MUTANT new-names-imported-by-name: KILLED — suite caught the defect
MUTANT stop-pass-discards: KILLED — suite caught the defect
MUTANT stop-message-blocks: KILLED — suite caught the defect
MUTANT stop-message-as-context: KILLED — suite caught the defect
MUTANT unarmed-runs-checker: KILLED — suite caught the defect
MUTANT no-disarm-on-advisory-pass: KILLED — suite caught the defect
MUTANT advisory-pass-drops-disarm-record: KILLED — suite caught the defect
MUTANT allowlist-by-spelling: KILLED — suite caught the defect
MUTANT ok-prefix-too-broad: KILLED — suite caught the defect
MUTANT ok-prefix-too-narrow: KILLED — suite caught the defect
MUTANT crash-header-asserts-clean: KILLED — suite caught the defect
MUTANT header-asserts-nothing-owed: KILLED — suite caught the defect
MUTANT crash-header-directs-wrap: KILLED — suite caught the defect
MUTANT crash-branch-needs-3.10: KILLED — suite caught the defect
MUTANT crash-message-carries-both-headers: KILLED — suite caught the defect
MUTANT skipped-read-as-ok: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: hooks/eluvian/_common.py sha256=5d8303e1a5e6
LIVE-TREE UNCHANGED: hooks/eluvian/wrap_debt_hook.py sha256=a68dd7ba19df
LIVE-TREE UNCHANGED: hooks/eluvian/wrap_stop_hook.py sha256=d1a7f7e20b50

MUTATION: 21 killed, 0 survived, 0 error
```


---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100129/knowledge/qa/evidence/
Files verified: 3
