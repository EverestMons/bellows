# Bellows — Next Session Baton

**Last session:** 2026-05-27 (session 11)
**Last session focus:** Coordinated daemon-side gate-FP fix — three 2026-05-27 BACKLOG entries closed in one ship (ceo_flags null-declaration, rule_22 (c) row-status enumerative-table FPs, hedging-detector domain-term FPs). First session to close daemon-side BACKLOG entries since they began accumulating.

---

## Session summary

Single diagnostic + single executable, ~3 hours wall-clock end-to-end. Diagnostic produced a 5c mixed-shape recommendation (CEO Flags independent + Rule 22 (c)/(d) coordinated). DEV shipped three fixes in `gates.py` per spec with one accepted divergence (stricter cell-scope for (d) than diagnostic specified). QA verified all 3 FPs closed via reproduction tests + 3 counter-tests + adjacent-suite regression check (133 passed, 0 failed). Daemon restart confirmed 20:14.

Three operational recoveries this session worth noting:
1. **R2 worktree-stranded-findings recovery.** The diagnostic's teardown failed on cherry-pick conflict (agent's own claim-rename in main's untracked tree). Recovery: copied findings from worktree to main, committed standalone, left the transient lifecycle artifact uncommitted. Commit `b3b9646`.
2. **Stale-worktree cleanup.** The diagnostic's failed teardown left `.bellows-worktrees/gate-fp-coordinated-shape-2026-05-27/` + git worktree registration intact. Downstream executable couldn't spin up its own worktree at the same path. Recovery: `git worktree remove --force`. Precondition-failure verdict then retried Step 1 successfully — first practical use of the 2026-05-24 precondition-failure-field shipped under the rename-first-ordering plan.
3. **Planner-authoring failure caught by Rule 20.** Plan was deposited with `### Deposits` (markdown h3 header) instead of `**Deposits:**` (bold-colon form per Rule 26). Step 2's `_gate_rule_20_self_check` fired with the 2026-05-26 line-441 evidence string "deposits block declares no .md paths..." which correctly routed Planner to "this is a Planner-authoring failure, not a QA-banner failure." Validates the 2026-05-26 evidence-string disambiguation ship. Recovery: in-place plan-file edit safe because `is_runnable_plan` returns False for `verdict-pending-*` prefix and `on_modified` lifecycle-prefix guard prevents `_seen` invalidation. No re-dispatch trigger fired.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Diagnostic | SA delivered 5c mixed-shape recommendation. Two BACKLOG-framing divergences flagged and accepted. Findings at `knowledge/research/gate-fp-coordinated-shape-2026-05-27.md`. Worktree teardown failed (R2 recovery applied). `Done/diagnostic-gate-fp-coordinated-shape-2026-05-27.md`. |
| 2 | Executable Step 1 (DEV) | First attempt failed precondition (stale worktree from diagnostic). Continue-verdict with `precondition_failure: true` retried Step 1; second attempt clean. Three gate fixes shipped: `_is_null_flag_declaration` at gates.py:73, defer-and-discard at gates.py:558-611, `_hedging_in_status_vicinity` at gates.py:94 + section-scoping. Commit `7e67b0b`. |
| 3 | Executable Step 2 (QA) | Gates passed substantively but tripped `_gate_rule_20_self_check` on Planner-authoring failure (`### Deposits` vs `**Deposits:**`). Rule 22(d) override after R2 plan-file edit. 6 new tests + 2 fixture updates. 133 tests pass. Commit `9f8a0d4`. |
| 4 | Session-wrap | 3 BACKLOG entries moved Open→Closed, lifecycle artifacts committed, submodule pointer bumped. Commits `d40afb0` (bellows), `30bdc83` + `3b7fa89` (governance). |
| 5 | Daemon restart | CEO-initiated, confirmed in log at 20:14:01. New `gates.py` symbols loaded. |

**Commits this session (5 bellows + 2 governance):**
- bellows `b3b9646` (R2 recovery of stranded diagnostic findings)
- bellows `7e67b0b` (DEV — three gate FP fixes)
- bellows `9f8a0d4` (QA — verification tests + fixture updates)
- bellows `d40afb0` (session-wrap — BACKLOG closures + lifecycle artifacts)
- governance `30bdc83`, `3b7fa89` (submodule pointer bumps)

**Daemon restarted.** Live `gates.py` now contains `_is_null_flag_declaration`, `_hedging_in_status_vicinity`, defer-and-discard table state, (d) section-scoping. Three FP classes structurally closed.

---

## In-flight threads (carry forward)

None active. All session work shipped and committed. Daemon running.

---

## Open BACKLOG items added this session (0)

None added. Three Closed entries filed (ceo_flags, rule_22 (c), hedging-detector).

---

## LESSONS candidates carried forward (not yet promoted)

Three patterns observed this session worth tracking for next-session LESSONS evaluation. None promoted today — discipline rule is to wait for second occurrence unless a single occurrence is structurally severe.

1. **`### Deposits` vs `**Deposits:**` Planner-authoring failure.** First occurrence this session, caught at Step 2 of executable plan by Rule 20 self-check. The h3-header form is visually similar to the bold-colon form but Rule 26's regex is strict. Either pre-emptive promotion as a Planner pre-deposit format-check rule, or wait for second occurrence. The 2026-05-26 evidence-string disambiguation ship correctly routed the failure mode this time — validates that earlier fix. Promote on second occurrence.

2. **Stale worktree from failed teardown blocks downstream plans.** First formal occurrence this session. The diagnostic's worktree-teardown cherry-pick conflict left `.bellows-worktrees/<slug>/` + git worktree registration intact; downstream executable plan couldn't spin up at the same path. Recovery is mechanical (`git worktree remove --force`). Could mechanize as teardown-failure cleanup hook in Bellows; for now, Planner-side recovery is fast. Promote on second occurrence, OR mechanize via small Bellows BACKLOG entry.

