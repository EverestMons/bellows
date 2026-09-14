# Dev Log — Abandoned-Runner-Close — 2026-09-12

## Pins re-derived (P1, P2, P3, P4, P7, P10)

← P3: `steps` lifecycle.py:83–97, `CHECK (status IN ('pending','running','awaiting_verdict','complete'))` :89, `UNIQUE(plan_id, step_number)` :96; four tables reference `steps(id)` — `commits` :102, `deposits` :111, `gate_events` :132, `step_files` :143 — with 207, 592, 1601 and 312 rows, none referring to a missing step; steps 166 rows (max id 166): `complete` 156, `awaiting_verdict` 7, `running` 3 — ids 90 (plan 100051 step 2), 141 (100081 step 1) and 142 (100082 step 1), each on an `abandoned` plan; plans `closed` 84, `halted` 11, `abandoned` 3, none `in_progress`; `PRAGMA foreign_keys` 0 on a fresh connection; the one index on `steps` is `sqlite_autoindex_steps_1`; no trigger and no view

Source: greps and reads run by this plan (100098) at Item 1; the transcript `logs/20260913-174007-step.json` (`raw_output`) at Item 2.

**This plan's P1 re-derived (HEAD = `8f836ac`, run here):**

```
$ git log --format='%h %s' 06b545f..HEAD
8f836ac dev(abandoned-runner-close): mutation run (30 killed, 0 survived, 0 error) and dev-log [100097] [thread 306]
aa9a9ed dev(abandoned-runner-close): fix c-t15 bool/int subclass assertion gap [100097] [thread 306]
a4bb61d dev(abandoned-runner-close): fix mutation manifest anchors and test discriminators [100097] [thread 306]
8b52344 dev(abandoned-runner-close): lifecycle migration, close function, idle-guard pid, notifier event, reconcile pass, four test files, mutation manifest [100097] [thread 306]

$ grep -n '^def init_lifecycle_db\|^def _migrate_steps_abandoned\|^def record_step_start\|^def mark_step_abandoned' lifecycle.py
24:def init_lifecycle_db(db_path=None):
203:def _migrate_steps_abandoned(path):
623:def record_step_start(plan_id, step_number, role=None, db_path=None):
696:def mark_step_abandoned(plan_id, db_path=None):

$ grep -n 'def _check_idle\|def _live_processes_in\|def _preserve_and_remove_stranded_worktree\|def _close_abandoned_runner\|def _run_startup_recovery' bellows.py
285:def _check_idle(db_path, config, holder_pid=None):
1029:def _live_processes_in(wt_path):
1108:def _preserve_and_remove_stranded_worktree(project_path, wt_path, slug, strict=False):
1243:def _close_abandoned_runner(plan_id, decisions_dir, project_root, config):
1510:def _run_startup_recovery(config):
```

MATCH: four commits over `06b545f`; all nine P1 functions present at their declared lines. No mechanism mismatch.

**This plan's P2 re-derived (run here):**

```
$ wc -l knowledge/development/dev-log-abandoned-runner-close-2026-09-13.md
106 knowledge/development/dev-log-abandoned-runner-close-2026-09-13.md

$ grep -n '^## ' knowledge/development/dev-log-abandoned-runner-close-2026-09-13.md
3:## What was built
44:## Key decisions
69:## Testing notes

$ wc -l /Users/marklehn/Developer/bellows/knowledge/decisions/halted-executable-100097.md
159 /Users/marklehn/Developer/bellows/knowledge/decisions/halted-executable-100097.md
```

MATCH: stray dev-log 106 lines; three generic headings (`## What was built`, `## Key decisions`, `## Testing notes`), none of the four declared, no P3 cell. Halted plan 159 lines at its canonical checkout path.

**This plan's P5 re-derived (run here):**

```
$ grep -n '^def test_' tests/test_abandoned_runner_close.py | head -4
173:def test_preserved_branch_and_worktree_removed(tmp_path, repo, decisions, db_path):
211:def test_lane_and_lifecycle_state_after_close(tmp_path, repo, decisions, db_path):
256:def test_claim_released_and_page_sent(tmp_path, repo, decisions, db_path):
310:def test_live_process_refused_then_closed(tmp_path, repo, decisions, db_path):
```

