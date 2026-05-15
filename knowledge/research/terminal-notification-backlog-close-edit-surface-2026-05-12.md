# Terminal+Notification BACKLOG Close — Edit-Surface Audit

**Diagnostic:** `diagnostic-terminal-notification-backlog-close-edit-surface-2026-05-12`
**Step:** 1
**Date:** 2026-05-12
**Source file:** `knowledge/BACKLOG.md`

---

## Question 1 — Locate the Open entry

**Task:** Find the bullet starting `2026-04-19: terminal output redesign + notification audit` and quote it verbatim with line numbers.

**Start line:** 11
**End line:** 11

The entry is a single line with no sub-bullets. Verbatim:

```
- 2026-04-19: terminal output redesign + notification audit — current terminal format has no visual hierarchy; heartbeats, plan lifecycle events, gate results, and error states all have equal visual weight. Heartbeats dominate the scroll at 60s cadence. Plan events don't group visually (6+ consecutive lines per plan lifecycle). Inconsistent timestamps (heartbeats have them, plan events don't). Activity-canary message "60s elapsed, last output 60s ago" reads ambiguously. Proposed decomposition: (a) diagnostic plan auditing current terminal output mechanism and event types, (b) design plan proposing severity-coded format with heartbeat suppression, plan event grouping, and consistent timestamps, (c) implementation plan. Parallel concern: Pushover notification structure audit — what triggers a push, what the payload contains, whether multi-plan sessions coalesce. Classify as quality-of-life, not reliability — defer until BACKLOG #1, #4, #5, and verdict lifecycle coupling ship.
```

No trailing blank line belongs to this entry specifically — the blank line at line 12 is the inter-bullet separator shared with the following entry.

---

## Question 2 — Line immediately before the Open entry

**Line number:** 10
**Content:** *(blank line)*

```

```

This blank line is the inter-bullet separator between the `2026-05-05: bellows-self parallel/concurrent activity exposure` entry (line 9) and the target entry (line 11).

---

## Question 3 — Line immediately after the Open entry

**Line number:** 12
**Content:** *(blank line)*

```

```

This blank line is the inter-bullet separator between the target entry (line 11) and the `2026-04-19: plan fixing bug X tripped bug X during its own close` entry (line 13).

---

## Question 4 — Top of Closed section

**Line 17:** `## Closed`
**Line 18:** *(blank line)*
**Line 19:** `- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19). Stale entry — structurally fixed by the 2026-05-10 Rule 20 single-source migration (governance commit `a109e47`, bellows commit `b05dc42`). Diagnostic at `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md` confirmed: (a) the current canonical block at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` uses placeholder-enforced absolute paths (`<absolute-path-to-qa-report.md>`, `<absolute-path-to-evidence-dir>/`) with no `bellows/` prefix anywhere; (b) the Planner no longer authors the Rule 20 block in plans, eliminating the original failure surface; (c) population audit of 17 post-migration QA reports (2026-05-10 and 2026-05-11) showed Rule 20 self-check PASSED in 17/17 with zero path-resolution failures. The companion pattern entry in `agent-prompt-feedback.md` (PATH-001 at line ~399) was updated to CLOSED in the same plan. Reference: `Done/diagnostic-path-001-rule-20-staleness-audit-2026-05-11.md`, `Done/diagnostic-path-001-hygiene-close-edit-surface-2026-05-11.md`, `Done/executable-rule-20-single-source-2026-05-10.md`.`
**Line 20:** *(blank line)*
**Line 21:** `- **Closed 2026-05-11 (hygiene):** Bellows-side parser fix-plans trip own bug (originally 2026-05-11). Recommended fix (governance combination 1+4) shipped via PLANNER_TEMPLATE v4.38 (`executable-planner-template-parser-self-trip-and-session-wrap-2026-05-11`, governance-root commit `4e54c02`). The new paragraph in the Restart Discipline subsection documents the structural inevitability of the QA-step gate trip on Bellows-side parser fix-plans, names the 5 affected parsers (`_extract_step_text`, `_gate_is_qa_step`, `extract_total_steps`, `_extract_step_text_from_plan`, `strip_fenced_code_blocks`), describes the correct CEO override pattern, and references the bait-laden canary verification post-restart. Lessons row also appended capturing both today's reproductions (commits `4d57fd3` and `0fab609`) and the meta-lesson that fix-plan correctness depending on code that does not load until after plan completion makes the gate trip a known cost rather than a defect. No code fix shipped — governance-only per the recommended combination. Reference: `Done/executable-planner-template-parser-self-trip-and-session-wrap-2026-05-11.md`, PLANNER_TEMPLATE v4.38 Restart Discipline subsection.`

---

## Question 5 — Count of Open bullets before edit

**Count:** 3

The three Open bullets are:
1. Line 9: `- 2026-05-05: bellows-self parallel/concurrent activity exposure...`
2. Line 11: `- 2026-04-19: terminal output redesign + notification audit...` *(target for removal)*
3. Line 13: `- 2026-04-19: plan fixing bug X tripped bug X during its own close...`

After the executable runs, the count should be **2**.

---

## Question 6 — Recommended anchor strings

### Anchor A — Remove Open entry

**old_string** (lines 10–12, inclusive — blank line before, the bullet, blank line after):

