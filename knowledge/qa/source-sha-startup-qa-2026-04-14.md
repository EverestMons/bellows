# QA Report — Source SHA Visibility at Startup
**Date:** 2026-04-14 | **Plan:** executable-source-sha-startup-2026-04-14.md | **QA Agent:** Step 2

## Pre-flight

- Step 1 commit verified: `4c524e5 feat: Bellows startup prints source SHA for staleness visibility`

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_source_sha` function defined in bellows.py | Present | ✅ | bellows.py:232 — `def _source_sha() -> str:` |
| Startup banner prints Source line | `Source: bellows.py @ {sha}` between title and Watching line | ✅ | bellows.py:362 — `print(f"  Source: bellows.py @ {_source_sha()}")` |
| `import subprocess` present | In imports block | ✅ | bellows.py:9 |
| `test_source_sha_returns_string` in test suite | Present and passing | ✅ | tests/test_bellows.py — passes (see pytest_targeted.txt) |
| All 12 tests pass | 12 passed, 0 failed | ✅ | pytest_targeted.txt — `12 passed` |
| Module imports clean | `import bellows` → `ok` | ✅ | smoke_import.txt |
| Live smoke returns valid SHA or "unknown" | `sha='4c524e5'`, sha contract OK | ✅ | smoke_sha.txt |

**Note on plan count:** Plan specified `_source_sha` must appear "at least 3 times (definition + 2 uses: import context, startup banner print)". Actual count is 2 (definition + 1 call in banner). "Import context" is not a separate token occurrence — the plan miscounted. Implementation matches the described intent exactly; marked ✅.

## Test Output Summary

```
12 passed, 1 warning in 0.10s
```

All prior tests from Plan 1 continue to pass. New test `test_source_sha_returns_string` passes.

## Smoke Output

```
sha='4c524e5'
sha contract OK
```

SHA matches the Step 1 commit hash. Format matches `^[0-9a-f]{7,12}$`.
