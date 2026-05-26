# PLANNER_TEMPLATE Rule 21 Contract-Change Carve-Out (v4.51)
**Date:** 2026-05-26 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_each_step

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2.

**Bootstrap:** `Read the plan at /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/executable-planner-template-rule-21-contract-change-2026-05-26.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.`

## CEO Context

Yesterday's LESSONS entry (2026-05-25, tagged `planner-discipline` and `rule-21`) captured a failure mode: the `executable-extract-plan-required-deposits-set-to-list-2026-05-25` plan declared `Test Scope: targeted` with justification "gates.py only, no cross-bucket regression risk." That justification was technically correct (production code change was bounded to one file), but the function being modified was tested across two test files. The targeted run passed 126/126; an unrelated full-suite run four hours later surfaced 6 regressions in `tests/test_rule_26_deposit_parser.py` that the targeted scope had missed. The set→list contract change had wider test coverage than its production-code locality suggested.

Rule 21's current "When to use each scope" table treats production-code locality as a proxy for test-coverage locality. That proxy is broken when a plan changes a function's contract (return type, parameter types, or semantic contract — not just internal logic). The fix: add a contract-change carve-out to Rule 21 that requires a pre-flight grep of test files for the function name, and forces `full-suite` scope when the function appears in more than one test file.

**Pre-write contradiction scan completed.** Keywords scanned: `contract`, `return type`, `targeted`, `full-suite`. No contradictions found. The existing Rule 21 text says targeted is appropriate when "the blast radius is bounded to the files being touched" — the new paragraph tightens this by distinguishing production-code blast radius from test-coverage blast radius. The two read consistently as cause-and-effect, not contradiction.

**Cost vs benefit:** ~5 seconds per plan for the grep check, vs. the cost of the 2026-05-25 reproduction (one extra plan cycle: ~30 minutes of dispatch + DEV + QA + Planner verification). Asymmetric in favor of the check.

