# Dev Log — Notifier Coverage — 2026-09-09

## Pins re-derived (P1, P2, P3, P4, P6)

Source: greps run by this plan (100055) at Item 1; 100054's transcript did not contain explicit pin grep outputs (the DEV used Read-tool inspection, not grep commands with printed line numbers — confirmed by searching `raw_output` of `logs/20260909-161445-step.json` for `379:def notify_watcher_down` and `255:def notify_event`: no matches in tool_result context).

**P1 re-derived (this plan):**

```
$ git log 615d2cc..main --oneline
6b4bfb5 chore(dev-log): mutation runs + dev-log for notifier-coverage [100054]
f5c82a4 feat(notifier): ruled event table, ownership signal, dedupe, central gate, new notifiers [100054]

$ grep -n "def notify_watcher_down" notifier.py
379:def notify_watcher_down(machine: str, status: str, age_seconds: float) -> bool:

$ grep -n "^def notify_event" notifier.py
255:def notify_event(event: str, plan_slug, title: str, message: str,

$ grep -n "def mark_machine_live" notifier.py
201:def mark_machine_live(machine: str) -> None:
```

MATCH: notify_watcher_down at :379, notify_event at :255, mark_machine_live present. No mechanism mismatch — notify_watcher_down calling push directly is the known state this plan fixes.

**P2 re-derived (this plan):**

```
$ grep -n "## " knowledge/development/dev-log-notifier-coverage-2026-09-09.md
(prior to this rewrite: ## What Changed, ## Why, ## What Was Hard, ## Decisions, ## Test Results)

$ grep -n "Headings\|Verbatim" /Users/marklehn/Developer/bellows/knowledge/decisions/halted-executable-100054.md
138:> **Headings:** `## Pins re-derived (P1, P2, P3, P4, P6)`; ...
139:> **Verbatim:** `## Coverage table` ← P1
```

MATCH: halted record had wrong headings; halted plan carries Headings/Verbatim at :138-139.

**P3 re-derived (this plan — measured from raw_output):**

```
$ python3 -c "import json; d=json.load(open('logs/20260909-161445-step.json')); r=d['raw_output']; print(len(r))"
4134784

Marker counts:
  P1:                         77
  Pins re-derived:             2
  FAILED tests/test_notifier_coverage:  6
  passed:                    370
  MUTATION::                  20
  wall:                        4
```

(Plan's walk-0 stated ×78/×2/×6/×377/×20/×4 — method differs slightly; all four markers confirm transcript size and content.)

**P4 re-derived (this plan):**

```
$ grep -n "_clear_notifier_dedupe\|_dedupe_memo" tests/conftest.py
40:def _clear_notifier_dedupe():
42:    notifier._dedupe_memo.clear()
44:    notifier._dedupe_memo.clear()
```

MATCH: autouse fixture at :39-44, clears before and after every test.

**P6 re-derived (this plan):**

```
halted-executable-100054.md present at /Users/marklehn/Developer/bellows/knowledge/decisions/
daemon pid 69409 running bellows.py@492f50d (pre-100054 notifier — restart deferred to this close)
```

## Failing-first (the sibling red, then green)

Source: `logs/20260909-161445-step.json` `raw_output`, tool_result blocks at timestamps 2026-09-09T21:30:34 (red) and 2026-09-09T21:33:33 (green).

**Red run (sibling, before test_4 and test_11 fixes):**

```
....F........F.                                                          [100%]
=================================== FAILURES ===================================
__________________________ test_4_ownership_attended ___________________________
tests/test_notifier_coverage.py:185: in test_4_ownership_attended
    assert result is False
E   assert True is False
----------------------------- Captured stdout call -----------------------------
16:30:34 [INFO] notifier: verdict_needed executable-foo-2026-09-09 paged
_____________________________ test_11_gate_watcher _____________________________
tests/test_notifier_coverage.py:638: in test_11_gate_watcher
    assert len(notify_calls) == 0, "notify_verdict_request should not be called by gate watcher"
E   AssertionError: notify_verdict_request should not be called by gate watcher
E   assert 1 == 0
E    +  where 1 = len([1])
=========================== short test summary info ============================
FAILED tests/test_notifier_coverage.py::test_4_ownership_attended - assert Tr...
FAILED tests/test_notifier_coverage.py::test_11_gate_watcher - AssertionError...
2 failed, 13 passed in 0.43s
```

**Green run (sibling, after both fixes committed at f5c82a4):**

```
...............                                                          [100%]
15 passed in 0.19s
```

## Mutation run

Source: `logs/20260909-161445-step.json` `raw_output`, tool_result block at timestamp 2026-09-09T21:46:20 (100054's run, HEAD=f5c82a4).

```
PYTHON: /Users/marklehn/Developer/bellows/.venv/bin/python
HEAD: f5c82a4ab1c914d1b907d09cafedf73e613840eb
TARGET: notifier.py sha256=b76467d3507f