MATCH: c-t1 to c-t4 at their declared lines.

**This plan's P6 re-derived (run here):**

```
$ .venv/bin/python status.py
● Bellows RUNNING  pid —  HEAD 8f836ac  bellows.py@8b52344  up —

IN-FLIGHT
 executable #100098  bellows   Step 1/2  running   …   bellows — executable: THE ABANDONED-R…
```

Daemon running `bellows.py@8b52344` (pre-restart code, as at drafting — the daemon restart remains deferred to this close). This plan (100098) is in flight during Item 1; `halted-executable-100097.md` remains in the canonical lane, untracked, absent from this worktree. The writes → `_assign_class` → **app-feature** (all writes under `knowledge/`, none read-only, no register pattern; clears without a release).

**Halted plan's P1 re-derived against `06b545f` (run here):**

```
$ git show 06b545f:bellows.py | sed -n '3723,3745p'
    # G2: flock single-instance guard — must precede all DB/recovery/watcher work
    _lock_path = str(BELLOWS_ROOT / ".bellows.lock")
    try:
        _lock_fd = acquire_instance_lock(_lock_path)
    ...
    migrate_db()
    lifecycle.init_lifecycle_db()
    for decisions_path in config.get("watched_projects", []):
        if os.path.isdir(decisions_path):
            _project_root = str(Path(decisions_path).parent.parent)
            actions = lifecycle.recover_half_claimed(
                decisions_path, project_root=_project_root,
            )
            for pid, action in actions:
                _log("INFO", f"lifecycle recovery: plan {pid} — {action}")
    notifier.init_notifications(config)

$ git show 06b545f:lifecycle.py | sed -n '328,332p'
def recover_half_claimed(decisions_dir, db_path=None, project_root=None,
                         age_guard_seconds=300):
```

MATCH: startup at `bellows.py:3723`; `recover_half_claimed` at `lifecycle.py:330` (line-number drift from :328 is not a mechanism mismatch). No mechanism mismatch.

**Halted plan's P2 re-derived against `06b545f` (run here):**

```
$ git show 06b545f:bellows.py | sed -n '1710,1715p'
    return sorted(changed)


def _create_worktree(project_path: str, slug: str) -> str:
    """Create a named-branch git worktree for a plan execution.
```

MATCH: `_create_worktree` at `bellows.py:1714`.

**Halted plan's P3 from the live DB — DEV's read (from transcript, event 50):**

```
steps DDL:
CREATE TABLE steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            ...
            CHECK (status IN ('pending','running','awaiting_verdict','complete')),
            ...
            UNIQUE(plan_id, step_number)
        )
steps count: 172
max step id: 172
  awaiting_verdict: 7
  complete: 161
  running: 4
running steps (id, plan_id): [(90, 100051), (141, 100081), (142, 100082), (172, 100097)]
  plans abandoned: 3
  plans closed: 85
  plans halted: 11
  plans in_progress: 1
foreign_keys pragma: 0
commits: 213 rows
deposits: 597 rows
gate_events: 1666 rows
step_files: 323 rows
steps indexes: [('sqlite_autoindex_steps_1',)]
triggers: []
views: []
```

(from the 100097 transcript, event 50 — after a first attempt from the worktree path failed at event 46 with `sqlite3.OperationalError: unable to open database file`)

**Halted plan's P3 from the live DB — this step's read (run here):**

Counts moved since the DEV's read; current values from `sqlite3.connect('file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro', uri=True)`:

