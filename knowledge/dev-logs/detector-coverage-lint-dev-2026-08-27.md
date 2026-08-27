# Dev Log: detector-coverage-lint (exec-576)

**Date:** 2026-08-27

## Task B — Funnel re-measurement (raw)

```
321 28 25 12
  executable-516.md -> wrap_check.py
  executable-520.md -> wrap_check.py
  executable-535.md -> wrap_check.py
  executable-560.md -> wrap_check.py
  executable-561.md -> plan_lint.py
  executable-562.md -> wrap_check.py
  executable-563.md -> run_check.py
  executable-565.md -> plan_lint.py
  executable-569.md -> gate_watcher.py
  executable-571.md -> gate_watcher.py
  executable-573.md -> gate_watcher.py
  executable-575.md -> mutation_check.py
```

Four numbers vs E4: **321 / 28 / 25 / 12** — exact match, no supersedes.

## Pin re-derivation

| id | pin | re-derived | status |
|---|---|---|---|
| E1 | seam at plan_lint.py:508-547 | `(f-stanza)` at :508, stanza_fields parsed at :515-530, field loop at :539-544 | confirmed |
| E2 | _STANZA_REQUIRED at :538-541 | list at :532-535; target_class/state_space/mutants NOT present | confirmed |
| E3 | WARN idiom: (f) at :542 prints, (a) at :228 appends FAIL | (f) `print(...)` at :542, (a) `results.append(("FAIL",...))` at :228 | confirmed |
| E4 | funnel 321/28/25/12 | 321/28/25/12 | exact match |
| E5 | 1623 collected | `pytest tests/ -q --collect-only` → 1632 (includes 9 new tests); baseline 1632-9=1623 | confirmed |
| E6 | knowledge/mutants/ with gate_watcher.json | `ls knowledge/mutants/` → gate_watcher.json | confirmed |

## Task D — Targeted test run

Module: `tests/test_plan_lint_detector_checks.py`

Collect: 9 tests collected

```
.........                                                                [100%]
9 passed, 1 warning in 0.55s
```

All 9 tests pass. The 1 warning is urllib3/OpenSSL version advisory (not test-related).
