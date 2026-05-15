# Session-End Full Suite QA Report — 2026-05-11

**Plan:** `executable-session-end-full-suite-2026-05-11`
**Date:** 2026-05-11
**Scope:** Cumulative full-suite run per Rule 21 session wrap
**Session commits under test:** `4d57fd3` (fence-strip), `0fab609` (line-anchor)

---

## Cumulative Test Results

| Metric | Value |
|---|---|
| Tests collected | 262 |
| Passed | 261 |
| Failed | 1 |
| Warnings | 1 (urllib3 NotOpenSSLWarning — unrelated) |

**Pass criterion:** All non-pre-existing tests pass. **MET.**

---

## Pre-Existing Failures

| Test | File | Status | Notes |
|---|---|---|---|
| `test_run_step_timeout` | `tests/test_runner_parser.py:57` | Pre-existing | Known `is_error` assertion mismatch; unrelated to session changes |

---

## New Tests Verified (8 total)

### Commit `4d57fd3` — fence-strip (5 tests)

| Test | File | Status |
|---|---|---|
| `test_strip_fenced_code_blocks_basic` | `tests/test_bellows.py` | PASS |
| `test_extract_total_steps_ignores_in_fence_headers` | `tests/test_bellows.py` | PASS |
| `test_extract_step_text_ignores_in_fence_headers` | `tests/test_gates.py` | PASS |
| `test_gate_is_qa_step_ignores_in_fence_headers` | `tests/test_gates.py` | PASS |
| `test_extract_step_text_from_plan_ignores_in_fence_headers` | `tests/test_verdict.py` | PASS |

### Commit `0fab609` — line-anchor (3 tests)

| Test | File | Status |
|---|---|---|
| `test_extract_step_text_ignores_inline_code_references` | `tests/test_gates.py` | PASS |
| `test_gate_is_qa_step_ignores_inline_code_references` | `tests/test_gates.py` | PASS |
| `test_extract_step_text_from_plan_ignores_inline_code_references` | `tests/test_verdict.py` | PASS |

---

## Evidence

- `knowledge/qa/evidence/session-2026-05-11/pytest_session_end.txt` — full pytest output

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/session-2026-05-11/
Files verified: 1
```
