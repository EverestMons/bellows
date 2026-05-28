# Bellows — Next Session Baton

**Last session:** 2026-05-28 (session 14)
**Last session focus:** Closed BACKLOG #1 (dirty-tree pre-check false-trip) and #2 (cascade). Shipped lifecycle filter, QA-verified it, smoke-tested live daemon. First fully clean Bellows dispatch in three sessions.

---

## Session summary

Diagnostic → DEV → QA → smoke test, four-arc ship across one session. Two Planner-direct R2 closures along the way (consistent with session 13's pattern — now a documented LESSON).

- **Diagnostic** (`Done/diagnostic-dirty-tree-precheck-false-trip-surface-2026-05-28.md`): mapped the filter surface, produced regex + predicate spec at Section 3, test surface at Section 6. Confirmed BACKLOG #2 (cascade) is a downstream symptom of #1.
- **DEV** (commit `7bb05ae` `feat: add lifecycle-artifact filter to dirty-tree pre-check`): `_LIFECYCLE_IGNORE_RE` at `bellows.py:32-51` + `_is_lifecycle_artifact()` at lines 43-51 + pre-check integration at lines 885-916. Shipped via R2 sub-variant Planner-direct close — the executable's own dispatch tripped the very bug it was designed to fix (daemon hadn't loaded the filter yet).
- **QA** (commit `3d79151`, halted Planner-direct on teardown cherry-pick conflict, substance shipped): 3 filter-positive + 4 filter-negative (CRITICAL SAFETY) + 1 regex-coverage + full-suite regression. All 7 new tests PASS locally on main at `f8edacc` (429 passed, 4 pre-existing failures only). Rule 20 self-check PASSED.
- **Smoke test** (commit `d4d7b56` deposit + `f8edacc` close): first fully clean Bellows dispatch this session (no R2 recovery). Confirms filter operational in live daemon. Single-step SA, single deposit, all 10 gates PASS.

| # | Artifact | Outcome |
|---|---|---|
| 1 | Diagnostic | `Done/diagnostic-dirty-tree-precheck-false-trip-surface-2026-05-28.md`; SA findings at `knowledge/research/`. |
| 2 | DEV executable | DEV shipped `7bb05ae`. Halted Planner-direct (substance landed via R2 recovery). |
| 3 | QA executable | QA shipped at `3d79151` (7 new tests, all pass). Halted Planner-direct (teardown cherry-pick conflict, substance landed). |
| 4 | Smoke test | `Done/executable-smoke-daemon-connectivity-2026-05-28.md`. Clean teardown, no R2 needed. Halted via verdict-stop consumption. |

**Commits this session (bellows):** `49baac9` (DEV close + verdicts), `3d79151` (QA close), `d4d7b56` (smoke deposit, Bellows-authored), `f8edacc` (smoke close). Main HEAD: `f8edacc`.

**Governance submodule pointer**: BUMPED at session wrap (`abc01f7` → new pointer reflecting `f8edacc`).

---

## In-flight threads (carry forward)

None active. Tree clean. Daemon idle.

---

## Open BACKLOG items added this session (4) — TOP OF OPEN

1. **`_LIFECYCLE_IGNORE_RE` false-strict on space-prefixed porcelain codes** (`dt_result.stdout.strip()` at bellows.py:886 strips leading space from ` D foo.md`). Safe direction; trivial fix (`rstrip()` instead).
2. **Pre-check trips on test fixtures' `.bellows-worktrees/` directory** (3 pre-existing `test_worktree.py` failures). Directory-prefix outside the lifecycle filter coverage. Add to regex or fix fixtures.
3. **Dispatch-validator `stop_prose` matches "do not proceed" in instructional prose.** Smoke-test surfaced. WARN-only, doesn't halt. Tighten detector.
4. **Vestigial `mv` claim-rename in plan prose.** R3 shadow-cache makes it a no-op; agents observe "doesn't exist, I'll skip" and produce intermediate-decision phrase-matches. Fix at PLANNER_TEMPLATE source.

---

