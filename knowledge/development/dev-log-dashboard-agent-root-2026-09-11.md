## Pins re-derived (P1, P4)

P2 (verbatim from the pin): `launchctl print gui/501/com.eluvian.bellows-daemon` on the mini: `path = /Users/marklehn/Library/LaunchAgents/com.eluvian.bellows-daemon.plist`, `program = /Users/marklehn/Developer/bellows/.venv/bin/python`, `arguments = { /Users/marklehn/Developer/bellows/.venv/bin/python, bellows.py }`, `working directory = /Users/marklehn/Developer/bellows`, `runs = 7`, `pid = 12770`; the template `scripts/com.eluvian.bellows-daemon.plist.template`: `ProgramArguments` `__BELLOWS_ROOT__/.venv/bin/python`, `bellows.py`; `WorkingDirectory` `__BELLOWS_ROOT__` (:17–23) — so the working directory IS the root, and the program is `<root>/.venv/bin/python`

P1 re-derived: `bellows.py:167 def _agent_loaded(label="com.eluvian.bellows-daemon")` (`launchctl print gui/<uid>/<label>`, `returncode == 0`); `:179 def _kickstart(label)` (before edit: `["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{label}"]`); `:196 def _perform_restart()` (`if _agent_loaded(label): _kickstart(label)` else detached `Popen`); `dashboard.py:425 _spawn_child` (before edit: `if bellows._agent_loaded(): bellows._kickstart("com.eluvian.bellows-daemon"); self.child = None` else `subprocess.Popen([sys.executable, "bellows.py"], cwd=str(self.bellows_root), …, start_new_session=True)`); callers `:484 _do_restart` and `:519 main loop`; `"agent_loaded": bellows._agent_loaded()` `:209`; `[agent]` suffix `:268`. No `_agent_root`, no `_agent_owns_root`, no `replace` parameter on `_kickstart`. No mechanism mismatch.

P4 re-derived: `tests/test_daemon_agent.py` (175 lines before edit); `import dashboard` before `import bellows` at :15–16; t3 `:60`, t5 `:85`, t6 `:97`, t7 `:108` with their `patch.object` shapes confirmed.

## Failing-first (red, then green)

Red (t8–t12 added, t5 updated with `create=True`, before production edits):

`5 failed, 7 passed in 2.74s`

— t8–t11 AttributeError: module 'bellows' has no attribute '_agent_root'; t12 TypeError: _kickstart() got an unexpected keyword argument 'replace'; t5 green (widening: `create=True` patch on `_agent_root` is ignored by the pre-edit `_spawn_child` which calls `_agent_loaded`, so t5 stays green before and after the production edit).

Green (after bellows.py and dashboard.py edits, all 12 tests):

`12 passed in 0.58s`

Full suite after edits: `2295 passed, 2 skipped in 110.05s`

## The branch closed (t10, t11)

t10 (`test_t10_spawn_child_foreign_root_spawns_a_child`): `_agent_root` patched to `str(tmp_path / "elsewhere")`; after `shell._spawn_child()`:
- `kickstart.assert_not_called()` — PASSED (foreign root → `_agent_owns_root` False → took Popen branch, never kickstarted)
- `popen.assert_called_once()` — PASSED (Popen called once, the old branch)
- `shell.child is popen.return_value` — PASSED

t11 (`test_t11_spawn_child_own_root_kickstarts_without_replace`): `_agent_root` patched to `str(tmp_path)` (same as `bellows_root`); after `shell._spawn_child()`:
- `kickstart.assert_called_once_with("com.eluvian.bellows-daemon", replace=False)` — PASSED (own root → kickstart with replace=False, no -k)
- `popen.assert_not_called()` — PASSED
- `shell.child is None` — PASSED

## Mutation run

`MUTATION: 5 killed, 0 survived, 0 error`
