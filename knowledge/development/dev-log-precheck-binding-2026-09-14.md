## Pins re-derived (P1, P2, P3, P4)

P2: `runner.run_step` :190 — its last parameters `step_num: Optional[int] = None,` :198 and `_retry_attempted: bool = False,` :199; the agent's process `subprocess.Popen(cmd, …, cwd=project_path, env={**os.environ, "BELLOWS_DISPATCH": "1"})` :218–225, the environment line :224 (#496, `384fffa`); the one retry `return run_step(prompt, project_path, model, session_id, allowed_tools, timeout, plan_slug, step_num, _retry_attempted=True)` :343 — the environment the agent's shell inherits

P1: `tools/check_deposit.py`, 295 lines, docstring :2–17 with "Read-only: opens no files for writing. Exit 1 on any gate failure, 0 on clean." at :7; `import argparse` :18, `import ast` :19; `GATES` :28–34; `main` :182, argparse block :183–195; worktree :197–205; `project_path = wt_path` :207; summary print :289; `return 1 if failures else 0` :291. Re-derived: `sed -n '1,34p;182,207p;286,291p' tools/check_deposit.py`.

P3: `bellows.py`: `BELLOWS_ROOT = Path(__file__).parent.resolve()` :29; `run_plan` :1540; `plan_text` :1548 and :1647; `inprogress_path` :1562; two agent dispatches at :1793–1797 and :1951–1958; `_create_worktree` :2266 (a project with no `.git` of its own runs in place, :2276–2279); `_auto_stage_deposits` :2321, daemon commit :2379–2383; `_teardown_worktree` :2759.

P4: git 2.55.0 on the mini; `core.hooksPath` unset in bellows, tuyere, forge_lessons, anvil; governance root sets `core.hooksPath=.githooks` with one `pre-commit` hook (walk-register lint, thread 44, `ab8b33e4`). Re-derived: `git --version`; `git config --get core.hooksPath`; `find .git/hooks -type f ! -name '*.sample'`.

## Failing-first (red, then green)

Red (base, unedited code): `23 failed, 2 passed`

Green (file): `25 passed`

Green (neighbour files — `tests/test_precheck_binding.py tests/test_check_deposit.py tests/test_runner.py tests/test_runner_parser.py tests/test_wrap_hooks.py tests/test_bellows.py`): `301 passed`

Green (full suite): `2431 passed, 2 skipped`

## The binding observed (b3, b4, b5, b9, b13)

tests/test_precheck_binding.py::TestB3CommitRefusedNoRecord::test_b3 PASSED [ 20%]
tests/test_precheck_binding.py::TestB4CommitAfterCleanPrecheck::test_b4 PASSED [ 40%]
tests/test_precheck_binding.py::TestB5EditedPathRefused::test_b5 PASSED  [ 60%]
tests/test_precheck_binding.py::TestB9RepoOwnHookRuns::test_b9 PASSED    [ 80%]
tests/test_precheck_binding.py::TestB13PreCheckEnvReturnsRightKeys::test_b13 PASSED [100%]

## Mutation run

MUTATION: 30 killed, 0 survived, 0 error
