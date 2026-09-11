## Pins re-derived (P1, P2, P3)

`hooks/eluvian/wrap_check.py:373–377`: `# --- R2 registry: informational line (fail-open, never suppressing)` … `print("[R2/registry] wrap(s) recorded today per the shared registry:")` — part of the stdout the hook injects as `checklist`

P1 re-derived (`sed -n 55,89p hooks/eluvian/wrap_debt_hook.py`): `main()` runs `[sys.executable, CHECK, check_sid, "debt"]` (`:63–66`), exits clean on returncode 0 (`:70–72`), else `emit(` the header `"⚠️ UNWRAPPED SESSION DEBT DETECTED. A prior session ended without completing the wrap ritual. Resolve this BEFORE starting new work:\n\n"` + `checklist` + `"This is not a fresh-session state. Treat it as a wrap in progress: …"` (`:74–82`); the `__main__` guard prints `{}` on any exception (`:85–89`). No `_compose_debt_message` present — no mechanism mismatch.

P3 re-derived: `tests/test_wrap_hooks.py` — `_run_hook(name, payload, env_overrides)` runs a hook as a subprocess under `ELUVIAN_WRAP_ROOT` = `tmp_path` (`:100–130`, the stop hook's block/exempt tests); `tests/test_hook_default_root.py` loads a hook module by `importlib.util.spec_from_file_location` for pure-function tests; `tests/test_align_hook_sync.py` (#100066) tests `_compose_context` that way.

## Failing-first (red, then green)

Red: `2 failed in 0.23s` — `AttributeError: module '_test_wrap_debt_hook' has no attribute '_compose_debt_message'`

Green: `2264 passed, 1 skipped in 102.16s`

## Mutation run

MUTATION: 2 killed, 0 survived, 0 error
