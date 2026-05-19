# Config Secrets/Operational Split — Dev Log

**Plan:** executable-bellows-config-split-2026-05-23
**Step:** 2 (DEV)
**Date:** 2026-05-23
**Author:** Bellows Developer

---

## Pre-Edit Verification Results (Rule 39)

All 8 SA verification queries re-run. All claims confirmed:

| Claim | Query | Result | Pass/Fail |
|---|---|---|---|
| 1: config.json has 9 top-level keys | `python3 -c "import json; ..."` | Keys: `['callback_port', 'default_model', 'notifications', 'planner_model', 'pushover', 'step_inactivity_timeout_seconds', 'step_timeout_seconds', 'tailscale_ip', 'watched_projects']`, Count: 9 | **Pass** |
| 2: Parent .gitignore line 18 = `bellows/config.json` | `grep -n 'config.json' ../.gitignore` | `18:bellows/config.json` | **Pass** |
| 3: Bellows .gitignore line 9 = `config.json` | `grep -n 'config.json' .gitignore` | `9:config.json` | **Pass** |
| 4: bellows.py has 3 `config[` bracket-access sites | `grep -n 'config\[' bellows.py` | Lines 360, 396, 979 | **Pass** |
| 5: test_bellows.py has 1 `test_load_config`, 106 total tests | `grep -c 'def test_' ...` | 106 tests, `test_load_config` at line 17 | **Pass** |
| 6: load_config is 4 lines at line 123 | `sed -n '123,126p' bellows.py` | Matches SA record | **Pass** |
| 7: `notifier.init_notifications(config)` at line 1382 | `grep -n 'init_notifications' ...` | bellows.py:1382, notifier.py:29 | **Pass** |
| 8: All pushover access uses `.get()` with empty-string fallback | `grep -n 'pushover' bellows.py` | Lines 310-311, 1015-1016, 1079-1080, 1094-1095 | **Pass** |

---

## Diff Summary

### 1. Loader change — `bellows.py`

`load_config()` expanded from 4 lines to ~20 lines (lines 123-145):
- Added inline comment block documenting the two-file layout
- Reads `config.json` into `config` dict (no longer returns immediately)
- Resolves `config.secrets.json` relative to config file's parent directory (`config_path.parent`)
- If secrets file exists: deep-merges (one level) secrets into config via `dict.update` for nested dicts, direct assignment for scalars
- If secrets file missing: logs `WARN` via `_log()`, returns operational config only
- SA note implemented: secrets path resolves relative to config file's directory (not hardcoded to BELLOWS_ROOT), so tests using temp dirs find secrets files correctly

### 2. Migration script — `scripts/migrate_config.py` (new)

- Location per SA spec: `bellows/scripts/migrate_config.py`
- Reads `config.json`, classifies keys per SA Key Classification Table (`SECRET_KEYS = {"pushover", "tailscale_ip"}`)
- Writes operational keys to `config.json`, secret keys to `config.secrets.json`
- Idempotency: if no secret keys in `config.json` and `config.secrets.json` exists → no-op
- Formatting: `json.dump(indent=2, sort_keys=True)` + trailing newline
- Script is NOT executed during this step — CEO runs post-plan

### 3. Gitignore edits

**bellows/.gitignore:** Line 9 changed from `config.json` to `config.secrets.json`
**Parent .gitignore:** Line 18 changed from `bellows/config.json` to `bellows/config.secrets.json`

### 4. Test additions — `tests/test_bellows.py`

Updated `test_load_config`: now creates both `config.json` and `config.secrets.json`, asserts merged result contains keys from both files.

New tests added (6):
- `test_load_config_merges_secrets` — both files present, assert merged dict contains operational + secret keys
- `test_load_config_missing_secrets` — only config.json, assert `pushover` absent, no error
- `test_load_config_deep_merge` — config.json has `pushover: {}` stub, secrets has `pushover: {app_key: "x"}`, assert merge produces `{app_key: "x"}`
- `test_migrate_config_idempotent` — run migration twice, assert output files byte-identical on second run
- `test_migrate_config_preserves_values` — run migration, merge output files, assert merged == original
- `test_migrate_config_already_split` — run migration on already-split config, assert no files changed

---

## Test Results

### Before DEV (baseline)
```
======================== 106 passed, 1 warning in 0.54s ========================
```

### After DEV
```
======================== 112 passed, 1 warning in 0.48s ========================
```

Delta: +6 tests (106 → 112), 0 failures, 0 errors.

### New tests only
```
tests/test_bellows.py::test_load_config PASSED
tests/test_bellows.py::test_load_config_merges_secrets PASSED
tests/test_bellows.py::test_load_config_missing_secrets PASSED
tests/test_bellows.py::test_load_config_deep_merge PASSED
tests/test_bellows.py::test_migrate_config_idempotent PASSED
tests/test_bellows.py::test_migrate_config_preserves_values PASSED
tests/test_bellows.py::test_migrate_config_already_split PASSED
================= 7 passed, 105 deselected, 1 warning in 0.08s =================
```

---

## Safety Property Verification

**config.json is byte-identical to pre-DEV state:**

The live `config.json` at `/Users/marklehn/Developer/GitHub/bellows/config.json` was not modified. It does not exist in the worktree (gitignored), and no code in this step touches it. The file's last-modified timestamp (May 19 10:56) predates this plan's execution.

The migration script exists on disk but was NOT executed. CEO runs it post-plan per SA spec.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented the config secrets/operational split per SA architecture deposit. Modified `load_config()` to read and merge two JSON files (operational + secrets), created an idempotent migration script, updated both `.gitignore` files, and added 6 new tests covering merge behavior, missing-secrets fallback, deep merge, and migration idempotency/correctness.

### Files Deposited
- `bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — `load_config()` expanded to two-file merge with lenient missing-secrets behavior
- `bellows/scripts/migrate_config.py` — new idempotent migration script (not executed)
- `bellows/.gitignore` — `config.json` → `config.secrets.json`
- `GitHub/.gitignore` — `bellows/config.json` → `bellows/config.secrets.json`
- `bellows/tests/test_bellows.py` — updated `test_load_config` + 6 new tests

### Decisions Made
- Secrets path resolves relative to `config_path.parent` (not hardcoded BELLOWS_ROOT) — enables test isolation with temp dirs while preserving production behavior
- Migration script handles edge case of no secret keys + no secrets file by creating empty `config.secrets.json`

### Flags for CEO
- Migration script must be run manually post-plan: `cd bellows && python3 scripts/migrate_config.py`
- Daemon restart required after migration to pick up new loader
- Parent `.gitignore` was edited directly (it's in the parent repo, not the bellows repo) — commit separately if needed

### Flags for Next Step
- QA should verify the parent `.gitignore` edit is correct (line 18 now reads `bellows/config.secrets.json`)
- QA should run migration against a test fixture copy, NOT against the live `config.json`
- The `config_path.parent` resolution is a minor deviation from SA pseudocode (which used `BELLOWS_ROOT`) — functionally equivalent in production, better for testing
