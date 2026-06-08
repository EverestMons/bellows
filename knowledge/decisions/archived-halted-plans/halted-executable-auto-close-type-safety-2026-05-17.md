---
project: bellows
date: 2026-05-17
author: Planner
total_steps: 2
pause_for_verdict: after_step_1
priority: 20
test_scope: targeted
auto_close: false
---

# Bellows — `auto_close` type-safety hardening for YAML frontmatter
**Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-auto-close-type-safety-2026-05-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-auto-close-type-safety-2026-05-17.md", "bellows/knowledge/decisions/in-progress-executable-auto-close-type-safety-2026-05-17.md")`.
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_DEVELOPER.md` and `bellows/knowledge/architecture/ADR-structured-plan-metadata-2026-05-20.md` (the structured-plan-metadata ADR shipped earlier today). Compounds context across sessions.
>
> **Context.** The 2026-05-17 Track D session enabled YAML frontmatter as the authoritative plan header source. Plans now use `pyyaml.safe_load` to parse frontmatter. Two-line risk surfaced in the dev log: `bellows.py` calls `header.get("auto_close", "false").lower()` against a value that can now be a Python `bool` (from YAML `auto_close: true` or `auto_close: false`) rather than a string. `.lower()` on a bool raises `AttributeError`. New plans currently keep `auto_close` in bold-Markdown so the default string is used, but any future plan that uses YAML frontmatter AND specifies `auto_close` will crash Bellows mid-dispatch.
>
> **Task.**
>
> 1. Grep `bellows/bellows.py` for `header.get("auto_close"` and inspect every call site. There are at least two: search for `effective_auto_close = header.get("auto_close"`. For each site, wrap the get in `str()` before `.lower()`:
>
>    ```python
>    effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
>    ```
>
> 2. After patching `auto_close`, grep `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, and `runner.py` for the pattern `header.get(` followed by anywhere with `.lower()` in close proximity (within 5 lines). Audit every match for the same boolean-coercion risk. If any other field has the same `.lower()`-after-`header.get()` pattern, apply the same `str(...)` wrap. Per LESSONS 2026-05-10: when shipping a path-resolution (or in this case, type-coercion) fix, audit ALL call sites of the shared helper pattern, not just the one named in the bug report. List every audited call site in the dev log, including ones that did NOT need a fix and why (e.g., "site uses `== 'true'` directly, no `.lower()` called").
>
> 3. Add a defensive test in `bellows/tests/test_bellows.py`. Test name: `test_auto_close_yaml_bool_does_not_crash`. Build a YAML-frontmatter plan with `auto_close: true` (Python bool after pyyaml parse), invoke the auto-close evaluation path, confirm no `AttributeError` is raised and that `effective_auto_close` resolves to `True`. Add a second test `test_auto_close_yaml_bool_false` with `auto_close: false` and confirm `effective_auto_close` is `False`. If the auto-close evaluation is buried inside `run_plan()`, test it via the smallest extractable unit (e.g., a helper or by feeding a fake parsed header dict to a partial flow). If no such unit is extractable, add a parameterized test against a small inline reproduction.
>
> **Constraints.** No other refactors. Do not introduce a new helper function unless the existing call sites cleanly support extraction in <3 LOC. Do not change the bold-Markdown parser's behavior. This is a defensive type-coercion fix, not a feature.
>
> **After editing.** Run `pytest bellows/tests/` (targeted) and confirm all tests pass. Commit with message `fix(bellows): str-coerce header values before .lower() to tolerate YAML bool` and push to origin/main.
>
> **Deposit:**
> - `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md` — DEV log with: exact lines edited (before/after) for each call site, full audit list (every `header.get(...).lower()` site found across the 5 files, with disposition), new test names and assertions, pytest exit code, commit SHA.
>
> **Output Receipt.**
> - Files Created or Modified (Code): `bellows/bellows.py`, `bellows/tests/test_bellows.py`, plus any other files patched per the audit
> - Files Deposited:
>   - `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md`
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/development/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read `bellows/knowledge/development/2026-05-17-auto-close-type-safety-dev-log.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **Read your specialist file and domain glossary first.** Open `bellows/agents/BELLOWS_QA.md` and prior QA reports in `bellows/knowledge/qa/`.
>
> **Task.** Verify the type-safety fix.
>
> 1. **All call sites patched:** Read the DEV log's audit list. For every site listed as "patched", grep the file/line to confirm `str(...)` wrap is present. For every site listed as "audited, no fix needed", grep to confirm the disposition reason still holds. Capture each grep output to `bellows/knowledge/qa/evidence/executable-auto-close-type-safety-2026-05-17/grep_<site_n>.txt` (one file per audited site).
> 2. **New tests run and pass:** `pytest bellows/tests/test_bellows.py::test_auto_close_yaml_bool_does_not_crash bellows/tests/test_bellows.py::test_auto_close_yaml_bool_false -v`. Capture to `pytest_new_tests.txt`. Both must pass.
> 3. **Full bellows suite passes:** `pytest bellows/tests/`. Capture to `pytest_targeted.txt`.
> 4. **Commit landed:** Read commit SHA from DEV log, `git --no-pager log --oneline -10`, confirm SHA present. Capture to `git_log.txt`. Anchor on SHA, NOT HEAD position.
> 5. **Reverse repro check:** Confirm the bug WAS real. Read the DEV log's pre-fix snippet of `effective_auto_close = header.get("auto_close", "false").lower() == "true"`. If the DEV log shows that snippet plus a Python repro proving `.lower()` raised AttributeError on a bool, the bug is verified. Capture the repro evidence quote to `bug_repro_verified.txt`. If the DEV did NOT include a pre-fix repro, mark this row ❌ and STOP.
>
> Write the QA report to `bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md`. Verification table with all 5 checks. No hedging keywords in ✅ rows.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-auto-close-type-safety-2026-05-17`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-auto-close-type-safety-2026-05-17/`
> - `required_evidence_files`: `["pytest_new_tests.txt", "pytest_targeted.txt", "git_log.txt", "bug_repro_verified.txt"]` (note: the per-site grep files are also required deposits but listed dynamically based on the audit list count — list them all in this array)
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> **Daemon restart awareness.** This fix patches code loaded into the running Bellows daemon. Per LESSONS 2026-04-19, Bellows does NOT hot-reload. The CEO will need to restart Bellows after this plan closes for the fix to take effect in the live daemon. Note this explicitly in the QA report under "Operational Notes". Do not restart Bellows yourself.
>
> **Final housekeeping.** After Rule 20 PASSED, update `bellows/PROJECT_STATUS.md` with a one-line session entry. Then move the plan: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-auto-close-type-safety-2026-05-17.md", "bellows/knowledge/decisions/Done/executable-auto-close-type-safety-2026-05-17.md")`.
>
> **Deposit:**
> - `bellows/knowledge/qa/2026-05-17-auto-close-type-safety-qa.md`
> - All evidence files in `bellows/knowledge/qa/evidence/executable-auto-close-type-safety-2026-05-17/`
>
> **Output Receipt.**
> - Files Created or Modified (Code): none
> - Files Deposited: (QA report + all evidence files)
> - Receipt Status: Complete
>
> **Prompt Feedback.** If anything in this prompt was unclear, deposit a brief note to `bellows/knowledge/qa/agent-prompt-feedback.md`.
