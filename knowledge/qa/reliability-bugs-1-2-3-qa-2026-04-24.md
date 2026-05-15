# Reliability Bugs 1, 2, 3 — QA Report
**Date:** 2026-04-24 | **Agent:** Bellows QA | **Plan:** executable-bellows-reliability-bugs-1-2-3-2026-04-24 | **Step:** 3

**REMINDER: restart Bellows daemon to load bug fixes from bellows.py — running daemon holds pre-fix code in memory until restart.**

---

## (a) Deliverable Verification

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | `bellows.py` — `plan_matched` boolean gate in `_consume_verdicts` | `plan_matched = False` before loop, set `True` on match, gates processed-move | ✅ | grep_plan_matched.txt: L655, L661, L714, L717 |
| 2 | `bellows.py` — `base_filename` canonicalization (Bug 2, 5 sites) | Lifecycle prefix stripped at L207-212, used at L243, L304, L362, L382 | ✅ | grep_bug2_fix.txt: 8 lines confirming all 5 sites + definition |
| 3 | `bellows.py` — `re.IGNORECASE` in `extract_total_steps` | Case-insensitive regex with `\s+\d+` requirement | ✅ | grep_ignorecase.txt: L87 shows `re.MULTILINE \| re.IGNORECASE` |
| 4 | `tests/test_bellows.py` — 10 new test functions | All 10 test names from DEV log present | ✅ | ls_tests_added.txt: 10 functions at L1473-L1725 |

**Result:** 4/4 deliverables verified. No blockers.

---

## (b) Targeted Test Regression

| Metric | DEV Baseline | QA Full Run | Delta |
|---|---|---|---|
| Tests collected | 150 | 150 | 0 |
| Passed | 149 | 149 | 0 |
| Failed | 1 | 1 | 0 |

**Pre-existing failure:** `test_run_step_timeout` in `tests/test_runner_parser.py` — timeout handling behavior mismatch, unrelated to this change. Present in both DEV baseline and QA full run.

**New tests (10):** All PASSED in QA full run, matching DEV baseline.

**Result:** No regression. Test count matches DEV baseline exactly.

---

## (c) Per-Bug Smoke Results

### Bug 1 — `_consume_verdicts` plan_matched gate
- **Harness:** Synthetic verdict file in `resolved/` with slug matching no on-disk plan
- **Result:** Verdict remained in `resolved/`, NOT moved to `processed-*`
- **Warning logged:** `no verdict-pending plan found for nonexistent-slug-2026-04-24 step 1 — leaving in resolved/ for retry`
- **Status:** ✅ PASS
- **Evidence:** smoke_bug1.txt

### Bug 2 — Pause-rename canonical path
- **Harness:** Full `run_plan()` invocation with `in-progress-` prefixed `plan_path`, failing gates to trigger pause branch
- **Result:** File renamed to `verdict-pending-executable-smoke-bug2-2026-04-24.md` (correct single prefix). No `verdict-pending-in-progress-*` file created.
- **Status:** ✅ PASS
- **Evidence:** smoke_bug2.txt

### Bug 3 — Case-insensitive `extract_total_steps`
- **Harness:** Three inputs tested via `contextlib.redirect_stdout` capture
- **Results:**
  - `## Step 1` + `## Step 2` → returned 2, warning fired (case mismatch)
  - `## STEP 1` → returned 1, no warning (exact match)
  - `## Step-by-step approach` → returned 0, no false positive
- **Status:** ✅ PASS
- **Evidence:** smoke_bug3.txt

---

## (d) Flags

- **REMINDER:** Restart Bellows daemon after this plan closes to load the three fixes from `bellows.py`. Running daemon holds pre-fix code in memory.
- **Pre-existing test failure:** `test_run_step_timeout` is unrelated to this change and was present before the plan started.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Executed Rule 17 deliverable verification (4/4 pass), full test regression (149/150 — no regression vs DEV baseline), and three behavioral smoke tests (all PASS). Produced QA report and 8 evidence files.

### Files Deposited
- `knowledge/qa/reliability-bugs-1-2-3-qa-2026-04-24.md` — this QA report
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/grep_plan_matched.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/grep_bug2_fix.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/grep_ignorecase.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/ls_tests_added.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/pytest_targeted.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/smoke_bug1.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/smoke_bug2.txt`
- `knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/smoke_bug3.txt`

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Marked all three smoke tests as PASS — behavioral results match expected fix behavior
- Acknowledged pre-existing `test_run_step_timeout` failure as unrelated

### Flags for CEO
- REMINDER: restart Bellows daemon to load fixes

### Flags for Next Step
- Do NOT move this plan to Done — Planner performs terminal move after Rule 22 verification
- Do NOT update PROJECT_STATUS.md — Planner handles post-verification
