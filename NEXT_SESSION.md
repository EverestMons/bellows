# Bellows — Next Session Baton

**Last session:** 2026-05-28 (session 12)
**Last session focus:** Worktree teardown dirty-tree pre-check shipped — new `worktree_teardown_dirty_tree` gate raises a clear pause-for-CEO when local main is dirty before the teardown cherry-pick, replacing the cryptic cherry-pick conflict. First daemon-side teardown-hardening ship. Closes the structural half of the 2026-05-22 BACKLOG entry (option (b)); the R2 recovery shape (operational half) was promoted to LESSONS this session.

---

## Session summary

One LESSON promotion + one diagnostic + one executable (2 steps). The session opened on the session-11 baton's option (2): the worktree teardown dirty-tree pre-check, second-occurrence threshold met. Direction chosen: promote the R2 recovery shape to LESSONS first, then ship the structural pre-check.

- **LESSON promotion (Planner-direct):** R2 recovery shape for worktree teardown cherry-pick conflict on agent's own claim-rename — second occurrence in 5 days, recovery mechanical. Shipped to LESSONS.md before dispatching the diagnostic (which made the diagnostic's evidence-string LESSONS pointer valid rather than forward-looking).
- **Diagnostic (SA):** mapped the `_teardown_worktree` cherry-pick site, pre-check insertion point, evidence-string format, test surface, 5 edge cases. Two SA corrections accepted (gate is not a new `_pause_reason` enum — flows through existing `WorktreeTeardownError`; LESSONS pointer valid). Continue verdict.
- **Executable (DEV + QA):** DEV shipped the pre-check (commit `6252f8c`, +41 prod / +107 test); QA verified (commit `d87caa2`, 8/8 checks, 122/122 suite). Both steps reviewed via Rule 22 with Planner independently re-running tests.

Three Planner-authoring failures this session, all same root cause (strict convention string authored from memory, not copied from a known-good artifact), all caught by gates/validators:
1. **Plan header field-line position.** Diagnostic v1 authored with pipe-fields on line 1 (title position); parser extracted zero header keys; dispatch-mode validator rejected. Recovery: rewrite to canonical two-line shape, `-v2-` rename to evade path-keyed rejection cache, local parse-check before re-deposit.
2. **QA Rule 20 banner string.** Executable's QA prompt mandated `RULE 20 SELF-CHECK: PASSED` instead of the gate-required `Rule 20 — QA Self-Check Results` / `PASSED — SELF-CHECK PASSED` pair. Gate fired accurately on the Planner-authoring defect; QA substance was sound (independently re-verified). Recovery: Rule 22 (d) override.
3. (Prior-session sibling) `### Deposits` vs `**Deposits:**` — same family.
Consolidated into a single LESSONS entry (2026-05-28) with a copy-from-artifact + local-parse-check mitigation.

One operational note: the executable plan sat unclaimed ~9 min after `move_file` deposit (watcher missed the move event); CEO-initiated daemon restart's startup scan claimed it immediately. Filed to BACKLOG (periodic `decisions/` rescan self-heal).

| # | Artifact | Outcome |
|---|---|---|
| 1 | LESSON (R2 recovery) | Promoted Planner-direct to LESSONS.md before dispatch. Second occurrence in 5 days, recovery shape stable. |
| 2 | Diagnostic | v1 rejected (header field-line). v2 ran clean after canonical-header rewrite + local parse-check. SA surface map at `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md`. Continue verdict. `Done/diagnostic-worktree-teardown-dirty-tree-precheck-v2-2026-05-27.md`. |
| 3 | Executable Step 1 (DEV) | Pre-check + evidence string + 4 tests. `cwd=project_path`, fail-open with correct exception ordering, gate name embedded in evidence string. Commit `6252f8c`. 9 teardown tests pass. |
| 4 | Executable Step 2 (QA) | 8/8 checks PASS, 122/122 adjacent suite. Gate tripped `rule_20_self_check` on Planner-authored non-canonical banner. Rule 22 (d) override. Commit `d87caa2`. |
| 5 | Session-wrap | LESSONS (2 entries), 3 BACKLOG entries added, PROJECT_STATUS + baton updated, all repos pushed, submodule pointer bumped. |

**Commits this session (bellows):** `654f1e7` (archive lifecycle), `6252f8c` (DEV pre-check), `d87caa2` (QA), + session-wrap commit (see final push). Governance: LESSONS.md edit + submodule pointer bump (see final push).

**Daemon restart REQUIRED** to load the new `_teardown_worktree` pre-check symbols. The running daemon's HEAD shows `6252f8c` but the process was restarted mid-session before the pre-check landed, so the live `_teardown_worktree` in memory predates it. Restart to load.

---

## In-flight threads (carry forward)

None active. All session work shipped and committed. Daemon running (restart pending to load pre-check symbols).

---

## Open BACKLOG items added this session (3)

1. **Rule 25 routing-table entry for `worktree_teardown_dirty_tree`** — new gate self-documenting in the evidence string but not yet named in the Planner's Rule 25 routing table. Small governance edit.
2. **Pre-deposit plan-lint script for strict-convention strings** — mechanization candidate for the three-strike authoring failure. Small-to-medium. Discipline considered sufficient until a fourth occurrence.
3. **Watcher misses `move_file`-deposited plans / periodic `decisions/` rescan self-heal** — small daemon change to remove the manual-restart failure mode.

