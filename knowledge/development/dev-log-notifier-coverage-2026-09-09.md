# Dev Log — Notifier Coverage — 2026-09-09

## What Changed

Rewrote `notifier.py` around a central `notify_event` gate that every push passes through: enabled check → `_event_enabled` (ruled `_DEFAULT_EVENTS` table, 7 true / 4 false) → `_dedupe` (in-process memo keyed by machine/plan/event/detail) → ownership check via `owned_by_live_session` (plan-scoped events only) → `push`. Added four new named notifiers: `notify_class_hold`, `notify_checkout_stale`, `notify_disk_low`, and `notify_watcher_down` (plus `mark_machine_live` to clear its dedupe between episodes). Re-pointed `notify_plan_halted`, `notify_failure`, and `notify_verdict_request` through `notify_event`. Added `_poll_liveness` to `Bellows.__init__` / `_rescan` and wired `notify_checkout_stale` at run_plan wire point A. Changed `gate_watcher._push_pause` to return a daemon-is-pager string rather than calling push. Updated `config.example.json` with the full 11-event table and the three new window keys.

## Why

The notifier was pushing independently from each call site with no shared gate: no deduplication between calls, no ownership check, no ruled defaults, and gate_watcher duplicating what the daemon now owns. The goal was a single point that could enforce all four invariants in one place so no new notifier can accidentally bypass them.

## What Was Hard

**Thread 243 hazard (test_11_gate_watcher):** importing `tools.gate_watcher` via `sys.path` resolved to the main checkout's old version, not the worktree's updated one. The old `_push_pause` still called `notifier.notify_verdict_request`, so the test saw 1 call instead of 0. Fix: load by explicit path via `importlib.util.spec_from_file_location`.

**Cross-test `_dedupe_memo` contamination (`test_log_hygiene.py`):** the module-level `_dedupe_memo` dict persisted across tests. An earlier test in `test_log_hygiene.py` wrote a `disk_low` dedupe entry; the `test_preflight_onset_flag_dedupes_notifier` test ran after it and saw its push blocked by stale state. Fix: added an autouse `_clear_notifier_dedupe` fixture to `tests/conftest.py` that clears the dict before and after every test.

**test_4_ownership_attended:** `notify_event` calls `owned_by_live_session(plan_slug)` without `receipts_dir`, so it resolved the bellows root receipts dir (empty in the worktree), not the test's tmp dir. Patched `notifier.owned_by_live_session` directly with `patch.object` for the `notify_event` integration sub-test; kept the unit test of the function itself using the `receipts_dir` parameter.

**`test_cycle_nudge.py` regressions:** the new `_DEFAULT_EVENTS` table defaults `cycle_nudge` to False. Tests created `Bellows(config)` with `events: {cycle_nudge: True}` but `Bellows.__init__` did not previously call `notifier.init_notifications(config)`. Fix: added that call to `__init__`.

## Decisions

- `notify_watcher_down` uses its own inline logic (3-tuple key, no detail_key, calls push directly) rather than going through `notify_event` — its dedupe key is a 3-tuple `(machine, "-", "watcher_down")` that `mark_machine_live` can pop without knowing a detail. Running it through the 4-tuple gate would require threading the machine name as plan_slug, which would pollute the gate's semantics.
- `notify_disk_low` passes `plan_slug=None` and `plan_scoped=False` — disk space is machine-wide, not plan-scoped, so no ownership check is appropriate.
- `init_notifications` now clears `_dedupe_memo` on re-init rather than only on module import. This means a Bellows restart flushes stale dedupe state, which is the right behaviour for a daemon that may restart mid-episode.
- `_receipt_slug` queries `lifecycle.db` for `deposit_placeholder_name` and strips the `.md` suffix so the ownership lookup matches the receipt filename pattern `receipt-<slug>-*.json`.

## Test Results

First commit (f5c82a4): 2160 passed, 1 skipped — all 15 new tests in `test_notifier_coverage.py` green.
Mutation run: 7 killed, 0 survived, 0 error (`knowledge/mutants/notifier-coverage.run.txt`).
