# bellows — Close Stranded Plan + Session Close-Out
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation Agent)

## CEO Context

Two concerns bundled into one plan because both are documentation-agent housekeeping and neither needs QA. (1) The `executable-extract-primary-deposit-block-aware-2026-04-19.md` plan completed all real work (code shipped, 45/45 tests pass, Rule 20 self-check PASSED, PROJECT_STATUS already updated by the QA agent) but tripped Gate 5 on a directory path declared in its own `**Deposits:**` block and got stranded in `verdict-pending-` state. Rule 22 verification on the QA report PASSED — plan is legitimately complete. (2) Session close-out: update BACKLOG (close #6, add verdict lifecycle coupling, add terminal output redesign) and add three Lessons Learned entries to PLANNER_TEMPLATE covering the session's discoveries. No test scope needed — text edits only.

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-session-close-out-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP.
```

---
---

## STEP 1 — Documentation Agent

---

> Skip specialist file and glossary reads — this is a housekeeping task.
>
> **Sub-step A — Move stranded plan to Done.** The `executable-extract-primary-deposit-block-aware-2026-04-19.md` plan was renamed by Bellows to `verdict-pending-` prefix when Gate 5 tripped on a declared directory path. Rule 22 verification passed on the deposit — all real work completed correctly. Strip the prefix and move to Done:
>
> ```python
> import shutil
> shutil.move(
>     "bellows/knowledge/decisions/verdict-pending-executable-extract-primary-deposit-block-aware-2026-04-19.md",
>     "bellows/knowledge/decisions/Done/executable-extract-primary-deposit-block-aware-2026-04-19.md"
> )
> ```
>
> **Sub-step B — Close BACKLOG #6.** Read `bellows/knowledge/BACKLOG.md`. Locate the entry starting with `2026-04-18: deposit-path parser false positives` in the `## Open` section. Move the entire multi-paragraph entry to a new `## Closed` section at the bottom of the file, prepending the close date and resolution note: `**Closed 2026-04-19:** resolved by executable-rule-26-deposit-parser-scope-2026-04-19 (`_extract_plan_required_deposits` now prefers declared `**Deposits:**` block over legacy prose regexes) + executable-extract-primary-deposit-block-aware-2026-04-19 (`extract_primary_deposit` now reads block form for verdict file `Deposit:` field). 12 tests added total. Smoke-tested end-to-end 2026-04-19.` Place the closed entry at the top of a new `## Closed` section (or append if the section already has entries). Use `Desktop Commander:edit_block` for surgical removal from Open; append-write for Closed section.
>
> **Sub-step C — Add two new BACKLOG items to `## Open` section.** Append after the last existing Open entry:
>
> Entry 1:
> ```
> - 2026-04-19: verdict lifecycle coupling — when a plan reaches terminal state (Done or halted), automatically clean up any `verdict-request-<slug>-*.md` files in `verdicts/pending/` matching the plan's slug. Addresses the stranded-files problem (33 files observed 2026-04-18, ~6+ more added 2026-04-19) and establishes the plan-timeline → verdict-lifecycle link without adding a new folder. Implementation: add slug-matching sweep to the move-to-Done path in `bellows.py` and to the `halted-` rename path. Related to BACKLOG #1 (scope_check race produces the same class of stranded files) and "verdict mechanization" — cleanup is a prerequisite for reliable mechanized resolution. Optional follow-on: per-plan verdict sidecar (`.verdicts.jsonl` next to the plan in Done/) for audit-trail visibility — defer until lifecycle coupling is observed working.
> ```
>
> Entry 2:
> ```
> - 2026-04-19: terminal output redesign + notification audit — current terminal format has no visual hierarchy; heartbeats, plan lifecycle events, gate results, and error states all have equal visual weight. Heartbeats dominate the scroll at 60s cadence. Plan events don't group visually (6+ consecutive lines per plan lifecycle). Inconsistent timestamps (heartbeats have them, plan events don't). Activity-canary message "60s elapsed, last output 60s ago" reads ambiguously. Proposed decomposition: (a) diagnostic plan auditing current terminal output mechanism and event types, (b) design plan proposing severity-coded format with heartbeat suppression, plan event grouping, and consistent timestamps, (c) implementation plan. Parallel concern: Pushover notification structure audit — what triggers a push, what the payload contains, whether multi-plan sessions coalesce. Classify as quality-of-life, not reliability — defer until BACKLOG #1, #4, #5, and verdict lifecycle coupling ship.
> ```
>
> **Sub-step D — Add three Lessons Learned entries to PLANNER_TEMPLATE.md.** File path: `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Locate the `## Lessons Learned` table (the final row is dated `2026-04-18` covering Rule 26 v4.25). Read the current last row to use as the `old_string` anchor for a `Desktop Commander:edit_block` call that appends three new rows immediately after it. The three rows (add as pipe-delimited markdown table rows, verbatim format matching existing rows):
>
> Row 1:
> ```
> | 2026-04-19 | `**Deposits:**` blocks must list only files, not directories. The `deposit_exists` gate uses `os.path.isfile()` which returns False for directory paths. When Rule 20's self-check references an evidence directory with multiple files, the plan's `**Deposits:**` block should either (a) list each individual evidence file, or (b) omit the directory entirely and rely on Rule 20's self-check to enumerate the files. Do NOT list a directory path in the block. Observed failure: executable-extract-primary-deposit-block-aware-2026-04-19 tripped Gate 5 on its own declared evidence directory despite all real work completing correctly. Rule 22 verification on the QA report PASSED; plan was manually closed out. |
> ```
>
> Row 2:
> ```
> | 2026-04-19 | Bellows terminal "paused" lines can reflect stale verdict files, not active work. When Bellows's scope_check race (BACKLOG #1) orphans a verdict request file after the agent has already moved the plan to Done, the terminal continues to display the plan as paused even though it is complete. Rule 22 verification by reading the deposited QA report (which lives in `knowledge/qa/`, not in `verdicts/pending/`) is how the Planner distinguishes "plan actually complete with orphaned verdict" from "plan genuinely awaiting verdict." Always read the deposit before assuming the terminal's pause state is accurate. |
> ```
>
> Row 3:
> ```
> | 2026-04-19 | Bellows does not hot-reload code — restart is CEO responsibility after any `gates.py` / `verdict.py` / `parser.py` / `bellows.py` change. Observed this session when Step 1 DEV committed a `gates.py` fix but the Bellows daemon (started before the fix) continued running the pre-fix gate code, causing a false-positive gate trip on the plan's own QA step. CEO restarted Bellows; subsequent smoke test confirmed new code loaded. The Rule-26-live-gate-smoke-test pattern (deposit a tiny plan with intentional false-positive bait immediately after a code change to verify the new code is actually loaded) is a cheap, proven way to catch this without having to wait for a real plan to fail. Consider adding a Planner rule: after any Bellows-side code change, deposit a gate smoke test before shipping dependent executables. |
> ```
>
> **Sub-step E — Commit.** Stage BACKLOG.md, PLANNER_TEMPLATE.md (note the governance-root path), and the stranded plan move. Single commit with message: `chore: close BACKLOG #6, add verdict lifecycle + terminal redesign items, add 3 Lessons Learned, close stranded extract_primary_deposit plan`. Use `git --no-pager status` to verify before commit; use `git --no-pager log -1` to confirm after.
>
> **Deposits:**
> - none
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP.**
