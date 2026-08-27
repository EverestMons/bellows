# Dev Log — gate-watcher arm-time snapshot (2026-08-27)

## Diff summary

**`tools/gate_watcher.py`** — Added `judge_watch_line(prev, cur, arm_pending)` pure helper directly above `main`. The helper wraps `judge_transition` with arm-time snapshot logic: a pause whose pending set matches the one present at arming is reported as `armed over pre-existing` on the first poll and silenced thereafter; the snapshot clears when the pending set empties so later pauses report normally. Modified `main`'s loop to seed the snapshot from the first readable poll (`armed` flag) and thread `arm_pending` through `judge_watch_line`. The `--status` path, `read_state`, `judge_transition`, exit codes, and `_log_line` are untouched.

**`tests/test_gate_watcher.py`** — Added `TestArmTimeSnapshot` class with 8 pure-function tests against `judge_watch_line`: armed-over framing on first poll, silence on later polls, normal reporting after snapshot cleared, snapshot cleared when pending empties, different pending set is a new pause, transparent pass-through when `arm_pending` is None, db-unreadable preserves snapshot, and `--status` output unchanged for a paused plan.

## Pin re-derivation

| id | plan value | my derivation | status |
|---|---|---|---|
| A1 | `main` returns 0 only under `if cur.get("phase") in TERMINAL`; returns 3 after the `while` on timeout; no pause arm exists | Confirmed: `gate_watcher.py:175-177` (TERMINAL → return 0), `:180` (return 3); no pause exit arm | matches |
| A2 | `_spawn_watcher` at `deposit_receipt.py:55-63`, called at `:119` during receipt writing — at deposit, pre-claim | Confirmed: `deposit_receipt.py:55-63` defines `_spawn_watcher`; called from `write_receipt` at `:119` | matches |
| A3 | `prev = "UNSET"`; first poll calls `judge_transition(None, cur)` via the ternary | Confirmed: `gate_watcher.py:166` sets `prev = "UNSET"`; `:171` passes `None if prev == "UNSET"` | matches |
| A4 | `read_state` returns `pending` key only on non-terminal awaiting-verdict; absent on all other phases | Confirmed: `gate_watcher.py:76-82` adds `pending` only when `hits` non-empty and state not terminal | matches |
| A5 | 16 baseline tests | Confirmed: `pytest --collect-only` → 16 tests collected | matches |

## Targeted test run

```
........................                                                 [100%]
24 passed, 1 warning in 0.29s
```

16 baseline + 8 new = 24 passed, 0 failed.
