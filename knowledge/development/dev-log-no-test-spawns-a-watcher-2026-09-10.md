# Dev-log: no-test-spawns-a-watcher (plan 100070, thread 274)
**Date:** 2026-09-10 | **Branch:** bellows-wt/100070 | **HEAD (first commit):** b7e7bbe

---

## Pins re-derived (P1, P2, P3)

**P2 (verbatim value cell):** `tools/deposit_receipt.py:55–66` `_spawn_watcher(claimable_name)` → `subprocess.Popen([sys.executable, watcher, claimable_name], stdout=DEVNULL, stderr=DEVNULL, start_new_session=True)`, returns the pid or `None`; `:69` `def write_receipt(plan_path, session_id, spawn_watcher=True)`; `:118–119` `if spawn_watcher: pid = _spawn_watcher(slug + ".md")`; the CLI `:148–152` `--no-spawn` → `spawn_watcher=not args.no_spawn`; `tools/gate_watcher.py:153–154` `--timeout-min` default 120, `--interval-sec` 15

**P1 — the measured producer (re-derived):**
- `tests/test_depositor_receipts.py:627` `test_16_hold_prefix_receipt_satisfies_check` (class `TestHoldSlugFix`, `:626`) stages `diagnostic-holdfix`, evaluates it to a hold, then calls `dr.write_receipt(hold_path, "test-session-16")` at `:653` — no `spawn_watcher` argument, so default `True` fires.
- `test_11_gate_watcher` (in `tests/test_notifier_coverage.py`) loads `gate_watcher.py` by path and patches the pager — it spawns nothing. Attribution corrected by thread 274.
- Confirmed via `grep -n 'write_receipt(' tests/*.py`: only t16 calls `write_receipt` with the default (no `spawn_watcher` argument).

**P3 — conftest and test structure (re-derived):**
- `tests/conftest.py` before this plan: four autouse fixtures — `isolate_verdicts_dir` `:17`, `isolate_runner_logs_dir` `:24`, `isolate_lifecycle_db` `:30`, `_clear_notifier_dedupe` `:39`.
- `tests/test_depositor_receipts.py` before this plan: 23 tests across classes. `TestHoldSlugFix` class at `:626`, `test_16` at `:627`, `write_receipt` call at `:653`.
- No mechanism mismatch: `spawn_watcher` default is `True`, only t16 reaches it, four autouse fixtures confirmed.

---

## Failing-first (two red, then green)

Tests written before implementation. Run output:

```
FAILED tests/test_depositor_receipts.py::TestHoldSlugFix::test_16_hold_prefix_receipt_satisfies_check
FAILED tests/test_depositor_receipts.py::TestNoSpawn::test_24_default_spawn_reaches_the_stub
2 failed, 22 passed in 0.59s
```

t16 fails with:
```
tests/test_depositor_receipts.py:684: in test_16_hold_prefix_receipt_satisfies_check
    assert dr._SPAWN_CALLS == []
           ^^^^^^^^^^^^^^^
AttributeError: module 'tools.deposit_receipt' has no attribute '_SPAWN_CALLS'
```

t24 fails with:
```
    assert dr._spawn_watcher.__name__ == "_stub_spawn_watcher"
AssertionError: assert '_spawn_watcher' == '_stub_spawn_watcher'
```

After edits (autouse fixture in conftest + `spawn_watcher=False` in t16):

```
........................
24 passed in 0.53s
```

Full suite:

```
2225 passed, 1 skipped in 96.45s (0:01:36)
```

---

## The watcher census (Items 1, 3, 5)

**Item 1 — before test_16 run (pre-fix baseline):**
```
84171  07:50  bellows/tools/gate_watcher.py executable-bellows-lens-commit-desc-guard.md
84464  07:44  bellows/tools/gate_watcher.py executable-bellows-close-cycle-walks-and-fixed-point.md
89137  02:22  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
93514  01:08  bellows/tools/gate_watcher.py executable-bellows-no-test-spawns-a-watcher.md
96024  00:00  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
```

**Item 1 — after test_16 run (pre-fix; one new process):**
```
84171  07:57  bellows/tools/gate_watcher.py executable-bellows-lens-commit-desc-guard.md
84464  07:51  bellows/tools/gate_watcher.py executable-bellows-close-cycle-walks-and-fixed-point.md
89137  02:29  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
93514  01:15  bellows/tools/gate_watcher.py executable-bellows-no-test-spawns-a-watcher.md
96024  00:07  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
96166  00:03  bellows/tools/gate_watcher.py diagnostic-holdfix.md   ← NEW (pid 96166)
```

New process pid 96166: `bellows/tools/gate_watcher.py diagnostic-holdfix.md` — the producer confirmed.

**Item 3 — after full suite (post-fix; no new watcher from suite):**
```
453    02:34  bellows/tools/gate_watcher.py diagnostic-holdfix.md
485    02:26  bellows/tools/gate_watcher.py diagnostic-holdfix.md
5125   01:06  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
84171  11:54  bellows/tools/gate_watcher.py executable-bellows-lens-commit-desc-guard.md
84464  11:48  bellows/tools/gate_watcher.py executable-bellows-close-cycle-walks-and-fixed-point.md
89137  06:26  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
93514  05:12  bellows/tools/gate_watcher.py executable-bellows-no-test-spawns-a-watcher.md
96024  04:04  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
96166  04:00  bellows/tools/gate_watcher.py diagnostic-holdfix.md
```

PIDs 453, 485, 5125 are real deposits from the daemon (not from the suite — their etimes predate the suite run). The suite spawned no new watcher processes.

**Item 5 — after mutation run (autouse mutant; t24 __name__ fires before any spawn):**
```
453    05:47  bellows/tools/gate_watcher.py diagnostic-holdfix.md
485    05:39  bellows/tools/gate_watcher.py diagnostic-holdfix.md
5125   04:19  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
22116  00:33  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
84171  15:07  bellows/tools/gate_watcher.py executable-bellows-lens-commit-desc-guard.md
84464  15:01  bellows/tools/gate_watcher.py executable-bellows-close-cycle-walks-and-fixed-point.md
89137  09:39  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
93514  08:25  bellows/tools/gate_watcher.py executable-bellows-no-test-spawns-a-watcher.md
96024  07:17  .bellows-worktrees/100068/tools/gate_watcher.py diagnostic-holdfix.md
96166  07:13  bellows/tools/gate_watcher.py diagnostic-holdfix.md
```

PID 22116 is from `100068/tools/gate_watcher.py` — a real deposit from the daemon, not from the mutation run. The mutation run uses `git archive HEAD` sandboxes; t24's `__name__` assertion fires before `write_receipt` is called, so the autouse mutant spawns nothing.

---

## Mutation run

Manifest: `knowledge/mutants/no-test-spawns-a-watcher.json` (two mutants).

```
LIVE-TREE UNCHANGED: tests/conftest.py sha256=9ba2bc437140
LIVE-TREE UNCHANGED: tests/test_depositor_receipts.py sha256=9e8319268f68

MUTATION: 2 killed, 0 survived, 0 error
```

Both mutants killed:
- `drop-autouse-from-isolate-watcher-spawn`: t24's `__name__` assertion fails (`_spawn_watcher` ≠ `_stub_spawn_watcher`) — killed without any real spawn.
- `revert-t16-spawn-watcher-false`: stub intercepts the default call; `_SPAWN_CALLS == ["diagnostic-holdfix.md"]`; t16's `assert dr._SPAWN_CALLS == []` fails.