3. **R2 recovery for cherry-pick conflict on agent's own claim-rename.** Second occurrence of the 2026-05-22 BACKLOG variant "Worktree teardown cherry-pick conflict on dirty PROJECT_STATUS.md (sequential-Planner-edit variant)" — different sub-variant (untracked claim-rename instead of dirty bookkeeping file). Recovery shape stable. Both occurrences in 5 days. Strong candidate for promotion as a Planner discipline LESSON on the recovery shape itself.

**Carried forward from session 10 baton (not yet promoted):**
- Same-day-overwrite assumption in Bellows scope_check (one occurrence so far).
- Blueprint FP-validation asymmetry (two occurrences last session). Third occurrence would qualify.

---

## Governance edits this session

None. No PLANNER_TEMPLATE, COMPANY.md, or specialist file changes. Pure Bellows code + BACKLOG hygiene.

---

## On the horizon (next session)

Session 10's horizon had 6 items. Session 11 closed 3 daemon-side BACKLOG entries (the three gate-FP entries that were ALSO horizon-relevant though not on the formal horizon list). Remaining horizon, updated:

1. **Bellows status UI** (2026-05-21) — still the natural next-session candidate if focus stays on Bellows. Genuine design work. Open design questions: deployment shape (web vs Tauri vs menu-bar vs TUI), data source (DB vs filesystem vs daemon endpoint), update mechanism, scope of v1. Needs a dedicated planning session.

2. **Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`** (2026-05-22) — second-occurrence threshold now met (this session's R2 recovery on the claim-rename variant). Option (b) from BACKLOG (~20 LOC pre-cherry-pick dirty-tree check) is the small build. **Likely next-session candidate.**

3. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — still defer-until-second-occurrence; discipline mitigation working.

4. **Deposits parser parenthetical qualifiers** (2026-05-21) — defer until first incident; Rule 26 prevents the pattern.

5. **No-match verdict warning rate-limit** (2026-05-21) — low priority, self-limiting.

6. **`_extract_step_text` regex case-sensitivity** (2026-05-13) — governance prevents the failure mode.

7. **Verdict filename prefix tolerance** (2026-05-27) — investigation-then-decide.

8. **`lessons-forge.db` tracked-but-gitignored disposition** (2026-05-27) — surface before next gate 2d cycle.

9. **Orphan-guard renormalization fires on wrong step** (2026-05-27) — single-line predicate strengthening, defer until reproduction.

**Bellows hardening sweep status:** substantively complete. The three 2026-05-27 gate-FP entries closed this session were the most actionable Open items. Remaining 9 Open items are all defer-by-disposition or low-priority. Next session options:

- **Start Bellows status UI (#1)** — biggest concrete next move within Bellows. Substantial design work.
- **Ship worktree-teardown dirty-tree pre-check (#2)** — small, well-scoped, second-occurrence threshold met this session. Quick win.
- **Shift focus to a different project** — forge (pre-scan sync workflow), anvil (COMPANY.md update + first executable plan pending), invoice-pulse (Phase B fuel bracket data migration pending Windows production query results), study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## Open governance follow-up

- **Line 1369 historical lesson** in PLANNER_TEMPLATE — still references "the Planner-owned terminal-move pattern from Rule 25 (rename the plan file directly to `Done/` via `Filesystem:move_file`...)" — carry-over from sessions 8, 9, 10 batons. Stale per the 2026-05-26 v4.52 reconciliation. Not blocking; flag for next session if/when touching governance text.

---

## Discipline reminders for next baton

- **Daemon restart required after gate code changes.** This session's three FP fixes require the running daemon to load new symbols (`_is_null_flag_declaration`, `_hedging_in_status_vicinity`, defer-and-discard state, (d) section-scoping). Restart confirmed 2026-05-27 20:14 (CEO-initiated). New plans dispatched after restart correctly use the fixed gates.
- **Rule 41 anchors mandatory for SA prompts >400w.** Session 11's diagnostic SA step used the canonical anchor template (claim-confirmation BEFORE reads, 1-line ack after each file read, 1-line marker at section starts) and completed cleanly in 481s. Pattern continues to function.
- **`**Deposits:**` is the canonical Rule 26 format.** Pre-deposit verification of the bold-colon format prevents the QA-step Rule 20 trip. Visual similarity with `### Deposits` markdown header is a latent failure mode.
- **2026-05-27 LESSONS entry on SA early-output anchors is codified as Rule 41.** Any Bellows-dispatched SA prompt >400w MUST include the three anchors. Compliance is author-discipline; the LESSON is for context.
- **Term-matching has structural limits for same-function-different-bug detection.** Retired script `scripts/check_backlog_freshness.py` has a header warning preserving this signal. Reconsider only if semantic-comparison primitives become available.
- **R2 recovery shape (copy-from-worktree-to-main, commit standalone) is the precedent for cherry-pick conflicts on agent's own claim-rename.** Second occurrence this session; recovery shape stable; LESSONS candidate noted.
- **Stale-worktree cleanup discipline:** if a teardown fails, the worktree directory persists and blocks downstream plans at the same slug. Check `git worktree list` after any teardown failure; `git worktree remove --force` clears it cleanly.

---

## CEO actions before next session

- None required. Daemon running with new gate code loaded. No pending verdicts. No manual filesystem operations needed.

- Optional: review the three gate-FP closures next session start as a Phase 1.5 sanity check — three Closed entries appended to `bellows/knowledge/BACKLOG.md` top of Closed section.