## BACKLOG closures this session

- **BACKLOG #1** (Dirty-tree pre-check false-trips on lifecycle artifacts) — CLOSED.
- **BACKLOG #2** (Failed teardown strands worktree → cascade) — CLOSED (subsumed by #1 fix).
- **QA regression tests for `_seen.discard`** — CLOSED (deferred indefinitely; precondition now met but standalone risk is low).

---

## LESSONS promoted this session

1. **R2 sub-variant Planner-direct close** is the documented working recovery shape for "substance shipped, teardown cherry-pick conflicts on lifecycle artifacts." Two-session recurrence count. Includes the 6-step recovery procedure. Filed at LESSONS.md top.

---

## On the horizon (next session)

1. **Rule 25 routing sub-note for `worktree_teardown_dirty_tree`** — STILL NOT DONE (deferred across two sessions). Single-edit governance plan through Documentation Agent. Option (i) routing decision already made (sub-note on `gate_failure` keyed on evidence-string prefix).
2. **Cherry-pick conflict on `in-progress-*` plan files during teardown** — NEW failure mode that the lifecycle-filter ship surfaced as the next layer of the teardown stack. Not in BACKLOG yet (only mentioned in this baton). The filter handles the *pre-check*; the cherry-pick command itself still chokes on the same file when the worktree commit treats `in-progress-*` as a tracked addition while main has it as `verdict-pending-*` at the same path. R2 sub-variant recovery now documented in LESSONS. **Decide:** file as new BACKLOG entry, or treat as known-and-documented operational pattern.
3. **Bellows status UI** (2026-05-21) — still unscoped, big design item.
4. **Open BACKLOG** (12 entries after this session's closures + adds): the four new this-session entries above + the existing 8 (Rule 25 routing, pre-deposit lint, verdict prefix tolerance, lessons-forge.db, orphan-guard wrong-step, dirty PROJECT_STATUS variant, parallel-diagnostic teardown, deposits parser parens, no-match warning rate-limit, `_extract_step_text` case).
5. **Other projects on horizon:** anvil (first executable still pending), invoice-pulse (Phase B pending Windows query results), forge, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest.

**Next session options:**
- **Quick wins** — Rule 25 routing sub-note (single governance edit), `rstrip()` fix + `.bellows-worktrees/` regex addition (the two follow-on BACKLOG entries this session created share a single file).
- **Shift to another project** — anvil first executable, invoice-pulse Phase B, or any other on the horizon.

---

## Discipline reminders for next baton

- **Lifecycle filter is live at commit `7bb05ae`.** Pre-check no longer trips on lifecycle artifacts. Tree still needs to be clean for *real* dirty files before dispatch — the filter doesn't change that. The R2 recovery shape (now in LESSONS) handles the teardown cherry-pick edge case that remains.
- **Copy strict convention strings from a known-good artifact, never author from memory.** Held this session — header parse-checked locally before both atomic moves.
- **Two-bellows.py-processes diagnostic** (this session): if you see duplicate `bellows.py` processes, the second one is detached (likely from Ctrl-Z then resume losing the controlling terminal). Always verify `ps aux | grep bellows.py | grep -v grep` shows exactly one process before starting a fresh daemon. Use `kill <pid>` for detached processes — Ctrl-C cannot reach them.
- **PROJECT_STATUS.md decision still pending** — last session's flag carried forward. NEXT_SESSION.md + BACKLOG.md are carrying session history; PROJECT_STATUS is partially backfilled but Rule 8 still mandates a one-line-per-step update. Decide: maintain (and what cadence), or retire (and dereference). Not blocking next session.
- **Diagnostic-first (Rule 10)** continues to earn its keep — this session's diagnostic correctly disposition'd BACKLOG #2 as a downstream symptom rather than a separate fix.

---

## CEO actions before next session

- **No required action.** Daemon idle, tree clean, no in-flight plans, no pending verdicts.
- Optional: kill the foreground daemon if not actively using; restart at session start.
- Top of next session: pick a thread from "On the horizon" above.
</content>