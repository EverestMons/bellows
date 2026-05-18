# Bellows — QA verification for auto_close type-safety fix (Step 2 recovery)
**Date:** 2026-05-17 | **Tier:** small | **Test Scope:** targeted | **Execution:** Step 1 (QA) | **pause_for_verdict:** after_step_1 | **Priority:** 20 | **auto_close:** false

## Context

The original plan `executable-auto-close-type-safety-2026-05-17` had its Step 1 DEV completed and pushed (commit `9e79e4d`), then halted before QA could run — the very bug this plan was fixing crashed Bellows mid-dispatch. The fix is now live in bellows.py:458 (verified post-restart). This plan is the QA recovery.

The DEV deposit lives at `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md`. The halted original plan is at `bellows/knowledge/decisions/halted-executable-auto-close-type-safety-2026-05-17.md` (untracked, kept for audit).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok"). Single-step QA-only recovery — no Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-auto-close-type-safety-qa-recovery-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — QA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-auto-close-type-safety-qa-recovery-2026-05-17.md", "bellows/knowledge/decisions/in-progress-executable-auto-close-type-safety-qa-recovery-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_QA.md` and prior QA reports in `bellows/knowledge/qa/`.
>
> **Read the existing DEV deposit.** Open `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md`. The DEV log records: bellows.py:458 patched with `str()` wrap, full audit of 5 files (only 1 site needed fix, 9 other sites cleared with disposition reasons), 2 new tests added (`test_auto_close_yaml_bool_does_not_crash`, `test_auto_close_yaml_bool_false`), pytest passed (106 test_bellows.py + broader suite with 2 pre-existing unrelated failures), commit SHA `9e79e4d`. Verify each claim.
>
> **Task.**
>
> 1. **Patch present in live source:** `grep -n 'effective_auto_close' bellows/bellows.py`. Expected: a line containing `str(header.get("auto_close", "false")).lower() == "true"`. Capture to `bellows/knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/grep_patch.txt`.
> 2. **Audit list spot-check:** For three of the audit items the DEV log marked as "no fix needed" — sites #2 (`pause_for_verdict` no-lower), #5 (`gates.py:100` regex match group), and #7 (`gates.py:391` regex match group) — grep each file/line and verify the disposition reason still matches reality. Capture each grep output to `audit_spot_<n>.txt` for n in {2, 5, 7}.
> 3. **New tests run and pass:** `pytest bellows/tests/test_bellows.py::test_auto_close_yaml_bool_does_not_crash bellows/tests/test_bellows.py::test_auto_close_yaml_bool_false -v`. Capture to `pytest_new_tests.txt`. Both must pass.
> 4. **Targeted suite passes:** `pytest bellows/tests/test_bellows.py`. Capture to `pytest_test_bellows.txt`. Expected: clean pass (per DEV log: 106 passed).
> 5. **Commit landed on main:** Read SHA `9e79e4d` from DEV log, `git --no-pager log --oneline -10`, confirm SHA present in main history. Capture to `git_log.txt`. Anchor on the SHA, NOT HEAD position.
> 6. **Reverse repro confirmation:** Build a Python REPL fixture demonstrating the OLD code (`header.get("auto_close", "false").lower()` where `header = {"auto_close": True}`) raises AttributeError, while the NEW code (`str(header.get("auto_close", "false")).lower()`) returns `"true"` cleanly. Run it and capture stdout+stderr to `bug_repro_verified.txt`.
> 7. **Live canary check:** This very plan uses bold-Markdown headers, not YAML frontmatter — chosen deliberately to avoid exercising the fixed code path on the post-recovery dispatch. Confirm this fact in a paragraph in the QA report. No evidence file needed; this is documentation.
>
> Write the QA report to `bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md` with the 7-row verification table. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values:
> - `plan_slug`: `executable-auto-close-type-safety-qa-recovery-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-auto-close-type-safety-qa-recovery-2026-05-17/`
> - `required_evidence_files`: `["grep_patch.txt", "audit_spot_2.txt", "audit_spot_5.txt", "audit_spot_7.txt", "pytest_new_tests.txt", "pytest_test_bellows.txt", "git_log.txt", "bug_repro_verified.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO.
>
> **Deposit:**
> - `bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md`
> - All 8 evidence files in the evidence directory
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (QA report + 8 evidence files)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/qa/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation.**
