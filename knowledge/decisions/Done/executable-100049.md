# bellows — executable: the lifecycle records the files a step's gates SAW — a `step_files` table written beside `gate_events`, and `tools/replay_scope_check.py` that re-runs today's `scope_check` over every recorded step (thread 209)

**Date:** 2026-09-08 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_step_files_record.py`, a new sibling) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** thread 209

**auto_close:** false

**Post-close:** ⚠️ **RESTART OWED** — `lifecycle.py` is imported by `bellows.py` in-process; until the daemon restarts, steps keep recording no files. The CEO's act at close.

**Depends on:** thread 209 (fork 2 of plan 100045): the gates plan measured its blast radius by replaying the lifecycle `commits` table through `git show --name-only` — available only for steps that committed, and by re-reading git rather than a record of what the gate saw. Clone origin BY KIND for the step layout: `Done/executable-100045.md` (2026-09-08, bellows — the mutation run as a Deposit, four dev-log headings, per-hunk QA); the newest shipped plan WRITING `lifecycle.py` is `Done/executable-570.md` (2026-08-26, T2 for its claim block — its `record_*` helper shape, `try/except` with `_warn`, is mirrored here). `clone-origin` threads naming either: none open (DC v2.33 query at walk 0).

**Tier computed (§1):** **T-2 fires** — a new table in the live `lifecycle.db` and a new write on every step's gate evaluation; T-6 not claimed (a recorder, not a gate); T-8 not fired. **T1.**

## What this changes

1. **`step_files` table** in `init_lifecycle_db`: `id INTEGER PRIMARY KEY AUTOINCREMENT, step_id INTEGER NOT NULL REFERENCES steps(id), path TEXT NOT NULL, UNIQUE(step_id, path)` — `CREATE TABLE IF NOT EXISTS`, the file's own migration idiom (P1).
2. **`record_gate_events` writes it** from `gate_result["files_changed"]` — the exact list `gates.check` received — after the gate rows have COMMITTED, in a second block under its own `try/except … _warn` on the same connection: `DELETE FROM step_files WHERE step_id = ?` then one INSERT per path, then commit — so a re-evaluation of the same step id REPLACES rather than duplicates (P4), and a files failure never loses a gate row. An empty list writes nothing and raises nothing.
3. **`tools/replay_scope_check.py <lifecycle.db> [--plan-root <bellows>]`** — reads every step with `step_files` rows, joins its plan (`plans.plan_doc_ref`, else `knowledge/decisions/Done/executable-<id>.md`, else the lane file by id) and the recorded `scope_check` result from `gate_events`, runs TODAY's `gates._gate_scope_check(plan_text, step_number, files, failures)` in-process, and prints one line per step — `<plan>/<step>: recorded=<pass|fail> now=<pass|fail>` — then `FLIPS: N` and the flip set. Read-only (`mode=ro`), no git. This is the walk-6 probe of plan 100045 promoted from scratch to a tool a gate change runs at its walk 0 and its DEV Item 1.

## Why this exists

A gate change must be measured against what the gate actually saw, per step, not against a proxy. Plan 100045 had to reconstruct that from the `commits` table (82 SHAs over 73 steps) and `git show` — and the reconstruction found a real hole the corpus proxy could not (absolute Scope entries), which is the argument for making the record first-class: every future gate change gets the replay for free, and steps that never committed (halts, refusals) are recorded too.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the schema idiom | `lifecycle.init_lifecycle_db` (`:24`) creates every table `CREATE TABLE IF NOT EXISTS`; one column migration exists (`PRAGMA table_info(plans)` → `ALTER TABLE plans ADD COLUMN plan_doc_ref`, `:55-57`); `gate_events` DDL at `:130-138` | read `init_lifecycle_db` |
| P2 | ⛔ the writer | `record_gate_events(step_id, gate_result, db_path=None)`: `if step_id is None: return`; opens its own connection; FAIL rows from `gate_result["failures"]`, PASS rows for `standard_gates` (ten names since `601f5b9`); `conn.commit()`; the whole body under `try/except Exception → _warn` | read `:497-535` |
| P3 | the call sites | `bellows.py:1187` and `:1345` — both pass the `gate_result` that `gates.check` returned, which carries `files_changed` (the list `check` received, from `_parse_diff_stat`'s `--relative` diff) | grep `record_gate_events(` |
| P4 | a step id can be evaluated more than once | the continue/resume path re-runs a step's gates on the same `steps` row (the `steps` table is `UNIQUE(plan_id, step_number)`; `record_step_start` reuses the id) — so the writer must REPLACE per step id | `record_step_start` (`:454-470`); `bellows.py:1412` region |
| P5 | live counts | `steps` 85, `gate_events` 617, `commits` distinct steps 79 — 6 steps never committed and are invisible to the commits replay | `sqlite3 "file:lifecycle.db?mode=ro"` |
| P6 | the replay's precedent | plan 100045's `replay_scope.py` (governance `panel-gates-verdict-pause-2026-09-08/replay_scope.py`): commits → `git show --name-only` → old vs new rule; 73 steps, 72 identical, 1 flip | read the script |
| P7 | tests today | `tests/test_lifecycle.py` 5 `record_gate_events` references (incl. thread 210's PASS-row test); its two schema tests tolerate a new table (`expected_tables.issubset(tables)` at `:378-380`; a no-BLOB scan over every table at `:396-400`); `tests/test_gate_transaction_mechanization.py` pins `STANDARD_GATES` at ten | grep; read the two tests |
| P8 | this plan's class | `lifecycle.py` + `tools/` from bellows → shop-infra; HOLDS by design, the CEO releases | `_assign_class` |
| P9 | in-flight | none (daemon pid 42126, `up 2h 30m` at walk 0) | `status.py` |

## What this does NOT do

- ⛔ **It does not back-fill `step_files` from the `commits` table.** History stays as it is; the replay covers steps from the restart onward, and the commits-based scratch probe stays the tool for older steps (fork 1: a `--from-commits` arm, later).
- ⛔ **It does not touch `gates.py` or any gate.** The tool reads the gate; it changes nothing.
- **It does not record `files_changed` on `gate_events` rows** (one path per gate row would multiply 617 rows by the file count); a sibling table keyed by step is the shape.
- **The record is the LATEST evaluation of a step** — a re-evaluation on the same step id replaces the rows (P4); the superseded evaluation's file list is not kept. By design: the replay answers 'what did the gate see when it last judged this step'.
- **It does not add the replay to the battery** (Ruling 117: the `validation:` key set is fixed); a gate plan's walk 0 and DEV Item 1 run it by hand.

## MUST-PRESERVE

⛔ **Invariants that must still be TRUE afterwards.**

- ⛔ **`record_gate_events` never raises** — a `step_files` failure is warned, not thrown (the envelope). Proven by test 6.
- ⛔ **`gate_events` rows are unchanged in count and content** by this plan. Proven by test 2 (the pass/fail rows the existing tests assert are asserted again beside the new rows) and the untouched `tests/test_gate_transaction_mechanization.py`.
- ⛔ **One row per (step, path), replaced on re-evaluation.** Proven by tests 3 and 4.
- ⛔ **The tool is read-only** — `mode=ro`, no git, no writes. Proven by test 5 (the db's mtime and row counts unchanged after a run).
- ⛔ **`init_lifecycle_db` on an existing db adds the table without touching existing rows.** Proven by test 1.

## Drafting Cycle

**Tier:** **T1** — T-2 fires (a live-table write on every step). **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-step-files-record-2026-09-08.md
**Walks:** walk 0 pinned (P1–P9 measured on bellows `b701924`; clone-diff against `Done/executable-100045.md` (layout) and `Done/executable-570.md` (the lifecycle helper shape) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7); `lens_order_check` runs with `cycle_check` at every walk close.

- Weak spots:          w1 5 folded — instruction 4 / record 1; w2 5 folded — instruction 5 / record 0; w3 dry
- Destruction:         w1 1 folded — instruction 0 / record 1; w2 dry; w3 dry
- Vulnerabilities:     w1 dry; w2 dry; w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry
- ACID:                w1 dry; w2 dry; w3 dry

**ESCALATE:yield-rising after walk 2** (instruction 4 → 5, all five walk-1 residue). **Direction verdict after walk 2: PROCEED** (CEO, 2026-09-09).

**Walk 3 — DRY, all five lenses, one commit per lens; `lens_order_check` OK across walks 1–3. Instruction 0 on a full pass: the WARM close meets §2's bar (T1, no panel) — a judged stop (11 findings: instruction 9 / record 2; yield by walk 4 → 5 → 0).**
**Closing:** WARM close after walk 3 — thread 209's plan. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases; the daemon restart is the CEO's act at close.

## Cycle Manifest
tier: T1
target: lifecycle.py
class: shop-infra
reads: lifecycle.py, bellows.py, gates.py, tests/test_lifecycle.py, tests/test_gate_transaction_mechanization.py, knowledge/decisions/Done/executable-100045.md, knowledge/decisions/Done/executable-570.md, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/panel-gates-verdict-pause-2026-09-08/replay_scope.py
writes: lifecycle.py, tools/replay_scope_check.py, tests/test_step_files_record.py, knowledge/mutants/step-files-record.json, knowledge/mutants/step-files-record.run.txt, knowledge/development/dev-log-step-files-record-2026-09-08.md
open_forks: 1. a `--from-commits` arm on the replay tool for steps recorded before the restart (the commits table + git) — a later direct edit; 2. whether `record_deposits` should record the same list for QA steps (a deposit is a file the gate saw) — not folded
walks: 3
yields: 4, 5, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:2
coherence: 3/3 body walks named in the register (16 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-step-files-record.md.foldcheck.json

---

## STEP 1 — DEV (the table, the writer, the tool; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f lifecycle.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE**; prove `VENV_OK` with `-c 'import pytest'`. ⛔ **Never open the live `lifecycle.db` for writing** — every test builds its own db under `tmp_path` via `lifecycle.init_lifecycle_db(path)`; the conftest's autouse isolation covers the module path, and a probe outside pytest is a production run (LESSONS 2026-09-08).
>
> **Scope:**
> - `lifecycle.py`
> - `tools/replay_scope_check.py`
> - `tests/test_step_files_record.py`
> - `knowledge/mutants/step-files-record.json`
> - `knowledge/mutants/step-files-record.run.txt`
> - `knowledge/development/dev-log-step-files-record-2026-09-08.md`
>
> **Item 1 — re-derive P1, P2, P3, P4, P7 and HALT on a mechanism mismatch** (P5's counts are a record). Paste into the dev-log.
>
> **Item 2 — write the failing tests FIRST**, in `tests/test_step_files_record.py` (each test builds a db under `tmp_path` with `init_lifecycle_db`, mints a plan and a step with the existing helpers as `test_lifecycle.py` does; the replay tests write a fixture plan file under `tmp_path` and pass `--plan-root tmp_path`):
> 1. ⛔ **`init_lifecycle_db` twice on one path → `step_files` exists (`PRAGMA table_info`), and a pre-existing `plans` row survives**
> 2. ⛔ **`record_gate_events` with `passed: True`, no failures and `files_changed=["a.py", "b/c.md"]` → two `step_files` rows for the step AND the ten PASS rows (files are recorded regardless of the verdict — M3's target); a second case with one FAIL and the same files → the same two rows beside the FAIL row**
> 3. ⛔ **an empty `files_changed` (and a missing key) → zero rows, no exception**
> 4. ⛔ **a second `record_gate_events` on the same step id with `["a.py"]` → exactly one row (`b/c.md` gone) — REPLACE, never duplicate**
> 5. ⛔ **the tool: a db with two recorded steps (one whose recorded `scope_check` was `pass` and whose files now FAIL under a fixture plan with a declared Scope that omits one path — a FLIP; one identical) → prints both lines and `FLIPS: 1` naming the first; the db's `st_mtime` and every table count are unchanged after the run**
> 6. ⛔ **a `step_files` write that raises (monkeypatch `sqlite3.connect` to return a connection whose `execute` raises on `step_files`) → `record_gate_events` returns without raising, `_warn` was called, AND the step's gate rows are present (committed before the files were attempted)**
> 7. **a step with no plan text resolvable → the tool prints `<plan>/<step>: plan text not found` and continues; exit 0**
> 8. ⛔ **a db whose schema predates the table (built by hand without `step_files`) → the tool prints the `table absent` line and exits 0 — no traceback**
>
> Run them and record the FAILURE output before implementing.
>
> **Item 3 — the table** (`lifecycle.py`, in `init_lifecycle_db` after the `gate_events` DDL): the DDL in *What this changes* 1, `CREATE TABLE IF NOT EXISTS`.
> **Item 4 — the writer** (`record_gate_events`, after the PASS-row loop): AFTER the existing `conn.commit()` of the gate rows, a SECOND block under its own `try/except Exception → _warn("record_gate_events: step_files failed …")`: `files = gate_result.get("files_changed") or []`; `conn.execute("DELETE FROM step_files WHERE step_id = ?", (step_id,))`; `conn.executemany("INSERT OR IGNORE INTO step_files (step_id, path) VALUES (?, ?)", [(step_id, p) for p in files])`; `conn.commit()`. The gate rows are committed before the files are attempted, so a files failure never loses a gate row (test 6 asserts the gate rows persisted). Nothing else in the function moves.
> **Item 5 — the tool** `tools/replay_scope_check.py`: `main(argv)` with `db` (positional) and `--plan-root` (default: the bellows root via `bellows_root`); `sqlite3.connect("file:<db>?mode=ro", uri=True)`; `SELECT s.id, s.plan_id, s.step_number, p.plan_doc_ref FROM steps s JOIN plans p ON p.id = s.plan_id WHERE s.id IN (SELECT DISTINCT step_id FROM step_files) ORDER BY s.plan_id, s.step_number`; per step: files from `step_files`, recorded result = `gate_events.result` for `gate_name = 'scope_check'` (`fail` if any fail row, else `pass`, `none` if absent), plan text by the three-way lookup in *What this changes* 3, `gates._gate_scope_check(text, step_number, files, failures, project_path=<plan root>)` → `now` (the `project_path` kwarg since plan 100045 — absolute declared entries normalize exactly as in production); print the line; collect flips (`recorded != now`, ignoring `none`); print `FLIPS: N` and each; exit 0 always (a measuring tool). ⛔ A db WITHOUT the `step_files` table (the live db until the daemon restarts) prints `step_files: table absent — the daemon has not restarted since the plan that added it; nothing to replay` and exits 0 (test 8). Imports `gates` from the repo root by `sys.path`.
> **Item 6 — first commit**, gated in one command on the targeted run: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/test_step_files_record.py tests/test_lifecycle.py tests/test_gate_transaction_mechanization.py -q && git add lifecycle.py tools/replay_scope_check.py tests/test_step_files_record.py knowledge/mutants/step-files-record.json && git commit -F <msg-file>` — four files, message tagged with the plan id AND `thread 209`. ⛔ The manifest is `{"target": "lifecycle.py", "mutants": [ … ]}` (`tools/replay_scope_check.py` mutants carry their own `"target"`), keys `name`/`why`/`anchor`/`replacement`/`expect_fail`, anchors count-1, one test per selector: M1 drop the DELETE → test 4; M2 insert only the first path → test 2; M3 skip the write when `gate_result["passed"]` is true → test 2's passing case; M4 the tool compares `recorded` to itself → test 5; M5 the tool opens the db without `mode=ro` and `VACUUM`s → test 5 (mtime). Five mutants.
> **Item 7 — the mutation run, REDIRECTED into `knowledge/mutants/step-files-record.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/step-files-record.json > knowledge/mutants/step-files-record.run.txt 2>&1; echo "exit=$?"` → `exit=0`; last `MUTATION:` line `5 killed, 0 survived, 0 error`; `HEAD:` the FULL sha of Item 6's commit. A survivor is a missing test: fix, re-commit, re-run.
> **Item 8 — dev-log** with FOUR literal headings QA greps: `## Pins re-derived (P1–P4, P7)`; `## Failing-first (the eight tests red, then green)`; `## Mutation run`; `## Cost` (median of three `record_gate_events` timings with 10 files on a tmp db, before and after — one DELETE and one executemany added).
> **Item 9 — second commit:** the run file and the dev-log, gated in one command on the run file — `grep -q 'MUTATION: [1-9][0-9]* killed, 0 survived, 0 error' knowledge/mutants/step-files-record.run.txt && git add knowledge/mutants/step-files-record.run.txt knowledge/development/dev-log-step-files-record-2026-09-08.md && git commit -F <msg-file>`. `numstat` over the two commits — exactly 6 files; `git reflog -n 6` → 0 amends, 0 resets.
>
> **Deposits:**
> - `knowledge/development/dev-log-step-files-record-2026-09-08.md`
> - `knowledge/mutants/step-files-record.run.txt`
>
> **Post-conditions:** all eight tests pass; `tests/test_lifecycle.py` and `tests/test_gate_transaction_mechanization.py` pass UNCHANGED; the run file ends `MUTATION: 5 killed, 0 survived, 0 error`; the four dev-log headings present; six files over two commits.

## STEP 2 — QA (full suite + the tool on the LIVE db, read-only)

> ⛔ **Re-establish the root first** — `cd "$(git rev-parse --show-toplevel)" && test -f lifecycle.py && echo TREE_OK`; interpreter `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE; prove `VENV_OK`.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt 2>&1 || { echo HALT-SUITE-RED; exit 1; }`; `tests/test_lifecycle.py` and `tests/test_gate_transaction_mechanization.py` unchanged (`git diff` in Item 5).
> **Item 2 — the tool on the LIVE db, read-only:** `tools/replay_scope_check.py /Users/marklehn/Developer/bellows/lifecycle.db` → before the restart the live db has NO `step_files` table, so the output is the single `table absent` line (test 8's) and exit 0; paste it, and paste `stat -f %m lifecycle.db` before and after (equal) and `sqlite3 "file:…?mode=ro" "select count(*) from sqlite_master where name = 'step_files'"` → 0 (the table does not exist until the restart). ⛔ The tool is proven read-only on the live db; nothing else touches it.
> **Item 3 — the writer on a tmp copy of the live db:** `cp lifecycle.db "$(git rev-parse --show-toplevel)/.qa-scratch/copy.db"` (the scratch dir under the worktree root, deleted before Item 5), `init_lifecycle_db(copy)` → `step_files` present, every other table's count unchanged (paste the counts before/after); then `record_gate_events(<an existing step id>, {"failures": [], "files_changed": ["x.py"]}, db_path=copy)` → one row; run the tool on the copy → one line `… recorded=pass now=<…>` and `FLIPS:` as computed. ⛔ Never the live file.
> **Item 4 — production writes, stated exactly:** none outside the two evidence files; the daemon restart is owed at close.
> **Item 5 — receipt** `knowledge/qa/evidence/step-files-record-qa-evidence-2026-09-08.md`: numstat over the DEV commits (six files); the run file's `HEAD:` equal to `git log -1 --format=%H -- knowledge/mutants/step-files-record.json`; `git diff <base>..<dev> -- tests/test_lifecycle.py tests/test_gate_transaction_mechanization.py` → EMPTY; toplevel; `git reflog -n 6` → 0 amends; the four dev-log headings grepped; Items 1–4 each on its own line; the Rule 20 block inside a `## Verification` section. ⛔ Quote test node ids only as pytest printed them; never place a hedging keyword in a ✅ row.
> **Item 6 — commit**, pathspec-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt && git add knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt knowledge/qa/evidence/step-files-record-qa-evidence-2026-09-08.md && git commit -F <msg-file>` — exactly two files.
>
> **Deposits:**
> - `knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt`
> - `knowledge/qa/evidence/step-files-record-qa-evidence-2026-09-08.md`
>
> **Scope:**
> - `knowledge/qa/evidence/step-files-record-suite-2026-09-08.txt`
> - `knowledge/qa/evidence/step-files-record-qa-evidence-2026-09-08.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
