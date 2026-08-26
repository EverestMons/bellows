# Depositor Cluster — Dev Log — 2026-08-26

## Task B — tools/gate_watcher.py post-probes

```
$ /usr/bin/grep -cF "mode=ro" tools/gate_watcher.py
1

$ /usr/bin/grep -cF "overridden = 0" tools/gate_watcher.py
1

$ chmod +x tools/gate_watcher.py
(done)
```

## Task C — tools/deposit_receipt.py post-probes

```
$ /usr/bin/grep -cF "_spawn_watcher" tools/deposit_receipt.py
2
(def + call — plan predicted 3, actual is 2; the parenthetical "def + call + nothing else" describes exactly two hits)

$ /usr/bin/grep -cF "no-spawn" tools/deposit_receipt.py
1

$ python3 -m pytest tests/test_deposit_receipt.py -q
11 passed, 1 warning in 0.14s
```

## Task D — tests/test_gate_watcher.py targeted run

```
$ python3 -m pytest tests/test_gate_watcher.py -q
9 passed, 1 warning in 0.14s
```

## Task E — Four verification probes

### E1: Checker re-runs at deposit (D1)

`_rerun_validation` call at depositor.py:159:
```
155:        if collision:
156:            self._hold(path, collision["reason"], collision)
157:            return
158:
159:        rerun = self._rerun_validation(path, plan_text)
160:        if rerun["hold"]:
161:            self._hold(path, rerun["reason"], rerun)
162:            return
163:
164:        if not self._check_receipt(path):
```

Hold arms (depositor.py:471-527):
- cycle_check != BAR_MET: lines 478-481
- cycle_check exception: lines 482-485
- plan_lint non-benign FAILs: lines 494-507
- plan_lint exception: lines 508-511
- manifest validation mismatch (cycle_check=expected vs got): lines 513-524

### E2: Duplicate-check (D2)

```
$ python3 tools/deposit_receipt.py /tmp/dup_probe_569.md probe-569 --no-spawn
Receipt written: .../receipts/receipt-dup_probe_569-probe-569-1a0cb94c9f80.json — watcher armed (not a liveness claim)
$ echo $?
0

$ python3 tools/deposit_receipt.py /tmp/dup_probe_569.md probe-569 --no-spawn
ERROR: receipt already exists for slug=dup_probe_569 hash=1a0cb94c9f80 — duplicate deposit
$ echo $?
1

$ rm receipts/receipt-dup_probe_569-*.json
$ ls receipts/ | /usr/bin/grep -cF dup_probe_569; true
0
```

### E3: Minting single-writer (D3)

```
$ /usr/bin/grep -rnF "id_sequence" *.py tools/ scripts/ tests/

lifecycle.py:4:   - comment (module docstring)
lifecycle.py:30:  - CREATE TABLE IF NOT EXISTS id_sequence (schema definition)
lifecycle.py:36:  - INSERT OR IGNORE INTO id_sequence (one-time seed, not a minting path)
lifecycle.py:255: - UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1
                    ^^^ THE SOLE WRITER — the only minting path

tests/test_lifecycle.py:329,331,341,346,349,353,379,387,388,685,689 — test setup/assertions (read or seed)
tests/test_wrap_receipts.py:23,27 — test schema setup
tests/test_dashboard.py:86 — test seed UPDATE
tests/test_consume_verdicts.py:1411,1705,1791,1820 — test seed INSERT/UPDATE
tests/test_status.py:83,84 — test seed UPDATE
tests/test_wrap_3b_keyed.py:18 — test schema setup
tests/test_plan_lint.py:2004 — embedded in plan text (documentation string)
```

Classification: ONE writer (lifecycle.py:255). All others are schema creation, one-time seed, test setup, or embedded text.

### E4: Shared-append mediation (D4)

bellows.py:1681-1722 confirmed:
- :1681-1682 — old-style agent write detection (skips if agent wrote directly)
- :1686-1690 — idempotency check via `check_ledger_write_exists`
- :1692-1698 — central `record_prompt_feedback` DB write
- :1700-1715 — `generate_feedback_md` + git add + git commit
- :1722 — `record_ledger_write` idempotency marker

```
$ python3 -m pytest tests/test_lifecycle.py -k "Idempotency or ledger" -q
7 passed, 88 deselected, 1 warning in 0.19s
```
