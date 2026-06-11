# QA Report — Id-Threading + Lifecycle Mint v2 (Step 2 QA)

**Plan:** bellows-id-threading-lifecycle-mint-v2-2026-06-11
**Date:** 2026-06-11
**Agent:** Bellows QA
**Test Scope:** unit + integration — Python module changes with corresponding test files

---

## Verification Table

| # | Item | Method | Evidence | Result |
|---|---|---|---|---|
| 1 | Mint atomicity + monotonicity | Scratch Python session against temp DB: 3 sequential `mint_and_claim` → ids 1,2,3; forced CHECK constraint failure mid-transaction → `next_id` not advanced; next mint → id 4 | `id1=1, id2=2, id3=3`; `IntegrityError` caught; `id4=4` (not 5) | PASS |
| 2 | Claim-rename contract | `pytest tests/test_bellows.py::test_claim_rename_draft_placeholder tests/test_bellows.py::test_claim_rename_legacy_descriptive_slug` — both PASSED; `diagnostic-draft-143022.md` and `diagnostic-foo-bar-2026-06-10.md` both claim to `in-progress-diagnostic-1.md` | 2 passed, 0 failed | PASS |
| 3 | Substring fixes (142 vs 1423) | `pytest` 6 regression tests: `test_consume_verdicts_numeric_slug_no_false_match`, `test_stale_scan_numeric_slug_no_false_match_done`, `test_stale_scan_numeric_slug_no_false_match_halted`, `test_exact_match_still_works_for_legacy_slugs`, `test_exact_match_done_legacy`, `test_exact_match_halted_legacy` | 6 passed, 0 failed | PASS |
| 4 | Dual-format tolerance | 10-case scratch check: `is_runnable_plan`, `slug_from_path`, `slug_for` each tested with both `diagnostic-142.md` (id-only) and `diagnostic-foo-bar-2026-06-10.md` (legacy); verdict regex and orphan-guard regex tested with both formats | All 10 assertions passed | PASS |
| 5 | Commit-tag plumbing | grep bellows.py: `_id_tag_instruction` at :467 (computed), :469/:471/:473 (bootstrap prompts), :588 (next-step prompt); auto-stage commit `[plan_id]` at :981; `--no-ff` merge `-m` with `[plan_id]` at :1085-1086; `plan_id` threaded through `_auto_stage_deposits` (:921 signature, :530/:626 call sites) and `_teardown_worktree` (:992 signature, :569/:665/:693 call sites) | All 6 injection sites confirmed; `plan_id=` threaded at all call sites | PASS |
| 6 | Recovery scan (recover_half_claimed) | `pytest tests/test_lifecycle.py::TestRecoverHalfClaimed` — 3 tests: deposit present → re-rename, deposit absent → abandoned, already renamed → in_progress | 3 passed, 0 failed | PASS |
| 7 | Full test suite (wall-clock bound) | `pytest tests/ --tb=line` under 120s subprocess timeout; wall-clock: 8.58s | 480 passed, 1 warning, 0 failed | PASS |
| 8 | Executable-B boundary | Schema check against temp lifecycle.db: `SELECT name FROM sqlite_master WHERE type='table'` → `{id_sequence, plans}` only; no steps/commits/deposits/verdicts/gate_events/diagnostic_meta/executable_meta/derivations | 2 tables, no Executable B tables leaked | PASS |

---

## Suite Count Reconciliation

| Metric | DEV Run (Step 1) | QA Run (Step 2) | Delta |
|---|---|---|---|
| Passed | 480 | 480 | 0 |
| Failed | 0 | 0 | 0 |
| Warnings | 1 | 1 | 0 |
| Duration | 8.86s | 8.58s | -0.28s |

**No new failures** vs the DEV run. Test counts match exactly.

---

## Detailed Evidence

### (1) Mint Atomicity + Monotonicity

```
MONOTONICITY CHECK: id1=1, id2=2, id3=3
MONOTONICITY: PASSED — consecutive integers 1, 2, 3
ATOMICITY CHECK: expected failure caught: IntegrityError: CHECK constraint failed: type IN ('diagnostic', 'executable', 'qa')
ATOMICITY CHECK: id4=4 (expected 4)
ATOMICITY: PASSED — failed INSERT did not consume an id
DB ROWS:
  id=1, type=diagnostic, title=Plan A, state=claimed
  id=2, type=executable, title=Plan B, state=claimed
  id=3, type=qa, title=Plan C, state=claimed
  id=4, type=diagnostic, title=Plan D, state=claimed
Total plans rows: 4 (expected 4 — the INVALID_TYPE should NOT appear)
ALL CHECKS PASSED
```

### (2) Claim-Rename Contract

```
tests/test_bellows.py::test_claim_rename_draft_placeholder PASSED        [ 50%]
tests/test_bellows.py::test_claim_rename_legacy_descriptive_slug PASSED  [100%]
2 passed, 1 warning in 0.22s
```

### (3) Substring Fixes

