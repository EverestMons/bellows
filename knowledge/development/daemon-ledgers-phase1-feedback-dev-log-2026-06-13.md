# Daemon-Owned Ledgers Phase 1: Feedback→DB Mechanism — Dev Log
**Date:** 2026-06-13 | **Agent:** Bellows Developer | **Plan:** 43 | **Step:** 1

---

## What Was Done

Implemented the daemon-side mechanism for Phase 1 of the daemon-owned ledgers migration: relocating `agent-prompt-feedback.md` writes from the worktree merge path into `lifecycle.db`. The mechanism is deliberately **DORMANT** and coexistence-safe — it activates only when the governance follow-on flips agents from writing the `.md` file to emitting feedback via the Output Receipt channel.

### Changes by File

#### `lifecycle.py`
- **`prompt_feedback` table** added to `init_lifecycle_db()` schema (idempotent `CREATE TABLE IF NOT EXISTS`). Columns: `id`, `plan_id`, `step_number`, `agent`, `project`, `entry_text`, `created_at`.
- **`record_prompt_feedback()`** — new write helper with log-and-continue semantics (matches all existing lifecycle write helpers). Inserts a single feedback row.
- **`generate_feedback_md()`** — read-only function that returns `agent-prompt-feedback.md` content from `SELECT ... FROM prompt_feedback WHERE project=? ORDER BY created_at DESC` (newest-first, matching current file convention). Tested but not yet wired as the live producer.

#### `parser.py`
- **`### Ledger Updates` extraction** added to `parse()`, mirroring the existing `### Flags for CEO` → `ceo_flags` pattern (parser.py:30–37). Extracts `#### Prompt Feedback` subsection into `parsed["ledger_updates"]["feedback"]`. Absent section → `None`, "None"/"N/A" values excluded. The `ledger_updates` key is always present in the returned dict.

#### `bellows.py`
- **`_apply_ledger_updates(parsed, project_path, plan_id, files_changed)`** — new function placed before `_teardown_worktree`. Phase 1 handles ONLY feedback:
  - If `agent-prompt-feedback.md` appears in `files_changed` → SKIP (coexistence: agent wrote old-style, do nothing).
  - Else if `parsed["ledger_updates"]["feedback"]` is present → call `record_prompt_feedback()`.
  - Never writes the feedback FILE. Wrapped in log-and-continue.
- **Wired at all 3 teardown sites** (lines ~622, ~733, ~764): called AFTER successful `_teardown_worktree()`, inside the same try block (so it only runs on successful merge).

### Test Coverage (20 new tests across 5 classes)

| Class | File | Tests | What it covers |
|---|---|---|---|
| `TestPromptFeedbackMigration` | test_lifecycle.py | 3 | Table creation, column spec, idempotent double-init |
| `TestRecordPromptFeedback` | test_lifecycle.py | 3 | Happy path + read back, multiple entries, log-and-continue on failure |
| `TestGenerateFeedbackMd` | test_lifecycle.py | 3 | Empty DB header, newest-first ordering, project filter |
| `TestLedgerUpdatesExtraction` | test_parser.py | 8 | Full extraction, absent section, absent subsection, None/N/A values, subsection boundary, key always present, non-interference with ceo_flags |
| `TestApplyLedgerUpdates` | test_bellows.py | 5 | Coexistence skip, DB write, no feedback noop, missing key noop, never writes file |

### Full Suite Result

**619 passed, 0 failed, 1 warning** (16.63s)

---

## Design Anchors Verified

- `parser.py:30–37` — `ceo_flags` extraction pattern confirmed; `### Ledger Updates` extraction mirrors it.
- `bellows.py:622/731/762` — all three teardown call sites confirmed and wired.
- `lifecycle.py` migration mechanism — `CREATE TABLE IF NOT EXISTS` is idempotent, matching all existing tables.
- `files_changed` variable is in scope at all three teardown sites (set at lines 579/690).

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented daemon-owned ledgers Phase 1: prompt_feedback table in lifecycle.db, record_prompt_feedback() writer, generate_feedback_md() generator, parser extraction of ### Ledger Updates → feedback channel, and _apply_ledger_updates() at all 3 bellows.py teardown sites with dormant coexistence logic. 20 new tests, full suite 619 passed.

### Files Deposited
- `knowledge/development/daemon-ledgers-phase1-feedback-dev-log-2026-06-13.md` — this dev log

### Files Created or Modified (Code)
- `lifecycle.py` — prompt_feedback table + record_prompt_feedback() + generate_feedback_md()
- `parser.py` — ### Ledger Updates extraction in parse()
- `bellows.py` — _apply_ledger_updates() + wired at 3 teardown sites
- `tests/test_lifecycle.py` — 9 new tests (migration, record, generate)
- `tests/test_parser.py` — 8 new tests (ledger_updates extraction) [new file]
- `tests/test_bellows.py` — 5 new tests (_apply_ledger_updates coexistence + write)

### Decisions Made
- Placed `_apply_ledger_updates` call INSIDE the try block after `_teardown_worktree` succeeds (not after the except) — ledger updates should only apply if the code merge succeeded.
- Used `any("agent-prompt-feedback.md" in f for f in files_changed)` for coexistence detection — substring match handles both relative and absolute path forms.
- `generate_feedback_md()` produces a header with "No feedback entries recorded" for empty DBs, matching the convention of other generated reports.

### Flags for CEO
- DAEMON RESTART REQUIRED — loads new code + migration (prompt_feedback table)
- Phase 1 is DORMANT (coexistence) — it does NOT close FORWARD rows 4/5/13 yet; the governance follow-on activates it
- Next up per the phased plan: Phase 2 (PROJECT_STATUS→daemon-post-merge) and the governance activation follow-on

### Flags for Next Step
- QA should verify: (1) prompt_feedback table columns match spec, (2) migration is idempotent, (3) parser extraction mirrors ceo_flags pattern, (4) coexistence SKIP when agent-prompt-feedback.md in files_changed, (5) generate_feedback_md renders newest-first, (6) no scope bleed (only in-scope files changed)

### Ledger Updates
#### Prompt Feedback
**2026-06-13 — daemon-ledgers-phase1-feedback (DEV Step 1)**

1. **Design doc was authoritative and accurate.** All anchors verified at edit time — parser.py:30–37 ceo_flags pattern, bellows.py teardown sites at ~622/731/762, lifecycle.py CREATE TABLE IF NOT EXISTS migration mechanism. No divergence from design doc.

2. **Coexistence logic is the load-bearing safety property.** The `any("agent-prompt-feedback.md" in f for f in files_changed)` check ensures Phase 1 never double-writes. This is the property QA must verify most carefully — if it fails, feedback would be written twice (once by agent old-style, once by daemon).

3. **Three teardown sites is a code smell.** The same teardown-then-pause/close pattern is repeated at lines ~622, ~733, and ~764 with near-identical surrounding code. A future refactor could extract a `_finalize_step()` helper. Not done here (out of scope, Phase 1 is mechanism-only).

4. **Parser regex boundary: `\n## ` vs `\Z`.** The `### Ledger Updates` section is terminated by `\n## ` (next H2 section) or end-of-string. This matches the ceo_flags pattern but may need adjustment if Output Receipts gain H2-level sections after Ledger Updates. Current format has Ledger Updates at the end of the receipt, so this is safe.

5. **`_step_number` and `_agent` enrichment fields.** The `_apply_ledger_updates` function reads `parsed.get("_step_number")` and `parsed.get("_agent")` — these are not set by the current parser (they'd come from bellows.py enrichment when the mechanism activates). Phase 1 stores them as None, which is acceptable for the dormant period.
