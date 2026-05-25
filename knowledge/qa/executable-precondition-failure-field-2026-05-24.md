# QA Report — Precondition-Failure Verdict-Request Field

**Plan:** `executable-precondition-failure-field-2026-05-24`
**Step:** 2 (QA)
**Date:** 2026-05-25
**Test Scope:** full
**DEV Commit:** `0a90e26`

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | `precondition_failure=False` in verdict.py signature | 1 match (line 178) | ✅ | `verdict_signature.txt` |
| 2 | `**Precondition Failure:**` in verdict.py content template | 1 match (line 232) | ✅ | `verdict_content_template.txt` |
| 3 | `precondition_failure=True` at Site 1 in bellows.py | 1 match (line 446) | ✅ | `site_1_passes_true.txt` |
| 4 | `precondition_failure_from_request` in bellows.py consumer | 3 matches (init, parser, dispatch) | ✅ | `consumer_uses_field.txt` |
| 5 | Old `resume_step=step_number + 1` dispatch absent | 0 matches | ✅ | `old_dispatch_absent.txt` |
| 6 | New `resume_step=next_step` dispatch present | 1 match (line 1248) | ✅ | `new_dispatch_present.txt` |
| 7 | `import bellows; import verdict` clean exit | Exit code 0 | ✅ | `import_smoke.txt` |
| 8 | 4 new test functions present | 3 in test_consume_verdicts.py + 1 in test_verdict.py | ✅ | `new_tests_present.txt` |
| 9 | Dev log with all 6 sections (a-f) + Output Receipt Complete | All sections present | ✅ | `dev_log_present.txt` |
| 10 | Prompt feedback entry for precondition-failure-field | Entry present | ✅ | `feedback_entry.txt` |

---

## Full Pytest Suite

```
394 collected | 389 passed | 5 failed | 0 skipped | 1 warning

Failed (all pre-existing carry-over):
- tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file
- tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases
- tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives
- tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth
- tests/test_runner_parser.py::test_run_step_timeout
```

All 4 new tests pass. No new failures introduced.

---

## Structural Compliance Check

**DEV commit:** `0a90e26` (`fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)`)

**Files in commit (5 — matches expected):**
- `bellows.py` — 19 insertions, 5 deletions
- `knowledge/development/precondition-failure-field-2026-05-24.md` — 232 insertions
- `tests/test_consume_verdicts.py` — 170 insertions
- `tests/test_verdict.py` — 44 insertions
- `verdict.py` — 3 insertions, 1 deletion

**bellows.py diff assessment:** Changes are additive and scoped. Site 1 adds `precondition_failure=True` keyword arg and a comment (2 lines). Parser adds `precondition_failure_from_request = False` init (1 line) and parser line (2 lines). Dispatch replaces 3-line unconditional advance with 7-line conditional block. No unscoped or unrelated modifications.

**verdict.py diff assessment:** Changes are additive and scoped. Signature adds `, precondition_failure=False` (1 line modified). Content template adds `**Precondition Failure:**` field line (1 line added). No unscoped or unrelated modifications.

Evidence: `dev_commit.txt`, `diff_bellows.txt`, `diff_verdict.txt`

---

## Backward Compatibility Verification

From `diff_bellows.txt`, the parser initialization line:
```
+            precondition_failure_from_request = False
```

Confirmed: `precondition_failure_from_request` is initialized to `False` (not `None` or undefined). Historical verdict-request files lacking the `**Precondition Failure:**` field will correctly default to `False`, preserving advance behavior (`resume_step = step_number + 1`).

Evidence: `backward_compat_default_false.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/
Files verified: 15
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 10 deliverables from DEV Step 1. Ran full pytest suite (389 passed, 5 pre-existing carry-over failures, 0 new failures). Confirmed structural compliance of DEV commit (5 files, additive and scoped changes). Verified backward compatibility (parser defaults to `False` when `**Precondition Failure:**` field is absent).

### Files Deposited
- `knowledge/qa/executable-precondition-failure-field-2026-05-24.md` — this QA report
- `knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/` — 15 evidence files

### Files Created or Modified (Code)
- None (QA step — no code changes)

### Decisions Made
- Accepted 3 matches for verification 4 (consumer uses field) — init, parser, and conditional dispatch. All 3 are correct usage sites.

### Flags for CEO
- None

### Flags for Next Step
- None
