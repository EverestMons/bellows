# Dev log — watcher-down-dedupe — 2026-09-14

## Pins re-derived (P1, P2, P3)

P2 (verbatim): `bellows.py` `_poll_liveness` :3482–3524: at most once per `liveness_poll_seconds` (default 300, :3490); each row stale or down → `notifier.notify_watcher_down(machine, status, age)` :3521–3522, each row live → `notifier.mark_machine_live(machine)` :3523–3524

P1 re-derived (`sed -n '24,29p;191,215p;264,293p;404,417p' notifier.py`):
- `_config` :24, `_dedupe_memo` :29
- `_dedupe(key)` :191–199, window :193
- `mark_machine_live(machine)` :202–212: pops keys where `k[:3] == (hostname, "-", "watcher_down")` AND `k[3].rsplit(":", 1)[0] == machine` (argument used — fix applied)
- `notify_event(event, plan_slug, title, message, priority=0, plan_scoped=True, detail_key="")` :264–293, key `(machine, plan_slug or "-", event, detail_key)` :274–275, log `notifier: {event} {plan_slug} paged` :292
- `notify_watcher_down(machine, status, age_seconds)` :404–417, passes `detail_key=f"{machine}:{status}"` :416 (fix applied)

Mechanism check: no mismatch. `mark_machine_live` now reads its argument and `notify_watcher_down` now carries the machine in the detail key. `_poll_liveness` at :3521–3524 passes each row's machine to both functions — unchanged. P2 confirmed at :3523–3524.

P3 re-derived:
- `tests/test_notifier_coverage.py`: test_8 `test_8_watcher_down_episodes` :343–385, route check now asserting `detail_key == "air:stale"` :385 (one plan-declared edit)
- New tests 8a–8e added after test_8, before the test_9 section comment; each patches `notifier.push` and counts calls
- test_10 `test_10_liveness_poll` from :494 — structure cloned for 8e with `_liveness_last_poll` reset to 0 before EACH poll
- `tests/conftest.py` `reset_notifier_state` :31–40 clears `_dedupe_memo` around every test

## Failing-first (red, then green)

Red (unedited notifier.py, tests written first):
`6 failed, 14 passed in 0.37s`

Green (file, after notifier.py fix):
`20 passed in 0.21s`

Green (full suite):
`2369 passed, 2 skipped, 9 warnings in 233.51s (0:03:51)`

## The pages counted (8a, 8c, 8d, 8e)

```
tests/test_notifier_coverage.py::test_8a_watcher_down_stale_plus_live_stale_first PASSED [ 25%]
tests/test_notifier_coverage.py::test_8c_watcher_down_two_machines_stale PASSED [ 50%]
tests/test_notifier_coverage.py::test_8d_watcher_down_mark_live_new_episode PASSED [ 75%]
tests/test_notifier_coverage.py::test_8e_liveness_poll_two_polls_one_page PASSED [100%]
```

8a asserts 1 page (stale row first, live row does not re-arm stale machine's key).
8c asserts 2 pages (two machines stale = two independent keys).
8d asserts 3 pages (both stale = 2; mark_machine_live("air") clears air only; both stale again = +1 for air, mini deduped).
8e asserts 1 page (_poll_liveness over [air stale, mini live] twice with clock reset each time — mark_machine_live("mini") does not clear air's key).

## Mutation run

`MUTATION: 3 killed, 0 survived, 0 error`
