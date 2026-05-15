# Bellows BACKLOG — Append Fix-Plan-Trips-Own-Bug Pattern Entry
**Date:** 2026-05-11 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. Test Scope: targeted — markdown-only edit to one file (BACKLOG.md); grep verification + git log + Rule 17 deliverable verification are sufficient.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-append-fix-plan-trips-own-bug-2026-05-11.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-backlog-append-fix-plan-trips-own-bug-2026-05-11.md", "bellows/knowledge/decisions/in-progress-executable-backlog-append-fix-plan-trips-own-bug-2026-05-11.md")`. You are the Bellows Documentation Analyst. Skip the specialist file and domain glossary reads — this is a mechanical BACKLOG.md append. **Context.** Today's session shipped two Bellows-side parser fixes (commits `4d57fd3` fence-strip + `0fab609` line-anchor) that addressed the "parser sees literal-in-prose" bug class. The fix-plans themselves tripped the very bug they were fixing because the running daemon was on pre-fix code. The line-anchor fix-plan required a CEO Rule 25 override on `rule_20_self_check` gate failure (its own QA step prose contained `## STEP N` inline references that tripped the unanchored regex). This is a recurring pattern worth logging as a Bellows-side BACKLOG item with Planner-side mitigation guidance — future Bellows-side parser fixes that affect plan-text parsing will exhibit the same failure mode. **Implementation.** Read `bellows/knowledge/BACKLOG.md` and locate the Open section. Append a new entry at the TOP of Open (most-recent-first ordering convention). Use the canonical Python file-write pattern: read the full file into memory, locate the `## Open` section header, insert the new entry as the first item after the section header, write the modified content back. Do NOT use `edit_block` for this — the BACKLOG.md content is large and the exact insertion point may have ambiguous anchors. Use `Filesystem:read_text_file` + `Filesystem:write_file` with explicit string manipulation. **New BACKLOG entry content (copy verbatim, preserving the 2-space indent on sub-bullets):**
> ```
> ### 2026-05-11: Bellows-side parser fix-plans trip the bug they fix until daemon restart
>
> **Observed behavior:** When a fix-plan modifies a Bellows-side parser that operates on plan text (e.g., `_extract_step_text`, `_gate_is_qa_step`, `extract_total_steps`, `strip_fenced_code_blocks`), the fix-plan's own prose is subject to the pre-fix bug while the daemon executes it. Bellows has no hot-reload, so the running daemon continues to execute pre-fix code through the entire fix-plan's lifecycle. The fix-plan's QA step prose often contains test-fixture descriptions or inline references that match the pattern the fix is correcting, tripping the very gate the fix repairs.
>
> **Two confirmed reproductions, 2026-05-11:**
>   - `executable-fence-strip-plan-text-parsers-2026-05-11` (commit `4d57fd3`) — gate failure on Step 2 (`rule_20_self_check`: "no QA deposit contains Rule 20 self-check banner"). Root cause: the unfixed daemon's `_extract_step_text` on Step 2 returned wrong step text because of inline `## STEP 2` references in Step 1's prose. CEO override via continue verdict.
>   - `executable-step-header-line-anchor-2026-05-11` (commit `0fab609`) — identical gate failure on Step 2, identical root cause. CEO override via continue verdict.
>
> **Operational impact:** Each occurrence requires CEO/Planner Rule 22 verification of the QA report, explicit override with reasoning, manual continue verdict deposit, and manual `Done/` move. Adds ~3-5 minutes of CEO attention per affected fix-plan. The override is correct (the fix is verifiably good), but the gate failure produces friction at exactly the moment the work is ready to ship.
>
> **Candidate fix shapes:**
>   1. **Planner-side mitigation (governance, no code).** Add a Planner-side rule: when authoring a Bellows-side fix-plan that modifies a plan-text parser, include an explicit warning in the plan header noting that the plan itself may trip the bug it fixes, and pre-document the override pattern in the plan. CEO knows what to expect; override happens faster.
>   2. **Code-side mitigation: scope-aware gate skip.** When Bellows dispatches a plan whose declared deposits include a Bellows source file (`bellows.py`, `gates.py`, `verdict.py`, `parser.py`), and the failing gate's evaluation depends on the code that plan is modifying, the gate is downgraded to advisory for that plan only. Risky — opens a self-exemption vector; agents could abuse it by claiming to modify Bellows code.
>   3. **Restart-before-shipping discipline.** Author fix-plans as DEV-only (no QA), commit the fix, restart Bellows, then dispatch a separate QA executable on the restarted daemon. Doubles the plan count for every Bellows-side fix.
>   4. **No code fix; document the pattern.** Accept the override pattern as a known cost of Bellows-side parser work. Add to the Bellows Restart Discipline subsection of PLANNER_TEMPLATE that fix-plans for plan-text parsers should expect a self-trip and pre-approve the override.
>
> **Recommended:** Combination of (1) + (4). (1) makes the failure expected; (4) makes the mitigation discoverable in governance.
>
> **Cross-reference:** LESSONS.md 2026-05-11 ("Bait-laden canaries verify Bellows-side fixes from both directions") for the post-restart verification side of this. Today's two false-positive overrides are the pre-restart side. The full lifecycle of a Bellows-side parser fix involves: (a) fix-plan trips own bug at QA step (this BACKLOG entry), (b) override + Done/ move, (c) daemon restart, (d) bait-laden canary verifies fix loaded (LESSONS.md entry).
> ```
> **Implementation constraints.** Do NOT modify any Open or Closed entries above or below the insertion point. Do NOT modify the section header or any other structural elements of BACKLOG.md. Preserve the existing newline conventions (one blank line between entries). After the write, run `grep -n "2026-05-11: Bellows-side parser fix-plans trip" bellows/knowledge/BACKLOG.md` to confirm the entry landed in the Open section. **Commit.** Single commit with message `docs: BACKLOG — fix-plan-trips-own-bug pattern (2026-05-11)`. Body cites both reproduction plan filenames. **Deposit dev log.** Brief dev log at the path in Deposits documenting: the new entry's line range in BACKLOG.md after the insert, the count of Open entries before and after (should be +1). Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/backlog-append-fix-plan-trips-own-bug-2026-05-11.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/backlog-append-fix-plan-trips-own-bug-2026-05-11.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows QA agent. Skip the specialist file and domain glossary reads — this is a markdown-only QA. **FIRST — Deliverable Verification.** (a) `grep -n "2026-05-11: Bellows-side parser fix-plans trip" bellows/knowledge/BACKLOG.md` — must return exactly one match. (b) `grep -n "^### " bellows/knowledge/BACKLOG.md` — capture the line numbers of all `### ` headers; verify the new entry's line number is in the Open section (before the `## Closed` header) and is the first `### ` entry after `## Open`. (c) `git --no-pager log -1 --stat bellows/knowledge/BACKLOG.md` — verify single commit with the expected message touching only BACKLOG.md. (d) `git --no-pager diff HEAD~1 -- bellows/knowledge/BACKLOG.md | head -100` — capture the diff and confirm only the new entry was added (no other lines modified). Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Capture each grep/git output to a separate file under `bellows/knowledge/qa/evidence/executable-backlog-append-fix-plan-trips-own-bug-2026-05-11/` (filenames: `grep_entry_present.txt`, `grep_header_positions.txt`, `git_log_stat.txt`, `git_diff.txt`). **Section structure check.** Confirm the Open section's entry count increased by exactly 1 from the prior commit's BACKLOG.md state: `git --no-pager show HEAD~1:bellows/knowledge/BACKLOG.md | awk '/^## Open/,/^## Closed/' | grep -c "^### "` and the same on the current HEAD. Difference must be exactly 1. Capture both counts to `evidence/section_count_delta.txt`. **No code or test verification.** This is a markdown-only edit; no production code or tests touched. No test suite run. **QA report deposit.** Write the QA report at the path declared in Deposits. Structure: top-level Deliverable Verification table, Section Structure Check section, Rule 20 Self-Check Results at the end. **Rule 20 Self-Check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `executable-backlog-append-fix-plan-trips-own-bug-2026-05-11`, `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/backlog-append-fix-plan-trips-own-bug-qa-2026-05-11.md`, `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-backlog-append-fix-plan-trips-own-bug-2026-05-11/`, `required_evidence_files`: `["grep_entry_present.txt", "grep_header_positions.txt", "git_log_stat.txt", "git_diff.txt", "section_count_delta.txt"]`. Include the literal stdout of the block in the QA report. If FAILED, halt and report to CEO. **No PROJECT_STATUS update.** This is a BACKLOG hygiene edit; the entry itself is the project status update. Skip the PROJECT_STATUS append. **STOP.** Do NOT move this plan to Done. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. Order of final operations (per Rule 23): evidence files → QA report → Rule 20 self-check → feedback append → final commit. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/qa/backlog-append-fix-plan-trips-own-bug-qa-2026-05-11.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-append-fix-plan-trips-own-bug-2026-05-11/`

---
