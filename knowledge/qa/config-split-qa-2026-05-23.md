# Config Secrets/Operational Split — QA Report

**Plan:** executable-bellows-config-split-2026-05-23
**Step:** 3 (QA)
**Date:** 2026-05-23
**Author:** Bellows QA

---

## Verification Table

| # | Check | Target | Result | Evidence |
|---|---|---|---|---|
| 1 | Loader change matches SA spec | `bellows.py:123-146` `load_config()` | PASS | `evidence/config-split-2026-05-23/loader_diff.txt` |
| 2 | Migration script exists, is idempotent | `scripts/migrate_config.py` run twice against test fixture | PASS | `evidence/config-split-2026-05-23/migration_idempotency.txt` |
| 3 | Migration script preserves values byte-for-byte | Test fixture split then merged == original | PASS | `evidence/config-split-2026-05-23/migration_preserves_values.txt` |
| 4 | Gitignore reconciliation | `bellows/.gitignore` and parent `.gitignore` | PASS | `evidence/config-split-2026-05-23/gitignore_state.txt` |
| 5 | Live config.json byte-identical | `/Users/marklehn/Developer/GitHub/bellows/config.json` timestamp + worktree status | PASS | `evidence/config-split-2026-05-23/live_config_unchanged.txt` |
| 6 | Test suite regression | 112 passed, 0 failed (was 106) | PASS | `evidence/config-split-2026-05-23/pytest_before_after.txt` |
| 7 | New tests pass | 7/7 new/updated tests pass | PASS | `evidence/config-split-2026-05-23/new_tests_output.txt` |
| 8 | No live secrets leaked | grep of bellows.py, migrate_config.py, test_bellows.py, deposits | PASS (with flag) | `evidence/config-split-2026-05-23/secrets_grep.txt` |
| 9 | Rule 20 self-check | QA report + 8 evidence files | See below | Inline stdout |

---

## Check Details

### Check 1 — Loader matches SA spec

Post-edit `load_config()` at `bellows.py:123-146`:
- Reads `config.json` into dict (no longer returns immediately)
- Resolves `config.secrets.json` relative to `config_path.parent`
- If secrets file exists: one-level deep merge via `dict.update` for nested dicts, direct assignment for scalars
- If secrets file missing: logs WARN via `_log()`, returns operational config only
- Inline comment block documents the two-file layout (SA Gap #8)
- Matches SA Decision 3 (lenient) pseudocode exactly
- Minor deviation from SA pseudocode: secrets path resolves relative to `config_path.parent` (not hardcoded `BELLOWS_ROOT`) — functionally equivalent in production, enables test isolation with temp dirs. Documented by DEV.

### Check 2 — Migration idempotency

Ran `migrate_config.migrate()` twice against a test fixture containing all 9 original keys. First run split correctly (7 operational, 2 secret). Second run printed "Already migrated" and produced no file changes. Output files byte-identical across runs.

### Check 3 — Migration preserves values

After splitting the test fixture, merged the two output files using the same merge logic as `load_config()`. Asserted `merged == original`. All 9 keys preserved with correct values, including nested `notifications` and `pushover` sub-objects.

### Check 4 — Gitignore reconciliation

- `bellows/.gitignore` line 9: changed from `config.json` to `config.secrets.json` — confirmed
- Parent `.gitignore` line 18: changed from `bellows/config.json` to `bellows/config.secrets.json` — confirmed
- `config.json` no longer gitignored in either file — ready for commit tracking
- `config.secrets.json` gitignored in both files — secrets protected

### Check 5 — Live config.json byte-identical

The live `config.json` at `/Users/marklehn/Developer/GitHub/bellows/config.json` has modification timestamp `May 19 10:56:01 2026`, predating this plan. The worktree is clean with no untracked files. `config.json` does not exist in the worktree (gitignored). Migration script was NOT executed.

### Check 6 — Test suite regression

Before DEV: 106 passed, 1 warning in 0.54s
After DEV (QA re-run): 112 passed, 1 warning in 0.57s
Delta: +6 new tests, 0 regressions, 0 errors. Warning is pre-existing urllib3/LibreSSL compatibility.

### Check 7 — New tests pass

All 7 config-related tests pass:
- `test_load_config` (updated) — two-file merge path
- `test_load_config_merges_secrets` (new) — operational + secret keys present in merged dict
- `test_load_config_missing_secrets` (new) — operational only, no error, pushover absent
- `test_load_config_deep_merge` (new) — secrets override operational nested dict
- `test_migrate_config_idempotent` (new) — second run produces identical files
- `test_migrate_config_preserves_values` (new) — merged output == original input
- `test_migrate_config_already_split` (new) — no-op on already-split config

### Check 8 — No live secrets leaked

**DEV-authored code and tests: PASS** — bellows.py contains only key name references (`.get("pushover", {}).get("app_key", "")`), migration script contains only `SECRET_KEYS = {"pushover", "tailscale_ip"}`, test fixtures use sentinel values only ("fake-app-key", "100.0.0.1", etc.). No real Pushover keys or tailscale IPs in any code or test file.

**Deposit files: FLAG** — The SA deposit (`knowledge/architecture/config-split-design-2026-05-23.md` line 49) contains the real `tailscale_ip` value `100.79.204.47` in its example JSON shape for `config.secrets.json`. This was committed in Step 1 (commit `062970a`), not introduced by Step 2. Flagged for CEO review — consider redacting to a placeholder.

**Pre-existing files (not from this plan):** `terminal-and-notification-surface-audit-2026-05-11.md` contains real Pushover keys; `phase-b-2-step-6-2026-05-18.md` contains real tailscale IP. These predate this plan.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bellows-config-split-2026-05-23/knowledge/qa/evidence/config-split-2026-05-23/
Files verified: 8
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Executed all 9 verification checks for the config secrets/operational split implementation. All checks pass. Produced 8 evidence files and this QA report. Flagged one pre-existing concern: the SA deposit (Step 1) contains the real `tailscale_ip` value in a committed file.

### Files Deposited
- `bellows/knowledge/qa/config-split-qa-2026-05-23.md` — this QA report
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/loader_diff.txt` — load_config() diff
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/migration_idempotency.txt` — idempotency test output
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/migration_preserves_values.txt` — value preservation test
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/gitignore_state.txt` — gitignore state verification
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/live_config_unchanged.txt` — safety property check
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/pytest_before_after.txt` — test regression results
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/new_tests_output.txt` — new tests output
- `bellows/knowledge/qa/evidence/config-split-2026-05-23/secrets_grep.txt` — secrets leak scan

### Files Created or Modified (Code)
- None (QA step produces verification only)

### Decisions Made
- Check 5 (live config unchanged): Used file timestamp + worktree status instead of `git diff` because config.json is gitignored — appropriate alternative verification method
- Check 8 (secrets): Scoped DEV-authored code/tests as PASS; flagged SA deposit's real tailscale_ip as pre-existing concern for CEO

### Flags for CEO
- SA deposit (`knowledge/architecture/config-split-design-2026-05-23.md` line 49) contains real `tailscale_ip` value `100.79.204.47`. Consider redacting to placeholder. This is committed in `062970a`.
- Pre-existing secret exposure in `terminal-and-notification-surface-audit-2026-05-11.md` (real Pushover keys) and `phase-b-2-step-6-2026-05-18.md` (real tailscale IP) — not from this plan but noted during secrets scan.
- Migration script must be run manually post-plan: `cd bellows && python3 scripts/migrate_config.py`
- Daemon restart required after migration to pick up new loader.

### Flags for Next Step
- None (terminal step)
