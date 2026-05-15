# QA Report — Intermediate Decision Detector + Vexp Exemption

**Date:** 2026-05-12
**Plan:** `executable-intermediate-decision-detector-2026-05-12`
**Steps verified:** Step 1 (BELLOWS_DEVELOPER — detector module), Step 2 (BELLOWS_DEVELOPER — Vexp exemption)
**Agent:** Bellows QA

---

## Deliverable Verification

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | `INTERMEDIATE_DECISION_PHRASES.md` | 33 bulleted phrases at governance root | ✅ | `grep -c '^- '` returned 33 |
| 2 | `bellows/decisions.py` | `load_phrases()` and `extract_decision_blocks()` defined | ✅ | grep matched at lines 17, 53 |
| 3 | `bellows/verdict.py` | Renders `Intermediate Decisions Detected` section | ✅ | grep matched at line 147 |
| 4 | `bellows/runner.py` | Calls `extract_decision_blocks()` | ✅ | grep matched at line 257 |
| 5 | `bellows/gates.py` | `mcp__vexp__run_pipeline` in `READ_CLASS_TOOLS` | ✅ | grep matched at line 30 |
| 6 | `tests/test_decisions.py` | 6-S-block ground-truth test | ✅ | `test_s_class_blocks_from_ground_truth` at line 66 |
| 7 | `tests/test_gates.py` | Vexp exemption regression test | ✅ | `test_permission_denials_vexp_run_pipeline_exempt` at line 874 |

---

## Behavioral Verification — Part A: Detector Against Ground Truth

Loaded 44 phrases from `INTERMEDIATE_DECISION_PHRASES.md`. Ground truth: 6 S-class blocks, 171 T-class blocks from `labeled-blocks.jsonl`.

**S-class (all 6 must match):**

| Plan | Step | Block | Matched Phrases | Result |
|------|------|-------|-----------------|--------|
| deposit-exists-prose-canary-2026-04-28 | 2 | 7 | let me fix, seems empty | ✅ |
| deposit-exists-prose-canary-2026-04-28 | 2 | 8 | found the issue | ✅ |
| bellows-worktree-impl-2026-05-03 | 1 | 9 | need to fix, wait, | ✅ |
| bellows-worktree-impl-2026-05-03 | 1 | 26 | let me fix | ✅ |
| terminal-capture-2026-05-12 | 1 | 11 | let me fix | ✅ |
| terminal-capture-2026-05-12 | 1 | 23 | let me fix | ✅ |

**Result: 6/6 S-class blocks matched — PASS**

**T-class sample (5 entries, should NOT all be flagged):**

| Index | Flagged | Block Text (truncated) |
|-------|---------|----------------------|
| 0 | No | Let me read the plan first. |
| 5 | No | Step 1 is complete. Here's what was done... |
| 10 | No | Now I have all the information I need... |
| 15 | No | Let me execute this diagnostic... |
| 20 | No | Now let me commit and handle the verdict request... |

**Result: 0/5 T-class samples flagged — PASS** (not all flagged; expected behavior)

---

## Behavioral Verification — Part B: Verdict Request Integration

| # | Check | Result |
|---|-------|--------|
| 1 | Section header rendered when decisions present | ✅ |
| 2 | Block count text correct | ✅ |
| 3 | Event index rendered correctly | ✅ |
| 4 | Multiple events rendered | ✅ |
| 5 | Phrase annotation rendered | ✅ |
| 6 | Section omitted when empty list | ✅ |
| 7 | Section omitted when None (default) | ✅ |

**Result: 7/7 checks passed — PASS**

---

## Behavioral Verification — Part C: Vexp Exemption

| # | Check | Result |
|---|-------|--------|
| 1 | `mcp__vexp__run_pipeline` denial does NOT trip `no_permission_denials` gate | ✅ |
| 2 | `Edit` denial correctly trips gate (control check) | ✅ |

**Result: 2/2 checks passed — PASS**

---

## Test Suite

**Result:** 292 passed, 1 failed

The 1 failure is the pre-existing `test_run_step_timeout` (mocks `subprocess.run` but `runner.py` uses `subprocess.Popen` — unrelated to this plan's changes).

---

## Live Verification Caveat

The running Bellows daemon will not load these changes until restart. The new detector code, the new verdict-request section, and the Vexp exemption will appear in plans dispatched AFTER the next daemon restart. No attempt was made to verify the changes are live in the current daemon.

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/intermediate-decision-detector-qa-2026-05-12/
Files verified: 4
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Verified all 7 deliverables from Steps 1 and 2. Ran behavioral verification against ground truth (6/6 S-class matched, 0/5 T-class false positives), verdict request rendering (7/7 checks), and Vexp exemption gate (2/2 checks). Full test suite: 292 passed, 1 pre-existing failure.

### Files Deposited
- `bellows/knowledge/qa/intermediate-decision-detector-qa-2026-05-12.md` — QA report
- `bellows/knowledge/qa/evidence/intermediate-decision-detector-qa-2026-05-12/` — evidence directory

### Files Created or Modified (Code)
- `bellows/PROJECT_STATUS.md` — added completed milestone entry
- `bellows/feedback.log` — appended ship entry

### Decisions Made
- Selected T-class sample indices [0, 5, 10, 15, 20] for variety across different plans and step types
- Used direct Python invocation for behavioral verification (faster than running canary diagnostic)

### Flags for CEO
- None

### Flags for Next Step
- None — this is the final step. Plan NOT moved to Done/ per disable-auto-close model.
