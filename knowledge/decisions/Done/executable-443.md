# on_failure canary #2 — post-fix clean auto-continue proof — Executable

**Type:** Executable
**Project:** bellows
**Depends on:** 442 (Done — the borderless-summary fix, now live post-restart).
**Created:** 2026-08-18
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** on_failure
**qa_steps:** 2
**known_failures:** 0
**Priority:** 10
**cycle_tier:** T0 — trivial doc-comment change; light preverify. REAL purpose: prove `on_failure` now auto-continues a clean plan end-to-end (both steps + auto-close, zero Planner verdicts) with the fixed test-result gate live.
**Deposit target:** `knowledge/decisions/executable-on-failure-canary2-2026-08-18.md`

---

## Purpose
Re-run the Fork-C canary after the 442 borderless fix + daemon restart. Under `pause_for_verdict: on_failure`, this plan MUST auto-continue STEP 1 → STEP 2 and auto-close to Done with NO verdict-request and NO Planner verdict — the fixed `_gate_qa_test_result` now parses the borderless full-suite summary and passes on a clean run. That end-to-end auto-continue IS the measurement.

## STEP 1 — DEV: document the content-based summary rationale at the gate site

`gates.py` — add a comment immediately ABOVE the `_PYTEST_SUMMARY_RE` definition (line ~726) documenting WHY it is content-based (borders optional): piped pytest output (`-q | cat`) writes a BORDERLESS counts line; a border-requiring regex fail-closes on clean suites. Cite the origin: "content-based per canary 441 finding / fix 442 — do not revert to `=+...=+` (border-based)." No logic change; comment only.

Run targeted (sanity — the gate tests must still pass): `python3 -m pytest tests/test_gate_qa_test_result.py -q 2>&1 | cat`

**Deposits:**
- `gates.py` (explanatory comment above `_PYTEST_SUMMARY_RE`)
- dev note: `knowledge/development/on-failure-canary2-dev-2026-08-18.md`

## STEP 2 — QA: full suite

Run the full suite: `python3 -m pytest tests/ -q 2>&1 | cat`. Deposit RAW output. Expect all pass (`known_failures: 0`); the fixed `_gate_qa_test_result` parses the borderless summary, sees `failed + errors = 0 <= 0`, and passes — enabling the auto-continue + auto-close that IS this canary.

**MANDATORY — Rule 20 self-check banner** (`## Rule 20 — QA Self-Check Results` + `**PASSED — SELF-CHECK PASSED**` verbatim, canonical block from `RULE_20_SELF_CHECK_BLOCK.md`). Values: `plan_slug`: `on-failure-canary2-2026-08-18`; `qa_report_path`: `<abs>/knowledge/qa/on-failure-canary2-qa-2026-08-18.md`; `evidence_dir`: `<abs>/knowledge/qa/evidence/on-failure-canary2-2026-08-18/`; `required_evidence_files`: `[full-suite.txt]`. FAILED → halt.

**Deposits:**
- `knowledge/qa/on-failure-canary2-qa-2026-08-18.md` — QA report
- `knowledge/qa/evidence/on-failure-canary2-2026-08-18/full-suite.txt` — raw full-suite stdout

---

## Scope / non-goals
One comment line in `gates.py`. No logic changed. Under `on_failure` with the fixed gate live, this plan must auto-continue both steps and auto-close to Done unattended — that behavior IS the canary result.
