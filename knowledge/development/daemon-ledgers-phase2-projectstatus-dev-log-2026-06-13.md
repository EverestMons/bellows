# Daemon-Owned Ledgers Phase 2: PROJECT_STATUS→Daemon-Post-Merge — Dev Log
**Date:** 2026-06-13 | **Agent:** Bellows Developer | **Plan:** 44 | **Step:** 1

---

## What Was Done

Implemented Phase 2 of the daemon-owned ledgers migration: relocating `PROJECT_STATUS.md` writes from the worktree merge path to daemon-post-merge append on main. This extends the Phase 1 framework (plan 43) — reuses the `### Ledger Updates` Output Receipt channel and the `_apply_ledger_updates()` function. Phase 2 is deliberately **DORMANT** and coexistence-safe: if the agent wrote `PROJECT_STATUS.md` old-style (visible in `files_changed`), the daemon skips its write. The mechanism activates only when the governance follow-on flips agents from writing `PROJECT_STATUS.md` directly to emitting the milestone text via the Output Receipt channel.

### Changes by File

#### `parser.py`
- **`#### Project Status` extraction** added to the existing `### Ledger Updates` section parser. Extracts into `parsed["ledger_updates"]["project_status"]`. Same pattern as Phase 1's `#### Prompt Feedback` — absent section → `None`, "None"/"N/A" values excluded. The `project_status` key is always present in the `ledger_updates` dict.

#### `bellows.py`
- **`_apply_ledger_updates()` restructured** — the Phase 1 early-return on feedback coexistence was replaced with per-handler if/elif branches so both Phase 1 (feedback) and Phase 2 (project_status) run independently. Each handler has its own coexistence check.
- **Phase 2 handler** — if `PROJECT_STATUS.md` appears in `files_changed` → SKIP. Else if `project_status` text is present → call `_append_project_status()`.
- **`_append_project_status(project_path, plan_id, milestone_text)`** — new function. Appends a milestone entry (`### Plan <id>
<text>`) to `PROJECT_STATUS.md` at the canonical position (after the first `## Completed` heading). If no `## Completed` heading exists, appends at EOF. Creates the file if absent. Then `git add PROJECT_STATUS.md && git commit` on main (daemon-post-merge). Logs which insertion path was taken (after-completed vs eof-fallback).
- **Log level fix** — existing Phase 1 `_log("DEBUG", ...)` calls used an invalid log level (valid levels: EVENT, WARN, ERROR, INFO, PAUSE). Changed to `"INFO"`. This was a latent bug masked by the log-and-continue try/except — the exception from the invalid log level prevented Phase 2 code from executing.

### Test Coverage (15 new tests across 2 classes)

| Class | File | Tests | What it covers |
|---|---|---|---|
| `TestProjectStatusExtraction` | test_parser.py | 7 | Extraction, absent subsection, None/N/A values, both feedback+status coexist, key always present, order independence |
| `TestApplyLedgerUpdatesProjectStatus` | test_bellows.py | 8 | Coexistence skip (PROJECT_STATUS.md in files_changed), canonical append after ## Completed, EOF fallback, file creation when absent, git commit verification, noop when no project_status, Phase 1 feedback regression (both paths work together) |

### Full Suite Result

**633 passed, 0 failed, 1 warning** (17.14s)

### Design Compliance

- **Section 3 File 1** — daemon-post-merge disposition: ✓ (milestone text appended by daemon on main post-merge, not by agent in worktree)
- **Section 4** — Output Receipt channel: ✓ (`#### Project Status` subsection under `### Ledger Updates`)
- **Section 6 Phase 2** — coexistence check on `files_changed`: ✓
- **Canonical-append positioning mitigation** (Section 3 File 1): ✓ (after first `## Completed` heading, with EOF fallback)
- **Phase 1 untouched** — feedback DB path unchanged (only log level fix, which is a bug fix)
- **FORWARD rows 4/5/13 NOT closed** — per plan context, governance follow-on activates all phases at once

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended daemon-owned ledgers framework (Phase 2): parser.py extracts `#### Project Status` from the Output Receipt; bellows.py appends the milestone text to `PROJECT_STATUS.md` on main post-merge at the canonical position (after first `## Completed` heading, EOF fallback). Dormant and coexistence-safe. Fixed latent invalid log level bug in Phase 1 code. 15 new tests, full suite green (633 passed).

### Files Deposited
- `knowledge/development/daemon-ledgers-phase2-projectstatus-dev-log-2026-06-13.md` — this dev log

### Files Created or Modified (Code)
- `parser.py` — added `#### Project Status` extraction into `parsed["ledger_updates"]["project_status"]`
- `bellows.py` — extended `_apply_ledger_updates()` with project_status handler + new `_append_project_status()` function; fixed log levels from invalid "DEBUG" to "INFO"
- `tests/test_parser.py` — 7 new tests (`TestProjectStatusExtraction`)
- `tests/test_bellows.py` — 8 new tests (`TestApplyLedgerUpdatesProjectStatus`)

### Decisions Made
- Changed _log level from "DEBUG" (invalid) to "INFO" — necessary for Phase 2 to function; was a latent bug in Phase 1
- Entry format uses `### Plan <id>
<text>` heading style for consistency with existing PROJECT_STATUS.md entries

### Flags for CEO
- DAEMON RESTART REQUIRED
- Phase 2 DORMANT — does not close FORWARD rows yet
- Next: Phase 3 (FORWARD new-rows) then the governance activation follow-on

### Flags for Next Step
- QA should verify: parser extraction, canonical-append behavior, dormancy/coexistence, Phase 1 intact, scope (only 4 files changed)

### Ledger Updates
#### Prompt Feedback

**2026-06-13 — daemon-ledgers-phase2-projectstatus (DEV Step 1)**

1. **Specialist file provided clear context.** `agents/BELLOWS_DEVELOPER.md` and the design doc were sufficient to implement Phase 2 without ambiguity. The phased migration pattern from Phase 1 (plan 43) made the extension straightforward.

2. **Latent log level bug discovered.** Phase 1 code used `_log("DEBUG", ...)` but "DEBUG" is not a valid log level. This was masked by the log-and-continue try/except wrapper — the exception silently prevented all post-feedback code from running. Phase 2 would have been dead code without this fix. Future phases should verify log levels at implementation time.

3. **Phase 1 early-return pattern needed restructuring.** The Phase 1 coexistence check used `return` to exit the entire function when `agent-prompt-feedback.md` was in `files_changed`. This prevented Phase 2's project_status handler from running. Restructured to per-handler if/elif branches so each handler's coexistence check is independent.

4. **Test isolation with tmp_path git repos worked well.** Phase 2 tests that verify git commit behavior use `_make_git_repo()` helper to create isolated git repos in pytest's tmp_path. This avoids interference with the real repo and tests the full write+commit path.

5. **Scope was clean and well-bounded.** Exactly 4 files modified (parser.py, bellows.py, test_parser.py, test_bellows.py) per the plan. No governance edits, no FORWARD handling, no Rule 8 changes.

#### Project Status
- 2026-06-13: **Daemon-owned ledgers Phase 2 (plan 44).** Extended daemon-post-merge framework to handle PROJECT_STATUS.md writes — parser extracts `#### Project Status` from Output Receipt, daemon appends milestone text at canonical position (after first `## Completed` heading). Dormant and coexistence-safe; activates when governance follow-on flips agents to the new channel.
