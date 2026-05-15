**project:** bellows | **type:** diagnostic | **steps:** 1 | **pause_for_verdict:** always | **auto_close:** false

# Diagnostic — Terminal+notification BACKLOG entry edit-surface audit

## Why this exists

The 2026-05-12 implementation plans `Done/executable-terminal-capture-2026-05-12.md` (commit `b11ecc4`) and `Done/executable-notification-coalescing-2026-05-12.md` (commit `07a87ad`) shipped the full design from `Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`. The originating BACKLOG entry `2026-04-19: terminal output redesign + notification audit` is now complete and should be moved from Open to Closed.

Same shape as the PATH-001 hygiene close. Per that precedent, the Planner is forbidden from reading source code directly, but BACKLOG.md is markdown that the Planner can read. The Planner already read BACKLOG.md to pick this item at session start, but the file may have shifted since (the 2026-05-11 PATH-001 closure added entries). This diagnostic captures the current exact text of the terminal+notification Open entry, the current top-of-Closed structure, and proposes deterministic anchor strings for the executable.

The diagnostic is cheap (Planner-readable, no specialist code investigation) and prevents the same "DEV reads and matches at execution time" anti-pattern that earlier led to the PATH-001 edit-surface diagnostic.

## Step 1 — Documentation Analyst: capture BACKLOG edit surface

You are the Bellows Documentation Analyst. Read `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` (or the closest match in `bellows/agents/`) before starting.

### Context

Two markdown edits will be authored against `bellows/knowledge/BACKLOG.md`:
1. Remove the entire `2026-04-19: terminal output redesign + notification audit` bullet (and its sub-bullets, if any) from the `## Open` section.
2. Insert a new `**Closed 2026-05-12:**` entry at the TOP of the `## Closed` section, above the existing 2026-05-11 closures.

This diagnostic captures the byte-level structure so the executable can specify deterministic `Desktop Commander:edit_block` anchors. No edits made in this step — read-only audit.

### Task

Answer the following. Cite exact line numbers and quote verbatim.

1. **Locate the Open entry.** Read `bellows/knowledge/BACKLOG.md` and find the bullet starting `2026-04-19: terminal output redesign + notification audit`. Quote the ENTIRE bullet verbatim — including all sub-bullets, indentation, and the trailing blank line (if any) before the next sibling entry. Report the start and end line numbers.

2. **Line immediately before the Open entry.** Quote the line directly before the entry's first line. Report its line number. This is needed to build an unambiguous `old_string` anchor.

3. **Line immediately after the Open entry.** Quote the line directly after the entry's last line. Report its line number. This is the line the executable's removal anchor will preserve.

4. **Top of Closed section.** Quote the `## Closed` header line and the first 3 bullets that follow it (verbatim, with line numbers). The new closure entry will be inserted between the `## Closed` header and the current first bullet.

5. **Count of Open bullets before edit.** Run `grep -c "^- " bellows/knowledge/BACKLOG.md` scoped to the `## Open` section. Report the count. After the executable runs, the count should decrease by exactly 1.

6. **Recommended anchor strings.** Produce two ready-to-use `Desktop Commander:edit_block` operations:

   **Anchor A — Remove Open entry.** The exact multi-line `old_string` that uniquely identifies the entire bullet + enough surrounding context (typically 1 line above and 1 line below) for unambiguous match. The corresponding `new_string` that removes the bullet but preserves the surrounding context.

   **Anchor B — Insert Closed entry.** The exact multi-line `old_string` that includes the `## Closed` header + first 2-3 lines of existing closure entries (for unambiguous match). The corresponding `new_string` that prepends the new 2026-05-12 closure entry above the existing entries.

   The closure entry text to insert (use this verbatim in Anchor B's `new_string`):

   ```
   - **Closed 2026-05-12:** Terminal output redesign + notification audit (originally 2026-04-19). Shipped as two implementation plans following the 2026-05-11 design diagnostic. Plan 1 (`Done/executable-terminal-capture-2026-05-12.md`, commit `b11ecc4`): added `_log()` helper with 5-level severity taxonomy (EVENT/INFO/WARN/ERROR/PAUSE), migrated 63 print() calls across `bellows.py`/`runner.py`/`notifier.py`, configured Python logging with RotatingFileHandler to `logs/terminal/bellows-YYYY-MM-DD.log` (14-day retention), heartbeat redesigned to 300s/state-bearing/suppression-during-activity, runner heartbeats now carry plan slug + step number, log rotation 14d terminal / 30d step JSON / 10MB planner-consultation. Plan 2 (`Done/executable-notification-coalescing-2026-05-12.md`, commit `07a87ad`): deleted 2 dead-code notification functions (`notify_escalation`, `notify_complete`), added 4 new named functions (`notify_plan_complete`, `notify_plan_halted`, `notify_plan_skipped`, `notify_queue_empty`), implemented urgency-gated coalescing buffer with 30s timer (verdict/failure push immediately, completions/halted/skipped/queue-empty buffer into a digest), migrated all 5 direct `notifier.push()` calls in `bellows.py` to named functions (0 remain), added `notifications` config block to `config.json` and `config.example.json` with backward-compatible defaults, Pushover priority/sound mapping per event type. CEO locked 5 design decisions on 2026-05-12: slug-tag-only plan grouping (no separator lines), combined heartbeat policy (300s state-bearing + 120s suppression), urgency-gated coalescing with 30s digest, 14d terminal log retention, 30d step JSON retention. Tests 268/269 pass (1 pre-existing `test_run_step_timeout` failure unrelated). Minor implementation deviation: `notify_plan_skipped` per-event priority -1 in design, but coalesced digest uses priority 0 since digests may contain higher-priority events. Reference: `Done/diagnostic-terminal-and-notification-surface-audit-2026-05-11.md`, `Done/diagnostic-terminal-notification-capture-design-2026-05-11.md`, `Done/executable-terminal-capture-2026-05-12.md`, `Done/executable-notification-coalescing-2026-05-12.md`.
   ```

### Out of scope

- Do NOT modify any file. Read-only audit.
- Do NOT propose changes to source code, agent files, or `RULE_20_SELF_CHECK_BLOCK.md`.
- Do NOT propose changes to other BACKLOG entries.

### Deliverables

A findings file at `bellows/knowledge/research/terminal-notification-backlog-close-edit-surface-2026-05-12.md` containing:
- One section per question (1–6) with the question restated, evidence quoted verbatim, and line numbers cited.
- A final "Anchor strings" section with the two ready-to-use `old_string` / `new_string` pairs from question 6.
- An Output Receipt at the bottom.

**Deposits:**
- `bellows/knowledge/research/terminal-notification-backlog-close-edit-surface-2026-05-12.md`
