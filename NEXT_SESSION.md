# bellows — Next Session Baton

**Created:** 2026-05-22 (replaces 2026-05-21 baton; all Priority 2 items shipped or closed)
**Carry-forward owner:** Planner

This file exists when bellows has work to carry into the next session. Delete it when all items here close.

---

## Session focus: clean up the Bellows flow

The 2026-05-22 session shipped two diagnostics characterizing operational gaps in the Bellows flow. Both have follow-on work queued. Plus three additional friction items from the open BACKLOG warrant attention. Five items total, sequenced below.

The sequencing principle: pair items with different cognitive modes when possible (e.g., diagnostic + documentation work in same session), keep items operating on the same code surface separated.

---

## Priority 1 — Recovery-pain items (need diagnostics first)

These cause ~10+ min recovery when triggered and will recur until fixed. Both touch `bellows.py` pause/dispatch logic. Run diagnostics separately; consider whether the executables can share a session.

### Item 1.A — Step 2 final-step gate_failure pause doesn't rename in-progress-* → verdict-pending-*

**State:** BACKLOG entry, no diagnostic yet.

**Symptom:** When a final step pauses on a `gate_failure` (e.g., `scope_check` false positive), Bellows posts the verdict-request file correctly, but the plan filename stays `in-progress-*` rather than renaming to `verdict-pending-*`. Verdict response cannot be consumed (no `verdict-pending-*` for `_consume_verdicts` to match); no-match WARN fires every 30s indefinitely. Manual recovery via Planner-side rename triggers `on_moved` re-dispatch → stale worktree → step-counter loop.

**Two candidate root causes** (BACKLOG entry 2026-05-22 lists both):
1. The `gate_failure` code path in `run_plan()` at the final-step pause site (bellows.py:580-625 region) may conditionally skip the rename when teardown was called before `post_verdict_request`.
2. Daemon restart between pause and verdict response may drop mid-pause rename-pending state.