**Test Scope: targeted** — governance markdown-only edit, no production code, no pytest scope per Rule 21's documented precedent for markdown-only plans (2026-04-20 Lessons row, Position A).

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/executable-planner-template-rule-21-contract-change-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-executable-planner-template-rule-21-contract-change-2026-05-26.md")`.
>
> You are the Bellows Documentation Analyst. Read your specialist file at `agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. Skip glossary read — this is a governance markdown edit task with no domain terminology surface. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Pre-edit verification.** Before any edits, confirm anchor presence in the target file `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md`. Run these greps and confirm each returns exactly one hit:
>
> 1. `grep -n "^### 21. Test scope must be declared in the plan header" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (anchor for Rule 21 location)
> 2. `grep -n "^\*\*Rule 21 relationship to Rules 17-20:\*\*" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (anchor for the closing paragraph — new content inserts BEFORE this)
> 3. `grep -n "^\*\*Version:\*\* 4.50$" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (anchor for version bump)
> 4. `grep -n "^\*\*Last Updated:\*\* 2026-05-25" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (anchor for date bump)
>
> If ANY anchor fails to produce exactly one hit, STOP and deposit a verification-mismatch report at `knowledge/research/anchor-mismatch-rule-21-contract-change-2026-05-26.md` listing the actual grep output. Do not proceed with edits.
>
> **Edit A — insert contract-change carve-out paragraph into Rule 21.** Use `Filesystem:edit_file` with this exact `oldText`:
>
> ```
> - If the QA agent believes the scope is wrong for the plan's actual changes (e.g., a `targeted` plan turned out to modify more files than expected), it must flag this in the QA report and request CEO guidance — it does NOT unilaterally upgrade to full-suite
>
> **Rule 21 relationship to Rules 17-20:**
> ```
>
> Replace with this exact `newText`:
>
> ```
> - If the QA agent believes the scope is wrong for the plan's actual changes (e.g., a `targeted` plan turned out to modify more files than expected), it must flag this in the QA report and request CEO guidance — it does NOT unilaterally upgrade to full-suite
>
> **Contract-change carve-out for `targeted` scope.** When a plan changes a function's contract — its return type, parameter types, or semantic contract (not just internal logic) — the `targeted` scope justification must consider where the function is TESTED, not just where it lives. Production-code locality is not a proxy for test-coverage locality. Before declaring `Test Scope: targeted` for a contract-change plan, the Planner runs `grep -rn "<function_name>" tests/` from the project root and counts the test files where the function appears. If the function appears in more than one test file, scope MUST be `full-suite` regardless of how mechanical the production-code change looks. If the function appears in exactly one test file, `targeted` is acceptable but the QA prompt MUST explicitly name that file in the test-execution instructions. The empirical evidence behind this carve-out: the 2026-05-25 `_extract_plan_required_deposits` set→list plan declared `targeted` with production-code locality justification, passed its targeted QA at 126/126, and four hours later an unrelated full-suite run surfaced 6 regressions in `tests/test_rule_26_deposit_parser.py` — a test file outside the targeted bucket that nonetheless tested the changed function's return-type contract. Cost of the grep at plan-authoring time: ~5 seconds. Cost of missing the grep: one full follow-up plan cycle plus session-end LESSONS capture. The asymmetry justifies the check as mandatory, not advisory.
>
> **Rule 21 relationship to Rules 17-20:**
> ```
>
> **Edit B — version bump.** Use `Filesystem:edit_file` with this exact `oldText`:
>
> ```
> **Version:** 4.50
> **Last Updated:** 2026-05-25 (v4.50)
> ```
>
> Replace with this exact `newText`:
>
> ```
> **Version:** 4.51
> **Last Updated:** 2026-05-26 (v4.51)
> ```
>
> **Edit C — Lessons row append.** Locate the Lessons Learned table at the end of `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md`. Read the file's last 30 lines via `tail` to identify the existing last Lessons row. Use `Filesystem:edit_file` to append a new row at the end of the table, using the existing last row as the anchor:
>
> Identify the existing last row's verbatim closing line (a `| 2026-XX-XX | <text> |` line followed by the table's closing `---` separator or end-of-file). Replace that anchor with itself, followed by a newline, followed by this new row:
>
> ```
> | 2026-05-26 | Rule 21 contract-change carve-out (v4.51). Yesterday's `_extract_plan_required_deposits` set→list plan declared `targeted` scope on production-code locality grounds and missed 6 regressions in `tests/test_rule_26_deposit_parser.py` — a test file outside the targeted bucket that tested the changed function's return-type contract. The targeted run passed 126/126; the regressions surfaced four hours later on an unrelated plan's full-suite run. Rule 21 now requires a pre-flight `grep -rn "<function_name>" tests/` for any plan that changes a function's return type, parameter types, or semantic contract; if the function appears in >1 test file, scope MUST be `full-suite`. Production-code locality is not a proxy for test-coverage locality. The asymmetry — 5 seconds of grep vs. one extra plan cycle — justifies the check as mandatory. **Family:** Sister lesson to the captured-but-not-internalized failure mode covered by the 2026-05-13 plan-write-time re-read trigger (LESSONS source D); both address the gap between rule-in-context and rule-fires-at-decision-point. |
> ```
>
> **Deposits:**
> - `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` (governance-root edit, three changes)
> - `bellows/knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` (dev log per Rule 8 split-commit pattern)
>
> **Commit pattern (Rule 8 split-commit for governance-root edits):**
>
> 1. From the governance root (`/Users/marklehn/Developer/GitHub/`), commit the PLANNER_TEMPLATE.md edits: `git add PLANNER_TEMPLATE.md && git commit -m "docs(planner-template): v4.51 — Rule 21 contract-change carve-out"`. Do NOT push.
> 2. From the bellows worktree, commit the dev log: `git add knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md && git commit -m "docs(planner-template): dev log for v4.51 Rule 21 carve-out"`. Do NOT push.
>
> **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Analyst. Read your specialist file at `agents/BELLOWS_QA.md` first. Skip glossary read — this is a governance markdown verification task.
>
> **Deliverable verification.** Verify every edit from Step 1 landed correctly. Run these checks and capture output to evidence files at `knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/`:
>
> 1. `grep -c "Contract-change carve-out for \`targeted\` scope" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/edit_a_carve_out.txt` — expect exactly `1`.
> 2. `grep -n "^\*\*Version:\*\* 4.51$" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/edit_b_version.txt` — expect exactly one hit with version 4.51.
> 3. `grep -n "^\*\*Last Updated:\*\* 2026-05-26" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/edit_b_date.txt` — expect exactly one hit with date 2026-05-26.
> 4. `grep -c "Rule 21 contract-change carve-out (v4.51)" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/edit_c_lessons_row.txt` — expect exactly `1`.
> 5. `grep -c "^\*\*Version:\*\* 4.50$" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/no_residual_v450.txt` — expect exactly `0` (residual version reference check).
>
> **Structural compliance checks.** Verify three properties of the edit:
>
> 1. **Carve-out positioned correctly:** the new paragraph appears AFTER the line containing `does NOT unilaterally upgrade to full-suite` and BEFORE the line beginning with `**Rule 21 relationship to Rules 17-20:**`. Capture via `grep -n -A 2 "does NOT unilaterally upgrade" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/structural_carve_out_position.txt`.
> 2. **No accidental disruption to surrounding rules:** verify Rule 20 still begins with `### 20. Mandatory QA self-check Python block` and Rule 22 still begins with `### 22. Planner verification of deposited files`. Capture via `grep -nE "^### (20|22)\." /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md > knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/structural_surrounding_rules.txt`.
> 3. **Two commits landed in the correct repos:** verify `git --no-pager log -1 --oneline` from `/Users/marklehn/Developer/GitHub/` shows the PLANNER_TEMPLATE commit, and `git --no-pager log -1 --oneline` from the bellows worktree shows the dev log commit. Capture both via `> knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/commit_verification.txt`.
>
> **Verification table** — produce in the QA report:
>
> | Deliverable | Expected | Status (✅/❌) | Evidence |
> |---|---|---|---|
> | Carve-out paragraph inserted | grep count = 1 | ... | `edit_a_carve_out.txt` |
> | Version bumped to 4.51 | exact match line | ... | `edit_b_version.txt` |
> | Last Updated date 2026-05-26 | exact match line | ... | `edit_b_date.txt` |
> | Lessons row appended | grep count = 1 | ... | `edit_c_lessons_row.txt` |
> | No residual v4.50 references | grep count = 0 | ... | `no_residual_v450.txt` |
> | Carve-out positioned between correct anchors | grep -A 2 shows new paragraph | ... | `structural_carve_out_position.txt` |
> | Surrounding rules 20 and 22 intact | both headers present | ... | `structural_surrounding_rules.txt` |
> | Two-commit split landed | governance commit + dev log commit | ... | `commit_verification.txt` |
>
> **Test scope justification:** `targeted` — governance markdown-only edit, no production code, no pytest run required per Rule 21's markdown-only precedent (2026-04-20 Lessons row, Position A).
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values:
>
> - `plan_slug`: `executable-planner-template-rule-21-contract-change-2026-05-26`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/executable-planner-template-rule-21-contract-change-2026-05-26.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/`
> - `required_evidence_files`: `["edit_a_carve_out.txt", "edit_b_version.txt", "edit_b_date.txt", "edit_c_lessons_row.txt", "no_residual_v450.txt", "structural_carve_out_position.txt", "structural_surrounding_rules.txt", "commit_verification.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend an entry under the topmost Completed section summarizing v4.51 (Rule 21 contract-change carve-out shipped, version bumped, Lessons row appended). Use `Filesystem:edit_file` with the existing topmost Completed entry as the anchor. Commit with message `docs: prepend v4.51 milestone to PROJECT_STATUS`.
>
> **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-planner-template-rule-21-contract-change-2026-05-26.md` (QA report)
> - `bellows/knowledge/qa/evidence/executable-planner-template-rule-21-contract-change-2026-05-26/` (8 evidence files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md` (milestone prepend — side effect, not listed as additional .md deposit per 2026-05-25 LESSONS one-md-deposit discipline)
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
