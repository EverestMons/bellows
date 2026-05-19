# Config Secrets/Operational Split — Architecture Deposit

**Plan:** executable-bellows-config-split-2026-05-23
**Step:** 1 (SA)
**Date:** 2026-05-23
**Author:** Bellows Systems Analyst

---

## File Structure Decision (Decision 1)

**Choice:** **(a)** `config.json` (operational, committed) + `config.secrets.json` (gitignored, JSON, deep-merged into a single dict)

**Justification:** The current loader is a single `json.load` call returning a dict. Option (a) keeps both files as JSON, so the merge is a second `json.load` plus a dict merge — no new parser, no new dependency, no format mismatch. Option (b) (`.env` KEY=VALUE) would require a flat-to-nested mapping layer for `pushover.app_key` and `notifications` sub-keys, adding parser complexity with no benefit. Option (c) (`config.local.json`) uses a convention that implies per-machine overrides rather than secrets — semantically misleading. Option (a) communicates intent clearly: one file is secrets, the other is operational.

**Post-split file shapes:**

`config.json` (committed):
```json
{
  "watched_projects": [ ... ],
  "default_model": "claude-opus-4-6",
  "planner_model": "claude-sonnet-4-6",
  "step_inactivity_timeout_seconds": 600,
  "step_timeout_seconds": 2400,
  "callback_port": 5000,
  "notifications": {
    "enabled": true,
    "events": {
      "verdict_needed": true,
      "failure": true,
      "plan_complete": true,
      "plan_halted": true,
      "plan_skipped": true,
      "queue_empty": true
    },
    "coalesce_window_seconds": 30
  }
}
```

`config.secrets.json` (gitignored):
```json
{
  "pushover": {
    "app_key": "<real-key>",
    "user_key": "<real-key>"
  },
  "tailscale_ip": "100.79.204.47"
}
```

---

## Key Classification Table (Decision 2)

| Key | Path | Classification | Justification |
|---|---|---|---|
| `watched_projects` | top-level | **Operational** | Directory paths — reviewable, not sensitive |
| `default_model` | top-level | **Operational** | Model selection — no credential value |
| `planner_model` | top-level | **Operational** | Model selection — no credential value |
| `pushover` | top-level (object) | **Secret** | Contains API credentials |
| `pushover.app_key` | nested | **Secret** | Pushover application token — credential |
| `pushover.user_key` | nested | **Secret** | Pushover user token — credential |
| `step_inactivity_timeout_seconds` | top-level | **Operational** | Timeout tuning — no credential value |
| `step_timeout_seconds` | top-level | **Operational** | Timeout tuning — no credential value |
| `callback_port` | top-level | **Operational** | Network port — not sensitive |
| `tailscale_ip` | top-level | **Secret** | Leaks Tailnet membership and internal addressing. Not a credential, but identifying: reveals that the host participates in a specific Tailnet and its stable IP within that network. Classified secret on principle-of-least-exposure grounds — the operational config can reference `tailscale_ip` via the merged dict at runtime without committing the value to git. |
| `notifications` | top-level (object) | **Operational** | Notification preferences — no credential value |
| `notifications.enabled` | nested | **Operational** | Boolean toggle |
| `notifications.events` | nested (object) | **Operational** | Event type toggles |
| `notifications.events.*` | nested | **Operational** | Individual event booleans |
| `notifications.coalesce_window_seconds` | nested | **Operational** | Timing parameter |

---

## Loader Behavior Decision (Decision 3)

**Choice:** **Lenient** — secrets file optional; missing → load operational only, log a warning, secret keys resolve to empty/default values via existing `.get()` fallbacks.

**Justification:**

