# Bellows — Next Session Baton

**Last session:** 2026-05-26 (session 7)
**Last session focus:** Bellows hardening batch — ship items 1, 3, 4 from session-6 horizon + BACKLOG hygiene

---

## Session summary

Six artifacts shipped end-to-end. Final BACKLOG state: Open down from 13 to 9 entries; 4 ship closures + 1 new entry filed.

| # | Artifact | Outcome |
|---|---|---|
| 1 | `diagnostic-bellows-hardening-batch-freshness-2026-05-26` | **Shipped SA.** Phase 1.5 caught Item 2 as already-shipped 2026-05-25 (`executable-extract-plan-required-deposits-set-to-list-2026-05-25`). Diagnostic verified items 1, 3, 4 still Open against current code; produced Gap Assessment table with exact line numbers + Q5 verification block + Q6 cross-item independence analysis. Item 3 re-characterized: not a dedicated `dispatch_mode_validator` cache but the existing `_seen` slug-keyed set in `PlanHandler`. Item 4 line numbers shifted +1 to +6 from intervening 2026-05-2x commits. |
| 2 | Item 2 BACKLOG hygiene close (Planner-direct) | Closed via Planner edit — `_extract_plan_required_deposits` set-vs-list resolved 2026-05-25, entry was leftover propagating through 2 batons as Open. |
| 3 | `executable-bellows-hardening-batch-items-1-3-4-2026-05-26` | **Shipped DEV + QA.** Three independent edits: (1) `gates.py:441` evidence string disambiguation; (2) `bellows.py:1033-1044` `_seen` invalidation in `on_modified` with three-prefix lifecycle guard; (3) `bellows.py:499` defensive default re-applied after header reassignment. 3 new regression tests + 1 existing test fix. Test suite: 411 passed / 5 known carry-overs / 0 regressions. Rule 20 self-check PASSED with 12 evidence files. |
| 4 | Test-isolation BACKLOG entry filed (Planner-direct) | New Open entry captures pattern reproduced 4× today: Bellows has no `tests/conftest.py`, `verdict.post_verdict_request()` is unmocked, tests that exercise it write real `verdict-request-*` files to production `verdicts/pending/`. Three resolution shapes documented (conftest autouse / signature refactor / point fixes). |
| 5 | Items 1, 3, 4 BACKLOG hygiene close (Planner-direct) | Three Closed entries inserted at top of Closed section with full ship citation, line number deltas (Item 4), and SA re-characterization (Item 3). |
| 6 | Operational cleanup | 4 test-spawned verdict-request orphans archived to `verdicts/pending/archived/` under `orphan-test-spawned-*` and `orphan-test-spawned-qa-rerun-*` prefixes. |

Three governance-region commits at session-wrap (Bellows + 2 submodule pointer bumps). Bellows submodule at `71c98b0`. Governance root at `658e847`. All pushed clean. Submodule status all space-prefixed.

**Daemon NOT restarted at session end.** Three fixes from items 1, 3, 4 require daemon restart to load:
- New Item 1 evidence string at `gates.py:441` (verdict-read disambiguation)
- New Item 3 `_seen` invalidation logic in `PlanHandler.on_modified` (corrected re-deposit recovery)
- New Item 4 defensive-default re-application at `bellows.py:499` (intermediate-step pause safety net)

**Restart before next session.**

---

## In-flight threads (carry forward)

None active. All session work shipped and committed.

**Pattern observed this session (worth carrying forward):** Phase 1.5 freshness check fired correctly on Item 2 — caught at plan-authoring time, before the executable was deposited. This is the third recurrence of the BACKLOG-stale-claim pattern in three days, but the first one caught by the discipline rule (LESSONS 2026-05-26 "BACKLOG entries authored from current-state grep without scanning Closed history can misframe already-evaluated work"). The fix shape that worked: when a baton-carried horizon item names a specific function/file/line, grep the BACKLOG Closed section AND the recent QA reports for that function name before treating the item as live work. ~30 seconds; prevented authoring an executable batch covering already-shipped work.

**Pattern observed this session (worth carrying forward, second):** The SA freshness diagnostic re-characterized Item 3's underlying mechanism. The BACKLOG framed it as a dedicated `dispatch_mode_validator` cache, but SA found it was the existing `_seen` slug-keyed set in `PlanHandler`. The diagnostic-before-executable discipline (Rule 22) caught this in time to author a correct fix shape (lifecycle-prefix guard on the `on_modified` invalidation) rather than a fix that would have created re-dispatch loops on Bellows's own lifecycle renames. Cost: 1 SA dispatch (~5 min). Avoided: a broken executable that would have re-dispatched plans into loops.

---

## Open BACKLOG items added this session (1)

