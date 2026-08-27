# Dev Log — mutation-runner-fix (exec-575) — 2026-08-27

## Task B — Before-state (raw)

```
FAILED tests/test_mutation_check.py::test_killed_when_mutant_breaks_the_test
1 failed, 7 passed, 1 warning in 3.61s
```

`test_killed_when_mutant_breaks_the_test` fails deterministically — the same-byte-length
mutant (`return a + b` → `return a - b`) survives because the stale `.pyc` is still valid.

## Pin re-derivations

| id | plan value | my value | note |
|---|---|---|---|
| D1 | 1 failed, 7 passed; `test_killed_when_mutant_breaks_the_test` | 1 failed, 7 passed; `test_killed_when_mutant_breaks_the_test` | matches |
| D2 | `pycache_prefix = /Users/marklehn/Library/Caches/com.apple.python`; `dont_write_bytecode = False` | same | matches |
| D3 | redirected `.pyc` at `~/Library/Caches/com.apple.python/...` | not re-probed (D2 confirms the mechanism) | — |
| D5 | `_run_pytest(` appears 3 times; no `env=` argument | 3 occurrences; `env=` NOW present after fix | supersedes (fixed) |
| D6 | 1620 collected, 1 failing; after fix: 1623, 0 failed | 1623 collected, 0 failed | matches expected after-state |

## Task C — the fix

`tools/mutation_check.py:42-61` — `_run_pytest` now builds `env = dict(os.environ)`,
sets `env["PYTHONDONTWRITEBYTECODE"] = "1"`, and passes `env=env` to `subprocess.run`.
Both the baseline and mutant pytest calls go through this single helper (confirmed: 3 occurrences
of `_run_pytest(` — 1 def, 2 call sites).

Docstring added explaining WHY: bytecode invalidation by `(mtime, size)` means a same-byte-length
mutation written within the same mtime second leaves the cached `.pyc` valid; and the cache location
is environment-dependent (`sys.pycache_prefix`), so clearing `__pycache__` is not portable.

## Task D — new tests (3)

1. `test_same_byte_length_mutation_is_killed` — regression test with `assert len(anchor) == len(replacement)` precondition.
2. `test_bytecode_isolation_env_is_set` — structural guard: reads source, asserts `PYTHONDONTWRITEBYTECODE` present and `env=` passed in `_run_pytest`.
3. `test_consecutive_same_length_mutants_are_both_killed` — two independent equal-length mutations on one target (`+ → -`, `* → /`), both must score KILLED.

Collection: `11 tests collected` (8 existing + 3 new).

## After-state (raw)

```
...........                                                              [100%]
11 passed, 1 warning in 4.56s
```

`test_killed_when_mutant_breaks_the_test`: FAILED (before) → PASSED (after).

## Preserved-property probes

| property | file:line | probe | result |
|---|---|---|---|
| exit-1-only KILLED | `mutation_check.py:201` | `grep -nF "exit_code == 1"` | present |
| green-baseline control | `mutation_check.py:176-183` | `grep -nF "baseline_exit"` | present (5 lines) |
| anchor-count==1 | `mutation_check.py:170` | `grep -nF "count != 1"` | present |
| replacement-present-after-write | `mutation_check.py:194` | `grep -nF "replacement not in written"` | present |
| live-tree sha256 in finally | `mutation_check.py:216-221` | `grep -nF "live_sha_after"` | present (4 lines) |
