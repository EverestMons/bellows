# QA Report — Rule 26 Deposit Parser: Scope Gate + Fix Scoping Bug
**Date:** 2026-04-19 | **Plan:** executable-rule-26-deposit-parser-scope-2026-04-19.md

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `gates.py` contains `_extract_step_text` | `def _extract_step_text` at line 155 | ✅ | grep_deliverables.txt line 1 |
| `_gate_deposit_exists` calls helper | `_extract_step_text(plan_text` at line 148 | ✅ | grep_deliverables.txt line 4 |
| `_gate_scope_check` calls helper | `_extract_step_text(plan_text` at line 220 | ✅ | grep_deliverables.txt line 6 |
| `_extract_plan_required_deposits` has Rule 26 block | `Deposits:` pattern at lines 169, 173, 174 | ✅ | grep_deliverables.txt lines 11-13 |
| `verdict.py` has scoping fix | `_extract_step_text_from_plan` + `current_step_text` at lines 19, 97, 108 | ✅ | grep_deliverables.txt lines 15-17 |

## Full Suite Regression

| Run | Total | Passed | Failed | New Failures |
|---|---|---|---|---|
| DEV baseline (pre-changes) | 104 | 93 | 11 | — |
| DEV post-changes | 104 | 93 | 11 | 0 |
| QA full suite (with 6 new tests) | 110 | 99 | 11 | 0 |

All 11 failures are pre-existing `test_runner.py` (10) and `test_runner_parser.py` (1) — stale mocks unrelated to this plan.

## Targeted Test Results

| Test | Description | Status |
|---|---|---|
| `test_extract_plan_required_deposits_prefers_declared_block` | Block with 2 paths + prose path; returns only block paths | ✅ |
| `test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block` | No block, prose only; returns prose path | ✅ |
| `test_extract_plan_required_deposits_handles_none_bullet` | Block with `- none`; returns empty set | ✅ |
| `test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present` | Block + code fence paths; returns only block path (BACKLOG #6 regression) | ✅ |
| `test_extract_primary_deposit_scoping_in_post_verdict_request` | Two-step plan, step_number=2; Deposit field is step-2.md not step-1.md | ✅ |
| `test_extract_step_text_helper_gates_py` | 3-step plan, extract step 2; starts with STEP 2, no STEP 3 | ✅ |

6/6 targeted tests pass.

## QA Fix Applied

During targeted test execution, the `_extract_plan_required_deposits` block-detection regex was found to not handle `> ` blockquote prefixes present in real plan step text. Fixed regex from `r'\*\*Deposits:\*\*\s*\n((?:\s*-\s+.*\n?)+)'` to `r'[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)'`. This is a refinement to the Step 1 code, not a new feature.

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-rule-26-deposit-parser-scope-2026-04-19/
Files verified: 3
```

## Output Receipt

- **Status:** Complete
- **Deposit:** `bellows/knowledge/qa/rule-26-deposit-parser-scope-qa-2026-04-19.md`
- **Evidence:** `bellows/knowledge/qa/evidence/executable-rule-26-deposit-parser-scope-2026-04-19/` (grep_deliverables.txt, pytest_full.txt, pytest_targeted.txt)
