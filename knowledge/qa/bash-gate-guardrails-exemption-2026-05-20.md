# QA Report — Bash Gate GUARDRAILS Exemption

**Date:** 2026-05-20 | **Agent:** Bellows QA | **Plan:** executable-bash-gate-guardrails-exemption-2026-05-20, Step 2

---

## Summary

Verified Step 1's implementation of `GUARDRAILS_BASH_EXEMPTION_PATTERN` in `gates.py`. All deliverables exist on disk with correct content. 93 tests pass in `test_gates.py` (91 pre-existing + 2 new, zero regressions). Full suite: 349 collected, 344 passed, 5 pre-existing failures (unchanged). Behavioral REPL verification confirms exempt denials pass through and non-exempt denials still block.

## Findings by Severity

None. No issues found.

## Testing Coverage

| Function | Tests | Edge Cases |
|---|---|---|
| `_gate_no_permission_denials` (Bash exemption) | `test_no_permission_denials_exempts_guardrails_lock_cleanup` | Full canonical GUARDRAILS command with all 3 lock file patterns + `2>/dev/null` |
| `_gate_no_permission_denials` (negative) | `test_no_permission_denials_still_blocks_other_bash_denials` | Non-matching `rm -rf /tmp/foo` still blocks |
| `_gate_no_permission_denials` (existing) | 8 pre-existing tests | Read-class exemption, string-form denials, missing/None tool_name, mixed read+write, vexp pipeline |

## Deliverable Verification Table

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `gates.py` contains `GUARDRAILS_BASH_EXEMPTION_PATTERN` near `READ_CLASS_TOOLS` | Compiled regex constant at lines 37-48 | OK | grep: `GUARDRAILS_BASH_EXEMPTION_PATTERN` at line 42, immediately after `READ_CLASS_TOOLS` at line 35 |
| `_gate_no_permission_denials` contains Bash exemption filter | `if tool_name == "Bash"` + pattern search at lines 200-203 | OK | grep: `GUARDRAILS_BASH_EXEMPTION_PATTERN.search(cmd)` at line 202 |
| `tests/test_gates.py` contains `test_no_permission_denials_exempts_guardrails_lock_cleanup` | Test function present | OK | grep: function def at line 1146 |
| `tests/test_gates.py` contains `test_no_permission_denials_still_blocks_other_bash_denials` | Test function present | OK | grep: function def at line 1163 |
| `knowledge/development/bash-gate-guardrails-exemption-2026-05-20.md` | Dev log with Output Receipt | OK | File exists, 142 lines, Status: Complete |

## Behavioral Verification Results

### Verification 1: pytest tests/test_gates.py -v

93 passed, 1 warning (urllib3/LibreSSL, pre-existing). Both new tests pass:
- `test_no_permission_denials_exempts_guardrails_lock_cleanup` PASSED
- `test_no_permission_denials_still_blocks_other_bash_denials` PASSED

Zero regressions in 91 pre-existing tests.

Evidence: `pytest_test_gates_v.txt`

### Verification 2: pytest tests/ -v (full suite)

349 collected, 344 passed, 5 failed (all pre-existing):
- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` (pre-existing)
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases` (pre-existing)
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` (pre-existing)
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` (pre-existing)
- `test_runner_parser.py::test_run_step_timeout` (pre-existing, documented in prior QA reports)

Test count delta: +2 (91 -> 93 in test_gates.py). Matches Step 1's claim.

Evidence: `pytest_full_suite.txt`

### Verification 3: REPL — exempt denial

Constructed mock `permission_denials` payload with canonical GUARDRAILS lock-cleanup command:
```
rm -f .git/index.lock .git/"index "*.lock .git/"index "[0-9]* 2>/dev/null
```
Passed through `_gate_no_permission_denials`. Result: `failures` list empty. PASS.

Evidence: `repl_exempt_denial.txt`

### Verification 4: REPL — blocking denial

Constructed mock `permission_denials` payload with non-exempt command:
```
rm -rf /tmp/foo
```
Passed through `_gate_no_permission_denials`. Result: `failures` list contains `no_permission_denials` entry. PASS.

Evidence: `repl_blocking_denial.txt`

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bash-gate-guardrails-exemption-2026-05-20/knowledge/qa/evidence/bash-gate-guardrails-exemption-2026-05-20/
Files verified: 4
```

## Recommendation

**Pass.** All deliverables verified, all behavioral tests pass, no regressions, no findings.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified Step 1's GUARDRAILS_BASH_EXEMPTION_PATTERN implementation in gates.py. Ran deliverable verification, pytest (targeted + full suite), REPL behavioral verification (exempt + blocking payloads), and Rule 20 self-check. All checks pass.

### Files Deposited
- `knowledge/qa/bash-gate-guardrails-exemption-2026-05-20.md` — QA report with verification table, behavioral results, and Rule 20 self-check banner
- `knowledge/qa/evidence/bash-gate-guardrails-exemption-2026-05-20/` — 4 evidence files (pytest_test_gates_v.txt, pytest_full_suite.txt, repl_exempt_denial.txt, repl_blocking_denial.txt)

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- Classified all 5 full-suite test failures as pre-existing (no changes to those test files in the commit)
- Accepted `test_run_step_timeout` as documented pre-existing failure per prior QA reports

### Flags for CEO
- None

### Flags for Next Step
- None
