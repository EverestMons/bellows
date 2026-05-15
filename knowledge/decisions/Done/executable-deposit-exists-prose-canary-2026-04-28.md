# Bellows — Deposit-Exists Prose-Path Canary
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 5

## Context

Closes BACKLOG.md item logged 2026-04-23: `deposit_exists false positive on prose-embedded directory paths — status: likely resolved by restart, needs confirmation.` The original failure observed Gate 5 flagging two prose-only directory references on a Rule 26-compliant plan that already declared its real deposit via a declaration block.

Since 2026-04-23, the structural fix in `_extract_plan_required_deposits()` shipped (closed entry 2026-04-19 — the function now scopes to the declared block when present and ignores legacy prose patterns). The hypothesis is that the original failure ran against pre-fix code; the restart loaded the fix; subsequent plans never reproduced because they didn't exercise the same prose-distractor density.

This canary is the controlled test the BACKLOG entry asked for: a Rule 26-compliant plan with the same prose-distractor density that produced the original failure, run against current Bellows code post-restart. If `deposit_exists` does NOT trip on the prose paths, the structural fix is confirmed live and the BACKLOG item closes. If it trips, we have a fresh repro and the fix is incomplete or has regressed.

Test Scope: targeted — markdown-only plan, no production code changed. QA evidence is grep verification + git log, no pytest.

## Success Criteria

- Step 1 dispatch passes `deposit_exists` gate cleanly. The DEV step's prose contains the same bare directory references that produced the original failure (`bellows/knowledge/decisions/` and `bellows/knowledge/decisions/Done/`), AND a Rule 26 declaration block declaring the real deposit. The gate must extract only the declared deposit and ignore the prose paths.
- Step 2 (QA) passes `deposit_exists` cleanly on its own deposit declaration.
- Both steps pause at terminal state per disable-auto-close model. Planner performs Rule 22 verification and terminal Done/ move.
- BACKLOG item closes with reference to this plan.

## How to Run This Plan

Bellows watcher claims this plan automatically per current disable-auto-close behavior. After Step 1 produces its Output Receipt, Bellows evaluates gates and posts a verdict request. Planner reads the verdict, performs Rule 22 verification on the declared deposit, and resolves the verdict. Same flow for Step 2. After Step 2's verdict resolves clean, Planner performs the terminal Done/ move.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-deposit-exists-prose-canary-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-deposit-exists-prose-canary-2026-04-28.md")`. **Skip specialist file and glossary reads — this is a mechanical canary deposit, no Bellows code is modified.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Task:** Write a single short findings file at `bellows/knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md` containing 4–6 sentences describing what this canary tested and the prose-distractor pattern being exercised. The file content is brief and self-explanatory; it is the deposit, not the focus. **The structural test is THIS step's prose itself.** This step prose intentionally contains the prose-path distractors that produced the original 2026-04-23 false positive: bare directory references to bellows/knowledge/decisions/ and to bellows/knowledge/decisions/Done/. These directory paths are mentioned in this step's body and exist nowhere in the declaration block at the bottom of this step. If the live `_extract_plan_required_deposits()` correctly scopes to the declared block (per the 2026-04-19 fix), the gate evaluator will ignore these prose directory paths and only check the declared deposits. **Write the findings file using `Filesystem:write_file`** (preferred over Python heredoc per Rule 24 / canonical pattern). Content should describe: (a) the BACKLOG item this canary closes, (b) the exact prose distractors used (the two directory paths above), (c) the expected gate behavior (extract only declared deposit, ignore prose), (d) the date and Bellows generation. **Deposit dev log** at `bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md` with: (1) the verbatim findings file content written, (2) confirmation that the findings file exists post-write via `Filesystem:get_file_info`, (3) any anomalies. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md && git commit -m "test: deposit-exists prose-path canary — findings + dev log"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md`
> - `bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md`

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is a mechanical verification of a markdown deposit, no domain content.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **FIRST — Deliverable Verification (Rule 17).** Read Step 1's dev log files-deposited list. For EACH listed file: verify it exists on disk and contains the described content. Specifically grep the findings file for the canary's signature phrase ("deposit-exists prose-path canary" or similar) to confirm it isn't empty or truncated. Pipe the grep output to `bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/grep_findings_file.txt`. Run `git --no-pager log --oneline -3 -- bellows/knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md > bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/git_log.txt` to confirm Step 1's commit landed. Build a verification table with columns `| Deliverable | Expected | Status | Evidence |` listing the findings file, the dev log, and Step 1's commit; cite evidence file paths in the Evidence column. **Deposit QA report** at `bellows/knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md` containing the verification table and a one-paragraph summary stating whether `deposit_exists` tripped on prose paths during Step 1 dispatch (this is observable from the Bellows log / verdict request body for Step 1 — if Step 1's verdict shows zero `deposit_exists` failures, the BACKLOG item closes; if it shows any prose-path failure, the canary failed and the item stays open). **Run the Rule 20 self-check** at the very end of the QA report. Use `plan_slug = "executable-deposit-exists-prose-canary-2026-04-28"`, `qa_report_path = "bellows/knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md"`, `evidence_dir = "bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/"`, and `required_evidence_files = ["grep_findings_file.txt", "git_log.txt"]`. Include the literal stdout of the self-check in the QA report. If the self-check prints `FAILED`, STOP and report. If `PASSED`, proceed. **Update PROJECT_STATUS.md** at `bellows/PROJECT_STATUS.md` — add a completed milestone entry under the appropriate section noting "Closed BACKLOG item: deposit_exists false-positive prose-path — confirmed structural fix holds via canary 2026-04-28. Reference: `executable-deposit-exists-prose-canary-2026-04-28`." Use `Filesystem:read_text_file` to find the right anchor line and `Desktop Commander:edit_block` to insert. **Append prompt feedback** to `bellows/knowledge/research/agent-prompt-feedback.md` per standard protocol. **Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/ PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: deposit-exists prose-path canary — verified, BACKLOG item closeable"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/grep_findings_file.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/git_log.txt`