MUTANT notify-event-drops-disabled-check: KILLED — suite caught the defect
MUTANT event-default-unknown-true: KILLED — suite caught the defect
MUTANT invert-dedupe-gate: KILLED — suite caught the defect
MUTANT drop-ownership-guard: KILLED — suite caught the defect
MUTANT ignore-plan-scoped-flag: KILLED — suite caught the defect
MUTANT watcher-key-4tuple: KILLED — suite caught the defect
MUTANT mark-live-pops-wrong-key: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: notifier.py sha256=b76467d3507f

MUTATION: 7 killed, 0 survived, 0 error
```

Note: This plan (100055) re-ran mutation check at HEAD=cfb968e (routing change; anchors watcher-key-4tuple and mark-live-pops-wrong-key re-targeted to mark_machine_live). Result: 7 killed, 0 survived, 0 error. Full output in `knowledge/mutants/notifier-coverage.run.txt`.

## Coverage table

← P1: bellows `f5c82a4` (notifier +205/−35, bellows +82/−11, depositor +11, gate_watcher +4/−37, config.example +13/−5, conftest +8, sibling +676) and `6b4bfb5` (manifest +54, run +15, dev-log +31); main = origin/main; `notify_watcher_down` at `notifier.py:379`, `notify_event` at `:255`, `mark_machine_live` present; the run file `MUTATION: 7 killed, 0 survived, 0 error`, `HEAD:` = `f5c82a4`'s full sha

| event | default | site |
|---|---|---|
| `verdict_needed` | True | `bellows.py` → `notify_verdict_request` → `notify_event` |
| `plan_halted` | True | `bellows.py` → `notify_plan_halted` → `notify_event` |
| `failure` | True | `bellows.py` → `notify_failure` → `notify_event` |
| `disk_low` | True | `bellows.py` → `notify_disk_low` → `notify_event` |
| `class_hold` | True | `depositor.py` → `notify_class_hold` → `notify_event` |
| `checkout_stale` | True | `bellows.py` → `notify_checkout_stale` → `notify_event` |
| `watcher_down` | True | `bellows.py:_poll_liveness` → `notify_watcher_down` → `notify_event` |
| `plan_complete` | False | `bellows.py` → `notify_plan_complete` → `_enqueue_deferred` (buffered) |
| `plan_skipped` | False | `bellows.py` → `notify_plan_skipped` → `_enqueue_deferred` (buffered) |
| `queue_empty` | False | `bellows.py` → `notify_queue_empty` → `_enqueue_deferred` (buffered) |
| `cycle_nudge` | False | `bellows.py` → `notify_cycle_nudge` → `_enqueue_deferred` (buffered) |

Source: `grep -n "_DEFAULT_EVENTS" notifier.py` and `grep -n "def notify_" notifier.py` on `f5c82a4`; sites confirmed from `grep -n "notify_" bellows.py depositor.py`.

100054's own P1 (from `halted-executable-100054.md:32`):

> `notifier.py` 235 lines at bellows `615d2cc`: `init_notifications` `:29-34` (module globals `_config`, `_app_key`, `_user_key`), `_event_enabled` `:41-46` (`events.get(name, True)`), `_coalesce_window` `:48`, `push` `:55-81` (`requests.post`, timeout (5, 10), returns `status_code == 200`), the digest `:83-171` (arms `plan_complete`/`plan_halted`/`plan_skipped`/`queue_empty`/`cycle_nudge`), `notify_plan_complete` `:173`, `notify_plan_halted` `:180`, `notify_plan_skipped` `:187`, `notify_queue_empty` `:194`, `notify_failure` `:201`, `notify_cycle_nudge` `:214`, `notify_verdict_request` `:221-235` (priority 1)

## Cost

No timings were printed in the 100054 transcript (`wall` ×4 occurrences are all plan text, not measured output). Measured fresh in this step:

**`notify_event` (plan_scoped=True, real ownership check — two globs + one stat on tmp receipt + transcript):**

```
run 1: 0.99 ms  (cold — module overhead)
run 2: 0.17 ms
run 3: 0.15 ms
median: 0.17 ms
```

Command: `python3 -c "import time, notifier, statistics; ..."` (ownership check via real glob; `push` patched; dedupe cleared between runs).

**`_poll_liveness` bellows overhead (subprocess mocked — JSON parse + notify dispatch):**

```
run 1: 0.12 ms
run 2: 0.03 ms
run 3: 0.03 ms
median: 0.03 ms
```

Liveness poll subprocess wall time (real `tuyere machines liveness` call) not measured here — depends on tuyere availability and is the dominant term; overhead path only. Measured 2026-09-09 on this plan's DEV step.
