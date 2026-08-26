# Dev log — diff-stat-rename-normalize — 2026-08-26

## Plan id: 567

## What changed

`_parse_diff_stat` in `bellows.py` now normalizes git's rename rendering
(`{old => new}/f` brace form and `old => new` bare form) to the NEW path
before appending to `files_changed`. Previously, the verbatim arrow literal
passed through, making it unmatchable by scope_check or any downstream
consumer expecting real paths.

## Probes (pre)

| probe | expected | actual |
|---|---|---|
| `grep -cF "rename rendering" bellows.py` | 0 | 0 |
| `test -f tests/test_diff_stat_renames.py` | 0 | 0 |
| Decision matrix | (0,0) → full run | full run |

## Probes (post)

| probe | expected | actual |
|---|---|---|
| `grep -cF "rename rendering" bellows.py` | 1 | 1 |
| `grep -c '{[^{}]* => ' bellows.py` | 1 | 1 |

## Targeted test run

```
5 passed, 0 failed (tests/test_diff_stat_renames.py)
```

Tests: 3 parser-level (monkeypatched subprocess with real captured fixtures)
+ 2 end-to-end real-git (tmp repo, actual git mv, no mocks).
