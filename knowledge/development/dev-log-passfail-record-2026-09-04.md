# Dev Log — Pass/Fail Record Census (diagnostic-100035)

**Date:** 2026-09-04 | **Plan:** diagnostic-100035

## What this corrects

Plan 100034 (gate fail-open census, 2026-09-04) concluded in Q5:

> `gates.py` (all) — "Not in manifest; only visible if plan was held (`.hold.json` shows reason) — ✗ gates run post-step; no plan-level record if passed"

**That conclusion was correct for ARTIFACTS.** It was incomplete for the system: `lifecycle.db` carries a `gate_events` table with 470 rows, 9 distinct gate names, and full coverage of the 38 plans that have completed at least one step. The DB was not examined in 100034.

## Why the DB was missed

100034's census tool (`tools/gate_failopen_census.py`) examined Python source files for gate logic, fail-open paths, and invocation patterns. It did not query `lifecycle.db`. The artifact framing — "can a reader of a closed plan determine from its file artifacts whether each check ran?" — was answered correctly from that scope. The DB is not a plan file artifact; it is a side-channel record. The census question was interpreted as an artifacts question, and the DB fell outside that interpretation.

The fix is not a correction to 100034's Q5 answer but a reframing: the ruling's ask splits into two subproblems — (a) does a record exist? YES, in the DB for daemon-invoked gates; and (b) is that record surfaced? NO, for closed plans, because no tool reads gate_events historically.

## Key findings (measured, not asserted)

### What gate_events covers

- 9 gates, all from `gates.py`, all daemon-invoked during a step where `_lc_step_id` exists
- 470 rows across 38 plans; 9 rows with `overridden=1`
- `record_gate_events` called at exactly two sites: `bellows.py:1179`, `:1317`; guarded by `if step_id is None: return` at `lifecycle.py:499`
- 7 gates have explicit pass rows (standard_gates hardcoded list at `lifecycle.py:518–522`)
- 2 gates (`ceo_flags`, `qa_test_result`) have fail-only rows — their "pass" is inferred by absence

### What gate_events does NOT cover

- **≈65 checks** from the 100034 Q1 inventory of ≈74:
  - **CLASS B (authoring-time):** plan_lint (22), cycle_check (11), walk_register_lint (6), fold_check, propagation_check — run before a step exists; no `step_id` anchor; `gate_events.step_id NOT NULL` blocks recording
  - **CLASS C (claim-time):** depositor.py holds (17) — plan_id exists after mint but no step_id; surfaced in `.hold.json` artifacts
  - **CLASS D (wrap-time):** wrap_check (8 tags) — no plan_id, no step_id; no anchor in current schema
  - **2 CLASS A advisory:** `_gate_is_qa_step` and `_gate_file_change_audit` — daemon-invoked with step_id available but not fed to `record_gate_events` (structural omission; not in `standard_gates` list)

### Surfacing gap

No tool surfaces `gate_events` to a human for a **closed plan**:
- `tools/gate_watcher.py` monitors active plans in real time (polling loop); exits on terminal state
- `tools/clear_plan.py` is the override workflow tool; reads fail rows to mark `overridden=1`
- `lifecycle.py:get_overridden_gates_for_step()` is internal to verdict consumption
- `reporting.py`, `dashboard.py`, `status.py` — zero `gate_events` references

A complete record exists in the DB; nothing reads it back as a historical report for closed plans. This is the surfacing problem the ruling's ask resolves to.

### Portability gap

`lifecycle.db` is git-ignored (`.gitignore:16`). `gate_events` rows are machine-local. A reader on another machine sees zero gate_events for plans executed here. The multi-machine id-range law is the governing design; this is a consequence, not an oversight.

### Overrides

All 9 `overridden=1` rows have non-NULL `override_ref` strings naming the gate class, substance verification, and authorizing party. Overrides are attributable on the originating machine but do not travel with the plan in git.

## How this plan was dispatched

The diagnostic was read-only. `tools/passfail_record_census.py` was built as the instrument; it opens `lifecycle.db` in read-only mode (`?mode=ro`), takes a single-connection snapshot, and prints Q1–Q7 answers with commands. The tool reports the queue idle state at execution so the snapshot's concurrency context is explicit.

Deposits: research note in governance, this dev-log in bellows. No code changed, no gates altered, no recommendation made.