```
tests/test_bellows.py::test_consume_verdicts_numeric_slug_no_false_match PASSED [ 16%]
tests/test_bellows.py::test_stale_scan_numeric_slug_no_false_match_done PASSED [ 33%]
tests/test_bellows.py::test_stale_scan_numeric_slug_no_false_match_halted PASSED [ 50%]
tests/test_bellows.py::test_exact_match_still_works_for_legacy_slugs PASSED [ 66%]
tests/test_bellows.py::test_exact_match_done_legacy PASSED               [ 83%]
tests/test_bellows.py::test_exact_match_halted_legacy PASSED             [100%]
6 passed, 1 warning in 0.12s
```

Code sites verified:
- bellows.py:1460 — `verdict.slug_from_path(pname) == lookup_slug` (exact comparison, not substring)
- bellows.py:1562 — `verdict.slug_from_path(dname) == lookup_slug` (exact comparison)
- bellows.py:1570 — `verdict.slug_from_path(dname[len("halted-"):]) == lookup_slug` (manual halted- strip + exact comparison)

### (4) Dual-Format Tolerance

```
is_runnable_plan("diagnostic-142.md") = True
is_runnable_plan("diagnostic-foo-bar-2026-06-10.md") = True
slug_from_path("diagnostic-142.md") = "142"
slug_from_path("diagnostic-foo-bar-2026-06-10.md") = "foo-bar-2026-06-10"
slug_for("in-progress-diagnostic-142.md") = "diagnostic-142"
slug_for("in-progress-diagnostic-foo-bar-2026-06-10.md") = "diagnostic-foo-bar"
verdict regex on "verdict-142-step-1.md": slug=142, step=1
verdict regex on legacy: slug=executable-foo-bar-2026-06-10, step=2
orphan-guard regex on "verdict-request-142-step-1.md": slug=142
orphan-guard regex on legacy: slug=foo-bar-2026-06-10
ALL 10 DUAL-FORMAT CHECKS PASSED
```

### (5) Commit-Tag Plumbing

```
467:        _id_tag_instruction = f" Tag all commits with [{plan_id}] in the commit message." if plan_id else ""
469:            bootstrap_prompt = ...{_id_tag_instruction}"
471:            bootstrap_prompt = ...{_id_tag_instruction}"
473:            bootstrap_prompt = ...{_id_tag_instruction}"
588:            default_next_prompt = ...{_id_tag_instruction}"
981:                 f"bellows: auto-stage declared deposits before teardown{f' [{plan_id}]' if plan_id else ''}"],
1085:            ["git", "--no-pager", "merge", "--no-ff", "-m",
1086:             f"Merge branch '{branch_name}'{f' [{plan_id}]' if plan_id else ''}", branch_name],
```

Signature threading confirmed:
- `_auto_stage_deposits(..., plan_id=None)` at :921; called with `plan_id=plan_id` at :530, :626
- `_teardown_worktree(..., plan_id: int = None)` at :992; called with `plan_id=plan_id` at :569, :665, :693

### (6) Recovery Scan

```
tests/test_lifecycle.py::TestRecoverHalfClaimed::test_deposit_present_re_renames PASSED [ 33%]
tests/test_lifecycle.py::TestRecoverHalfClaimed::test_deposit_absent_marks_abandoned PASSED [ 66%]
tests/test_lifecycle.py::TestRecoverHalfClaimed::test_already_renamed_transitions_to_in_progress PASSED [100%]
3 passed, 1 warning in 0.13s
```

Startup wiring confirmed at bellows.py:1717-1723:
```python
lifecycle.init_lifecycle_db()
for decisions_path in config.get("watched_projects", []):
    if os.path.isdir(decisions_path):
        actions = lifecycle.recover_half_claimed(decisions_path)
        for pid, action in actions:
            _log("INFO", f"lifecycle recovery: plan {pid} — {action}")
```

### (7) Full Suite

Full output: `knowledge/qa/pytest_full_id_threading_qa.txt`

```
480 passed, 1 warning in 8.58s
```

### (8) Executable-B Boundary

```
TABLES IN lifecycle.db:
  id_sequence
  plans
Total tables: 2
PASS: No Executable B tables present
Schema boundary check: PASSED
```

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/id-threading-lifecycle-mint-qa-2026-06-11/
Files verified: 0
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed 8 verification items for the id-threading + lifecycle mint v2 implementation. All items passed: mint atomicity/monotonicity, claim-rename contract, substring fix regression, dual-format tolerance, commit-tag plumbing, recovery scan, full test suite (480 passed, 0 failed), and Executable-B schema boundary. Suite counts match DEV run exactly.

### Files Deposited
- `bellows/knowledge/qa/id-threading-lifecycle-mint-qa-report-2026-06-11.md` — this QA report
- `bellows/knowledge/qa/pytest_full_id_threading_qa.txt` — full pytest output

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- All 8 verification items passed — no fixes required

### Flags for CEO
- None

### Flags for Next Step
- None
