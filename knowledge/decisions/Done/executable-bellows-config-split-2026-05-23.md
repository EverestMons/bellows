# Executable Plan — Bellows Config Secrets/Operational Split

**Plan:** executable-bellows-config-split-2026-05-23
**Author:** Planner
**Date:** 2026-05-23
**Last Updated:** 2026-05-23
**Project:** bellows
**Dispatch Mode:** bellows
**Auto Close:** disabled
**Total Steps:** 3
**Priority:** 1
**Depends on:** none

---

## Purpose

Split `bellows/config.json` into two files: a committed operational config (carrying `watched_projects`, model selections, timeouts, port, and other non-sensitive settings) and a gitignored secrets file (carrying credentials and any host-identifying values the SA classifies as sensitive). The loader merges both at startup. The goal is to make watched-project additions reviewable via commit history — today, all ten current `watched_projects` entries were added invisibly to git, and the `bellows-config-secrets-and-operational-split` shop_backlog entry captures this gap.

This plan ships code changes only. Operational rollout (running the migration script, daemon restart) is performed by the CEO outside the plan, because Bellows is dispatching this plan against the live config it is reading from — restarting Bellows mid-step would interrupt the plan executing the restart.

## Test Scope

Test suite (`tests/test_bellows.py`) regression. Plus targeted unit tests for the new loader merge behavior. No daemon restart during plan execution.

---

## Execution Map

Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)

All sequential. Each step pauses for verdict before the next claims.

---

## STEP 1 — BELLOWS SYSTEMS ANALYST

You are the Bellows Systems Analyst. Read your specialist file at `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` before starting.

### Reads (mandatory, in order)

1. `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — your specialist file
2. `/Users/marklehn/Developer/GitHub/SPECIALIST_TEMPLATE.md` — particularly the "Claim Verification Blocks" subsection under Output Format (your findings deposit must include claim/query/output blocks for every load-bearing population claim)
3. `/Users/marklehn/Developer/GitHub/shop_backlog.md` — the `bellows-config-secrets-and-operational-split` entry (the source of truth for this plan's intent)
4. `/Users/marklehn/Developer/GitHub/bellows/bellows.py` — full file is large; focus on `load_config()` at line ~123 and its single call site in `main()` at line ~1357. Note all sites that read from `config[<key>]` (DEV will need to know every consumer).
5. `/Users/marklehn/Developer/GitHub/bellows/config.json` — current state of the live file (you have read access; read it directly so your claims have grounding)
6. `/Users/marklehn/Developer/GitHub/bellows/.gitignore` and `/Users/marklehn/Developer/GitHub/.gitignore` — current gitignore state for `config.json`

### Work

Produce an architecture deposit that makes three design decisions:

**Decision 1 — File structure.** Choose one of:
- **(a)** `config.json` (operational, committed) + `config.secrets.json` (gitignored, JSON, mergeable into a single dict)
- **(b)** `config.json` (operational, committed) + `.env` (gitignored, KEY=VALUE shell-env style — requires a separate parser)
- **(c)** Some other structure you justify (e.g., `config.json` + `config.local.json`)

Decide on cost-of-loader-complexity vs. consistency-with-existing-shape grounds. The current code is pure JSON; the loader currently does one `json.load`. Optimize for minimal loader change.

**Decision 2 — Which keys are secret?** Classify every top-level key in `config.json` (and relevant nested keys) as `secret` or `operational`. Clear secrets: `pushover.app_key`, `pushover.user_key`. Ambiguous: `tailscale_ip` (network coordinate — not a credential, but does it leak tailnet membership? Decide). Clear operational: `watched_projects`, `default_model`, `planner_model`, timeouts, `callback_port`, `notifications.enabled/events/coalesce_window_seconds`. Justify each ambiguous classification.

**Decision 3 — Loader behavior on missing secrets file.** Choose one of:
- **Strict:** secrets file required; missing → hard fail at startup
- **Lenient:** secrets file optional; missing → load operational only, log a warning, set secret keys to `None` so notifier code can detect and skip Pushover calls
- **Per-key strict:** secrets file required IF any operational code path needs a secret key; if no secret keys referenced, can run without

Decide on dev-ergonomics (running locally without Pushover credentials) vs. fail-fast-on-misconfigured-prod grounds.

**Migration mechanics.** Specify the one-shot migration approach:
- A standalone Python script (e.g., `bellows/scripts/migrate_config.py`) that reads existing `config.json`, writes `config.json` (operational keys only) and `config.secrets.json` (secret keys only) — or whichever file shape you chose
- The script must be idempotent (running twice is safe; second run is a no-op)
- The script must preserve all existing values byte-for-byte (no whitespace normalization, no key reordering beyond what's necessary)
- Specify whether the script is part of the DEV step's deliverables or invoked by CEO manually post-DEV

**Gitignore reconciliation.** Specify the exact `.gitignore` edits:
- Remove `bellows/config.json` from the parent `.gitignore` (line 18) — committed config is now safe
- Remove `config.json` from `bellows/.gitignore` — same reason
- Add the chosen secrets file to both `.gitignore` files

**Test surface.** Identify every test in `tests/test_bellows.py` that touches `config` or `load_config`. Specify what new tests are needed for the loader merge behavior (at minimum: missing-secrets behavior per Decision 3, secrets-present merge correctness, idempotent migration script).

### Required output

A Gap Assessment table per Rule 27 with columns `| Gap | Current State | Proposed State | Change Required |`. Each row enumerates one concrete edit (code change, file create, config edit, test addition). DEV will copy rows directly into edit blocks in Step 2.

Also include:

- **File Structure Decision** section: choice + justification + the exact file contents shape (JSON schema sketch is fine)
- **Key Classification Table** with columns `| Key | Path | Classification | Justification |` covering every key in `config.json`
- **Loader Behavior Decision** section: choice + justification + pseudocode for `load_config()` post-change
- **Migration Mechanics** section: script location, script behavior, idempotency contract, who runs it
- **Gitignore Edits** section: exact lines to add/remove in each `.gitignore` file
- **Test Surface** section: existing tests touched + new tests required
- **Self-application risk** section: explicit acknowledgment that this plan modifies the file Bellows is reading from. State the safety property: DEV's changes must produce a config that the CURRENT loader can still read on plan-execution-time daemon reads, so the in-flight daemon does not break. Daemon restart to pick up the new loader is CEO-operated post-plan.
- **Structural Impact** section: files affected, blast radius, downstream dependencies (none expected)
- **Claim Verification Blocks** for every load-bearing population claim (e.g., "config.json has exactly N top-level keys", "test_bellows.py has M tests touching load_config", ".gitignore line 18 contains `bellows/config.json`")
- **Output Receipt** per your specialist file

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/config-split-design-2026-05-23.md`

