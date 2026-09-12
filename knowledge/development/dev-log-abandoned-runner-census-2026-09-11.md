# Dev-log — Abandoned-Runner Census (#100091, thread 296)

**Date:** 2026-09-11 | **Plan:** #100091 | **Tier:** T1 | **Class:** app-feature
**Scope:** read-only diagnostic; writes dev-log + two governance research files (Planner-commit deposits)
**Before readings:** `PRAGMA data_version = 2`; `git -C /Users/marklehn/Developer/bellows status --porcelain -- knowledge/qa/evidence` = clean

---

## Pins re-derived (P1, P4, P5, P6)

P7 cell (verbatim): plan 100051 `abandoned`, placeholder `d.md`, created 2026-09-09T11:10:35, closed 2026-09-09T16:34:27Z; plan 100081 `abandoned`, created 2026-09-11T15:07:00, closed 20:57:16Z by the reconcile tool; plan 100082 `abandoned`, created 16:01:24, closed 21:27:57Z; their steps 90, 141 and 142 all `running`, with no end and no cost; no verdict rows for 100081 or 100082; three abandoned plans in the DB and three running phantoms; the tuyere claim on `executable-bellows-readonly-wal-open-v2`: event released, seq 2, at #100083's close

**P1 re-derived (bellows.py drain mechanism):**
- `_DRAIN_TIMEOUT = 30` at bellows.py:114 — matches P1 pin.
- `_sigterm_handler` at bellows.py:3581; second-signal branch: `_log("WARN", "second signal during drain — forcing immediate exit")` at :3583, `sys.exit(1)` at :3586; SIGTERM log at :3588; drain loop at :3589–3598; drain-timeout log at :3600; `sys.exit(0)` at :3605.
- `_run_tracked` `finally` decrements `_active_count` at :2868; `handle_new_plan` logs `▶ started` at :2901 after thread spawn — no conditional on the thread's outcome.
- `recover_half_claimed` called at :3738.
- `release_for_plan` called at 7 sites (bellows.py:953, 1138, 1190, 1575, 3412, 3450, 3489); none is on the drain-timeout exit path.
- **No mechanism mismatch.**

**P4 re-derived (lifecycle.py recovery + reconcile tools):**
- `recover_half_claimed` at lifecycle.py:330; in_progress strand arm at :402–440; worktree check `os.path.isdir(wt_path)` at :433; `skipped_worktree_exists` at :434; abandonment write at :438.
- `tools/reconcile_plan.py`: `UPDATE plans` at :102, `UPDATE verdicts` at :106, `os.rename` of pending verdict files at :126. Steps rows: untouched.
- `tools/reconcile_steps.py`: lists `running` rows on non-in_progress plans at :50; `--apply` flips only `awaiting_verdict` on closed plans at :85; `running` rows not touched.
- **No mechanism mismatch.**

**P5 re-derived (plan_claim.py claim gate memo):**
- `_outcome_memo` dict at plan_claim.py:22; `claim_gate` at :123; memo lookup at :133; short-circuit at :134–135; memo write at :136; first-decline WARN at :150.
- Confirmed: first decline for `executable-bellows-readonly-wal-open-v2` at 15:59:56 logged WARN with self-strand hint; two subsequent rescans (16:00:17, 16:00:50) logged `▶ started` only — memo suppressed the WARN.
- **No mechanism mismatch.**

**P6 re-derived (gate_watcher.py resolution):**
- `read_state` at gate_watcher.py:62; placeholder resolution: `ORDER BY id DESC LIMIT 1` at :74.
- Confirmed: watch log shows both 15:57:27 and 15:57:36 arms resolved to `id=100081` (still newest at arm time); 16:35:31 arm resolved to `id=100082` (also abandoned).
- **No mechanism mismatch.**

**After readings:** `PRAGMA data_version = 2` (unchanged — no DB writes during census).

---

## The surfaces after an abandonment (Q2)

Path: SIGTERM drain timeout (observed twice on 2026-09-11).

