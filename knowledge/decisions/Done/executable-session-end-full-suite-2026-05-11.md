# Bellows — Session-End Full Suite Run (2026-05-11)
**Date:** 2026-05-11 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (QA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Per Rule 21 session-level full suite, this plan runs the cumulative test suite after the session's two production fixes (`4d57fd3` fence-strip + `0fab609` line-anchor). Output is the ledger entry for this session's aggregate test state.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-session-end-full-suite-2026-05-11.md. Execute Step 1. After completing, STOP and wait for my confirmation.
```

---
---

## STEP 1 — Bellows QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-session-end-full-suite-2026-05-11.md", "bellows/knowledge/decisions/in-progress-executable-session-end-full-suite-2026-05-11.md")`. You are the Bellows QA agent. Skip the specialist file and domain glossary reads — this is a mechanical test-suite run. **Context.** Two production fixes shipped this session: commit `4d57fd3` (fence-strip across 4 parsers in `bellows.py`, `gates.py`, `verdict.py`; +5 tests) and commit `0fab609` (line-anchor across 3 parsers in `gates.py`, `verdict.py`; +3 tests). Per Rule 21, the session wrap requires a cumulative full-suite run captured to a session evidence directory. **Run.** From the bellows repo root: `cd bellows && python3 -m pytest 2>&1 | tee bellows/knowledge/qa/evidence/session-2026-05-11/pytest_session_end.txt`. The evidence directory may need to be created first via `mkdir -p`. Capture full output to the evidence file. Note the cumulative pass/fail count and any unexpected failures. The known pre-existing failure pattern is `test_run_step_timeout` — if it appears, mark as pre-existing in the QA report. **Pass criterion.** All non-pre-existing tests pass. New tests from commits `4d57fd3` and `0fab609` must be in the passing set (8 new tests total). **QA report.** Write a brief report at the path declared in Deposits. Structure: cumulative test count, pass/fail breakdown, pre-existing failures table (if any), new tests verified table, Rule 20 self-check banner. **Rule 20 self-check.** Run the canonical block from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug`: `executable-session-end-full-suite-2026-05-11`, `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/session-end-full-suite-qa-2026-05-11.md`, `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/session-2026-05-11/`, `required_evidence_files`: `["pytest_session_end.txt"]`. Include literal stdout. **No PROJECT_STATUS update.** The Planner handles the session-wrap PROJECT_STATUS entry separately after this QA report verifies green. **No move-to-Done.** Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Order of final operations (per Rule 23): evidence file → QA report → Rule 20 self-check → feedback append → final commit. **Deposits:**
> - `bellows/knowledge/qa/session-end-full-suite-qa-2026-05-11.md`
> - `bellows/knowledge/qa/evidence/session-2026-05-11/`
>
> **STOP. Wait for CEO confirmation.**

---
