# Bellows — _parse_diff_stat Path Truncation Fix
**Date:** 2026-05-26 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_each_step

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2.

**Bootstrap:** `Read the plan at /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/executable-parse-diff-stat-truncation-fix-2026-05-26.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.`

## CEO Context

`_parse_diff_stat` at `bellows.py:702-755` runs `git diff --stat --relative <pre_diff> -- .` to populate the `files_changed` list consumed by `_gate_scope_check` and `_gate_file_change_audit`. `git diff --stat` truncates long file paths with a `...` prefix when paths exceed git's default terminal-width column allocation. This produced false-positive scope_check trips on two plans this session:

1. **The original Rule 21 plan** (2026-05-25): scope_check tripped on what was hypothesized to be the dev log deposit not being mentioned in step text. The prior diagnostic (`scope-check-text-mention-audit-2026-05-26.md`) empirically disproved the hypothesis — the deposit path WAS mentioned — but couldn't identify the actual tripping file because `_consume_verdicts` had already destroyed the gate_result evidence.

2. **The verdict-ledger-gate-result-preservation diagnostic plan** (2026-05-26, this session): scope_check tripped with `out-of-scope files: ...t-ledger-gate-result-preservation-2026-05-26.md`. The `...` prefix appears literally in the `## Files Changed` section of the verdict request file — confirmed it's a writer-side artifact, not display truncation. Direct Planner verification: running `_gate_scope_check` against the same plan_text with the correct non-truncated path produces `failures: []`. Running `git --no-pager diff --stat=300 --relative HEAD~2 -- .` shows full paths.

Root cause: `git diff --stat` defaults to ~80-column terminal width and truncates filenames longer than the column allocation with `...` prefix. The bellows code at bellows.py:712 invokes git without specifying a column width, so any file path longer than git's default budget gets truncated, and the resulting string is fed to scope_check verbatim.

Fix: specify `--stat=300` (or wider) on the git command line. 300 chars accommodates any reasonable nested project path. Verified empirically this session: `git --no-pager diff --stat=300 --relative HEAD~2 -- .` produces full untruncated paths for the same files that were truncated with the default invocation.

This is a one-parameter change. `_parse_diff_stat` is referenced in `tests/test_bellows.py` only (verified via `grep -rln "_parse_diff_stat" tests/`), so targeted scope is acceptable per Rule 21 contract-change carve-out — the QA prompt explicitly names this test file.

**Self-recursion note for the Planner.** This plan's Step 1 will produce a dev log at `bellows/knowledge/development/parse-diff-stat-truncation-fix-2026-05-26.md` and Step 2 will produce a QA report at `bellows/knowledge/qa/executable-parse-diff-stat-truncation-fix-2026-05-26.md` plus evidence files. Both deposit paths are long enough to risk the very truncation bug this plan fixes — the gate run for each step will use the pre-fix daemon code (since the daemon does not hot-reload). Expect scope_check FAIL on one or both steps with a `...`-prefixed truncated path. Substance check (b) is the operative verification; Rule 22 override is the explicit escape hatch when substance is verified but the gate fired correctly to surface an anomaly (here: the very anomaly being fixed). The Planner issues a continue verdict with override reasoning when this occurs.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/executable-parse-diff-stat-truncation-fix-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-executable-parse-diff-stat-truncation-fix-2026-05-26.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip the domain glossary read — this is a mechanical one-parameter git command fix.
>
> **Task.** Modify `_parse_diff_stat` in `bellows/bellows.py` so the `git diff --stat` invocation uses a wide column allocation that prevents git's default ~80-column path truncation. Change the subprocess argument list to use `--stat=300` instead of `--stat`. The current invocation is at approximately bellows.py:712 (`["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."]`); change `--stat` to `--stat=300`. Do NOT change any other arguments. Do NOT change the function signature, return shape, or any other code path.
>
> **Why 300.** Empirically verified this session: `git --no-pager diff --stat=300 --relative HEAD~2 -- .` produces full untruncated paths in the bellows worktree. 300 chars accommodates any plausible nested-project path including governance-root absolute paths up to ~280 chars plus padding. Going higher is harmless but unnecessary.
>
> **Deposits.**
> - `bellows/knowledge/development/parse-diff-stat-truncation-fix-2026-05-26.md` — dev log per Rule 8 split-commit pattern. Document the one-line change, cite the before/after diff in the file, note the empirical verification command used to choose 300, and update the file's Output Receipt.
>
> **Commits.** Standard commit in the bellows repo: `git add bellows.py knowledge/development/parse-diff-stat-truncation-fix-2026-05-26.md && git commit -m "fix(bellows): widen _parse_diff_stat stat column to prevent path truncation"`. Do NOT push — Planner handles all push activity at session-wrap.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **FIRST — before doing anything else, verify Step 1 completion:** Read `bellows/knowledge/development/parse-diff-stat-truncation-fix-2026-05-26.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. Skip the domain glossary read — this is a mechanical verification.
>
> **FIRST — Deliverable Verification.** Read the Step 1 Output Receipt's "Files Created or Modified (Code)" list. For each file: verify it exists on disk and contains the described change. Specifically `grep -n "stat=300" bellows/bellows.py` should return the modified line. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If ANY item is ❌, attempt to fix (re-commit, re-create) before proceeding; if unfixable, stop and report to CEO — do NOT move plan to Done.
>
> **Test execution.** Run targeted tests for `_parse_diff_stat`: `pytest tests/test_bellows.py -k parse_diff_stat -v` (this is the only test file that references the function — verified via `grep -rln _parse_diff_stat tests/` before plan authoring). Deposit raw output to `bellows/knowledge/qa/evidence/executable-parse-diff-stat-truncation-fix-2026-05-26/pytest_targeted.txt`. All tests must pass.
>
> **Integration verification.** Run the empirical command in the bellows worktree to confirm the fix produces full paths: `cd /Users/marklehn/Developer/GitHub/bellows && git --no-pager diff --stat=300 --relative HEAD~5 -- . > knowledge/qa/evidence/executable-parse-diff-stat-truncation-fix-2026-05-26/git_diff_stat_output.txt`. Inspect the output and confirm no `...` prefixes appear on filename portions (the divider `|` and the histogram bars are not filename truncation). Document the inspection in the QA report.
>
> **QA report.** Deposit at `bellows/knowledge/qa/executable-parse-diff-stat-truncation-fix-2026-05-26.md` with a verification table covering: (a) deliverable verification, (b) pytest targeted results, (c) integration verification (no `...` prefixes), (d) Rule 20 self-check results. Cite evidence file paths in each row.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values:
> - `plan_slug`: `executable-parse-diff-stat-truncation-fix-2026-05-26`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/executable-parse-diff-stat-truncation-fix-2026-05-26.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-parse-diff-stat-truncation-fix-2026-05-26/`
> - `required_evidence_files`: `[pytest_targeted.txt, git_diff_stat_output.txt]`
>
> Include literal stdout in the QA report. If FAILED, halt and report to CEO.
>
> **Final.** Update `bellows/PROJECT_STATUS.md` — add a completed milestone entry summarizing the fix (one parameter change in `_parse_diff_stat`, root cause of two scope_check false-positive trips this session). Commit with: `git add knowledge/qa/ knowledge/qa/evidence/ PROJECT_STATUS.md && git commit -m "qa: parse-diff-stat truncation fix verified"`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