1. **Dev ergonomics:** Running Bellows locally for testing (e.g., running the test suite, developing new features) does not require Pushover credentials. The test suite already constructs config dicts without Pushover keys. A strict requirement would force every dev/test invocation to have a secrets file.
2. **Existing code is already lenient:** Every access to `pushover` keys in bellows.py uses `config.get("pushover", {}).get("app_key", "")` — empty-string fallback. The notifier checks `_app_key` truthiness before sending. A missing secrets file produces the same behavior as the current config with empty pushover keys: notifications silently skip.
3. **Fail-fast is not needed:** There is one deployment (CEO's machine). If secrets are missing, the first notification attempt will silently no-op and the `notifier.init_notifications` log line will show the state. No silent data loss occurs — plans still execute, only push notifications are skipped.

**Pseudocode for `load_config()` post-change:**

```python
def load_config(path: str = "config.json") -> dict:
    config_path = BELLOWS_ROOT / path
    with open(config_path, "r") as f:
        config = json.load(f)

    secrets_path = BELLOWS_ROOT / "config.secrets.json"
    if secrets_path.exists():
        with open(secrets_path, "r") as f:
            secrets = json.load(f)
        # Deep merge: secrets keys override/extend operational keys
        for key, value in secrets.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            else:
                config[key] = value
    else:
        _log("WARN", "config.secrets.json not found — running without secrets (Pushover disabled)")

    return config
```

Note: The deep merge is one level deep — sufficient because the only nested secret key is `pushover` (an object), and `tailscale_ip` is a scalar. No recursive merge needed. If `pushover` exists in both files (it shouldn't post-migration, but for safety), the secrets version wins via `dict.update`.

---

## Migration Mechanics

**Script location:** `bellows/scripts/migrate_config.py`

**Script behavior:**
1. Read `config.json` from `BELLOWS_ROOT`
2. Classify keys per the Key Classification Table above
3. Write `config.json` with operational keys only (preserving JSON formatting with `indent=2`)
4. Write `config.secrets.json` with secret keys only (same formatting)
5. Print summary of what was moved

**Idempotency contract:**
- If `config.secrets.json` already exists and `config.json` does not contain any secret keys → no-op (print "already migrated" and exit)
- If `config.json` still contains secret keys → split them out (handles partial migration or manual config edits)
- Running twice produces byte-identical output files on the second run

**Who runs it:** CEO, manually, post-plan. The DEV step ships the script but does NOT execute it. This is critical because Bellows is reading `config.json` while executing this plan — splitting the file mid-execution would cause the running daemon to read a config missing `pushover` keys on its next config access.

**Note on formatting:** The migration script should use `json.dump(data, f, indent=2)` with a trailing newline to match the existing file's style. Exact byte-for-byte preservation of the original file is not achievable with `json.dump` (Python's JSON encoder may reorder keys or normalize whitespace), so the contract is: **logical equivalence** (the merged dict from the two output files equals the original dict) and **consistent formatting** (indent=2, sorted keys for determinism). The `sort_keys=True` flag ensures idempotency across runs.

---

## Gitignore Edits

### Parent `.gitignore` (`/Users/marklehn/Developer/GitHub/.gitignore`)

| Action | Line | Content |
|---|---|---|
| **Remove** | 18 | `bellows/config.json` |
| **Add** | after line 17 (under `# Sensitive`) | `bellows/config.secrets.json` |

Post-edit, the `# Sensitive` section becomes:
```
# Sensitive
github-recovery-codes.txt
bellows/config.secrets.json
```

### Bellows `.gitignore` (`/Users/marklehn/Developer/GitHub/bellows/.gitignore`)

| Action | Line | Content |
|---|---|---|
| **Remove** | 9 | `config.json` |
| **Add** | after line 8 (where `config.json` was) | `config.secrets.json` |

Post-edit, the relevant section becomes:
```
.venv/
config.secrets.json
.env
```

---

## Test Surface

### Existing tests touching config/load_config

| Test | Location | What it does | Impact |
|---|---|---|---|
| `test_load_config` | `tests/test_bellows.py:17` | Creates a temp `config.json`, calls `load_config(path)`, asserts `default_model` | **Must update:** now tests the two-file merge path. Expand to cover both files present and secrets-file-missing cases. |

All other tests construct config dicts inline (e.g., `config = {"watched_projects": [...], "callback_port": 5999}`) and pass them directly to `run_plan()` or `Bellows()`. These are **not affected** by the loader change — they bypass `load_config()` entirely.

### New tests required

| Test | Description |
|---|---|
| `test_load_config_merges_secrets` | Create both `config.json` (operational) and `config.secrets.json` (secrets) in a temp dir. Call `load_config`. Assert merged dict contains keys from both files. Assert `pushover.app_key` comes from secrets file. |
| `test_load_config_missing_secrets` | Create only `config.json` in a temp dir (no secrets file). Call `load_config`. Assert it returns operational keys. Assert `pushover` key is absent (not an error). Verify warning was logged. |
| `test_load_config_deep_merge` | Create both files where `config.json` has a `pushover: {}` stub and `config.secrets.json` has `pushover: {app_key: "x"}`. Assert the merge produces `pushover: {app_key: "x"}` (secrets override). |
| `test_migrate_config_idempotent` | Run migration script against a test fixture. Run again. Assert output files are byte-identical across both runs. |
| `test_migrate_config_preserves_values` | Run migration script against a test fixture. Read both output files and merge. Assert merged dict equals original input dict. |
| `test_migrate_config_already_split` | Run migration against an already-split config (no secret keys in `config.json`, `config.secrets.json` exists). Assert no files changed. |

---

## Self-Application Risk

**Acknowledgment:** This plan modifies `bellows/config.json`'s loading code and `.gitignore` entries while Bellows is actively reading `config.json` to execute this plan.

**Safety property:** The DEV step (Step 2) changes the loader code in `bellows.py` and ships a migration script, but does **not** run the migration script and does **not** modify `config.json` itself. The live daemon continues to read the existing single-file `config.json` using the existing `load_config()` code (loaded at daemon startup). The new loader code exists on disk but is not loaded by the running process.

**Why this is safe:**
1. Python loads module code at import time. The running daemon has already imported `bellows.py` — editing the file on disk does not affect the running process.
2. `config.json` remains byte-identical throughout DEV and QA steps (verified by `git diff bellows/config.json` at end of DEV).
3. Daemon restart (to pick up the new loader) is CEO-operated post-plan, after QA verification.
4. The new loader is backwards-compatible: if `config.secrets.json` does not exist (which it won't until migration runs), the new loader falls back to loading `config.json` only — producing the same dict as the current loader.

---

## Structural Impact

| Affected File | Change Type | Blast Radius |
|---|---|---|
| `bellows/bellows.py` | Modified (`load_config` function) | Contained — only the loader function changes; all consumer code continues to read from the same merged dict |
| `bellows/scripts/migrate_config.py` | New file | Zero runtime impact — script is not imported or invoked by bellows.py |
| `bellows/.gitignore` | Modified (swap `config.json` → `config.secrets.json`) | Git tracking only |
| `GitHub/.gitignore` | Modified (swap `bellows/config.json` → `bellows/config.secrets.json`) | Git tracking only |
| `tests/test_bellows.py` | Modified (new tests, updated `test_load_config`) | Test-only |
| `bellows/config.json` | **Not modified by DEV** — will be split by CEO post-plan | No runtime impact during plan execution |

**Downstream dependencies:** None. No other project imports `bellows.load_config`. The config dict shape is unchanged — all consumer code sees the same merged dict.

---

## Gap Assessment Table (Rule 27)

| # | Gap | Current State | Proposed State | Change Required |
|---|---|---|---|---|
| 1 | Config is a single gitignored file | `config.json` contains both secrets and operational keys; gitignored in both `.gitignore` files | `config.json` (operational, committed) + `config.secrets.json` (secrets, gitignored) | Split file; modify loader; update gitignore |
| 2 | Loader reads one file | `load_config()` does `json.load(config.json)` — 3 lines | Loader reads `config.json`, optionally reads `config.secrets.json`, deep-merges | Modify `load_config()` in `bellows.py` (~15 lines) |
| 3 | No migration tooling | N/A | Idempotent Python script at `bellows/scripts/migrate_config.py` | Create new file |
| 4 | Parent `.gitignore` blocks `bellows/config.json` | Line 18: `bellows/config.json` | Line 18: `bellows/config.secrets.json` | Remove old line, add new line |
| 5 | Bellows `.gitignore` blocks `config.json` | Line 9: `config.json` | Line 9: `config.secrets.json` | Remove old line, add new line |
| 6 | `test_load_config` tests single-file load only | Tests one file load, asserts `default_model` | Tests two-file merge, missing-secrets fallback, deep merge | Update existing test + add 5 new tests |
| 7 | Watched-project additions are invisible to git | All 10 `watched_projects` entries were added to gitignored file | `watched_projects` in committed `config.json` — additions appear in commit history | Achieved by gaps 1+4+5 |
| 8 | No config layout documentation | N/A | Comment block in `load_config()` documenting the two-file layout | Add inline comment (SA recommends inline comment over separate file — keeps documentation co-located with code) |

---

## Verification Blocks

### Claim 1: config.json has exactly 9 top-level keys

- **Claim:** `config.json` has exactly 9 top-level keys: `callback_port`, `default_model`, `notifications`, `planner_model`, `pushover`, `step_inactivity_timeout_seconds`, `step_timeout_seconds`, `tailscale_ip`, `watched_projects`
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && python3 -c "import json; c=json.load(open('config.json')); print('Keys:', sorted(c.keys())); print('Count:', len(c.keys()))"`
- **Query output:**
  ```
  Keys: ['callback_port', 'default_model', 'notifications', 'planner_model', 'pushover', 'step_inactivity_timeout_seconds', 'step_timeout_seconds', 'tailscale_ip', 'watched_projects']
  Count: 9
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 2: Parent .gitignore line 18 contains `bellows/config.json`

- **Claim:** `/Users/marklehn/Developer/GitHub/.gitignore` line 18 is `bellows/config.json`
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -n 'config.json' ../.gitignore`
- **Query output:**
  ```
  18:bellows/config.json
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 3: Bellows .gitignore line 9 contains `config.json`

- **Claim:** `/Users/marklehn/Developer/GitHub/bellows/.gitignore` line 9 is `config.json`
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -n 'config.json' .gitignore`
- **Query output:**
  ```
  9:config.json
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 4: bellows.py has exactly 3 `config[` access sites

- **Claim:** `bellows.py` has exactly 3 direct `config[<key>]` bracket-access sites (lines 360, 396, 979) — all other config access uses `.get()` with defaults
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -n 'config\[' bellows.py`
- **Query output:**
  ```
  360:        model = header.get("Model", header.get("model", config["default_model"]))
  396:        if model != config["default_model"]:
  979:        self.response_server = server.ResponseServer(config["callback_port"])
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 5: test_bellows.py has 1 test directly testing load_config

- **Claim:** `tests/test_bellows.py` has exactly 1 test function named `test_load_config` (line 17) that directly calls `bellows.load_config()`. Total test count: 106.
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -c 'def test_' tests/test_bellows.py; grep -n 'def test_load_config' tests/test_bellows.py`
- **Query output:**
  ```
  106
  17:def test_load_config():
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 6: load_config is a 4-line function at line 123

- **Claim:** `load_config()` is defined at line 123 of `bellows.py` and is 4 lines (123-126)
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && sed -n '123,126p' bellows.py`
- **Query output:**
  ```
  def load_config(path: str = "config.json") -> dict:
      config_path = BELLOWS_ROOT / path
      with open(config_path, "r") as f:
          return json.load(f)
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 7: notifier.init_notifications receives the full config dict

- **Claim:** `notifier.init_notifications(config)` is called at line 1382 with the full config dict; notifier extracts `pushover` and `notifications` sub-keys internally
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -n 'init_notifications' bellows.py notifier.py`
- **Query output:**
  ```
  bellows.py:1382:    notifier.init_notifications(config)
  notifier.py:29:def init_notifications(config: dict) -> None:
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

### Claim 8: All pushover access uses .get() with empty-string fallback

- **Claim:** Every access to pushover keys in bellows.py uses `config.get("pushover", {}).get("app_key", "")` pattern — empty-string fallback, not KeyError
- **Verification query:** `cd /Users/marklehn/Developer/GitHub/bellows && grep -n 'pushover' bellows.py`
- **Query output:**
  ```
  310:    app_key = config.get("pushover", {}).get("app_key", "")
  311:    user_key = config.get("pushover", {}).get("user_key", "")
  1015:            app_key = self.config.get("pushover", {}).get("app_key", "")
  1016:            user_key = self.config.get("pushover", {}).get("user_key", "")
  1079:                    app_key = self.config.get("pushover", {}).get("app_key", "")
  1080:                    user_key = self.config.get("pushover", {}).get("user_key", "")
  1094:        app_key = self.config.get("pushover", {}).get("app_key", "")
  1095:        user_key = self.config.get("pushover", {}).get("user_key", "")
  ```
- **Timestamp:** 2026-05-23T00:00:00Z

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced architecture deposit for the config secrets/operational split. Made three design decisions: (a) `config.json` + `config.secrets.json` (both JSON, deep-merged), (b) key classification with `pushover` and `tailscale_ip` as secrets and all other keys as operational, (c) lenient loader behavior when secrets file is missing. Specified migration mechanics, gitignore edits, test surface, and safety properties.

### Files Deposited
- `bellows/knowledge/architecture/config-split-design-2026-05-23.md` — Architecture deposit with design decisions, gap assessment, and verification blocks

### Files Created or Modified (Code)
- None (SA step produces design only)

### Decisions Made
- Decision 1: `config.json` + `config.secrets.json` (both JSON) — minimal loader change
- Decision 2: `pushover` (object) and `tailscale_ip` classified as secret; all other keys operational
- Decision 3: Lenient loader — missing secrets file logs warning, does not error
- Documentation approach: inline comment block in `load_config()` (not a separate file)
- Migration script location: `bellows/scripts/migrate_config.py`

### Flags for CEO
- `tailscale_ip` classified as secret — if you want it committed (e.g., for documentation or debugging), reclassify to operational before DEV executes
- Migration script must be run manually post-plan: `cd bellows && python scripts/migrate_config.py`
- Daemon restart required after migration to pick up new loader

### Flags for Next Step
- DEV must re-run all 8 verification queries before editing (Rule 39)
- The 3 bracket-access sites (`config["default_model"]` at lines 360, 396 and `config["callback_port"]` at line 979) access operational keys — they will work without secrets. No code change needed for these sites.
- The `load_config` function signature stays the same (`path: str = "config.json"`) — `test_load_config` calls it with a full path, so DEV must handle the secrets file path resolution relative to the config file's directory, not just `BELLOWS_ROOT`
