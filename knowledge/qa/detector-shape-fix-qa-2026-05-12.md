# QA Report — Detector NDJSON Shape Fix + Fixture Rewrite + Observability

**Date:** 2026-05-12
**Plan:** executable-detector-shape-fix-2026-05-12, Step 2
**Agent:** Bellows QA

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `decisions.py` reads `event.get("message", {}).get("content", [])` | Wrapped NDJSON path at line 94 | ✅ | grep confirms literal string at line 94 |
| `test_decisions.py` fixtures use `"message": {"content"` wrapping | 4 occurrences (helper + 3 inline) | ✅ | grep count = 4: line 13 (helper), 131 (multiple_content_items), 181-182 (event_idx_tracking) |
| `bellows.py::_module_fingerprints()` includes `decisions.py` | 6th entry in modules list | ✅ | grep confirms `decisions.py` in modules list at line 855 |
| `test_bellows.py` expects 6 modules | `expected_keys` includes `decisions.py` | ✅ | Test renamed to `test_module_fingerprints_returns_all_six_modules`, asserts 6-key set at line 2954 |
| Dev log at `knowledge/development/detector-shape-fix-dev-log-2026-05-12.md` | Covers all 3 parts + test counts | ✅ | File exists, documents Part A (line 94 change), Part B (4 fixtures), Part C (6th module), test delta 0 |

All 5 deliverables verified. No fixes needed.

---

## Behavioral Verification — Real-Data Detection Test

### Primary File: `logs/20260512-103456-step.json`
- **Source:** Step 1 of intermediate-decision-detector executable (multi-file DEV work)
- **raw_output length:** 1,428,320 chars
- **Result:** 6 blocks matched (phrases: "let me fix", "i need to update", "instead of", "i'll update", "let me also", "had to")
- **Verdict:** PASS — non-empty result confirms the fixed detector extracts decisions from real wrapped NDJSON

### Canary File: `logs/20260512-184339-step.json` (negative control)
- **Source:** Canary diagnostic step.json — known to have 3 assistant text blocks but 0 phrase matches
- **raw_output length:** 225,794 chars
- **Result:** 0 blocks matched
- **Verdict:** PASS — empty result as expected (no narration phrases in canary's text blocks)

### End-to-End Conclusion
The fixed `event.get("message", {}).get("content", [])` path correctly traverses real Claude CLI NDJSON. The primary file yields 6 phrase-matched decision blocks; the canary file yields 0 (correct negative control). The detector is working against production data.

---

## Test Suite Results

| Metric | Value |
|---|---|
| Total passed | 292 |
| Total failed | 1 |
| Failed test | `test_run_step_timeout` (pre-existing, out of scope) |
| Warnings | 1 (urllib3 LibreSSL compatibility, informational) |
| Test count vs Step 1 | 292/1 → 292/1 (no delta) |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/
Files verified: 3
```

---

## Evidence Files

All evidence deposited at `knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/`:
- `deliverable-verification.txt` — grep outputs for all 4 anchors
- `real-data-detection-test.txt` — detector results for both step.json files
- `test-suite-output.txt` — full test suite pass/fail summary

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 5 Step 1 deliverables via grep anchors. Ran behavioral real-data detection test against production step.json (6 matches) and canary step.json (0 matches — correct negative control). Ran full test suite (292 passed, 1 pre-existing failure). Deposited evidence files and QA report.

### Files Deposited
- `knowledge/qa/detector-shape-fix-qa-2026-05-12.md` — this QA report
- `knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/deliverable-verification.txt` — grep evidence
- `knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/real-data-detection-test.txt` — behavioral test output
- `knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/test-suite-output.txt` — test suite results

### Files Created or Modified (Code)
- None (QA step — no code changes)

### Decisions Made
- Used `logs/20260512-103456-step.json` as primary behavioral test file (plan specified this file)
- Used `logs/20260512-184339-step.json` as negative control per plan specification
- Non-assistant events in `test_non_assistant_events_ignored` confirmed correct — not affected by NDJSON shape fix (they test system/user types)

### Flags for CEO
- None

### Flags for Next Step
- None