1. **Test-isolation orphan pattern** — Bellows `tests/` has no `conftest.py`; tests that exercise `verdict.post_verdict_request()` write real verdict-request files to production `verdicts/pending/`. Reproduced 4× today (2× DEV pytest + 2× QA pytest re-run). At least 2 leaking tests identified by orphan filenames (`item4-test`, `regression-slug-collision-2026-05-01`). Operational tax today: manual archive per occurrence + WARN flood every 30s until archived. Three resolution shapes documented (conftest autouse recommended). **Disposition recommendation:** schedule once current hardening sweep clears; not blocking. **Defer until** a planning session can scope the conftest write and the leaking-test audit.

---

## LESSONS entries added this session (0)

No new LESSONS entries this session. The 2026-05-26 entries on BACKLOG-current-state-grep and stale-priority-baton-propagation from session 6 already cover today's observed patterns. Today's third-recurrence-but-first-catch on Item 2 is a confirming data point for those entries, not a new lesson.

**Consider adding a LESSONS entry next session** if the test-isolation pattern recurs in a new form, or if the SA-re-characterization-of-BACKLOG-framing pattern produces a third occurrence (precedent + today's Item 3 = 2). Worth watching but not yet codified.

---

## On the horizon (next session)

The session-6 baton listed 12 items. Items 1, 3, 4 shipped this session. Item 2 closed via hygiene. Remaining 8 from prior baton + 1 new from this session = **9 items** on the horizon, in priority order:

1. **Test-isolation orphan pattern** (new this session) — concrete code-grounded, conftest fix is structural. Option (a) recommended in BACKLOG entry. Small (~10-15 LOC + 1 audit pass). The next plan that adds a Bellows test exercising `verdict.post_verdict_request()` paths will spawn more orphans; cost compounds. Worth scheduling sooner rather than later.

2. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — Planner-side mitigation (commit before session-wrap) is working. Option (b) from BACKLOG (teardown detects dirty working tree, pause-for-CEO with explicit recovery) is small (~20 LOC). Defer until second occurrence demonstrates discipline alone is insufficient.

3. **WebSearch/WebFetch not in agents' `--allowedTools` list** (2026-05-22) — real capability gap for SA diagnostics that need current external docs. Small fix (~2 LOC). Open question: uniform allowance vs role-conditional. Defer pending decision.

4. **MCP tool denials `mcp__vexp__*` not on READ_CLASS_TOOLS exemption** (2026-05-22) — low frequency (~2 gate failures/30 days). Small fix. Defer until usage increases.

5. **Bellows status UI** (2026-05-21) — genuine design question, not misframed. Worth a dedicated planning session. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1.

6. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — BACKLOG explicitly says defer-until-second-occurrence; Planner-discipline mitigation (serialize same-project plans) working.

7. **Deposits parser parenthetical qualifiers** (2026-05-21) — BACKLOG says defer until first incident; Rule 26 governance prevents the problematic pattern. No incidents to date.

8. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

9. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode. Defer.

**Bellows hardening sweep status (per session-6 baton's framing):** "After items 1-4 ship, Bellows hardening is substantively complete absent second-occurrence triggers on the deferred items." This session shipped items 1, 3, 4 and closed Item 2 via hygiene. **Hardening sweep is now substantively complete.** Remaining 9 horizon items are deferred-by-disposition; none are blocking. Next session can either start the deferred items based on a CEO priority pick (Item 1 test-isolation recommended), tackle the Bellows status UI design session (Item 5), or move to a non-hardening Bellows item, or shift focus to a different project (forge, anvil, invoice-pulse, etc.).

---

## Discipline reminders for next baton

- **Cross-reference every horizon item against current state before propagating.** Today's Item 2 catch confirms the rule works — apply it to every baton-carried item.
- **Before filing any new "X is missing/never done/half-implemented" BACKLOG entry, grep Closed section for the feature/function name.** Today's test-isolation entry passed this check (no precedent in Closed); the 2026-04-21 invoice-pulse precedent was correctly cited.
- **2026-05-26 LESSONS entries (3 from sessions 5–7) remain fresh and high-relevance to baton authoring.** Re-read before drafting the next baton.
- **Daemon restart is a CEO action that gets lost between sessions** — every baton should restate it explicitly when fixes from prior session haven't loaded.

---

## CEO actions before next session

- **Restart Bellows daemon** to load the three fixes from session 7 (Items 1, 3, 4 code changes at `gates.py:441`, `bellows.py:1033-1044`, `bellows.py:499`). The simplified discriminator from session 6 (Fix F, commit `cf96a27`) loaded successfully when daemon was restarted mid-session 7 (Bellows successfully dispatched the diagnostic and executable batch using post-restart code), so only the new session-7 fixes need to load.
- No other actions required — all session work shipped, committed, pushed. Submodule pointer bumped twice, both clean.
