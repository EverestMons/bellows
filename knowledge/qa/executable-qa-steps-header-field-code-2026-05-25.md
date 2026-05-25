# QA Report: qa_steps Header Field for Authoritative QA-Step Detection

**Date:** 2026-05-25
**Plan:** executable-qa-steps-header-field-code-2026-05-25
**Agent:** Bellows QA

## Deliverable Verification Table

| # | Check | Evidence | Line(s) | Verbatim Excerpt | Result |
|---|-------|----------|---------|-----------------|--------|
| 1 | `_gate_is_qa_step` signature accepts `plan_header=None` kwarg | `evidence/signature.txt` | gates.py:556 | `def _gate_is_qa_step(plan_text, step_number, plan_header=None):` | ✅ |
| 2 | `qa_steps` field checked as primary path (≥2 references) | `evidence/qa_steps_references.txt` | gates.py:559,560,565,568 | `qa_steps_raw = plan_header.get("qa_steps", "")` + 3 more | ✅ |
| 3 | YAML list handling present (`isinstance(..., list)`) | `evidence/yaml_list_branch.txt` | gates.py:563 | `if isinstance(qa_steps_raw, list):` | ✅ |
| 4 | Keyword fallback preserved (`"qa" in` substring check) | `evidence/keyword_fallback.txt` | gates.py:575 | `return "qa" in match.group(0).lower()` | ✅ |
| 5 | Call site passes `plan_header=header` | `evidence/call_site.txt` | gates.py:178 | `is_qa_step = _gate_is_qa_step(plan_text, step_number, plan_header=header)` | ✅ |
| 6 | 7 new test functions present in `tests/test_gates.py` | `evidence/new_tests_present.txt` | test_gates.py:1583-1632 | 7 `def test_qa_steps_field_*` matches | ✅ |
| 7 | Dev log has all 6 sections (a-f) + Output Receipt Complete | `evidence/dev_log_present.txt` | knowledge/development/ | All 6 headings + `**Status:** Complete` | ✅ |

## Full-Suite Test Summary

```
collected 406 items
401 passed, 5 failed, 1 warning
```

**5 pre-existing failures (all carry-overs, not regressions):**
- 3 x `test_decisions.py::TestLoadPhrases` (worktree artifact — INTERMEDIATE_DECISION_PHRASES.md missing)
- 1 x `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` (same worktree artifact)
- 1 x `test_runner_parser.py::test_run_step_timeout` (BACKLOG-documented runner mock mismatch)

**0 new regressions. All 7 new `test_qa_steps_*` tests PASSED.**

Evidence: `evidence/pytest_full.txt`

## New Test Verification

All 7 new tests confirmed PASSED in pytest output:
- `test_qa_steps_field_single_step_matches` — PASSED
- `test_qa_steps_field_single_step_excludes_other` — PASSED
- `test_qa_steps_field_multi_step` — PASSED
- `test_qa_steps_field_absent_falls_back_to_keyword` — PASSED
- `test_qa_steps_field_malformed_falls_back_to_keyword` — PASSED
- `test_qa_steps_field_yaml_list` — PASSED
- `test_qa_steps_field_non_qa_role_header` — PASSED

## Structural Compliance Check

**DEV commit (`git show --stat HEAD`):**
```
gates.py                                           | 18 ++++-
knowledge/development/qa-steps-header-field-2026-05-25.md | 90 ++++++++++++++++++++++
tests/test_gates.py                                | 61 +++++++++++++++
3 files changed, 167 insertions(+), 2 deletions(-)
```

Exactly 3 files changed as required. Evidence: `evidence/dev_commit.txt`

**Diff scope (`git diff HEAD~1 gates.py`):**
- Line 178: call site change — `_gate_is_qa_step(plan_text, step_number)` → `_gate_is_qa_step(plan_text, step_number, plan_header=header)`
- Lines 556-576: `_gate_is_qa_step` function replacement — old 6-line function → new 20-line function with `qa_steps` primary path + keyword fallback

No other functions modified. Diff is bounded to `_gate_is_qa_step` and its single call site in `check()`. Evidence: `evidence/diff_gates.txt`

## Rule 20 Self-Check

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/qa-steps-header-field-code-2026-05-25/knowledge/qa/evidence/executable-qa-steps-header-field-code-2026-05-25/
Files verified: 10
```

## Output Receipt

**Agent:** Bellows QA
**Status:** Complete
**Files deposited:**
- `knowledge/qa/executable-qa-steps-header-field-code-2026-05-25.md` (this report)
- `knowledge/qa/evidence/executable-qa-steps-header-field-code-2026-05-25/` (evidence directory)
- `PROJECT_STATUS.md` (updated)