### Pause for verdict

After deposit, pause. Bellows will issue a `verdict-request-*-step-1.md`; Planner will verify and continue.

---

## STEP 2 — BELLOWS DEVELOPER

You are the Bellows Developer. Read your specialist file at `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_DEVELOPER.md` before starting.

### Pre-edit verification

Per Rule 39, re-run the SA's verification queries from Step 1's deposit before editing. Specifically:
- Re-run the query that established the current `config.json` top-level key list (the SA will record this in their Claim Verification Blocks). If the keys differ from the SA's recorded set, halt and deposit a verification-mismatch report instead of proceeding.
- Re-run any other load-bearing claim queries the SA marked in their deposit.

If all verifications pass, proceed.

### Reads (mandatory, in order)

1. `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_DEVELOPER.md` — your specialist file
2. `/Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/config-split-design-2026-05-23.md` — Step 1's deposit, the source of truth for what you implement
3. `/Users/marklehn/Developer/GitHub/bellows/bellows.py` — `load_config()` and all `config[<key>]` consumer sites
4. `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py` — current test coverage of `load_config` and config access

### Work

Implement the changes per Step 1's Gap Assessment table. Specifically:

1. **Loader change** in `bellows/bellows.py` — modify `load_config()` per Step 1's pseudocode. The new loader reads both files (operational + secrets) and merges them into a single dict. Handle the missing-secrets case per the SA's Decision 3 (strict / lenient / per-key strict).
2. **Migration script** at the path specified by SA (likely `bellows/scripts/migrate_config.py`) — idempotent script that splits the existing config. Script does not run automatically; CEO invokes manually post-DEV.
3. **Gitignore edits** — exact line additions/removals per SA's spec. Both `bellows/.gitignore` and parent `.gitignore`.
4. **New tests** in `tests/test_bellows.py` per SA's Test Surface — at minimum: missing-secrets behavior, merge correctness, idempotent migration. Keep existing test coverage intact.
5. **Documentation** — add a comment block to `load_config()` documenting the two-file layout, or create a short `bellows/agents/CONFIG_LAYOUT.md` describing the layout for future agents. SA chooses.

### Critical safety property

