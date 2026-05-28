# Bellows — Next Session Baton

**Last session:** 2026-05-28 (session 13)
**Last session focus:** Hygiene + small-hardening pass that turned into a real build + a significant finding. Shipped the `_seen.discard`-on-rejection fix (the root cause of the session-12 plan-claim miss). But the session's more important output: last session's `worktree_teardown_dirty_tree` pre-check (shipped session 12) is **net-negative for multi-step plans** — it false-trips on Bellows's own lifecycle artifacts and trapped a plan in a recovery loop.

---

## Session summary

Session opened on the session-12 baton's option (2): hygiene + small-hardening (Rule 25 routing entry, rescan self-heal, worktree sweep). Diagnostic-first discipline (Rule 10) paid off twice and exposed a real problem.

- **Worktree sweep (Planner-direct):** removed the two stale worktrees (`bash-gate-guardrails-exemption-2026-05-20`, `remove-pre-scan-processed-rename-v2-2026-05-24`). Both clean, both shipped work. Closed.
- **Rescan self-heal diagnostic (SA):** REFRAMED the BACKLOG entry. The entry proposed "add a periodic `decisions/` rescan" — but reading the code showed `_rescan` already does exactly that (bellows.py:1172-1177, since 2026-05-15). Real root cause (hypothesis (b), confirmed against the session-12 log): the dispatch-mode validator rejection path was the ONLY `run_plan` early-exit that didn't call `_seen.discard()`. A rejected v1 diagnostic stranded its slug; `slug_from_path` strips both `diagnostic-`/`executable-` prefixes, so the follow-on executable inherited the stranded slug and was silently skipped every rescan tick until the manual restart cleared `_seen`. The proposed fix was dead code; the real fix is 2 LOC.
- **`_seen.discard` fix (DEV):** shipped commit `0322124` — adds `if bellows is not None: bellows._seen.discard(verdict.slug_from_path(plan_path))` to the rejection path, mirroring the line-668 auto-close precedent. Planner-verified by direct code read. Dev log `7069793`.
- **THE FINDING — dirty-tree pre-check false-trips on lifecycle artifacts.** The `worktree_teardown_dirty_tree` pre-check tripped teardown THREE times this session, every time on Bellows's own untracked bookkeeping (`verdict-pending-*`, `processed-verdict-*`, `in-progress-*`, Done/ plans), never a real cherry-pick conflict. On the multi-step `_seen` executable it created a cascade: teardown abort → stranded worktree → next-step `worktree_creation` precondition failure → precondition-retry resumes the SAME (already-run) step → re-trips teardown → loop. Broke the loop by closing the executable Planner-direct (commit `3b9a997`); QA regression tests deferred.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Worktree sweep | 2 orphans removed, Planner-direct. |
| 2 | Diagnostic (rescan miss) | Reframed BACKLOG premise; root cause = `_seen` stranding on validator rejection. `Done/diagnostic-rescan-miss-disposition-2026-05-28.md`. Continue verdict (after R2 dirty-tree recovery). |
| 3 | Executable (`_seen` fix) | DEV shipped 2-LOC fix `0322124` + dev log `7069793`. QA NEVER RAN — closed Planner-direct (`3b9a997`) after dirty-tree pre-check loop. |

**Commits this session (bellows):** `cb57887` (diagnostic findings, recovered via checkout), `427765d` (diagnostic lifecycle artifacts), `0322124` (the `_seen` fix), `7069793` (dev log), `3b9a997` (executable close). Main HEAD: `3b9a997`.

**No daemon restart strictly required** for the `_seen` fix to take effect on NEW slugs (the bug only stranded already-seen slugs), but a restart WILL clear the stale "1 awaiting verdict" in-memory count (see below) and load `0322124` into the running process. Recommend restart at session start.

---

## In-flight threads (carry forward)

None active. All plans resolved. BUT: the running daemon (PID 80902 at session-13 close) has a **stale in-memory "1 awaiting verdict" count** for the closed `seen-discard-rejection-path` plan — the plan file was moved to Done/ Planner-direct and its verdict bookkeeping removed, but the daemon's in-memory awaiting-set still holds it. Not re-dispatching (nothing on disk to claim), purely cosmetic. Clears on restart.

---

## Open BACKLOG items added this session (3) — TOP OF OPEN

1. **Dirty-tree pre-check false-trips on Bellows's own lifecycle artifacts** — HIGHEST priority. The session-12 pre-check checks `git status --porcelain` for ANY uncommitted state, but Bellows constantly generates untracked lifecycle files (`verdict-pending-*`, `processed-verdict-*`, `in-progress-*`, `halted-*`, Done/ plans, `verdict-request-*`). None are real cherry-pick conflicts. Fix: narrow the check to exclude daemon-managed paths/prefixes (diagnostic first to enumerate the set). **The session-12 ship was net-negative for multi-step plans as it stands.**
2. **Failed teardown strands the worktree → blocks next step's worktree creation (cascade)** — likely subsumed by #1; if not, add a worktree-recreate-on-collision guard. Also documents the precondition-retry-resumes-same-step interaction that made it a loop.
3. **QA regression tests for the `_seen.discard` fix — deferred** — a standalone 1-step QA plan (tests only, fix already shipped). Dispatch AFTER #1 is fixed or the QA plan's own teardown risks the same loop.

---

## LESSONS to promote (session-wrap — NOT yet written to LESSONS.md)

Two candidates, both from this session:

