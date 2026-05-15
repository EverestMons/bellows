**project:** bellows | **type:** executable | **steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

# Executable — Close terminal+notification BACKLOG entry

## Why this exists

The 2026-04-19 BACKLOG entry `terminal output redesign + notification audit` is complete. Two implementation plans shipped today:
- Plan 1 `Done/executable-terminal-capture-2026-05-12.md` (commit `b11ecc4`) — terminal output redesign + log capture
- Plan 2 `Done/executable-notification-coalescing-2026-05-12.md` (commit `07a87ad`) — notification coalescing + dead-code cleanup

This plan moves the Open entry to Closed with full provenance. Edit surface captured by the 2026-05-12 diagnostic at `Done/diagnostic-terminal-notification-backlog-close-edit-surface-2026-05-12.md`. Anchor strings are deterministic — no DEV inference required.

## Execution Map

Step 1 (Documentation Analyst) → Step 2 (Bellows QA)

## Step 1 — Documentation Analyst: BACKLOG close

You are the Bellows Documentation Analyst. Read `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` (or the closest match in `bellows/agents/`) before starting.

### Context

Two `Desktop Commander:edit_block` operations on `bellows/knowledge/BACKLOG.md`, then commit. Anchors are pre-validated by the 2026-05-12 edit-surface diagnostic. Do NOT freelance, do NOT modify the anchor strings, do NOT add other changes.

### Edit 1 — Remove Open entry

Use `Desktop Commander:edit_block` with:

**old_string**:
```

verdict. Workaround for full isolation deferred at 2026-05-04 close: option (b) governance-root-worktree with subdirectory cwd (~50-80 LOC, may confuse agents expecting absolute paths). Reference: bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md (population audit), 2026-05-04 monorepo-worktree-fix close in this file's Closed section.

- 2026-04-19: terminal output redesign + notification audit — current terminal format has no visual hierarchy; heartbeats, plan lifecycle events, gate results, and error states all have equal visual weight. Heartbeats dominate the scroll at 60s cadence. Plan events don't group visually (6+ consecutive lines per plan lifecycle). Inconsistent timestamps (heartbeats have them, plan events don't). Activity-canary message "60s elapsed, last output 60s ago" reads ambiguously. Proposed decomposition: (a) diagnostic plan auditing current terminal output mechanism and event types, (b) design plan proposing severity-coded format with heartbeat suppression, plan event grouping, and consistent timestamps, (c) implementation plan. Parallel concern: Pushover notification structure audit — what triggers a push, what the payload contains, whether multi-plan sessions coalesce. Classify as quality-of-life, not reliability — defer until BACKLOG #1, #4, #5, and verdict lifecycle coupling ship.

- 2026-04-19: plan fixing bug X tripped bug X during its own close
```

**new_string**:
```

verdict. Workaround for full isolation deferred at 2026-05-04 close: option (b) governance-root-worktree with subdirectory cwd (~50-80 LOC, may confuse agents expecting absolute paths). Reference: bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md (population audit), 2026-05-04 monorepo-worktree-fix close in this file's Closed section.

- 2026-04-19: plan fixing bug X tripped bug X during its own close
```

This removes the entire bullet at line 11 and one of the two surrounding blank lines, preserving the one-blank-line inter-bullet spacing convention.

### Edit 2 — Insert Closed entry

Use `Desktop Commander:edit_block` with:

**old_string**:
```
## Closed

- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19).
```

**new_string**:
```
## Closed

- **Closed 2026-05-12:** Terminal output redesign + notification audit (originally 2026-04-19). Shipped as two implementation plans following the 2026-05-11 design diagnostic. Plan 1 (`Done/executable-terminal-capture-2026-05-12.md`, commit `b11ecc4`): added `_log()` helper with 5-level severity taxonomy (EVENT/INFO/WARN/ERROR/PAUSE), migrated 63 print() calls across `bellows.py`/`runner.py`/`notifier.py`, configured Python logging with RotatingFileHandler to `logs/terminal/bellows-YYYY-MM-DD.log` (14-day retention), heartbeat redesigned to 300s/state-bearing/suppression-during-activity, runner heartbeats now carry plan slug + step number, log rotation 14d terminal / 30d step JSON / 10MB planner-consultation. Plan 2 (`Done/executable-notification-coalescing-2026-05-12.md`, commit `07a87ad`): deleted 2 dead-code notification functions (`notify_escalation`, `notify_complete`), added 4 new named functions (`notify_plan_complete`, `notify_plan_halted`, `notify_plan_skipped`, `notify_queue_empty`), implemented urgency-gated coalescing buffer with 30s timer (verdict/failure push immediately, completions/halted/skipped/queue-empty buffer into a digest), migrated all 5 direct `notifier.push()` calls in `bellows.py` to named functions (0 remain), added `notifications` config block to `config.json` and `config.example.json` with backward-compatible defaults, Pushover priority/sound mapping per event type. CEO locked 5 design decisions on 2026-05-12: slug-tag-only plan grouping (no separator lines), combined heartbeat policy (300s state-bearing + 120s suppression), urgency-gated coalescing with 30s digest, 14d terminal log retention, 30d step JSON retention. Tests 268/269 pass (1 pre-existing `test_run_step_timeout` failure unrelated). Minor implementation deviation: `notify_plan_skipped` per-event priority -1 in design, but coalesced digest uses priority 0 since digests may contain higher-priority events. Reference: `Done/diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`, `Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`, `Done/executable-terminal-capture-2026-05-12.md`, `Done/executable-notification-coalescing-2026-05-12.md`.

- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19).
```

