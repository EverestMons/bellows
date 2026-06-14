# Feedback Activation Dev Log — 2026-06-14

**Plan:** 49 (implements diagnostic 42)
**Agent:** Bellows Developer
**Step:** 1

---

## Part 1 — Idempotency Table

Added `ledger_writes` table to `init_lifecycle_db()` in lifecycle.py:
- Schema: `(id, step_id TEXT, ledger_file TEXT, content_hash TEXT, applied_at TEXT)`
- UNIQUE constraint on `(step_id, ledger_file, content_hash)` for duplicate detection
- `CREATE TABLE IF NOT EXISTS` for idempotent migration

Added two helper functions:
- `check_ledger_write_exists(step_id, ledger_file, content_hash)` — returns True if duplicate
- `record_ledger_write(step_id, ledger_file, content_hash)` — INSERT OR IGNORE with log-and-continue

**Verification:** `ledger_writes` table present after `init_lifecycle_db()`. Double-init does not raise. PRAGMA confirms columns: id, step_id, ledger_file, content_hash, applied_at.

## Part 2 — Wire Generation as Live Producer

Modified `_apply_ledger_updates()` feedback branch in bellows.py:
- Before recording: compute `content_hash = sha256(feedback_text)`, build `step_id_key = "<plan_id>-<step_number>"`
- Idempotency check: `check_ledger_write_exists()` — if True, skip and log
- After `record_prompt_feedback()`: call `generate_feedback_md(project_path)` to get the generated content
- Write the result to `<project_path>/knowledge/research/agent-prompt-feedback.md`
- `git add` + `git commit` on main (daemon-post-merge)
- Record idempotency marker via `record_ledger_write()`
- All wrapped in log-and-continue (never crashes teardown)

Added `import hashlib` to bellows.py.

**Verification:** Test `test_writes_generated_feedback_md` confirms .md file is created. Test `test_generated_md_matches_generate_feedback_md` confirms written content matches `generate_feedback_md()` output.

## Part 3 — Gate Allowlist

Removed `"agent-prompt-feedback.md"` from `SCOPE_ALLOWLIST` in gates.py. `PROJECT_STATUS.md` remains (later activation slice).

**Before:**


**After:**


**Verification:** Test `test_scope_check_rejects_feedback_file_post_activation` confirms scope_check fires when `agent-prompt-feedback.md` appears in files_changed. Test `test_scope_check_allowlist` updated to use only remaining allowlisted files.

## Part 4 — Freeze Existing Feedback Files (6 Projects)

| Project | ARCHIVE Lines | Fresh Lines | Status |
|---|---|---|---|
| bellows | 2,238 | 6 | Frozen in this step (worktree) |
| forge | 1,968 | 6 | Already frozen (Phase 3) |
| anvil | 134 | 6 | Already frozen (Phase 3) |
| invoice-pulse | 8,460 | 6 | Already frozen (Phase 3) |
| governance | 114 | 6 | Already frozen (Phase 3) |
| study | 756 | 6 | Already frozen (Phase 3) |

For bellows: renamed original (2,238 lines, 320KB) to `agent-prompt-feedback-ARCHIVE.md` with frozen header prepended. Wrote fresh generated file with archive pointer.

**Verification:** All 6 projects confirmed with ARCHIVE and fresh files.

## Part 5 — Governance Flip (PLANNER_TEMPLATE.md)

The prompt-instruction sites (diagnostic L265, fix L299, compressed L341, Rule 23 L649, session-wrap L1505, Ledger Updates channel spec L320) were already updated in Phase 3.

This step updated:
1. **"Agent Prompt Feedback" section (L1609-1634):** Rewrote from old process (agent writes directly) to new process (daemon-owned, Output Receipt channel). Updated capture process steps, standard feedback instruction, and standard locations.
2. **Parallel dispatch section (L1319):** Updated to note that `agent-prompt-feedback.md` merge conflicts are now eliminated by activation.
3. **Version:** Bumped from 4.65 to 4.66.
4. **Changelog:** Added 2026-06-14 lesson row describing the go-live.

