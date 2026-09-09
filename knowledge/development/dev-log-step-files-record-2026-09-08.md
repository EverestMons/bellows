# Dev-log: step_files record (plan 100049, thread 209)
**Date:** 2026-09-09 | **Branch:** bellows-wt/100049 | **HEAD (first commit):** 9ffb96cbdbf637bf6befd1a5489b76f12664ccc0

---

## Pins re-derived (P1–P4, P7)

**P1 — schema idiom** (`lifecycle.init_lifecycle_db`, `:24`):
Every table uses `CREATE TABLE IF NOT EXISTS`. One column migration exists for `plan_doc_ref` (PRAGMA table_info → ALTER TABLE). The `gate_events` DDL is at lines 129–138 (prior to this plan's addition of `step_files` immediately after). The `step_files` DDL added here follows the same idiom: `CREATE TABLE IF NOT EXISTS step_files (id INTEGER PRIMARY KEY AUTOINCREMENT, step_id INTEGER NOT NULL REFERENCES steps(id), path TEXT NOT NULL, UNIQUE(step_id, path))`.

**P2 — writer** (`record_gate_events`, `:493–536` before this plan):
`if step_id is None: return`; opens its own `conn = sqlite3.connect(path)` (no `uri`); FAIL rows from `gate_result["failures"]`, PASS rows for the ten `standard_gates`; `conn.commit()`; the whole body under `try/except Exception → _warn`. Confirmed: ten `standard_gates` names in the list (receipt_status, no_errors, no_permission_denials, deposit_exists, scope_check, rule_20_self_check, rule_22_verification, qa_test_result, quoted_test_nodes_exist, mutation_result).

**P3 — call sites** (`bellows.py:1187` and `:1345`):
Both sites call `lifecycle.record_gate_events(_lc_step_id, gate_result)` immediately after `record_step_end`. The `gate_result` dict carries `files_changed` (set by `gates.check` from `_parse_diff_stat`'s `--relative` diff, see `gates.py:270–323`).

**P4 — step re-use**: `steps` table has `UNIQUE(plan_id, step_number)`. The continue/resume path calls `record_step_start` for the same (plan_id, step_number), which either reuses the existing row or the daemon re-runs `record_gate_events` on the same `step_id` (the id is stored in `_lc_step_id` across iterations). The `step_files` writer uses DELETE + INSERT to REPLACE rather than accumulate — test 4 proves correctness.

**P7 — existing tests**: `test_lifecycle.py` schema tests use `expected_tables.issubset(tables)` at `:378–380` (adding `step_files` is additive, not breaking) and a no-BLOB scan over every table at `:396–400` (`step_files` has no BLOB columns). `test_gate_transaction_mechanization.py` pins `STANDARD_GATES` at ten — unchanged by this plan.

No mechanism mismatch found. Proceeding.

---

## Failing-first (the eight tests red, then green)

Tests written in `tests/test_step_files_record.py` before implementing. Run output before implementation:

```
FFFFFFFF                                                                 [100%]
test_1_init_twice_table_exists_row_survives
  AssertionError: step_files table missing after second init
  assert []

test_2_files_recorded_with_gate_rows
  sqlite3.OperationalError: no such table: step_files

test_3_empty_files_no_rows_no_exception
  sqlite3.OperationalError: no such table: step_files

test_4_replace_on_re_evaluation
  sqlite3.OperationalError: no such table: step_files

test_5_tool_flip_and_read_only
  (tool does not exist yet)

test_6_step_files_failure_no_raise_gate_rows_present
  sqlite3.OperationalError: no such table: step_files

test_7_tool_no_plan_text_not_found
  (tool does not exist yet)

test_8_tool_table_absent
  (tool does not exist yet)
```

All 8 FAIL as expected. After implementing the table (lifecycle.py), the writer (record_gate_events), and the tool (tools/replay_scope_check.py):

```
tests/test_step_files_record.py tests/test_lifecycle.py tests/test_gate_transaction_mechanization.py
124 passed in 1.51s
```

All 8 new tests + 116 existing tests: GREEN.

---

## Mutation run

Five mutants, all killed:

| # | name | target | expect_fail test |
|---|------|--------|-----------------|
| M1 | drop-delete-before-insert | lifecycle.py | test_4_replace_on_re_evaluation |
| M2 | insert-only-first-path | lifecycle.py | test_2_files_recorded_with_gate_rows |
| M3 | skip-write-when-passed | lifecycle.py | test_2_files_recorded_with_gate_rows |
| M4 | tool-compare-recorded-to-itself | tools/replay_scope_check.py | test_5_tool_flip_and_read_only |
| M5 | tool-opens-without-mode-ro | tools/replay_scope_check.py | test_5_tool_flip_and_read_only |

Run output tail:
```
LIVE-TREE UNCHANGED: lifecycle.py sha256=f3fbfae998a8
LIVE-TREE UNCHANGED: tools/replay_scope_check.py sha256=e08623c40e2f

MUTATION: 5 killed, 0 survived, 0 error
```

HEAD: `9ffb96cbdbf637bf6befd1a5489b76f12664ccc0` (the first commit of Step 1, four files).

---

## Cost

`record_gate_events` timing with 10 files on a tmp db (REPLACE path — same step_id re-evaluated), three runs:

| Run | ms |
|-----|-----|
| 1 | 0.76 |
| 2 | 0.80 |
| 3 | 0.75 |
| **Median** | **0.76 ms** |

The step_files block adds one DELETE and one `executemany` (10 rows). On the live db with WAL mode, overhead per step evaluation is well under 1 ms — negligible against the step runtime.
