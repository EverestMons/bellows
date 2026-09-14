# Dev log — abandoned-runner-close — 2026-09-13

## What was built

Startup-time cleanup for abandoned plan runners: when the Bellows daemon restarts
after a crash it now detects plans that were `in_progress` with a registered git
worktree and closes them cleanly before starting normal work.

**`bellows.py`** — `_live_processes_in(wt_path)`: calls `/usr/sbin/lsof -Fpn`
with `LC_ALL=C` and `\xNN`-encodes the worktree realpath so non-ASCII byte paths
match lsof's locale-C escape output.  `_snapshot_uncommitted`: commits any dirty
index into the worktree branch before preservation.  `_preserve_and_remove_stranded_worktree`:
creates a `bellows-preserved/<slug>-<ts>` branch for un-landed commits, then
removes the worktree; raises `PreserveFailed` in strict mode.
`_close_abandoned_runner`: orchestrates schema check → live-process guard → snapshot
→ preserve-and-remove → lane-file move → step/plan state writes → claim release →
page.  `_run_startup_recovery`: calls `notifier.init_notifications` FIRST (so pages
are armed before any close page fires), then loops over watched projects via
`recover_half_claimed`, wrapping each `abandoned_runner` close in a try/except so
one failure doesn't abort recovery for subsequent plans.  `_check_idle`: new
`holder_pid` parameter — a running step whose `daemon_pid` differs from the holder
skips the idle guard, allowing `stop_daemon` to proceed for a step started by a
previous daemon.  `stop_daemon`: passes `holder_pid` to `_check_idle`.

**`lifecycle.py`** — `_migrate_steps_abandoned`: one-time rebuild migration that
adds `'abandoned'` to the steps CHECK constraint and `daemon_pid INTEGER` column,
with a date-stamped backup.  `init_lifecycle_db`: calls the migration after applying
the `daemon_pid` ALTER TABLE.  Partial unique index on
`plans(deposit_placeholder_name) WHERE lifecycle_state IN (claimed/in_progress/awaiting_verdict)`
prevents duplicate active claims.  `record_step_start`: ON CONFLICT upsert with
RETURNING that records `daemon_pid = os.getpid()` and refreshes the field on resume.
`mark_step_abandoned`: flips running steps to `abandoned` for a given plan.
`recover_half_claimed`: in-progress arm now applies a lane-file discriminator
(in-progress or done/abandoned lane → `abandoned_runner`; parked lane → `skipped_parked`)
before the age guard.

**`notifier.py`** — `plan_abandoned` event added to `_DEFAULT_EVENTS` (default True).
`notify_plan_abandoned`: sends a Pushover page with closed/not-closed title and body.

**`tools/reconcile_steps.py`** — `_apply`: initialises the DB before writing;
runs a second pass that flips `running` steps on `abandoned` plans to `abandoned`
status, with the early-return moved below both passes.

## Key decisions

**`LC_ALL=C` + `\xNN` encoding for lsof output**: macOS lsof with `LC_ALL=C`
outputs non-ASCII bytes in path names as literal `\xNN` sequences (e.g. `\xc3\xa9`
for UTF-8 `é`). The production daemon runs under launchd with a minimal PATH and
no locale; without the absolute path `/usr/sbin/lsof` it would raise
`FileNotFoundError`. Both fixes are required and independently mutation-tested.

**`strict=True` in `_preserve_and_remove_stranded_worktree`**: the close path
raises `PreserveFailed` on branch-creation failure so that an un-preserved commit
is never silently lost. The caller logs and pages with `closed=False` so the
operator knows to retry after clearing the cause.

**`daemon_pid` upsert on step resume**: `record_step_start` uses
`ON CONFLICT(plan_id, step_number) DO UPDATE ... WHERE steps.status = 'running'`
with `RETURNING id`. On resume, the new daemon stamps its own pid so stop-daemon's
idle guard can distinguish "step started by the current daemon (refuse)" from
"step started by a previous daemon (pass through)".

**init_notifications called once before the recovery loop**: if it were called
inside the loop, a pages-disabled config could arm notifications mid-loop and fire
a page for the wrong plan, or — with the mutation — notifications might not be
armed at all before the first page. Placing it before the loop is the only correct
position.

## Testing notes

25 tests in `tests/test_abandoned_runner_close.py` (c-t1 through c-t25).  18 tests
in `tests/test_lifecycle.py` covering the migration and new lifecycle functions.
4 tests in `tests/test_reconcile_steps.py` (r-t1 through r-t4).  3 tests in
`tests/test_stop_path.py` (i-t1 through i-t3).  Full suite: 2364 passed, 2 skipped.

Three test fixes were required after the first mutation run:

- **c-t12 `target_project` mismatch**: `_make_plan` was called with `repo` (at
  `tmp_path/repo`) while `_run_startup_recovery` computes `_project_root` as
  `Path(decisions).parent.parent` = `tmp_path/proj`. `recover_half_claimed` filters
  by `target_project`, so the plan was never found, the try/except never entered,
  and the mutation silently survived. Fix: use `proj_root = tmp_path / "proj"` for
  the plan's target.

- **c-t15 `bool` is a subclass of `int`**: `_live_processes_in` returns `False`
  when no process is found and `None` on error. `isinstance(False, int)` is `True`
  in Python, so the assertion let both `remove-xnn-encoding-of-realpath` and
  `remove-lc-all-c-pin` survive. Fix: `isinstance(result, int) and result is not False`.

- **c-t25 dual-outcome `else`**: the test accepted either `refused_preserve_failed`
  or `closed`, so suppressing `PreserveFailed` let the mutation survive with the
  close continuing to completion. Fix: remove the `else: assert outcome == "closed"`
  branch so only `refused_preserve_failed` is accepted.

Additionally three manifest ERRORs were fixed: `if False:` without a body is a
`SyntaxError` (pytest exit 4) for the inprogress and parked lane-check mutants
(fixed: `if False:\n    pass`); the `verdict-slug-for-status-read` anchor had
12-space indentation but the code has 8-space (fixed in anchor string).
`remove-snapshot-call`'s `expect_fail` was pointing at `test_preserved_branch_and_worktree_removed`
which doesn't check that `_snapshot_uncommitted` ran — the correct discriminating test is
`test_stale_index_lock_refused_snapshot_failed`. The `init-notifications-after-closes`
mutation was moving init inside the loop (still before each close), which c-t7's
`call_order[0] == "init"` check still passes; changed to remove init entirely so
`call_order[0]` is the close call.

Mutation result: **30 killed, 0 survived, 0 error**.
