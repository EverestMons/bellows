# Corrective: test-result gate mis-parses borderless pytest summaries — Executable

**Type:** Executable
**Project:** bellows
**Depends on:** 439 (Done — shipped the gate this fixes). Canary 441 surfaced the defect.
**Created:** 2026-08-18
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** after_step_1
**qa_steps:** 2
**known_failures:** 0
**Priority:** 10
**cycle_tier:** T1 — small, fully-understood fix to the safety gate; the load-bearing verification is the new borderless-evidence regression test.
**Deposit target:** `knowledge/decisions/executable-qa-gate-borderless-fix-2026-08-18.md`

---

## Defect (canary 441, verified)
`_gate_qa_test_result` locates the pytest summary via `_PYTEST_SUMMARY_RE = re.compile(r'=+\s+.+\s+=+')` (`gates.py:726`) with `.match()` (`:765`) — it REQUIRES `=====` borders. Real piped pytest output (`-q | cat`) writes a BORDERLESS counts line (`1101 passed, 1 warning in 31.08s`); the only bordered line is `=== warnings summary ===` (no counts). So the gate matches the wrong line, finds no `passed`, and fail-closes on a genuinely clean suite. Fail-closed worked (safe pause, not auto-ship), but it makes `on_failure` unusable — every clean QA pauses. The unit tests missed this because they used synthetic bordered evidence.

## STEP 1 — DEV: content-based summary detection + borderless regression tests

`gates.py`:
- Replace `:726`: `_PYTEST_SUMMARY_RE = re.compile(r'\b\d+\s+(?:passed|failed|error|errors|xfailed|xpassed)\b')` — content-based, borders optional, matches the counts tokens (rejects `warnings summary`/`test session starts`/`collected N items`).
- Replace `:765`: use `_PYTEST_SUMMARY_RE.search(line.strip())` (NOT `.match` — a bordered line does not START with `\d`, and a borderless one does; `.search` handles both). The loop still takes the LAST matching line. The downstream `failed`/`error`/`passed` extraction is unchanged.

`tests/test_gate_qa_test_result.py` — add cases with BORDERLESS evidence (the exact gap):
- `test_borderless_clean_passes` — evidence `"collected 1101 items\n=== warnings summary ===\n1101 passed, 1 warning in 31.08s"` → gate PASSES (picks the counts line, not the warnings header; bad=0).
- `test_borderless_failed_pauses` — `"2 failed, 100 passed in 5s"` (no borders) → gate FAILS (bad=2 > 0).
- `test_borderless_zero_failed_with_errors` — `"0 failed, 5 passed, 3 errors in 2s"` (no borders) → gate FAILS (bad=3, the F-Cold2 class, borderless).
- `test_warnings_summary_header_not_matched` — a `=== warnings summary ===` line present but the borderless counts line is chosen.

Run targeted: `python3 -m pytest tests/test_gate_qa_test_result.py -q 2>&1 | cat`

**Deposits:**
- `gates.py` (`_PYTEST_SUMMARY_RE` content-based + `.search`)
- `tests/test_gate_qa_test_result.py` (borderless regression cases)
- dev note: `knowledge/development/qa-gate-borderless-fix-dev-2026-08-18.md`

## STEP 2 — QA: full suite

Run the full suite: `python3 -m pytest tests/ -q 2>&1 | cat`. Deposit RAW output. Expect all pass.

**Planner note (expected benign gate failure):** the LIVE daemon still runs the OLD (buggy) gate until it is restarted, so this QA step's own `qa_test_result` gate will fail-closed on its borderless evidence exactly as canary 441 did. The Planner overrides with verified-clean reasoning (reads the raw `full-suite.txt`), same as 441. The fix takes effect only after the CEO restarts the daemon; a fresh canary then confirms true clean auto-continue.

**MANDATORY — Rule 20 self-check banner** (`## Rule 20 — QA Self-Check Results` + `**PASSED — SELF-CHECK PASSED**` verbatim, canonical block from `RULE_20_SELF_CHECK_BLOCK.md`). Values: `plan_slug`: `qa-gate-borderless-fix-2026-08-18`; `qa_report_path`: `<abs>/knowledge/qa/qa-gate-borderless-fix-qa-2026-08-18.md`; `evidence_dir`: `<abs>/knowledge/qa/evidence/qa-gate-borderless-fix-2026-08-18/`; `required_evidence_files`: `[full-suite.txt]`. FAILED → halt.

**Deposits:**
- `knowledge/qa/qa-gate-borderless-fix-qa-2026-08-18.md` — QA report
- `knowledge/qa/evidence/qa-gate-borderless-fix-2026-08-18/full-suite.txt` — raw full-suite stdout

---

## Scope / non-goals
Two-line detection fix + regression tests. No change to the pause modes, the three-site guard, or the `bad = failed + errors` / fail-closed logic — those are correct. `pause_for_verdict: after_step_1` (NOT `on_failure`) because the live gate is buggy until this ships + a restart.