### Commit

After both edits land, stage and commit. Use `Desktop Commander:start_process` with `timeout_ms: 5000`:

```
git add bellows/knowledge/BACKLOG.md && git commit -m "docs(backlog): close terminal output redesign + notification audit (2026-04-19) — shipped via Plan 1 (b11ecc4) + Plan 2 (07a87ad)"
```

Capture commit SHA for the dev log.

### Out of scope

- Do NOT modify any other BACKLOG entries.
- Do NOT modify any other file.
- Do NOT push to remote. Local commit only.

### Deliverables

- `bellows/knowledge/BACKLOG.md` updated (open entry removed, closure entry added at top of Closed)
- Dev log at `bellows/knowledge/development/terminal-notification-backlog-close-dev-log-2026-05-12.md` capturing:
  - Confirmation that both `edit_block` operations succeeded on first try (no anchor-match failures)
  - Commit SHA
  - Output Receipt

**Deposits:**
- `bellows/knowledge/development/terminal-notification-backlog-close-dev-log-2026-05-12.md`

## Step 2 — Bellows QA: Verify BACKLOG close

You are the Bellows QA specialist. Read `bellows/agents/BELLOWS_QA.md` before starting.

### Context

Step 1 moved the `2026-04-19: terminal output redesign + notification audit` entry from Open to Closed. Read the dev log at `bellows/knowledge/development/terminal-notification-backlog-close-dev-log-2026-05-12.md` to confirm what was done.

### Task

Markdown-only QA — no test suite, no PRAGMA.

1. **Open entry removed.**
   - 1a. Run `grep -n "2026-04-19: terminal output redesign" bellows/knowledge/BACKLOG.md`. Expected: 0 matches.
   - 1b. Run `grep -c "^- 20" bellows/knowledge/BACKLOG.md` scoped to the Open section (lines before `## Closed`). Expected: 2 (down from 3).

2. **Closed entry inserted.**
   - 2a. Run `grep -n "Closed 2026-05-12: Terminal output redesign" bellows/knowledge/BACKLOG.md`. Expected: exactly 1 match in the `## Closed` section.
   - 2b. Confirm the closure entry references all four artifacts: `Done/diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`, `Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`, `Done/executable-terminal-capture-2026-05-12.md`, `Done/executable-notification-coalescing-2026-05-12.md`.
   - 2c. Confirm the closure entry references both commits `b11ecc4` and `07a87ad`.

3. **Diff verification.**
   - 3a. Run `git diff HEAD~1 -- bellows/knowledge/BACKLOG.md` and confirm the diff shows ONLY: removal of the Open bullet + one surrounding blank line, and insertion of the new Closed bullet + one surrounding blank line. No other changes.

4. **Commit verification.**
   - 4a. Run `git log -1 --stat` and confirm exactly one file changed: `bellows/knowledge/BACKLOG.md`.
   - 4b. Confirm commit message starts with `docs(backlog): close terminal output redesign`.

5. **Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use:
   - `plan_slug`: `executable-terminal-notification-backlog-close-2026-05-12`
   - `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/terminal-notification-backlog-close-qa-2026-05-12.md`
   - `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-terminal-notification-backlog-close-2026-05-12/`
   - `required_evidence_files`:
     - `open_entry_removed.txt` — captured grep from 1a (zero matches)
     - `closed_entry_present.txt` — captured grep from 2a (one match)
     - `open_bullet_count.txt` — captured grep from 1b (expected 2)
     - `commit_log.txt` — captured `git log -1 --stat` from 4a

### Deliverables

- QA report at `bellows/knowledge/qa/terminal-notification-backlog-close-qa-2026-05-12.md` with verification table covering 1a–4b + 5, the literal Rule 20 self-check stdout, and an Output Receipt.
- Evidence directory at `bellows/knowledge/qa/evidence/executable-terminal-notification-backlog-close-2026-05-12/` containing the 4 files listed above.

**Deposits:**
- `bellows/knowledge/qa/terminal-notification-backlog-close-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/executable-terminal-notification-backlog-close-2026-05-12/`
