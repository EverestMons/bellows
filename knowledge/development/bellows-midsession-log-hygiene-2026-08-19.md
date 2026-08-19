# Dev Log: Mid-Session Log Hygiene Timer + 5 GB Disk-Floor Default [461]

**Date:** 2026-08-19
**Plan:** executable-461 (bellows — mid-session log hygiene + 5 GB disk floor default)
**Step:** 1 (DEV)

## Problem

`_rotate_logs()` and `_prune_old_logs(config)` are called only at startup. A daemon up for days never prunes, allowing logs to accumulate unchecked. Measured live 2026-08-19: 18h22m uptime with neither callee having fired since startup. Currently benign (logs/ = 2.5 MB) but a latent gap.

The disk-floor default of 2 GB was too low — one agent run's scratch can exceed 2 GB.

## Design Decisions

### Helper extraction (`_maybe_run_hygiene`)

The `while True` run loop in `start()` cannot be unit-tested directly. Extracted the periodic hygiene tick into a testable pure function `_maybe_run_hygiene(config, last_hygiene, now, interval)` that returns the updated timestamp. This mirrors the existing pattern of `_disk_preflight` as a testable helper called from the loop.

### Never-crash try/except (F4 fold — critical)

`_rotate_logs` has NO internal error guard — it uses bare `os.remove`/`os.rename` that can raise. The `while True` run loop body has no try/except around its body. A propagating exception from `_rotate_logs` (or `_prune_old_logs`, though it self-guards) would crash the daemon. The helper wraps both callees in a fail-safe try/except that logs WARN and advances the timestamp (so a persistent error doesn't retry every loop tick). Test `test_hygiene_swallows_callee_error` validates this contract.

### Gitignored config vs code default

The live `config.json` is gitignored and does NOT set `disk_min_free_gb`, so it runs on the code default. Raising the default from 2 to 5 in `_disk_preflight` (and documenting in `config.example.json`) is the clean, tracked, tested path — no gitignored-file edits needed.

### Timer initialization

`last_hygiene` is initialized to `time.time()` at loop entry, so the first mid-session tick fires 6h after startup — correct, since startup already runs both callees at lines 2632 and 2710.

## Changes

1. **bellows.py** — `_disk_preflight` default 2 → 5; added `_maybe_run_hygiene` function after `_disk_preflight`; wired `HYGIENE_INTERVAL` (6h) and `last_hygiene` into the `start()` run loop.
2. **config.example.json** — `disk_min_free_gb` 2 → 5.
3. **tests/test_log_hygiene.py** — updated `test_config_defaults_disk_min_free_gb` assertion from 2 to 5; added 4 new tests:
   - `test_hygiene_skips_before_interval` — no-op before interval, neither callee called
   - `test_hygiene_runs_after_interval` — both callees fire, timestamp advances
   - `test_hygiene_tick_prunes_old_log` — integration test proving wiring reaches real prune
   - `test_hygiene_swallows_callee_error` — validates never-crash contract (F4 fold)

## Verification

- `python3 -c "import ast; ast.parse(open('bellows.py').read())"` — exit 0, syntax valid.
- `python3 -m pytest tests/test_log_hygiene.py -q` — 15 passed (11 existing + 4 new).

## Output Receipt

- **Status:** Complete
- **DEV commit sha:** (see commit below)
