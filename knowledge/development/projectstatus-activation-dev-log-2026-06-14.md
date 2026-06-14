# PROJECT_STATUS Activation — Dev Log
**Date:** 2026-06-14 | **Plan:** 51 | **Agent:** Bellows Developer | **Step:** 1

---

## Summary

Activated PROJECT_STATUS.md as a daemon-owned ledger (Slice 2 of the daemon-owned-ledgers design, diagnostic 42). Agents now emit PROJECT_STATUS milestone summaries via the Output Receipt `### Ledger Updates > #### Project Status` channel instead of writing the file directly. The daemon appends milestones to `PROJECT_STATUS.md` on main post-merge at the canonical position (after `## Completed`). Also fixed the agent-column rider: `record_prompt_feedback` now receives the actual agent name extracted from the Output Receipt.

## Changes Made

### (1) Idempotency — PROJECT_STATUS append path guarded

- **bellows.py**: Extended the `ledger_writes` idempotency guard (previously only covering feedback) to the PROJECT_STATUS handler. A teardown retry that re-invokes `_apply_ledger_updates` with the same project_status text is now a no-op — the content hash + step_id_key are checked against the `ledger_writes` table before appending.
- **tests/test_bellows.py**: Added `TestProjectStatusIdempotency.test_duplicate_project_status_is_noop` — calls `_apply_ledger_updates` twice with identical content, asserts the milestone appears exactly once.

### (2) Gate allowlist — PROJECT_STATUS.md removed

- **gates.py**: Removed `PROJECT_STATUS.md` from `SCOPE_ALLOWLIST`. After this change, both `agent-prompt-feedback.md` (removed in plan 49) and `PROJECT_STATUS.md` are out of the allowlist. Only `.gitkeep` remains.
- **tests/test_gates.py**: Updated `test_scope_check_allowlist` to remove `PROJECT_STATUS.md` from the test fixture. Added `test_scope_check_rejects_project_status_post_activation` — asserts that `PROJECT_STATUS.md` in `files_changed` now triggers scope_check failure.

### (3) Agent-column rider — extract_agent + parsed injection

- **bellows.py**: Added `extract_agent(result_text)` function that parses `**Agent:** <name>` from the Output Receipt. After each `runner.run_step()` call (2 sites), the parsed dict is augmented with `_step_number` (from `current_step`) and `_agent` (from `extract_agent`). These values flow to `record_prompt_feedback` via `_apply_ledger_updates`.
- **tests/test_bellows.py**: Added `TestExtractAgent` (3 tests: extracts name, returns None when absent, strips whitespace) and `TestAgentColumnPopulated` (1 test: verifies the `agent` column in `prompt_feedback` is populated when `_agent` is set).

### (4) Governance flip — PLANNER_TEMPLATE.md

- **Version:** 4.66 → 4.67
- **Rule 8 heading**: "updates PROJECT_STATUS.md" → "emits PROJECT_STATUS milestone via channel"
- **Rule 8 body**: Ordering changed from "deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit" to "deliverable verification → QA deposit → ledger updates in Output Receipt → final commit"
- **Rule 8 instruction template**: `**Final:** Update PROJECT_STATUS.md` → `**Final:** Emit the PROJECT_STATUS milestone summary in the Output Receipt ### Ledger Updates > #### Project Status section`
- **Rule 23 (b)**: Example sub-steps updated (removed "feedback append" and "move-to-Done" from example)
- **Rule 23 (c)**: Updated to reference both feedback and project status as Output Receipt channels
- **Diagnostic plan paragraph**: Ordering reference updated
- **Template prompt mention (~L378)**: Updated final-step description
- **Ledger Updates channel format spec**: Added `#### Project Status` subsection with format example; rules updated to list both Prompt Feedback and Project Status as active channels (FORWARD remains Slice 3)
- **Session-wrap**: Added parenthetical clarifying per-plan milestones are daemon-written; session-wrap entry is the Planner's session-level summary
- **Scope_check gate reference**: Updated to reflect both feedback and PROJECT_STATUS are no longer in allowlist
- **Serialize same-project plans**: Updated to reflect both files are daemon-owned; FORWARD new-row conflict is the remaining source
- **Changelog**: Added v4.67 entry

### Edit sites verified (ANCHOR/grep)

Each site was located by grep for `PROJECT_STATUS` before editing. FORWARD/Rule 42 instructions confirmed untouched.

## Test Results

- **Full suite**: 666 passed, 0 failed, 1 warning
- **New tests added**: 6 (1 idempotency, 1 scope_check rejection, 3 extract_agent, 1 agent column)
- **Updated tests**: 1 (scope_check_allowlist fixture updated)

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Activated PROJECT_STATUS.md as daemon-owned ledger (Slice 2): idempotency guard extended, SCOPE_ALLOWLIST updated, agent-column rider fixed, PLANNER_TEMPLATE.md governance flip completed (10 edit sites). Full suite: 666 passed, 0 failed.

### Files Deposited
- `bellows/knowledge/development/projectstatus-activation-dev-log-2026-06-14.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added `extract_agent`, injected `_step_number`/`_agent` into parsed dict (2 sites), added idempotency guard to PROJECT_STATUS handler
- `gates.py` — removed `PROJECT_STATUS.md` from `SCOPE_ALLOWLIST`
- `tests/test_bellows.py` — added 6 new tests (idempotency, extract_agent, agent column, scope rejection)
- `tests/test_gates.py` — updated allowlist test, added PROJECT_STATUS rejection test
- `/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` — governance flip v4.66→v4.67 (10 edit sites)

### Decisions Made
- Used the same idempotency pattern (content_hash + step_id_key via ledger_writes table) for PROJECT_STATUS as for feedback — minimal deviation from established pattern
- Extracted agent name from Output Receipt `**Agent:**` field rather than from plan metadata — this is where the agent self-identifies

### Flags for CEO
- DAEMON RESTART REQUIRED after this plan fully closes — the first plan after restart is the live canary (its PROJECT_STATUS milestone must be daemon-appended via channel, not agent-written)

### Flags for Next Step
- PLANNER_TEMPLATE.md changes are at the governance root (`/Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md`), not in the bellows worktree — QA should verify the governance-root diff
- Both feedback and PROJECT_STATUS are now activated; FORWARD remains for Slice 3

### Ledger Updates
#### Prompt Feedback
**2026-06-14 — projectstatus-activation (Bellows Developer Step 1)**

1. **Specialist file read was efficient.** The BELLOWS_DEVELOPER.md specialist file provided the correct module scope and operating procedures without additional exploration needed.

2. **Design doc Section 3 File 1 + Section 5 were essential.** The edit-site enumeration in Section 5 served as a checklist for governance changes — every site was located by grep and verified before editing. The coexistence design in Section 3 File 1 confirmed the handler was already built dormant with the correct append logic.

3. **The agent-column rider was correctly scoped.** The bug was that `parsed.get("_agent")" was never set — the fix required both a new extraction function and injection at both `runner.run_step()` call sites. The plan correctly identified this as the same handler area.

4. **Existing test coverage made regression detection immediate.** The `test_scope_check_allowlist` test failed as expected when PROJECT_STATUS.md was removed from SCOPE_ALLOWLIST — this confirmed the gate change was working and the test needed updating.

5. **Governance edit count matched the design doc prediction.** Section 5 predicted 10 edit sites; the implementation touched 10 sites. The FORWARD/Rule 42 non-edit constraint was straightforward to verify via diff grep.
