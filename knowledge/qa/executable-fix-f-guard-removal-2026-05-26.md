# QA Report — Fix F isinstance Guard Removal

**Date:** 2026-05-26 | **Agent:** Bellows QA
**Plan:** executable-fix-f-guard-removal-2026-05-26
**Step:** 2 (QA)

---

## DEV Output Receipt Check

DEV deposit: `knowledge/development/fix-f-guard-removal-2026-05-26.md`
Output Receipt Status: **Complete**

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows.py:495` Fix F guard removed | `f["gate"]` without isinstance | ✅ | `bellows_495_grep.txt` |
| `bellows.py:587` Fix F guard removed | `f["gate"]` without isinstance | ✅ | `bellows_587_grep.txt` |
| `tests/test_bellows.py` fixture updated | dict shape `{"gate": ..., "evidence": ...}` | ✅ | `test_fixture_grep.txt` |
| 2026-05-21 symmetric isinstance pattern intact | Lines 509, 600 preserved | ✅ | `isinstance_pattern_grep.txt` |
| DEV log deposited and documents changes | Three changes with before/after | ✅ | `dev_log_check.txt` |

---

## Test Execution

| Metric | DEV Reported | QA Observed | Match |
|---|---|---|---|
| Passed | 407 | 407 | ✅ |
| Failed | 5 | 5 | ✅ |
| New failures | 0 | 0 | ✅ |
| Regressions | 0 | 0 | ✅ |

Failed tests (all pre-existing carry-over):
1. `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file` — worktree phrase file missing
2. `test_decisions.py::TestLoadPhrases::test_includes_known_phrases` — worktree phrase file missing
3. `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives` — worktree phrase file missing
4. `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` — worktree phrase file missing
5. `test_runner_parser.py::test_run_step_timeout` — long-standing known failure

Key test: `test_run_plan_inprogress_entry_renames_to_verdict_pending` — **PASSED** with dict fixture.

Evidence: `pytest_full.txt`

---

## Structural-Compliance Checks

### (a) Guard Site Classification

Fix F guards removed ONLY at the two Fix F sites (lines 495, 587 — `.join()` log expressions).
2026-05-21 symmetric pattern guards preserved at their own sites (lines 509, 600 — `all()` predicates).
The two sets are structurally distinct: different code paths, different purposes.

Evidence: `guard_site_classification.txt`

### (b) Production Contract Consistency

Every `gate_result["failures"]` assignment in `bellows.py`, `gates.py`, and `verdict.py` uses dict shape `{"gate": str, "evidence": str}`. No string-list format exists in production code. `gates.py:162` documents the contract explicitly.

Evidence: `contract_consistency.txt`

### (c) Test Fixture Audit

Every non-empty `"failures"` list in test fixtures uses the dict shape. Zero non-conformant string-list fixtures remain across `test_bellows.py`, `test_verdict.py`, `test_consume_verdicts.py`, and `test_rule_26_deposit_parser.py`.

Evidence: `fixture_audit.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-fix-f-guard-removal-2026-05-26/
Files verified: 9
```

---

## Flags for CEO

- REMINDER: restart Bellows daemon to load the updated pause-reason discriminator code. The running daemon executed this plan with pre-edit code; the simplified discriminator (without isinstance guards) activates on next plan dispatched after restart.

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done

Verified all three DEV deliverables (Fix F guard removal at lines 495 and 587, test fixture conformance update). Ran full test suite confirming 407 passed / 5 carry-over failures / zero regressions. Performed structural-compliance checks confirming guard site classification, production contract consistency, and test fixture audit all pass.

### Files Deposited

- `knowledge/qa/executable-fix-f-guard-removal-2026-05-26.md` — this QA report
- `knowledge/qa/evidence/executable-fix-f-guard-removal-2026-05-26/` — 9 evidence files

### Files Created or Modified (Code)

- `PROJECT_STATUS.md` — added 2026-05-26 entry for Fix F guard removal completion

### Decisions Made

- Classified the two isinstance sites at lines 509 and 600 as 2026-05-21 symmetric pattern (not Fix F), confirming they should be preserved

### Flags for CEO

- REMINDER: restart Bellows daemon to load the updated pause-reason discriminator code. The running daemon executed this plan with pre-edit code; the simplified discriminator (without isinstance guards) activates on next plan dispatched after restart.

### Flags for Next Step

- None
