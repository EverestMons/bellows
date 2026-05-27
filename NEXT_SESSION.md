# Bellows — Next Session Baton

**Last session:** 2026-05-26 (session 8)
**Last session focus:** Test-isolation conftest + BACKLOG hygiene + PLANNER_TEMPLATE v4.52 governance reconciliation

---

## Session summary

Three shipped, two BACKLOG closures, one governance reconciliation. Bellows hardening sweep continues winding down.

| # | Artifact | Outcome |
|---|---|---|
| 1 | `diagnostic-bellows-test-isolation-conftest-2026-05-26` | **Shipped SA.** Patch-surface audit confirmed `VERDICTS_DIR` patches cleanly (3 call sites, 0 direct imports, no subprocess defeat). Enumerated 2 leaking tests both via dispatch-spawn vector. Designed 7-LOC function-scoped autouse fixture (corrected the BACKLOG's "session-scoped" recommendation because monkeypatch is inherently function-scoped). No production code change required. |
| 2 | `executable-bellows-test-isolation-conftest-2026-05-26` | **Shipped DEV + QA.** Created `tests/conftest.py` with the SA-prescribed fixture. Full-suite: 411 passed, 5 known carry-overs, 0 regressions. Load-bearing leak-closure check (after full suite + after individual leaker reproductions): `verdicts/pending/` empty in both cases. Both previously-leaking tests pass without leaking. |
| 3 | Test-isolation BACKLOG hygiene close (Planner-direct) | Open → Closed at top of Closed section. |
| 4 | `mcp__vexp__` BACKLOG hygiene retire (Planner-direct) | **4th recurrence of "leftover after ship" pattern caught at Phase 1.5.** Item was shipped 2026-05-25 via `executable-mcp-read-class-tools-extension-2026-05-25` (commit `9473cf7`), commit message literally said "closes BACKLOG mcp_tool_denials" — but Open entry never moved to Closed. Propagated through 3 session batons (5, 6, 7). Pre-flight grep of `READ_CLASS_TOOLS` in gates.py caught it at first read; no diagnostic or executable authored. Closed-as-shipped. |
| 5 | PLANNER_TEMPLATE v4.52 governance reconciliation | **8 locations updated.** Five PLANNER_TEMPLATE locations (Rule 8 prose, Rule 8 PROJECT_STATUS instruction, Rule 8 Rule-23 paragraph, Rule 8 diagnostic-flow paragraph, Bellows Execution Model "Terminal Done/ move" entry) claimed Planner performs terminal Done/ move via `Filesystem:move_file`. Rule 25 separately distinguished `auto_close_disabled` (Planner-owned) from `qa_checkpoint` (Bellows-owned). Observed behavior + code verification at `bellows.py:1263`: daemon unconditionally moves on any terminal-step continue verdict regardless of pause reason. Reconciled all 8 locations to: **Bellows owns the terminal move on continue-verdict consumption; Planner-direct `Filesystem:move_file` is recovery when daemon is not running.** Locations: Rule 8 prose (473), agent instruction (477), Rule-23 paragraph (479), diagnostic-flow paragraph (481), Rule 22 diagnostic-plans paragraph (617), Rule 22 executable-plans paragraph (619), Rule 23 (c) (635), Rule 25 terminal-step section consolidated (691), Bellows Execution Model (944), Disable-Auto-Close rationale (979), cross-reference (1108). New LESSONS row appended. |

Two governance-region commits total (Bellows submodule pointer bumped twice, then PLANNER_TEMPLATE v4.52 standalone). Bellows submodule at `8415435`. Governance root at `ce7021b`. All pushed clean. All three submodules space-prefixed.

**Daemon NOT restarted at session end.** No code changes shipped this session (the conftest is in tests/, not the dispatched daemon; v4.52 is governance text). Restart is optional, not required.

---

## In-flight threads (carry forward)

None active. All session work shipped and committed.

**Pattern observed this session (worth carrying forward):** The "leftover after ship" pattern fired for the FIFTH time in three days (Item 2 set→list, precondition-failure duplicate, Phase 3b read-side, today's mcp__vexp__, plus today's test-isolation which DID get properly closed). The discipline rule (LESSONS 2026-05-26 "BACKLOG entries authored from current-state grep without scanning Closed history can misframe already-evaluated work") is catching it reliably at Phase 1.5, but the underlying cause — BACKLOG hygiene not running at ship-time — remains. Strong signal for either a discipline rule addition (PLANNER_TEMPLATE: "when a plan's commit message says 'closes BACKLOG X', the Planner moves the BACKLOG entry to Closed in the same plan or immediately after") or tooling (script that scans BACKLOG Open entries against PROJECT_STATUS recent Completed entries). Worth a Forge proposal.

**Pattern observed this session (worth carrying forward, second):** Reconciliation of aspirational governance prose to code-grounded behavior produces real friction reduction. Today's v4.52 caught me about to redundantly move plans the daemon had already moved. The principle: "code-grounded behavior is the truth; aspirational prose creates friction and false discipline." Generalizable to other places where PLANNER_TEMPLATE claims X but observed behavior is Y.

**Pattern observed this session (worth carrying forward, third — Forge candidate):** SA's "Total LOC: 7" label in Deliverable C was a non-blank code-line count, but the actual code block was 9 lines (with comment + PEP 8 blank lines). Planner copied "7 lines" verbatim into DEV/QA prompts. QA handled gracefully. Generalizable: "count what you paste, not what the upstream artifact labels." Worth filing as a Forge observation.

---

## Open BACKLOG items added this session (0)

None. Two items closed.

---

## LESSONS entries added this session (1)

- 2026-05-26: "Terminal Done/ move ownership reconciled to match daemon code (v4.52)" — documents the 8-location reconciliation. Family with 2026-05-21 verdict-enrichment lesson on stopping Planner re-runs of mechanized checks; both reflect the same pattern (when Bellows mechanizes, Planner governance text must shrink to match).

---

## On the horizon (next session)

Session-7 baton listed 9 items. Test-isolation shipped (#1). mcp__vexp__ retired (was #4 in session-7's list, now Closed). Remaining **7 items**, in priority order:

1. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — Planner-side mitigation (commit before session-wrap) is working. Option (b) from BACKLOG (teardown detects dirty working tree, pause-for-CEO with explicit recovery) is small (~20 LOC). Defer until second occurrence demonstrates discipline alone is insufficient.

2. **WebSearch/WebFetch not in agents' `--allowedTools` list** (2026-05-22) — real capability gap for SA diagnostics needing current external docs. Small fix (~2 LOC). Open question: uniform allowance vs role-conditional. Defer pending decision.

3. **Bellows status UI** (2026-05-21) — genuine design question, not misframed. Worth a dedicated planning session. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1.

4. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — BACKLOG explicitly says defer-until-second-occurrence; Planner-discipline mitigation (serialize same-project plans) working.

5. **Deposits parser parenthetical qualifiers** (2026-05-21) — BACKLOG says defer until first incident; Rule 26 governance prevents the problematic pattern. No incidents to date.

6. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

7. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode. Defer.

**Bellows hardening sweep status:** substantively complete as of session 7. Remaining 7 horizon items are all deferred-by-disposition (`defer until second occurrence`, `defer pending decision`, `defer until first incident`), not blocking. Next session can:
- Tackle WebSearch/WebFetch (#2) — small, has a clear CEO-decision blocker that can be resolved in a few minutes
- Start Bellows status UI (#3) — biggest item, needs a planning session
- Shift focus to a different project (forge, anvil, invoice-pulse, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest)
- Address the "leftover after ship" meta-pattern (5th recurrence today) — could be a discipline rule addition to PLANNER_TEMPLATE or a tooling proposal

---

## Open governance follow-up

- **Line 1369 historical lesson** references "the Planner-owned terminal-move pattern from Rule 25 (rename the plan file directly to `Done/` via `Filesystem:move_file`...)" — this is in the historical lessons table from 2026-05-01 and was left verbatim. A future reader might be confused. Options: leave as history, or add `(superseded by v4.52)` annotation. Not blocking; flag for next session if/when touching governance text.

---

## Discipline reminders for next baton

- **Cross-reference every horizon item against current state before propagating.** This session caught mcp__vexp__ at Phase 1.5 first-read; session 7 caught Item 2 the same way. The discipline works — apply it to every baton-carried item, every time.
- **Before filing any new "X is missing/never done/half-implemented" BACKLOG entry, grep Closed section AND current code state for the feature/function name.** Today's mcp__vexp__ catch was at the code-state grep (`READ_CLASS_TOOLS` already contained the tools).
- **Pre-write contradiction scan for governance edits applies to file-wide edits too.** Today's v4.52 reconciliation started scoped to 5 locations and found 8. A formal pre-write `grep -in <keyword>` pass at the start would have surfaced all 8 immediately.
- **2026-05-26 LESSONS entries (4 from sessions 5–8) remain fresh and high-relevance.** Re-read before drafting the next baton.
- **Daemon restart is not required this session-wrap.** No daemon-loaded code changed; only tests/ and governance text.

---

## CEO actions before next session

- None required. No daemon restart needed (no code changes shipped). No manual filesystem operations needed. No pending verdicts to resolve.