---

## LESSONS promoted this session (2)

1. **R2 recovery shape for worktree teardown cherry-pick conflict on agent's own claim-rename** (2026-05-27) — promoted at session start (second occurrence in 5 days). Decision tree + recovery commands for both sub-variants.
2. **Strict Bellows convention strings must be copied from a known-good artifact, never authored from memory** (2026-05-28) — consolidates the three-strike authoring pattern. Mitigation: copy strict strings from verified artifacts; local parse-check headers before deposit.

**Carried forward (not yet promoted):**
- Same-day-overwrite assumption in Bellows scope_check (one occurrence).
- Blueprint FP-validation asymmetry (two occurrences; third would qualify).
- Stale worktree from failed teardown blocks downstream plans (mechanization candidate). NOTE: two stale worktrees still present (`bash-gate-guardrails-exemption-2026-05-20`, `remove-pre-scan-processed-rename-v2-2026-05-24`) — sweep candidate.

---

## Governance edits this session

None to PLANNER_TEMPLATE/COMPANY.md/specialist files. LESSONS.md edited (governance root). Rule 25 routing entry for the new gate filed to BACKLOG, not yet shipped.

---

## On the horizon (next session)

1. **Bellows status UI** (2026-05-21) — natural next-session candidate if focus stays on Bellows. Genuine design work: deployment shape (web vs Tauri vs menu-bar vs TUI), data source, update mechanism, v1 scope. Dedicated planning session.
2. **Three new session-12 BACKLOG entries** — Rule 25 routing for the new gate, pre-deposit lint script, periodic `decisions/` rescan. The Rule 25 routing entry pairs with any next governance touch.
3. **Stale-worktree sweep** — two orphaned worktrees present. `git worktree remove --force` both; ~30 sec. Deferred this session to keep scope narrow.
4. **Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files** (2026-05-22) — defer-until-second-occurrence.
5. **Verdict filename prefix tolerance** (2026-05-27) — investigate-then-decide.
6. **`lessons-forge.db` tracked-but-gitignored disposition** (2026-05-27) — surface before next gate 2d cycle.
7. **Orphan-guard renormalization fires on wrong step** (2026-05-27) — single-line predicate strengthening, defer until reproduction.
8. **Lower-priority defer-by-disposition:** Deposits parser parenthetical qualifiers (2026-05-21), no-match verdict warning rate-limit (2026-05-21), `_extract_step_text` regex case-sensitivity (2026-05-13).

**Next session options:**
- **Start Bellows status UI** — biggest concrete next move within Bellows.
- **Hygiene + small-hardening session** — Rule 25 routing + rescan self-heal + (optionally) lint script + stale-worktree sweep.
- **Shift to another project** — forge (pre-scan sync), anvil (COMPANY.md + first executable pending), invoice-pulse (Phase B pending Windows query results), study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## Open governance follow-up

- **Line 1369 historical lesson** in PLANNER_TEMPLATE — still references the stale "Planner-owned terminal-move pattern from Rule 25" per the 2026-05-26 v4.52 reconciliation. Not blocking. The session-12 Rule 25 routing-table BACKLOG entry is a natural opportunity to fix this in the same pass.

---

## Discipline reminders for next baton

- **Daemon restart required to load the dirty-tree pre-check.** New `_teardown_worktree` symbols (pre-cherry-pick `git status --porcelain` check, `worktree_teardown_dirty_tree` evidence string) require a restart.
- **Copy strict convention strings from a known-good artifact — never author from memory.** Three failures this session. Before depositing: copy header line 1-2 from a recent `Done/` plan; copy the QA Rule 20 banner pair (`Rule 20 — QA Self-Check Results` / `PASSED — SELF-CHECK PASSED`) from a recent passing `knowledge/qa/*.md`; confirm `**Deposits:**` bold-colon form. See LESSONS 2026-05-28.
- **Parse-check plan headers locally before the atomic move:** `python3 -c "import gates; print(gates._parse_plan_header(open(PATH).read()))"` — assert `dispatch_mode` extracts. Caught the v2 header this session.
- **R2 recovery shape codified (LESSONS 2026-05-27).** Decision tree at teardown cherry-pick conflict: transient lifecycle artifact → copy deposit to main, commit standalone, leave artifact uncommitted; dirty bookkeeping file → commit Planner edit first, then cherry-pick. The pre-check shipped this session catches these before the cryptic conflict once the daemon is restarted.
- **Watcher can miss `move_file` deposits.** If a deposited plan sits unclaimed (heartbeats continue, no `detected plan`), a restart's startup scan claims it. BACKLOG entry filed.
- **Rule 41 SA anchors mandatory for prompts >400w.** This session's SA step completed cleanly with anchors.
- **Stale-worktree cleanup discipline:** `git worktree list` after any teardown failure; `git worktree remove --force` clears blockers. Two stale worktrees currently present.

---

## CEO actions before next session

- **Restart the Bellows daemon** to load the dirty-tree pre-check symbols. Until restart, the pre-check is on disk/main but not live in the running process.
- Optional: stale-worktree sweep (`git worktree remove --force` on the two orphaned worktrees).
- Optional: review the session-12 ship next session start as a Phase 1.5 sanity check — new `worktree_teardown_dirty_tree` gate, 122/122 suite, three new BACKLOG entries at top of Open.