**Anchors verified:**
- L265 (diagnostic): ✅ Already says "Do NOT write to agent-prompt-feedback.md directly"
- L299 (fix): ✅ Same
- L341 (compressed): ✅ References Output Receipt channel
- L649 (Rule 23): ✅ Says "commit (feedback is daemon-owned)"
- L1505 (session-wrap): ✅ References `prompt_feedback` table and ARCHIVE
- L320-335 (channel spec): ✅ Exists with format template and rules
- L1609-1634 (Agent Prompt Feedback): ✅ Updated to daemon-owned model
- L1319 (parallel dispatch): ✅ Updated to note eliminated conflict
- PROJECT_STATUS (Rule 8): ✅ NOT touched
- FORWARD (Rule 42): ✅ NOT touched

## Tests

| Test | File | Assertion |
|---|---|---|
| ledger_writes migration idempotent | test_lifecycle.py | Table present, columns match, double-init OK |
| Idempotency guard blocks duplicate | test_lifecycle.py + test_bellows.py | check returns True after record; duplicate call skipped |
| Feedback handler writes DB + .md + commits | test_bellows.py | File created, content matches generate_feedback_md |
| generate_feedback_md output is what gets written | test_bellows.py | Written content == lifecycle.generate_feedback_md(project) |
| Coexistence SKIPS when file in files_changed | test_bellows.py | DB count == 0 when agent wrote old-style |
| Scope check rejects feedback file post-activation | test_gates.py | scope_check fires on agent-prompt-feedback.md |

**Suite tail:** 660 passed, 0 failed, 1 warning (16.93s)

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Activated the feedback ledger as the live canary: added idempotency table, wired generate_feedback_md as the live producer in _apply_ledger_updates, removed agent-prompt-feedback.md from SCOPE_ALLOWLIST, froze the bellows feedback file (5 others already frozen from Phase 3), updated PLANNER_TEMPLATE.md governance sites, wrote 10 new tests. 660/660 tests pass.

### Files Deposited
- `bellows/knowledge/development/feedback-activation-dev-log-2026-06-14.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added hashlib import, updated _apply_ledger_updates feedback branch (idempotency + generation + commit)
- `lifecycle.py` — added ledger_writes table, check_ledger_write_exists(), record_ledger_write()
- `gates.py` — removed agent-prompt-feedback.md from SCOPE_ALLOWLIST
- `tests/test_bellows.py` — updated/added 7 feedback activation tests
- `tests/test_lifecycle.py` — added 7 ledger_writes idempotency tests
- `tests/test_gates.py` — updated allowlist test, added post-activation rejection test
- `knowledge/research/agent-prompt-feedback.md` — fresh generated (archive created)
- `knowledge/research/agent-prompt-feedback-ARCHIVE.md` — frozen pre-activation history

### Files Created or Modified (Governance)
- `PLANNER_TEMPLATE.md` — v4.66: updated Agent Prompt Feedback section, parallel dispatch note, version bump, changelog

### Decisions Made
- step_id key format for idempotency: "<plan_id>-<step_number>" (string, not integer)
- content_hash uses SHA-256 of the raw feedback text
- Idempotency marker recorded AFTER successful application (not before)
- Phase 3 already froze 5/6 projects; only bellows frozen in this step

### Flags for CEO
- DAEMON RESTART REQUIRED to load the activation
- **LIVE CANARY** — the FIRST bellows plan dispatched after restart is the live test: its feedback must appear in the `prompt_feedback` table and regenerate `agent-prompt-feedback.md`, with NO hand-append; watch it
- Feedback is now activated; PROJECT_STATUS + FORWARD remain dormant (later slices)

### Flags for Next Step
- QA should verify the 7 evidence items per the plan
- The bellows ARCHIVE file has 2,238 lines (320KB) — confirm line count ≈ pre-freeze

### Ledger Updates
#### Prompt Feedback
**2026-06-14 — Feedback Activation (Bellows Developer Step 1)**

1. Prompt was well-scoped: all 5 parts clearly enumerated with exact file/line references
2. Design doc sections 3-6 were essential context; the Phase 1 code read was also necessary to understand the existing dormant mechanism
3. Discovery that 5/6 project freezes were already done (Phase 3) saved significant work — the plan could have noted this
4. The PLANNER_TEMPLATE governance sites (diagnostic/fix/compressed/Rule 23/session-wrap) were already updated from Phase 3 — only the descriptive "Agent Prompt Feedback" section needed rewriting
5. Test update for scope_check_allowlist was a necessary follow-on from the gate allowlist change — predictable but not called out in the plan
