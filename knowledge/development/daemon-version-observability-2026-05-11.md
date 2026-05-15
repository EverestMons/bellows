# Output Receipt — Daemon Version Observability

## Files Created or Modified (Code)
- `bellows.py` — added `_module_fingerprints()` helper, `MODULE_FINGERPRINT_HEARTBEAT_INTERVAL` constant, startup module log block, heartbeat periodic surfacing

## Files Created or Modified (Tests)
- `tests/test_bellows.py` — added 3 regression tests for `_module_fingerprints()`

## Files Created (Knowledge)
- `bellows/knowledge/development/daemon-version-observability-2026-05-11.md` (this file)

## Commits
1. `6411054` — `fix(bellows): module fingerprint observability — startup log + heartbeat surfacing`
2. `fd0efd7` — `test(bellows): regression tests for module fingerprint helper`
3. `0199aaa` — `docs: dev log for daemon version observability`

## Test Results
- **Before:** 101 passed (test_bellows.py subset of 261-pass full suite baseline)
- **After:** 104 passed, 0 failed
- **New tests:**
  - `test_module_fingerprints_returns_all_five_modules`
  - `test_module_fingerprints_handles_git_failure`
  - `test_module_fingerprints_fallback_to_unknown_on_unexpected_error`

## Constraints Verified
- No existing log line modified
- Heartbeat cadence unchanged (60s)
- Fingerprint helper never raises (try/except with "unknown" fallback per module)
- `MODULE_FINGERPRINT_HEARTBEAT_INTERVAL` is a module-level constant, not in config.json
- `subprocess.run` called with `timeout=5`, `capture_output=True`, no `shell=True`

## Status: Complete
