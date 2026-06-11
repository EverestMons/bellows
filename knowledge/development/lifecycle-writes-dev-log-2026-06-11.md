# Dev Log — Lifecycle DB Transition Writes (Executable B)

**Date:** 2026-06-11
**Plan:** Reporting Phase 1, Executable B
**Step:** 1 (DEV)

## Work Items

### 1. lifecycle.py schema extension (blueprint 3.4 DDL verbatim)

Added 8 tables to `init_lifecycle_db()` with `CREATE TABLE IF NOT EXISTS` for upgrade-in-place from A-era DBs:

| Table | Key strategy | File:line |
|---|---|---|
| `diagnostic_meta` | `plan_id INTEGER PRIMARY KEY REFERENCES plans(id)` | lifecycle.py:68-73 |
| `executable_meta` | `plan_id INTEGER PRIMARY KEY REFERENCES plans(id)` | lifecycle.py:74-79 |
| `derivations` | `id INTEGER PRIMARY KEY AUTOINCREMENT`, `UNIQUE(executable_id, diagnostic_id)` | lifecycle.py:80-86 |
| `steps` | `id INTEGER PRIMARY KEY AUTOINCREMENT` (surrogate), `UNIQUE(plan_id, step_number)` | lifecycle.py:87-100 |
| `commits` | `step_id INTEGER NOT NULL REFERENCES steps(id)` | lifecycle.py:101-107 |
| `deposits` | `step_id INTEGER NOT NULL REFERENCES steps(id)` | lifecycle.py:108-114 |
| `verdicts` | `plan_id INTEGER NOT NULL REFERENCES plans(id)` | lifecycle.py:115-124 |
| `gate_events` | `step_id INTEGER NOT NULL REFERENCES steps(id)`, `result CHECK ('pass','fail')` | lifecycle.py:125-134 |

Key strategy matches blueprint 3.4 VERBATIM: `steps.id` as surrogate PK with `step_id` FK references in per-step child tables (`commits`, `deposits`, `gate_events`). No composite keys, no flattening.

### 2. lifecycle.py write helpers

Each helper wraps DB work in try/except that logs WARN via `_warn()` and returns (log-and-continue contract):

| Helper | Purpose | File:line |
|---|---|---|
| `record_step_start` | INSERT steps row (status=running) | lifecycle.py:247-260 |
| `record_step_end` | UPDATE steps (status, cost, duration, log_ref) | lifecycle.py:263-278 |
| `record_gate_events` | INSERT gate_events (pass + fail rows) | lifecycle.py:281-315 |
| `record_deposits` | INSERT deposits rows | lifecycle.py:318-333 |
| `record_commits` | INSERT commits rows (one per SHA) | lifecycle.py:336-349 |
| `record_verdict_request` | INSERT verdicts (outcome=NULL pending) | lifecycle.py:352-366 |
| `record_verdict_outcome` | UPDATE verdicts (outcome, decided_by) | lifecycle.py:369-383 |
| `record_meta` | INSERT diagnostic_meta or executable_meta | lifecycle.py:386-410 |
| `parse_derivations` | Regex parse "implements diagnostic <id>" | lifecycle.py:413-425 |
| `record_derivations` | INSERT derivations rows | lifecycle.py:428-441 |
| `get_step_id` | Lookup step_id by plan_id + step_number | lifecycle.py:444-455 |

### 3. bellows.py call sites at 7 transition boundaries

Relocated each site by symbol (blueprint line numbers predate Exec A):

| Boundary | Symbol anchor | Current file:line | Lifecycle write |
|---|---|---|---|
| CLAIM | `mint_and_claim` block | bellows.py:449-452 | `record_meta` + `record_derivations` |
| STEP START (first) | before `runner.run_step` (bootstrap) | bellows.py:504-505 | `record_step_start` |
| STEP START (loop) | before `runner.run_step` (next prompt) | bellows.py:611-612 | `record_step_start` |
| STEP END (first) | after `gates.check` + log line | bellows.py:556-560 | `record_step_end` + `record_gate_events` + `record_deposits` |
| STEP END (loop) | after `gates.check` + log line (while) | bellows.py:665-669 | `record_step_end` + `record_gate_events` + `record_deposits` |
| VERDICT REQUEST | 4 sites: worktree fail, mid-pause, final-pause, auto-close fail | bellows.py:494,598,707,741 | `record_verdict_request` |
| TEARDOWN/LAND | `_teardown_worktree` return | bellows.py:588,697,728 | `record_commits` |
| CLOSE (auto) | auto-close Done/ move | bellows.py:757 | `mark_plan_state(closed)` |
| CLOSE (continue-to-done) | `_consume_verdicts` continue-to-done | bellows.py:1585 | `mark_plan_state(closed)` |
| CLOSE (halted) | `_consume_verdicts` halted paths | bellows.py:1556,1610 | `mark_plan_state(halted)` |
| VERDICT CONSUMED | `_consume_verdicts` match | bellows.py:1533 | `record_verdict_outcome` |

### 4. verdict.py / runner.py

No edits needed. `post_verdict_request` already returns the filepath string. Cost/duration extracted from parsed dict and time.monotonic() in bellows.py.

### 5. _teardown_worktree return value change

Changed `_teardown_worktree` from `-> None` to `-> list` (returns commit_shas). All callers updated to capture and pass to `lifecycle.record_commits`.

### 6. _build_deposit_records helper

New helper `_build_deposit_records` (bellows.py:1033-1052) builds deposit records from plan text + header for lifecycle DB deposit rows.

### 7. Tests

**test_lifecycle.py** — 33 new tests (44 total):
- `TestSchemaUpgradeInPlace`: A-era DB upgrade, no blob columns
- `TestRecordStepStart/End`: happy path + None step_id
- `TestRecordGateEvents`: pass/fail rows
- `TestRecordDeposits`: landed/not-landed
- `TestRecordCommits`: multiple SHAs
- `TestRecordVerdicts`: request + outcome
- `TestRecordMeta`: diagnostic + executable
- `TestParseDerivations`: numeric id, legacy slug, no citation, case-insensitive
- `TestRecordDerivations`: link + duplicate ignore
- `TestGetStepId`: found + missing
- `TestLogAndContinueContract`: 9 tests — every write helper on read-only DB, assert no exception

**test_bellows.py** — 3 new integration tests:
- `test_lifecycle_writes_auto_close_flow`: full claim→step→gate→close, asserts plans.closed_at + steps + gate_events
- `test_lifecycle_writes_verdict_pause_flow`: claim→step→verdict request, asserts verdicts row with pause_reason
- `test_lifecycle_meta_and_derivations_at_claim`: asserts executable_meta + derivations rows

### 8. Full suite

516 passed, 0 failed (baseline: 480 → +36 new tests). Output: `knowledge/development/pytest_full_lifecycle_writes.txt`.

### 9. Self-verification

Scratch DB simulation: claim → step start → step end → verdict request → verdict consumed → close. All tables dumped with correct FKs, cost/duration populated, gate reason codes present. PASSED.

## Blueprint Verification Block Relocations

| V# | Blueprint claim | Relocated current file:line |
|---|---|---|
| V6 | validate_at_claim at ~396, shutil.move at ~411 | bellows.py:397, bellows.py:440 |
| V7 | record_run writes to bellows.db | bellows.py:24 (DB_PATH), bellows.py:276 (record_run) |
| V9 | bellows-wt/{slug} at ~984 | bellows.py:1082 (_teardown_worktree branch_name) |
