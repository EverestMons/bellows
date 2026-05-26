# QA Report: `_extract_plan_required_deposits` set-to-list conversion

**Plan:** `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
**Date:** 2026-05-25
**QA Agent:** Bellows QA (Step 2)

## Deliverable Verification Table

| # | Check | Status | Line(s) | Evidence (verbatim excerpt) |
|---|-------|--------|---------|---------------------------|
| 1 | `_filter_transient_paths` returns list comprehension `[p for p in paths if ...]` | ✅ | 369 | `return [p for p in paths if not os.path.basename(p).startswith("_staging_")]` |
| 2 | Block-form branch uses `paths = []` and `paths.append(...)` | ✅ | 391, 393 | `paths = []` / `paths.append(m.group(1))` |
| 3 | Inline-form branch uses `paths = []` and `paths.append(...)` | ✅ | 402, 404 | `paths = []` / `paths.append(m.group(1))` |
| 4 | Legacy prose-matching uses `paths = []`, three `paths.append(...)`, and `dict.fromkeys` dedup | ✅ | 409, 414, 419, 422, 425 | `paths = []` / three `paths.append(...)` calls / `paths = list(dict.fromkeys(paths))` before `return _filter_transient_paths(paths)` at line 426 |
| 5 | Docstring updates on both functions | ✅ | 366-368, 375-377 | `_filter_transient_paths`: "Drop paths whose basename starts with `_staging_` and return as a list preserving input order." / `_extract_plan_required_deposits`: "Returns a list preserving insertion order; for the block form, this equals the authoring order of bullets in the ``**Deposits:**`` block. Convention: the QA report is the first ``.md`` entry in the block." |
| 6 | `test_extract_plan_required_deposits_preserves_block_order` present with correct assertions | ✅ | 575-589 | `assert isinstance(result, list)` and `assert md_paths[0] == "knowledge/qa/foo.md"` |
| 7 | Stale-comment cleanup at both `patch.object` sites | ✅ | 1533, 1554 | Both updated to: "_extract_plan_required_deposits now returns a list preserving authoring order (per BACKLOG 2026-05-24 fix); patch is retained for test isolation." |

**Result: 7/7 checks PASS.**

## Targeted Pytest Summary

```
126 passed, 1 warning in 0.23s
```

Full output captured to `evidence/pytest_targeted.txt`. Zero new regressions. All pre-existing tests pass. New `test_extract_plan_required_deposits_preserves_block_order` PASSED.

## Call-Site Safety Check

`grep -n 'md_paths\[0\]' gates.py` output:

```
450:    qa_report_path = md_paths[0]
505:    qa_report_path = md_paths[0]
```

Exactly two hits at the two known consumers:
- Line 450: `_gate_rule_20_self_check` — confirmed still indexes `md_paths[0]`
- Line 505: `_gate_rule_22_verification` — confirmed still indexes `md_paths[0]`

Both consumers unchanged. The fix makes the index deterministic (first-authored `.md` deposit), not changing the consumers.

Full output captured to `evidence/grep_md_paths.txt`.

## Structural Compliance Check

**DEV commit (`git show --stat HEAD`):**

```
 gates.py                                           | 31 ++++---
 ...lan-required-deposits-set-to-list-2026-05-25.md | 98 ++++++++++++++++++++++
 tests/test_gates.py                                | 21 ++++-
 3 files changed, 136 insertions(+), 14 deletions(-)
```

Exactly 3 files touched: `gates.py`, `tests/test_gates.py`, `knowledge/development/extract-plan-required-deposits-set-to-list-2026-05-25.md`. Confirmed.

**Diff scope (`git diff HEAD~1 gates.py`):** All changes bounded to `_extract_plan_required_deposits` (lines 372-426) and `_filter_transient_paths` (lines 365-369). No other functions modified. Confirmed.

Full outputs captured to `evidence/dev_commit.txt` and `evidence/diff_gates.txt`.

## Rule 20 Self-Check

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/extract-plan-required-deposits-set-to-list-2026-05-25/knowledge/qa/evidence/executable-extract-plan-required-deposits-set-to-list-2026-05-25/
Files verified: 4
```

## Output Receipt

**Status: Complete**