**Diagnostic shape:** Single-step SA or two-step (SA characterize → SA reproduce). Header should be `pause_for_verdict: always` if multi-step (today's lesson) or split into separate single-step diagnostics.

**Operational mitigation in place today:** When a plan is stuck `in-progress-*` with a verdict-request file in pending/, do NOT manually rename. Issue `verdict: stop`, then manually move `halted-*` → `Done/` if work shipped.

### Item 1.B — Step-counter loop after precondition-failure verdict

**State:** BACKLOG entry, no diagnostic yet.

**Symptom:** When Bellows pauses on a precondition gate (e.g., worktree creation failure) labeled `step-N` and the Planner verdict-continues, Bellows re-dispatches step N rather than advancing to N+1. If step N's work was already on origin from a prior run (parallel-SHA pattern), the agent's fresh worktree forks from origin tip → no-op → empty commit → teardown empty cherry-pick fails → gate_failure → re-pause same step. Loops indefinitely until verdict-stop. Three iterations seen in one reproduction (2026-05-21).

**Two candidate root causes** (BACKLOG entry 2026-05-21):
1. `_consume_verdicts` interprets continue-on-precondition-failure as "step N done, advance to N+1" without checking whether step N actually produced work.
2. Step counter is computed from verdict request's `Step` field rather than internal daemon state, so a precondition-failure labeled `step-1` propagates as "step 1 resolved, start step 2."

**Diagnostic shape:** Single-step SA. The two hypotheses are mutually exclusive and the diagnostic should pick which one.

**Sequencing note:** Items 1.A and 1.B both touch pause/dispatch code. Diagnostics can run independent sessions; the executables should NOT bundle blindly — re-evaluate when diagnostics complete whether they share enough surface to combine.

**Operational mitigation today:** `verdict: stop` on the second teardown-empty in a row for the same step. Author follow-up plan covering only remaining steps. ~10 min recovery cost per occurrence.

---

## Priority 2 — Already-diagnosed, ready for executable

### Item 2.A — Document `.claude/settings.local.json` bash-fallback in BELLOWS_DEVELOPER.md

**State:** Diagnostic complete (2026-05-22). Fix-shape findings at `bellows/knowledge/research/claude-settings-permission-gap-fix-shape-2026-05-22.md`.

**Recommended fix:** Shape 1 + supplementary plan-prompt instruction.

1. Add a new paragraph to BELLOWS_DEVELOPER.md "Project-Specific Procedure" section documenting the bash-fallback (`python3 -c` JSON-edit pattern) for `.claude/settings.local.json` edits.
2. Template plan-prompts that target this file with: "Edit `.claude/settings.local.json` using Bash (python3 -c) — the Edit tool will be denied on this path because the file is outside the worktree. See BELLOWS_DEVELOPER.md 'Project-Specific Procedure' for the pattern."

**Combined effect:** Agent never attempts Edit → denial never fires → no `gate_failure` verdict → no Rule 22 override. Effectively closes the vector without any code changes.

**Executable shape:** Documentation Analyst → QA. Doc-only, no code changes. Tier: Small.

**Plan staged:** `_staging_executable-settings-local-bash-fallback-doc-2026-05-22.md` at governance root. Move to `bellows/knowledge/decisions/executable-settings-local-bash-fallback-doc-2026-05-22.md` to dispatch.

**Proposed filename:** `executable-settings-local-bash-fallback-doc-2026-05-22.md` (already authored).

### Item 2.B — Implement `qa_steps` plan-header field

**State:** Diagnostic complete (2026-05-22). Fix-shape findings at `bellows/knowledge/research/qa-step-detection-fix-shape-2026-05-22.md`.

**Recommended fix:** Add `qa_steps` header field (comma-separated integers, e.g., `qa_steps: 2,4`) with keyword fallback for legacy plans.

1. Code change to `gates.py` — extend `_gate_is_qa_step` to accept `plan_header` kwarg, check `qa_steps` field first, fall back to keyword detection.
2. Governance edit to PLANNER_TEMPLATE.md in three places: header example in Plan File Structure, new definitional paragraph after "Execution map", Gate 6 description in "The Eight Gates" table.
3. Test surface: unit tests for the field parse cases (string, list, malformed, missing).

**Caveat from Planner review (2026-05-22):** The SA's proposed Doc Analyst → QA may under-scope. This is a multi-file change (gates.py + governance) with parse contract decisions. Re-evaluate at planning time whether SA → DEV → QA is more appropriate.

**Pre-write check before authoring:** Verify the PLANNER_TEMPLATE.md insertion point ("Gate 6 description in The Eight Gates table around line 955") matches actual file structure. SA proposal cited the line number from agent-side read; Planner should confirm.

**Proposed filename:** `executable-qa-steps-header-field-2026-05-XX.md`.

**Closes BACKLOG:** the 2026-05-22 Closed entry already references this follow-on.

---

## Priority 3 — Small friction items

### Item 3.A — Pre-scan orphan-guard INFO log flood

**State:** BACKLOG entry (2026-05-22). Resolution shape recommended in the entry.

**Symptom:** ~300 INFO log lines per daemon restart from the orphan-guard pre-scan re-discovering historical `processed-verdict-*` files. Daemon-lifetime dedup works correctly during runtime but resets on every restart. Bellows dev sessions have frequent restarts.

**Recommended fix (from BACKLOG entry):** Shape 1 — at startup before the first rescan, populate `_prescan_orphan_logged` with every existing `processed-verdict-*.md` in `resolved/` whose paired-plan check would fail. Dedup short-circuits silently; only NEW orphans during runtime would log.

**Effort:** small (~5 LOC change to `_consume_verdicts` + 1-2 regression tests).

**Executable shape:** DEV → QA. Tier: Small. Could ship without further diagnostic — shape is already specified.

### Item 3.B — MCP tool denials not on READ_CLASS_TOOLS exemption

**State:** BACKLOG entry (2026-05-22).

**Symptom:** `mcp__vexp__run_pipeline` and `mcp__vexp__get_context_capsule` denials fire `no_permission_denials` gate. 5 events / 2 gate failures over 30 days.

**Recommended fix:** Add `mcp__vexp__*` patterns to `READ_CLASS_TOOLS` in `gates.py` so denials filter from gate evaluation. Follows the existing READ_CLASS_TOOLS architectural precedent (shipped 2026-04-28).

**Effort:** small (~3 LOC + 1-2 regression tests).

**Executable shape:** DEV → QA. Tier: Small. Could ship without further diagnostic — shape is already specified.

**Open question:** Is the right resolution to extend READ_CLASS_TOOLS specifically (treating MCP read tools as a known class), or to generalize the exemption mechanism (any tool name matching `mcp__*_read*` or similar pattern)? Worth a brief SA blueprint if the answer isn't obvious.

---

## Suggested session sequencing

**Single-item sessions (lowest contention):**
- Session A: Item 2.A (settings.local.json doc). Doc-only, no code conflicts. Cleanest standalone.
- Session B: Item 3.A or 3.B (small DEV → QA). Either ships clean without diagnostic.

**Diagnostic-first sessions:**
- Session C: Diagnostic for Item 1.A (Step 2 rename bug). Single-step SA.
- Session D: Diagnostic for Item 1.B (step-counter loop). Single-step SA.

**Combinable in one session if bandwidth allows:**
- Item 2.A doc work + Item 1.A diagnostic (different cognitive modes, no surface contention).
- Item 3.B small fix + Item 1.B diagnostic.

**Do NOT combine without re-evaluation:**
- Items 1.A and 1.B executables. Both touch `bellows.py` pause/dispatch logic. Re-evaluate after diagnostics complete.
- Item 2.B (qa_steps field) executable. Multi-file change across bellows + governance. Stands alone.

---

## What's CLEAN at session end 2026-05-22

- Two diagnostics shipped to Done/ (`qa-step-detection-audit`, `claude-settings-permission-gap`).
- BACKLOG: 4 closes (2 from morning hygiene pass + 2 from today's diagnostics), 2 new opens (MCP tool denials, WebSearch in --allowedTools).
- Two LESSONS.md entries shipped (Rule 25 codification invalidating defer rationale; `pause_for_verdict: after_step_1` plan-authoring miss for multi-step diagnostics).
- Both bellows + governance-root repos pushed to origin.
- Submodule pointer bumped and verified clean.
- No parallel-SHA divergence carried forward.

## Outstanding from other sessions (not Planner-owned in this baton)

- invoice-pulse specialist-file-drift diagnostic in flight from a separate session as of 2026-05-22 11:31. Awaiting verdict from that session's owner. Not part of bellows-flow cleanup.

---

## Definition of Done for this file

Delete this file when:
1. Items 1.A and 1.B have shipped executables (diagnostics + fixes).
2. Items 2.A and 2.B have shipped executables.
3. Items 3.A and 3.B have shipped executables OR been explicitly deferred with reason.

Until then, this baton carries forward into each next session as Phase 1.5 Source 0b reading.