- commits: 217 rows (was 213 at DEV's read; 207 at drafting)
- deposits: 600 rows (was 597; 592 at drafting)
- gate_events: 1683 rows (was 1666; 1601 at drafting)
- step_files: 334 rows (was 323; 312 at drafting)
- steps total: 173 (max id 173); was 172; 166 at drafting
- complete: 161; awaiting_verdict: 8; running: 4 (ids 90, 141, 142, 173 — the last is this plan)
- plans: closed 85, halted 12, abandoned 3, in_progress 1
- DDL unchanged: `CHECK (status IN ('pending','running','awaiting_verdict','complete'))`, no `daemon_pid` — migration not yet run (daemon restart still owed from this close)
- foreign_keys: 0; index: sqlite_autoindex_steps_1; no trigger and no view

**Halted plan's P4 re-derived against `06b545f` (run here):**

```
$ git show 06b545f:bellows.py | sed -n '940,960p'
        _cleanup_verdicts_for_slug(plan_slug)
        ...
        shutil.move(inprogress_path, halted_path)
        _delete_shadow(base_filename)
        lifecycle.mark_plan_state(plan_id, "halted", ...)
        _retire_receipts(plan_id)
        plan_claim.release_for_plan(plan_id, "halt: teardown-failed park", config, _log)
        record_run(db_path, halted_path, ...)
        notifier.notify_plan_halted(base_filename, plan_slug=plan_slug)
```

MATCH: halt route at `bellows.py:943–957`; `_cleanup_verdicts_for_slug`, `mark_plan_state`, `_retire_receipts`, `release_for_plan`, `record_run`, `notify_plan_halted` all present in sequence.

**Halted plan's P7 re-derived against `06b545f` (run here):**

```
$ git show 06b545f:tests/test_lifecycle.py | sed -n '1216,1220p'
class TestInProgressStrandRecovery:
    """Plan 54: recover_half_claimed also recovers stranded in_progress plans

$ git show 06b545f:tests/test_lifecycle.py | wc -l
1566

$ git show 06b545f:tests/test_lifecycle.py | sed -n '443,446p'
class TestMarkStepComplete:
    def test_awaiting_verdict_row_flips_to_complete(self):

$ git show 06b545f:tests/test_teardown_recording.py | sed -n '220,224p'
def test_park_path_failure_routes_to_halted(monkeypatch, tmp_path):
    """Teardown failure during park must route to halted-, not parked-."""
```

MATCH: `test_lifecycle.py` 1566 lines; `TestInProgressStrandRecovery` at :1218; `TestMarkStepComplete` at :445; `test_park_path_failure_routes_to_halted` at `test_teardown_recording.py:222`.

**Halted plan's P10 re-derived against `06b545f` (run here):**

```
$ git show 06b545f:bellows.py | sed -n '119,122p'
def acquire_instance_lock(lock_path: str):
    """Acquire the flock-based instance lock, write PID+timestamp.

$ git show 06b545f:bellows.py | sed -n '302,306p'
def stop_daemon(lock_path, db_path, config):
    """Guarded stop path — reaches any incumbent regardless of how it was started.

$ git show 06b545f:lifecycle.py | sed -n '493,497p'
def record_step_start(plan_id, step_number, role=None, db_path=None):
    """Insert a steps row with status='running'. Returns step_id or None."""

$ git show 06b545f:tests/test_stop_path.py | sed -n '22,25p'
def _make_lifecycle_db(db_path, rows):
    """Create a minimal lifecycle.db matching the production schema's required columns."""

$ git show 06b545f:tests/test_stop_path.py | sed -n '108,112p'
def test_idle_guard_running_refuses(tmp_path):
```

MATCH: `acquire_instance_lock` at `bellows.py:121` (line-number drift from :119 is not a mechanism mismatch); `stop_daemon` at :304 (drift from :302 not a mismatch); `record_step_start` at `lifecycle.py:495` (drift from :493 not a mismatch); `_make_lifecycle_db` at `test_stop_path.py:24` (drift from :22 not a mismatch); `test_idle_guard_running_refuses` at :110 (drift from :108 not a mismatch).

## Failing-first (four red, then green)

Source: control run and four red runs made by this plan (100098) at Item 3, in a `mktemp -d /tmp/abandoned-close-record.XXXXXX` scratch directory (`bellows` subdirectory, named so `lifecycle.db`'s default path resolves correctly); green line from full suite run at Item 5. The transcript's red runs (P4) were mid-implementation runs, not failing-first: at events 979, 1059, 1119, 1210, 1339 and 1404, covering partial states of the code under development.

**Control (three files at `06b545f`, run here — each green before test files overwritten):**

```
tests/test_lifecycle.py:      104 passed in 0.98s
tests/test_reconcile_steps.py:  3 passed in 0.23s
tests/test_stop_path.py:        7 passed in 5.18s
```

**Four red lines (four test files from HEAD, run over `06b545f` archive, run here):**

```
tests/test_lifecycle.py:            17 failed, 105 passed in 1.06s
tests/test_reconcile_steps.py:       4 failed,   3 passed in 0.35s
tests/test_stop_path.py:             5 failed,   5 passed in 4.89s
tests/test_abandoned_runner_close.py: 25 failed in 3.21s
```

(rehearsed at drafting: `17 failed, 105 passed`, `25 failed`, `4 failed, 3 passed`, `5 failed, 5 passed` — the run supersedes it)

**Green line (full suite in worktree, Item 5, run here):**

```
2364 passed, 2 skipped, 9 warnings in 229.85s (0:03:49)
```

## The close observed (c-t1 to c-t4)

Source: `-m pytest -v` run of the four close test node ids in this worktree, Item 4, run here.

```
tests/test_abandoned_runner_close.py::test_preserved_branch_and_worktree_removed PASSED [ 25%]
tests/test_abandoned_runner_close.py::test_lane_and_lifecycle_state_after_close PASSED [ 50%]
tests/test_abandoned_runner_close.py::test_claim_released_and_page_sent PASSED [ 75%]
tests/test_abandoned_runner_close.py::test_live_process_refused_then_closed PASSED [100%]
```

4 passed in 28.94s

## Mutation run

Source: `git show 8f836ac:knowledge/mutants/abandoned-runner-close.run.txt | tail -1`, run here.

```
MUTATION: 30 killed, 0 survived, 0 error
```

## The halt, recorded

Source: `git log --format='%h %s' 06b545f..8f836ac` (the four commits, run here); transcript `logs/20260913-174007-step.json` for commit messages and absent `check_deposit` call (Items 1 and 2).

**Four commits where the halted plan (100097) asked for two:**

The halted plan's STEP 1 called for one DEV commit (nine source, test and manifest files, then the run file and dev-log in a second); its STEP 2 called for one QA commit. Instead, four commits were made, all in the DEV step, before the halted plan's STEP 2 ever ran:

1. `8b52344` — `dev(abandoned-runner-close): lifecycle migration, close function, idle-guard pid, notifier event, reconcile pass, four test files, mutation manifest [100097] [thread 306]`
2. `a4bb61d` — `dev(abandoned-runner-close): fix mutation manifest anchors and test discriminators [100097] [thread 306]`
3. `aa9a9ed` — `dev(abandoned-runner-close): fix c-t15 bool/int subclass assertion gap [100097] [thread 306]`
4. `8f836ac` — `dev(abandoned-runner-close): mutation run (30 killed, 0 survived, 0 error) and dev-log [100097] [thread 306]`

**Two fix commits' own messages:**

- `a4bb61d`: three manifest ERRORs (syntax gaps in `if False:` replacements, indentation mismatch in `verdict-slug-for-status-read` anchor, wrong discriminating test for `remove-snapshot-call`) and three test discriminator fixes (c-t12 `target_project` mismatch; c-t15 `bool` is a subclass of `int`; c-t25 dual-outcome `else`).
- `aa9a9ed`: c-t15 bool/int subclass assertion gap — `isinstance(False, int)` is `True` in Python; fix: `isinstance(result, int) and result is not False`.

**Absent `check_deposit` call:**

Confirmed by parsing `logs/20260913-174007-step.json` `raw_output` at Item 2: searching all 2,716 parsed events for assistant `tool_use` blocks with `tools/check_deposit` in the `command` field returns zero results. The four git commit commands are at events 1912, 2544, 2689 and 2709 — none preceded by a `check_deposit` call.
