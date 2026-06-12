# Bellows — Forward Register

> Standing queue of deferred work and parked CEO decisions. Persists across sessions
> until acted on. Supersedes the former BACKLOG.md Open section.
>
> **Reconciliation:** at session wrap, each entry is checked against lifecycle DB /
> reconstruction reports for closure (see PLANNER_TEMPLATE.md Rule 42 — the canonical reconciliation rule).

---

| # | Added | Item | Type | Plan-id link | Status |
|---|---|---|---|---|---|
| 1 | 2026-05-13 | `_extract_step_text` regex case-sensitivity — allow mixed-case `## Step N` headers (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 2 | 2026-05-21 | Bellows status UI — design shape decision for real-time plan/step observability surface (context in BACKLOG-ARCHIVE.md) | ceo-decision-fork | — | open |
| 3 | 2026-05-21 | Deposits parser: strip parenthetical qualifiers from backtick paths in `_extract_plan_required_deposits` (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 4 | 2026-05-22 | Worktree teardown cherry-pick conflict when local `main` has uncommitted `PROJECT_STATUS.md` edits (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 5 | 2026-05-22 | Parallel-diagnostic cherry-pick conflicts on shared append-only bookkeeping files at teardown (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 6 | 2026-05-27 | Verdict-response filename prefix tolerance vs. README convention — investigate matching logic (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 7 | 2026-05-27 | `lessons-forge.db` tracked-but-gitignored disposition — commit-on-change vs un-track (context in BACKLOG-ARCHIVE.md) | ceo-decision-fork | 30 | closed-by-plan-30 |
| 8 | 2026-05-28 | `stop_prose` false-positive on `do not proceed` inside Rule 20 instructional prose — closed 2026-06-12: subsumed by row 17 fix (diagnostic 27) (context in BACKLOG-ARCHIVE.md) | deferred-work | 29 | closed-by-plan-29 |
| 9 | 2026-05-28 | Pre-deposit plan-lint script for strict-convention strings (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 10 | 2026-05-29 | `scope_check` cannot evaluate plans delegating file lists to a referenced blueprint (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 11 | 2026-05-29 | `stop_prose` matches PLANNER_TEMPLATE-prescribed `STOP. Do NOT proceed` step-boundary language — closed 2026-06-12: subsumed by row 17 fix (diagnostic 27) (context in BACKLOG-ARCHIVE.md) | deferred-work | 29 | closed-by-plan-29 |
| 12 | 2026-05-30 | Worktree re-creation on resume checks out `main` HEAD, not the step's branch (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 13 | 2026-05-31 | Worktree teardown→resume: Gap 2(b)/(c) auto-resume-from-branch + Gap 3 auto-stash — deferred friction-reduction (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 14 | 2026-06-01 | QA report verification-table status glyph corrupted to U+FFFD — cosmetic one-cell fix (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 15 | 2026-06-06 | `__file__`-relative root resolution: 3 latent instances (`bellows.py`, `planner.py`, `verdict.py`) deferred by CEO disposition (context in BACKLOG-ARCHIVE.md) | deferred-work | — | open |
| 16 | 2026-06-08 | `scope_check` false-positive on continuous-run multi-step plans — withdrawn 2026-06-12: already fixed pre-id by union scope_check (commit 706fbe7); per diagnostic 27 (context in BACKLOG-ARCHIVE.md) | deferred-work | — | withdrawn |
| 17 | 2026-06-08 | `stop_prose` WARN on legitimate error-handling prose (context in BACKLOG-ARCHIVE.md) | deferred-work | 29 | closed-by-plan-29 |
| 18 | 2026-06-11 | Persist partial agent output stream on inactivity-timeout kill (context in BACKLOG-ARCHIVE.md) | deferred-work | 24 | closed-by-plan-24 |
| 19 | 2026-06-12 | Concurrent-daemon startup recovery race — misclassifies actively-running plan as abandoned (context in BACKLOG-ARCHIVE.md) | deferred-work | 22 | closed-by-plan-22 |
| 20 | 2026-06-12 | `plans.lifecycle_state` intermediate states (`in_progress`, `awaiting_verdict`) never written (context in BACKLOG-ARCHIVE.md) | deferred-work | 22 | closed-by-plan-22 |
| 21 | 2026-06-12 | Parallel-plan worktree diff contamination trips scope_check — a concurrent plan's merged artifacts appear in a later-pausing plan's files_changed (observed: plan 19 QA artifacts flagged in plan 20's gate; CEO override required) (context: processed-verdict-20-step-1) | deferred-work | 28 | closed-by-plan-28 |
