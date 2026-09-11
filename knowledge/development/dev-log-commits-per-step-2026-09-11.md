# Dev log — commits-per-step — 2026-09-11

## Pins re-derived (P1, P3, P4)

**P2 (live DB, mode=ro):** `commits` 172 rows; plans with rows by `total_steps`: 1 → 17, 2 → 58, 3 → 2; rows by `steps.step_number`: 1 → 76, 2 → 92, 3 → 4; #100063's three rows (`de7dd4f`, `8b25282`, `f0760af`) all under its step 2 (the thread's measurement); `steps` columns: `id, plan_id, step_number, role, status, step_started_at, step_ended_at, cost_usd, turns, duration_s, log_ref` — NO sha column, so no historical range is recoverable from the DB

**P1 re-derived (bellows.py):**

| pin | value (post-edit) |
|-----|-------------------|
| `plan_baseline_sha = _capture_git_diff(wt_path)` | :1199 |
| `pre_diff = plan_baseline_sha` | :1200 |
| `_lc_step_id = lifecycle.record_step_start(plan_id, current_step)` | :1204 |
| `post_diff = _capture_git_diff(wt_path)` (first region) | :1254 |
| `lifecycle.record_gate_events(_lc_step_id, gate_result)` (first region) | :1270 |
| NEW: `lifecycle.record_commits(_lc_step_id, …, _step_commit_shas(…, pre_diff, post_diff))` | :1271 |
| merge site :1322–1323 | unchanged |
| `pre_diff = _capture_git_diff(wt_path)` (while-loop) | :1359 |
| `_lc_step_id = lifecycle.record_step_start(plan_id, current_step + 1)` | :1362 |
| `post_diff = _capture_git_diff(wt_path)` (while-loop) | :1414 |
| `lifecycle.record_gate_events(_lc_step_id, gate_result)` (while-loop) | :1430 |
| NEW: `lifecycle.record_commits(_lc_step_id, …, _step_commit_shas(…, pre_diff, post_diff))` | :1431 |
| merge sites :1459–1460, :1498–1499, :3357 | unchanged |

No `_step_commit_shas` or `SELECT` inside `record_commits` found on main — no mechanism mismatch.

**P3 re-derived (lifecycle.py):**

- Schema: lines 100–106 (unchanged)
- `def record_commits(step_id, repo, shas, db_path=None)` at :663 (drift from plan's :639, not a mismatch)
- Before edit: returns `None`, no dedupe; after edit: returns `int`, plan-scoped SELECT dedupe

**P4 re-derived:**

- `tests/test_bellows.py:774` `test_run_plan_resume_step_uses_correct_prompt` (clone basis)
- `tests/test_teardown_recording.py:44/55` `_clean_gates` / `_setup_plan`
- `tests/test_worktree.py:29` `git_repo` fixture (initial commit on `main`)
- `tests/test_lifecycle.py:562/563` `TestRecordCommits` / `test_records_multiple_shas`
- `conftest.isolate_lifecycle_db` :31 (autouse, redirects `LIFECYCLE_DB_PATH` to `tmp_path`)

## Failing-first (three red, then green)

**Red — test_lifecycle.py::TestRecordCommits (t1–t3):**
```
FAILED tests/test_lifecycle.py::TestRecordCommits::test_dedupes_within_a_plan
FAILED tests/test_lifecycle.py::TestRecordCommits::test_repeat_in_one_call_inserted_once
2 failed, 3 passed in 1.76s
```
(t2 `test_no_dedupe_across_plans` passes correctly with old code — the old code always inserts, so two plans recording the same sha yields 2 rows, which is the assertion.)

**Red — test_worktree.py (t4–t6):**
```
FAILED tests/test_worktree.py::test_step_commit_shas_range_in_order - AttributeError: module 'bellows' has no attribute '_step_commit_shas'
FAILED tests/test_worktree.py::test_step_commit_shas_equal_shas_empty - AttributeError: module 'bellows' has no attribute '_step_commit_shas'
FAILED tests/test_worktree.py::test_step_commit_shas_empty_sha_empty - AttributeError: module 'bellows' has no attribute '_step_commit_shas'
3 failed in 0.52s
```

**Red — test_bellows.py (t7–t8, _step_commit_shas patch restored):**
```
FAILED tests/test_bellows.py::test_two_step_run_records_each_step_under_its_own_row
FAILED tests/test_bellows.py::test_resumed_step_records_only_its_own_commits
2 failed in 0.44s
```

**Green (all eight tests + full suite):**
```
2290 passed, 2 skipped in 109.44s (0:01:49)
```
(Two skips: `test_gate_watcher` live-DB skip + `test_fallback_live_wal_window` from #100083.)

## The rows observed (t7, t8)

**Before the fix** (tests run with `_step_commit_shas` patch removed, old `_teardown_worktree` mock returns `["s1a","s1b","s2"]`):

- t7: `step1_shas = set()` (no rows under step 1), all three shas under step 2 via the merge site
- t8: `step2_shas = {'s1a', 's1b', 's2'}` (merge site put all three under step 2)

**After the fix** (full patch restored, both call sites active):

- t7: `step1_shas = {'s1a', 's1b'}`, `step2_shas = {'s2'}`, total = 3, `_step_commit_shas.call_count == 2`
- t8: `step2_shas = {'s2'}`, `step1_shas = {'s1a', 's1b'}`, total = 3

## Mutation run

```
MUTATION: 5 killed, 0 survived, 0 error
```