The DEV step **MUST NOT** run the migration script. The migration script's invocation is CEO-operated post-plan, after DEV ships the code and QA verifies. If you run the script during the DEV step, the in-flight daemon (which is executing this plan) will see `config.json` change shape mid-step and may produce unexpected behavior on its next config read. Ship code only; do not split the live file.

Verification of this property: after DEV is complete, `git diff bellows/config.json` shows no changes; the live file is byte-identical to its pre-DEV state.

### Required output

A dev log recording:

- Pre-edit verification results (which queries were re-run, results, pass/fail per claim)
- Diff summary for each modified file (loader change, new script, gitignore edits, test additions)
- Test results: full suite run before and after — log line counts for the test summary (passed/failed/errors deltas)
- Confirmation that `bellows/config.json` is byte-identical to pre-DEV state (`git diff` output included)
- Output Receipt per your specialist file

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py` (modified)
- `/Users/marklehn/Developer/GitHub/bellows/scripts/migrate_config.py` (new — or whichever path SA chose)
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py` (modified)
- `/Users/marklehn/Developer/GitHub/bellows/.gitignore` (modified)
- `/Users/marklehn/Developer/GitHub/.gitignore` (modified)

### Pause for verdict

After deposit, pause. Bellows will issue a `verdict-request-*-step-2.md`; Planner will verify and continue.

---

## STEP 3 — BELLOWS QA AGENT

You are the Bellows QA Agent. Read your specialist file at `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_QA.md` before starting.

### Reads (mandatory, in order)

1. `/Users/marklehn/Developer/GitHub/bellows/agents/BELLOWS_QA.md` — your specialist file
2. `/Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/config-split-design-2026-05-23.md` — Step 1's design (the spec to verify against)
3. `/Users/marklehn/Developer/GitHub/bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` — Step 2's dev log
4. `/Users/marklehn/Developer/GitHub/bellows/bellows.py` — post-edit state of `load_config()`
5. `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` — canonical Rule 20 block

### Verification checks

Produce a verification table with columns `| Check | Target | Result | Evidence |`. At minimum:

1. **Loader change matches SA spec.** Read post-edit `load_config()`. Confirm two-file read, merge logic, and missing-secrets handling match SA Decision 3.
2. **Migration script exists, is idempotent.** Run the script twice against a test-fixture copy of the current config (do NOT run against `bellows/config.json`). Confirm second run produces zero diff against first run output.
3. **Migration script preserves values byte-for-byte.** Compare test-fixture config inputs to the merged dict produced by the new loader reading the two output files. Confirm logical equivalence.
4. **Gitignore reconciliation.** Confirm `bellows/.gitignore` and parent `.gitignore` no longer ignore `config.json` (or, if SA changed strategy, confirm new state). Confirm secrets file (whatever shape SA chose) is gitignored in both.
5. **Live config.json byte-identical.** Run `git diff bellows/config.json` — must be empty. This is the safety property check.
6. **Test suite regression.** Full pytest run — record before/after numbers. No new failures introduced.
7. **New tests pass.** The tests added in Step 2 pass.
8. **No live secrets leaked.** Grep for `pushover.*key`, `tailscale_ip`, or any string that looks like a Pushover key or IP in: post-edit `bellows.py`, the migration script, the test fixtures, and any deposit file. Secrets should appear only in test fixtures with sentinel values (e.g., `app_key: "fake-test-key"`), never real values.
9. **Rule 20 self-check.** Run the canonical Python block from `RULE_20_SELF_CHECK_BLOCK.md` against this plan's expected evidence files. Include literal stdout in the QA report.

### Evidence files

Write evidence to `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/config-split-2026-05-23/`:

- `loader_diff.txt` — diff of `load_config()` showing pre/post change
- `migration_idempotency.txt` — output of running the migration script twice and diffing the outputs
- `migration_preserves_values.txt` — comparison of pre-split config dict to post-split-then-merged dict (Python: `assert pre == merged_post`)
- `gitignore_state.txt` — current state of both `.gitignore` files (relevant lines)
- `live_config_unchanged.txt` — `git diff bellows/config.json` output (must be empty)
- `pytest_before_after.txt` — pytest summary lines from before-DEV and after-DEV runs
- `new_tests_output.txt` — pytest output for just the new tests
- `secrets_grep.txt` — grep results showing no real secrets in non-config files

### Deposits

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/config-split-qa-2026-05-23.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/config-split-2026-05-23/` (directory containing eight evidence files)

### Pause for verdict

After deposit, pause. This is the terminal step. Per Rule 25, Bellows owns the `qa_checkpoint` terminal close via the continue-verdict consume cycle.

---
