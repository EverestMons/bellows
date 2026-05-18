# Bellows — QA verification for Rule 20 bold-tolerance fix (Step 2 recovery)
**Date:** 2026-05-17 | **Tier:** small | **Test Scope:** targeted | **Execution:** Step 1 (QA) | **pause_for_verdict:** after_step_1 | **Priority:** 30 | **auto_close:** false

## Context

The original plan `executable-rule-20-bold-tolerance-2026-05-17` had its Step 1 DEV completed and pushed (commit `f130573`), then halted before QA could run (auto_close type-safety crash). The fix is now live in gates.py:374. This plan is the QA recovery.

The DEV deposit lives at `bellows/knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md`. The halted original plan is at `bellows/knowledge/decisions/halted-executable-rule-20-bold-tolerance-2026-05-17.md` (untracked).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok"). Single-step QA-only recovery — no Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17.md", "bellows/knowledge/decisions/in-progress-executable-rule-20-bold-tolerance-qa-recovery-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_QA.md` and prior QA reports in `bellows/knowledge/qa/`.
>
> **Read the existing DEV deposit.** Open `bellows/knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md`. The DEV log records: gates.py:374 regex extended from `^\s*PASSED` to `^\s*\*{0,2}\s*PASSED`, 2 new tests added (`test_rule_20_gate_tolerates_bold_passed_line`, `test_rule_20_gate_tolerates_single_asterisk_passed_line`), 91 gate tests pass, commit SHA `f130573`. Verify each claim.
>
> **Task.**
>
> 1. **Regex extension in live source:** `grep -n "PASSED.*SELF-CHECK" bellows/gates.py`. Expected: line 374 containing `\*{0,2}`. Capture to `bellows/knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/grep_regex.txt`.
> 2. **New tests pass:** `pytest bellows/tests/test_gates.py::test_rule_20_gate_tolerates_bold_passed_line bellows/tests/test_gates.py::test_rule_20_gate_tolerates_single_asterisk_passed_line -v`. Capture to `pytest_new_tests.txt`. Both must pass.
> 3. **Full gate-test suite passes (regression):** `pytest bellows/tests/test_gates.py -v`. Capture to `pytest_gates.txt`. Expected: 91 passed per DEV log.
> 4. **Commit landed on main:** Read SHA `f130573` from DEV log, `git --no-pager log --oneline -10`, confirm SHA present in main history. Capture to `git_log.txt`. Anchor on SHA, NOT HEAD position.
> 5. **Reverse repro confirmation:** Build a Python REPL fixture demonstrating that the OLD regex (`r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'`) fails to match `**PASSED — SELF-CHECK PASSED**` while the NEW regex (`r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'`) succeeds. Run it and capture stdout to `bug_repro_verified.txt`. Use `re.search(...)` with `re.MULTILINE` to match production conditions.
>
> Write the QA report to `bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md` with the 5-row verification table. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values:
> - `plan_slug`: `executable-rule-20-bold-tolerance-qa-recovery-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/`
> - `required_evidence_files`: `["grep_regex.txt", "pytest_new_tests.txt", "pytest_gates.txt", "git_log.txt", "bug_repro_verified.txt"]`
>
> Emit the `PASSED — SELF-CHECK PASSED` line in BARE form (no bold markdown) per the canonical block — the bold-tolerance test lives in test_gates.py, not in this QA report's own self-check output. Include the literal stdout output of the block in the QA report. If FAILED, halt and report to CEO.
>
> **Deposit:**
> - `bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md`
> - All 5 evidence files in the evidence directory
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (QA report + 5 evidence files)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/qa/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation.**