1. **The dirty-tree pre-check shipped as hardening has a worse failure mode than the conflict it replaced, for multi-step plans.** It doesn't distinguish Bellows's own bookkeeping from real source conflicts. Meta-lesson: a "hardening" ship that surfaces a clearer error can still be net-negative if it fires on benign daemon-generated state. Validate hardening against the daemon's OWN operational artifacts, not just the failure case it targets.
2. **Diagnostic-first (Rule 10) overturned the BACKLOG premise twice this session** — the rescan entry proposed adding code that already existed; the line-1369 baton item was already shipped (v4.54). Both caught by reading current state before authoring. Continued recurrence of "BACKLOG/baton entries authored from observation without scanning the code/governance that explains them."

(Note: LESSONS.md was NOT edited this session — these are candidates for next session's promotion, or promote now if continuing.)

---

## On the horizon (next session)

1. **Dirty-tree pre-check false-trip fix** (BACKLOG #1 above) — the clear top priority. Diagnostic to enumerate daemon-managed paths, then narrow-filter executable. This unblocks clean multi-step plan execution.
2. **QA tests for the `_seen` fix** (BACKLOG #3) — after #1.
3. **Rule 25 routing-table entry for `worktree_teardown_dirty_tree`** — STILL NOT DONE (deferred this session when the `_seen` work took over). Single-edit governance plan through the Documentation Agent. NOTE: scope is single-edit — the line-1369 pairing the session-12 baton suggested is ALREADY SHIPPED (v4.54, confirmed this session); do not re-do it. Routing decision already made: option (i) — `gate_failure` sub-note keyed on the evidence-string prefix (NOT a new routing-table row, because the gate has no distinct Pause Reason Code), stop-and-report but report surfaces the inline recovery commands.
4. **Bellows status UI** (2026-05-21) — still the big unscoped design item.
5. Lower-priority carryovers: verdict filename prefix tolerance (2026-05-27), lessons-forge.db disposition (2026-05-27), orphan-guard wrong-step (2026-05-27), parallel-diagnostic teardown conflicts (2026-05-22), and the Priority-3 defer-by-disposition items.

**Next session options:**
- **Fix the dirty-tree pre-check false-trip** — clear top priority; it's actively breaking multi-step plans. Diagnostic → executable.
- **Quick wins** — Rule 25 routing sub-note (single governance edit) + the deferred `_seen` QA tests (after the pre-check fix).
- **Shift to another project** — forge, anvil (first executable still pending), invoice-pulse (Phase B pending Windows query results), study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

---

## Open governance follow-up

- **Rule 25 routing sub-note for `worktree_teardown_dirty_tree`** — scoped this session (option (i), evidence-string-prefix sub-note on the `gate_failure` row), not authored. Single-edit governance executable through Documentation Agent. The line-1369 historical-lesson fix the session-12 baton paired with this is ALREADY DONE (v4.54) — confirmed by reading LESSONS row at PLANNER_TEMPLATE line ~1604.
- **PROJECT_STATUS.md is STALE** — last dated section is 2026-04-19, despite multiple session batons claiming it was updated. Session history is being carried entirely by NEXT_SESSION.md + BACKLOG.md. **Decision needed:** is PROJECT_STATUS.md meant to be maintained, or has it been de facto retired in favor of the baton? If retired, say so explicitly; if maintained, it needs ~5 weeks of backfill or a "see baton history" pointer. Flagged but not acted on this session.

---

## Discipline reminders for next baton

- **Dirty-tree pre-check WILL trip on lifecycle artifacts until BACKLOG #1 ships.** Until then: commit/clean ALL Bellows lifecycle artifacts (Done/ plans, processed verdicts, in-progress renames) BEFORE any plan's teardown, not at session-wrap. The pre-check forces lifecycle commits eagerly. For multi-step plans, expect teardown trips between steps and keep the tree clean throughout — or close Planner-direct if it loops.
- **Copy strict convention strings from a known-good artifact, never author from memory.** Held this session — header parse-checked locally before both atomic moves (`gates._parse_plan_header`), no authoring failures. NOTE: a recent QA report (`knowledge/qa/executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md`) contains the WRONG banner (`RULE 20 SELF-CHECK: PASSED`) — it is the artifact of a session-12 failure, NOT a known-good source. Pull the canonical banner (`Rule 20 — QA Self-Check Results` / `PASSED — SELF-CHECK PASSED`) from `gates.py:475` + the PASSED regex at `gates.py:505`, or `RULE_20_SELF_CHECK_BLOCK.md`.
- **Verdict filenames must match `^verdict-(.+)-step-(\d+)\.md$` EXACTLY.** A `-step-1-retry.md` suffix was silently skipped this session (`verdict filename format mismatch`) until renamed to bare `-step-1.md`. No suffixes.
- **Diagnostic-first (Rule 10) is earning its keep.** Two BACKLOG/baton premises overturned this session by reading current state before authoring. Keep grepping Closed + current code before treating any baton item as live.
- **Daemon restart at session start** clears the stale awaiting-count and loads `0322124`.

---

## CEO actions before next session

- **Restart the Bellows daemon** — clears the stale "1 awaiting verdict" in-memory count for the closed `seen-discard-rejection-path` plan and loads the `_seen` fix (`0322124`) into the running process.
- Decide on **PROJECT_STATUS.md** — maintain or retire (see Open governance follow-up).
- Top of next session: **fix the dirty-tree pre-check false-trip** (BACKLOG #1) — it's actively breaking multi-step plans.