| surface | after exit | after restart+recovery | after reconcile_plan.py | after hand acts (thread 296) |
|---|---|---|---|---|
| plan row | `in_progress` (drain exits 0, no DB write) | `in_progress` — `skipped_worktree_exists` (worktree present, lifecycle.py:434) | `abandoned`, `closed_at` set (reconcile_plan.py:102) | unchanged |
| step row | `running`, `step_ended_at=None`, `cost_usd=None` | `running` — recovery untouched | `running` — reconcile_plan.py untouched; reconcile_steps.py lists but `--apply` flips `awaiting_verdict` only | `running` — still phantom in DB |
| lane file | `in-progress-executable-<id>.md` present | present | present (reconcile_plan.py prints wrong filename; thread 296) | moved to `Done/abandoned-executable-<id>.md` |
| worktree+branch | both present | both present (discriminator for `skipped_worktree_exists`) | both present (reconcile_plan.py untouched) | both removed by hand |
| tuyere claim | `event=claimed, seq=0, liveness=live` | claimed; first rescan decline logged once (15:59:56); subsequent rescans: `▶ started` only | claimed (reconcile_plan.py untouched) | released via `tuyere.claims release <slug> --reason self-strand` |
| receipt+watcher | watcher resolves placeholder to newest id; sees abandoned; exits `terminal — abandoned` | on redeposit: same placeholder still resolves to abandoned run; redeposit unwatched | unchanged | receipt archived |
| verdict files | none (step 1 never reached verdict request; 0 verdict rows in DB for 100081/100082) | none | none (reconcile_plan.py:126 would archive if present) | none |
| model child | dead (process group killed by launchd; no `AbandonProcessGroup`; transcript last line = drain second) | n/a | n/a | n/a |

---

## Q1–Q5 in one table

| Q | question | answer (one line) | primary source |
|---|---|---|---|
| Q1 | Every way the daemon can stop while a step runs | 8 paths: SIGTERM drain completes, SIGTERM drain timeout (2 observed), second signal (inferred), SIGKILL (inferred), main-thread exception (inferred), runner-thread exception (daemon continues — not a stop), host asleep (not a stop), logout/reboot (inferred) | bellows.py:3581–3605; plist:37–41 |
| Q2 | What each surface holds after drain-timeout abandonment | Plan row: `in_progress`; step row: `running` phantom; lane file: `in-progress-` present; worktree+branch: both present; claim: held; watcher: resolves to abandoned id; verdict files: none; model child: dead | DB queries; logs/terminal/bellows-2026-09-11.log; transcript timestamps; thread 296 |
| Q3 | Which existing tool restores which surface | `reconcile_plan.py` restores plan row and archives verdict files; `reconcile_steps.py --apply` restores `awaiting_verdict` step rows (not `running`); `tuyere.claims release` restores claim; `recover_half_claimed` half-claimed arm restores deposit rename; all others: untouched by any tool | lifecycle.py:330,434; reconcile_plan.py:102,106,126; reconcile_steps.py:50,85; plan_claim.py:157 |
| Q4 | The three running phantoms in the DB | Step 90/plan 100051: scratch-script import of lifecycle outside pytest (LESSONS.md:6564); steps 141/plan 100081 and 142/plan 100082: drain timeouts of 2026-09-11 (15:25:27, 16:15:10) | DB; logs/terminal/bellows-2026-09-11.log; LESSONS.md:6564 |
| Q5 | The two quiet signals | (a) claim-memo deduplicates WARN: only first decline per slug per daemon process logged (plan_claim.py:134); (b) watcher resolves to newest plan by id: redeposit watcher reads the abandoned run and exits immediately (gate_watcher.py:74; watch log 15:57:27, 15:57:36) | plan_claim.py:133–136; gate_watcher.py:74; logs/terminal/bellows-2026-09-11.log 15:59:56, 16:00:17, 16:00:50 |

---

## What the doc does not establish

- The paths marked `inferred` in Q1 were not observed in the 2026-09-11 logs; `sigterm_drain_completes` is inferred as clean because 36 of 39 SIGTERM events left no drain-timeout line (total 39 at time of reading; Planner measured 38 at bellows `36901bd` — the extra occurred after the 31st wrap).
- The model child's death on the drain's own second is two samples; the mechanism (process group, no `AbandonProcessGroup`) is read from code and the plist.
- Phantom 90's origin is read from the record (LESSONS.md:6564), not reproduced.
- The Air runs the same code and was not read.
- Which surfaces a recovery tool should restore, and whether the daemon should refuse to exit mid-step, are the fix plan's (thread 296). This document only records what currently happens.
