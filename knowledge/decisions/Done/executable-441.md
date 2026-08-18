# on_failure canary — regression-guard test for the new pause mode — Executable

**Type:** Executable
**Project:** bellows
**Depends on:** 439 (Done) — the on_failure mode this canary exercises + guards.
**Created:** 2026-08-18
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** on_failure
**qa_steps:** 2
**known_failures:** 0
**Priority:** 10
**cycle_tier:** T0 — test-only, trivial; light mechanical preverify (no full drafting cycle). Its REAL purpose is the Fork-C canary: prove `on_failure` auto-continues a clean plan end-to-end in the LIVE daemon with zero manual verdicts.
**Deposit target:** `knowledge/decisions/executable-on-failure-canary-2026-08-18.md`

---

## Purpose
Dual: (1) add a real regression guard so `on_failure` cannot be silently dropped from the recognized modes; (2) serve as the live canary for plan 439 — run under `pause_for_verdict: on_failure` and confirm the daemon auto-continues both steps + auto-closes to Done, firing `notify_plan_complete`, with NO verdict issued by the Planner.

## STEP 1 — DEV: regression-guard test for on_failure

Add `tests/test_on_failure_canary.py`:
- `test_on_failure_in_recognized_tokens` — asserts `"on_failure"` is in `plan_lint.RECOGNIZED_PAUSE_TOKENS` (import from `scripts.plan_lint`).
- `test_header_says_pause_on_failure_returns_false` — asserts `bellows.header_says_pause({"pause_for_verdict": "on_failure"}, 1, 3, False)` is `False` and `...(..., is_qa_step=True)` is also `False` (a clean step never pauses from the header under this mode).
- `test_effective_auto_close_implied_by_on_failure` — documents the mode-implies-auto-close contract by asserting the `pause_for_verdict == "on_failure"` disjunct is present (either a direct expression test or a source-substring assertion on the `effective_auto_close` computation).

Run targeted: `python3 -m pytest tests/test_on_failure_canary.py -q 2>&1 | cat`

**Deposits:**
- `tests/test_on_failure_canary.py`
- dev note: `knowledge/development/on-failure-canary-dev-2026-08-18.md`

## STEP 2 — QA: full suite

Run the full suite: `python3 -m pytest tests/ -q 2>&1 | cat`. Deposit RAW output. Expect all pass (baseline `known_failures: 0`); the new test-result gate (`_gate_qa_test_result`) will parse this evidence and, with `failed + errors = 0 <= known_failures = 0`, pass — allowing the auto-continue that IS this canary.

**MANDATORY — Rule 20 self-check banner** (`## Rule 20 — QA Self-Check Results` + `**PASSED — SELF-CHECK PASSED**` verbatim, canonical block from `RULE_20_SELF_CHECK_BLOCK.md`). Values: `plan_slug`: `on-failure-canary-2026-08-18`; `qa_report_path`: `<abs>/knowledge/qa/on-failure-canary-qa-2026-08-18.md`; `evidence_dir`: `<abs>/knowledge/qa/evidence/on-failure-canary-2026-08-18/`; `required_evidence_files`: `[full-suite.txt]`. FAILED → halt.

**Deposits:**
- `knowledge/qa/on-failure-canary-qa-2026-08-18.md` — QA report
- `knowledge/qa/evidence/on-failure-canary-2026-08-18/full-suite.txt` — raw full-suite stdout

---

## Scope / non-goals
Adds one test file. No production code changed. Under `on_failure`, this plan must auto-continue both steps and auto-close to Done unattended — that behavior IS the canary measurement.
