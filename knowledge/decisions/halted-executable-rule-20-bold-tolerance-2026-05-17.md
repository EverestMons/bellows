---
project: bellows
date: 2026-05-17
author: Planner
total_steps: 2
pause_for_verdict: after_step_1
priority: 30
test_scope: targeted
auto_close: false
---

# Bellows — Rule 20 gate tolerates bold-Markdown `PASSED` line
**Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-rule-20-bold-tolerance-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-rule-20-bold-tolerance-2026-05-17.md", "bellows/knowledge/decisions/in-progress-executable-rule-20-bold-tolerance-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_DEVELOPER.md` and the structured-plan-metadata ADR at `bellows/knowledge/architecture/ADR-structured-plan-metadata-2026-05-20.md`. Compounds context.
>
> **Context.** The Anvil Cycle 13 Step 2 QA report ended with `**PASSED — SELF-CHECK PASSED**` (bold-Markdown). The `rule_20_self_check` gate in `bellows/gates.py` failed because its regex `r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'` does not tolerate leading `**`. The `\s*` portion matches whitespace but asterisks are not whitespace. The Planner issued a Rule 22 override; the report content was correct. This is the next instance of the parser-fragility class the ADR addresses, but on the `rule_20_self_check` gate which the Phase 1 prototype intentionally left untouched.
>
> **Task.**
>
> 1. Open `bellows/gates.py` and locate `_gate_rule_20_self_check`. The regex check is approximately at line ~270:
>
>    ```python
>    if re.search(r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
>    ```
>
>    Extend the regex to tolerate 0–2 leading asterisks (matching `**`, `*`, or no markdown emphasis). New regex:
>
>    ```python
>    if re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
>    ```
>
>    The added `\*{0,2}\s*` allows zero, one, or two asterisks followed by optional whitespace before `PASSED`. This is narrow by design — tolerates `**`, `*`, and bare. Per CEO decision 2026-05-17: do NOT broaden to tolerate other markdown emphasis tokens (underscores, etc.). Stay narrow.
>
> 2. Add a test in `bellows/tests/test_gates.py`. Test name: `test_rule_20_gate_tolerates_bold_passed_line`. Build a minimal QA report fixture with the banner `Rule 20 — QA Self-Check Results` followed by `**PASSED — SELF-CHECK PASSED**` (bold). Invoke `_gate_rule_20_self_check` (or `gates.check` with `is_qa_step=True`). Assert no `rule_20_self_check` failure is appended to the failures list.
>
> 3. Add a second test `test_rule_20_gate_tolerates_single_asterisk_passed_line` with `*PASSED — SELF-CHECK PASSED*` (italic-style). Same assertion shape.
>
> 4. Confirm the existing tests for the bare `PASSED — SELF-CHECK PASSED` form still pass (regression).
>
> **Constraints.** Single-line regex edit + 2 new tests. No other changes to `_gate_rule_20_self_check`. Do not modify the banner string (`Rule 20 — QA Self-Check Results` is byte-enforced — out of scope here). Do not modify `RULE_20_SELF_CHECK_BLOCK.md` — the canonical block already emits bare `PASSED`, this fix is only for QA reports where the banner gets bold-wrapped downstream (e.g., when QA agents copy the stdout into a bold-emphasized markdown line manually).
>
> **After editing.** Run `pytest bellows/tests/test_gates.py -v` (targeted, fast). Then `pytest bellows/tests/` (full bellows suite). Commit with message `fix(gates): rule_20_self_check tolerates 0-2 leading asterisks on PASSED line` and push to origin/main.
>
> **Deposit:**
> - `bellows/knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md` — DEV log with: before/after regex, new test names, pytest output excerpts, commit SHA.
>
> **Output Receipt.**
> - Files Created or Modified (Code): `bellows/gates.py`, `bellows/tests/test_gates.py`
> - Files Deposited:
>   - `bellows/knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md`
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/development/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read `bellows/knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_QA.md` and prior QA reports in `bellows/knowledge/qa/`.
>
> **Task.** Verify the Rule 20 regex extension.
>
> 1. **Regex extension in source:** `grep -n "PASSED.*SELF-CHECK" bellows/gates.py`. Expect to see the new pattern with `\*{0,2}`. Capture to `bellows/knowledge/qa/evidence/executable-rule-20-bold-tolerance-2026-05-17/grep_regex.txt`.
> 2. **New tests pass:** `pytest bellows/tests/test_gates.py::test_rule_20_gate_tolerates_bold_passed_line bellows/tests/test_gates.py::test_rule_20_gate_tolerates_single_asterisk_passed_line -v`. Capture to `pytest_new_tests.txt`. Both must pass.
> 3. **Existing tests pass (regression):** `pytest bellows/tests/test_gates.py -v`. Capture to `pytest_gates.txt`. All must pass.
> 4. **Full bellows suite passes:** `pytest bellows/tests/`. Capture to `pytest_targeted.txt`.
> 5. **Commit landed:** Read commit SHA from DEV log, `git --no-pager log --oneline -10`, confirm SHA present. Capture to `git_log.txt`. Anchor on SHA, NOT HEAD position.
> 6. **Reverse repro confirmation:** Build a Python REPL fixture demonstrating the OLD regex (`r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'`) fails on `**PASSED — SELF-CHECK PASSED**` while the NEW regex (`r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'`) succeeds. Run it and capture stdout to `bug_repro_verified.txt`. The fixture proves the bug class was real and the fix addresses it.
>
> Write the QA report to `bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md` with the 6-check verification table. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-rule-20-bold-tolerance-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-rule-20-bold-tolerance-2026-05-17/`
> - `required_evidence_files`: `["grep_regex.txt", "pytest_new_tests.txt", "pytest_gates.txt", "pytest_targeted.txt", "git_log.txt", "bug_repro_verified.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO. Emit the `PASSED — SELF-CHECK PASSED` line in BARE form (no bold), per the canonical block — bold output in this QA report would be ironic given the fix, but the test that proves bold-tolerance is in `test_gates.py`, not here.
>
> **Daemon restart awareness.** This fix patches `bellows/gates.py` loaded into the running Bellows daemon. Per LESSONS 2026-04-19, Bellows does NOT hot-reload. The CEO will need to restart Bellows after this plan closes for the fix to take effect. After daemon restart, a bait-laden canary (a tiny QA-step plan whose QA report uses `**PASSED — SELF-CHECK PASSED**`) would verify the patch is loaded. Mention the restart requirement explicitly in the QA report under "Operational Notes" — do not restart Bellows yourself, and do not deposit a canary plan.
>
> **Final housekeeping.** After Rule 20 PASSED, update `bellows/PROJECT_STATUS.md` with a one-line session entry. Then move the plan: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-rule-20-bold-tolerance-2026-05-17.md", "bellows/knowledge/decisions/Done/executable-rule-20-bold-tolerance-2026-05-17.md")`.
>
> **Deposit:**
> - `bellows/knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md`
> - All 6 evidence files in `bellows/knowledge/qa/evidence/executable-rule-20-bold-tolerance-2026-05-17/`
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (QA report + 6 evidence files)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/qa/agent-prompt-feedback.md`.