```
verdict. Workaround for full isolation deferred at 2026-05-04 close: option (b) governance-root-worktree with subdirectory cwd (~50-80 LOC, may confuse agents expecting absolute paths). Reference: bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md (population audit), 2026-05-04 monorepo-worktree-fix close in this file's Closed section.

- 2026-04-19: terminal output redesign + notification audit — current terminal format has no visual hierarchy; heartbeats, plan lifecycle events, gate results, and error states all have equal visual weight. Heartbeats dominate the scroll at 60s cadence. Plan events don't group visually (6+ consecutive lines per plan lifecycle). Inconsistent timestamps (heartbeats have them, plan events don't). Activity-canary message "60s elapsed, last output 60s ago" reads ambiguously. Proposed decomposition: (a) diagnostic plan auditing current terminal output mechanism and event types, (b) design plan proposing severity-coded format with heartbeat suppression, plan event grouping, and consistent timestamps, (c) implementation plan. Parallel concern: Pushover notification structure audit — what triggers a push, what the payload contains, whether multi-plan sessions coalesce. Classify as quality-of-life, not reliability — defer until BACKLOG #1, #4, #5, and verdict lifecycle coupling ship.

- 2026-04-19: plan fixing bug X tripped bug X during its own close
```

**new_string** (remove the bullet, preserve one blank line between siblings):

```
verdict. Workaround for full isolation deferred at 2026-05-04 close: option (b) governance-root-worktree with subdirectory cwd (~50-80 LOC, may confuse agents expecting absolute paths). Reference: bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md (population audit), 2026-05-04 monorepo-worktree-fix close in this file's Closed section.

- 2026-04-19: plan fixing bug X tripped bug X during its own close
```

**Rationale:** Uses the tail of line 9 (unique in file) as the leading anchor and the head of line 13 (unique in the Open section) as the trailing anchor. The bullet on line 11 and one of the two inter-bullet blank lines are removed, preserving the single-blank-line spacing convention between the remaining Open entries.

---

### Anchor B — Insert Closed entry

**old_string** (lines 17–19, inclusive — Closed header + blank line + first bullet start):

```
## Closed

- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19).
```

**new_string** (insert the new 2026-05-12 entry between the header and the existing first bullet):

```
## Closed

- **Closed 2026-05-12:** Terminal output redesign + notification audit (originally 2026-04-19). Shipped as two implementation plans following the 2026-05-11 design diagnostic. Plan 1 (`Done/executable-terminal-capture-2026-05-12.md`, commit `b11ecc4`): added `_log()` helper with 5-level severity taxonomy (EVENT/INFO/WARN/ERROR/PAUSE), migrated 63 print() calls across `bellows.py`/`runner.py`/`notifier.py`, configured Python logging with RotatingFileHandler to `logs/terminal/bellows-YYYY-MM-DD.log` (14-day retention), heartbeat redesigned to 300s/state-bearing/suppression-during-activity, runner heartbeats now carry plan slug + step number, log rotation 14d terminal / 30d step JSON / 10MB planner-consultation. Plan 2 (`Done/executable-notification-coalescing-2026-05-12.md`, commit `07a87ad`): deleted 2 dead-code notification functions (`notify_escalation`, `notify_complete`), added 4 new named functions (`notify_plan_complete`, `notify_plan_halted`, `notify_plan_skipped`, `notify_queue_empty`), implemented urgency-gated coalescing buffer with 30s timer (verdict/failure push immediately, completions/halted/skipped/queue-empty buffer into a digest), migrated all 5 direct `notifier.push()` calls in `bellows.py` to named functions (0 remain), added `notifications` config block to `config.json` and `config.example.json` with backward-compatible defaults, Pushover priority/sound mapping per event type. CEO locked 5 design decisions on 2026-05-12: slug-tag-only plan grouping (no separator lines), combined heartbeat policy (300s state-bearing + 120s suppression), urgency-gated coalescing with 30s digest, 14d terminal log retention, 30d step JSON retention. Tests 268/269 pass (1 pre-existing `test_run_step_timeout` failure unrelated). Minor implementation deviation: `notify_plan_skipped` per-event priority -1 in design, but coalesced digest uses priority 0 since digests may contain higher-priority events. Reference: `Done/diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`, `Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`, `Done/executable-terminal-capture-2026-05-12.md`, `Done/executable-notification-coalescing-2026-05-12.md`.

- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19).
```

**Rationale:** The `## Closed` header is unique in the file (only one Closed section). The first bullet's opening phrase `- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence` is unique across all Closed entries. Together these form an unambiguous anchor. The new entry is inserted with a blank line after it, maintaining the one-blank-line-between-bullets convention.

---

## Output Receipt
**Agent:** Bellows Documentation Analyst
**Step:** 1 (diagnostic, single-step)
**Status:** Complete

### What Was Done
Read-only audit of `knowledge/BACKLOG.md` to capture the byte-level edit surface for closing the `2026-04-19: terminal output redesign + notification audit` Open entry. All 6 questions answered with verbatim quotes, line numbers, and two ready-to-use anchor string pairs for the executable.

### Files Deposited
- `knowledge/research/terminal-notification-backlog-close-edit-surface-2026-05-12.md` — edit-surface audit with anchor strings for BACKLOG Open→Closed move

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Anchor A uses the tail of the preceding bullet (line 9) and head of the following bullet (line 13) for unique match context
- Anchor B uses the `## Closed` header + first bullet opening phrase for unique match context
- One blank line removed (of two) when deleting the Open entry, preserving single-blank-line inter-bullet convention

### Flags for CEO
- None

### Flags for Next Step
- The Open entry is a single line (line 11) with no sub-bullets — the executable's removal operation is a simple single-line delete with surrounding context
- After removal, Open bullet count drops from 3 to 2
- The Closed entry text provided in the diagnostic is 1 very long line — the executable should use it verbatim from the diagnostic's Step 1 Task section
