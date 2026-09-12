# bellows — ONE READ-ONLY OPENER FOR THE LIFECYCLE DB: `lifecycle.connect_readonly` tries `?mode=ro` and, when SQLite refuses an existing WAL file because no writer holds it (SQLITE_CANTOPEN, no `-shm`), falls back to a plain connection under `PRAGMA query_only=1`; `status.py`, the dashboard, the depositor's in-flight resolution and the gate watcher use it — so the readers that exist to report a stopped daemon work in the stopped state (thread 286, measured at the launchd migration 2026-09-11)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one helper, four call sites, one test file, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — `lifecycle.py`, `status.py` and `depositor.py` are imported across the suite; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 286 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** a daemon restart owed on each machine (`depositor.py` is daemon-loaded) — `.venv/bin/python bellows.py restart`, the first restarts through the agents (#100079): the mini by the CEO or the Planner, the Air by the Planner over ssh. No doctrine.

**Depends on:** thread 286 (2026-09-11): between the guarded stop and the new daemon's first open, `status.py` tracebacked with `unable to open database file`; the DB is WAL (`lifecycle.py:28` `PRAGMA journal_mode=WAL`), a clean close of the last connection removes `-wal` and `-shm`, and a `?mode=ro` open cannot create the `-shm` a WAL reader needs. Clone origin by kind and layout: `Done/executable-100073.md` (one lifecycle helper with the `_warn` shape and tests that read the DB, 2026-09-11).

**Tier computed (§1):** **T1** — T-1 fires (a helper the depositor and the status readers call on every machine); T-6 does not; T-2 does not (no schema; the fallback's only write is the `-shm` file SQLite creates for a WAL reader).

## CEO Context

Four readers open the lifecycle DB read-only with `?mode=ro`: `status.py` (raises), the dashboard (catches everything and reports the DB as absent), the depositor's in-flight-writes resolution (returns `None` — a deposit then resolves in-flight writes blind), and the gate watcher (returns `None`). All four fail in one state: a WAL database with no writer attached, which is the stopped daemon — the state a status reader exists to report, and the state every deposit made between a stop and a start lands in. SQLite's read-only URI mode forbids creating the shared-memory index a WAL reader needs; a plain connection creates it and, under `PRAGMA query_only`, can write nothing else. One helper makes the fallback explicit and keeps `mode=ro` as the first attempt, so the four readers keep their read-only contract and gain the stopped state.

## What this changes

1. **`lifecycle.py`** — `connect_readonly(db_path, timeout=5.0) -> sqlite3.Connection`: first `sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=timeout)`; on `sqlite3.OperationalError` whose text contains `unable to open database file` AND `os.path.exists(db_path)`, a plain `sqlite3.connect(db_path, timeout=timeout)` followed by `PRAGMA query_only = 1` (a read-only connection that may create `-shm`); any other error, or a missing file, propagates unchanged. Beside `_warn` (`:452`), the `try` / never-swallow shape of the readers, not the writers.
2. **`status.py`** — `query_in_flight` and `query_awaiting_verdict` (`:227–252`) open through `lifecycle.connect_readonly`; the module docstring's "all read-only, ?mode=ro" (`:4`, `:225`) gains ", with the WAL fallback"; `main`'s absent-DB branch unchanged.
3. **`dashboard.py`** — `assemble_state` (`:150–155`) keeps its `try`, but on the exception sets a new `db_unreadable = True` instead of `db_absent = True`, and the render shows `lifecycle.db unreadable` rather than `no lifecycle.db` — the two states are different facts for the viewer.
4. **`depositor.py`** — `_resolve_in_flight_writes` (`:562–575`) opens through the helper; its `except Exception: return None` stays (the caller's contract), so a genuine failure still returns `None` but the stopped-daemon state now returns the rows.
5. **`tools/gate_watcher.py`** — the read at `:65` opens through the helper; its `except sqlite3.Error: return None` stays.
6. **`tests/test_lifecycle_readonly.py`** — new: (t1) a WAL DB built by `init_lifecycle_db` under `tmp_path`, every connection closed, `-shm` and `-wal` absent (asserted) → `status.query_in_flight` returns rows, no raise; the `-shm` file's creation is asserted through `connect_readonly` directly, while the returned connection is still OPEN (SQLite deletes `-wal` and `-shm` again when the last connection closes, so an assertion after `close()` would fail on a correct fix); (t2) the same DB with a writer holding an open connection → the rows come through `mode=ro` — the fallback never runs: `monkeypatch.setattr(sqlite3, "connect", wrapper)` where the wrapper records each call's first argument and delegates to the real `connect`; the test asserts exactly one call and that its argument starts with `file:` (t1 asserts two calls, the second a bare path); (t3) a missing file → `sqlite3.OperationalError` propagates from `connect_readonly` (the absent-DB branch of `main` still decides); (t4) the fallback connection refuses `INSERT` (`sqlite3.OperationalError: attempt to write a readonly database`); (t5) `_resolve_in_flight_writes` on the t1 DB returns a list, not `None`; (t6) a source assertion — no `?mode=ro` literal remains outside `lifecycle.py` (`grep` over `status.py`, `dashboard.py`, `depositor.py`, `tools/gate_watcher.py`).
7. **`knowledge/mutants/readonly-wal-open.json`** — three mutants: (m1) the fallback removed → t1; (m2) the `mode=ro` attempt removed (always the plain connection) → t2; (m3) `PRAGMA query_only` dropped → t4.
8. **Not changed:** the writers, the WAL mode, the daemon's lock, `probe_daemon`.

## Why this exists

A viewer dashboard (#100079) that shows a traceback, or "no DB", at every stop is not a viewer; and a depositor that resolves in-flight writes blind whenever the daemon is between stop and start admits on missing information exactly when the operator is restarting things.

## What this does NOT do

- Use `immutable=1` (it skips the WAL and can read stale pages) — rejected in the thread and here.
- Change what any reader does with its rows, or any writer.

## MUST-PRESERVE

- ⛔ **`mode=ro` first, the fallback only on CANTOPEN with the file present** (t2, t3; m2).
- ⛔ **The fallback connection can write nothing but the `-shm`** (t4; m3).
- ⛔ **No `?mode=ro` literal outside the helper** (t6), so the next reader cannot reintroduce the window.
- ⛔ **Every `expect_fail` is a class-qualified node id where the test is a method**; the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop** (PT v4.108 §8).

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `c2dc785`, governance `a1983641`, daemon pid 29470 under the agent)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the four openers | `status.py:230` and `:245` `sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)` in `query_in_flight` / `query_awaiting_verdict` (docstring `:4`, `:225` "all read-only, ?mode=ro"); `dashboard.py:150–155` `try: … status.query_in_flight … except Exception: db_absent = True`; `depositor.py:564` in `_resolve_in_flight_writes`, `except Exception: return None` (`:573`); `tools/gate_watcher.py:65` `sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)`, `except sqlite3.Error: return None` | `grep -nF 'mode=ro' status.py dashboard.py depositor.py tools/gate_watcher.py` |
| P2 | ⛔ the measured failure | 2026-09-11 14:04:28 the dashboard's `q` stopped the daemon (SIGTERM drain, exit 0); until 14:05:0x, when the agent's daemon opened the DB, `python3 status.py` → `sqlite3.OperationalError: unable to open database file` at `query_in_flight`, and `sqlite3 "file:lifecycle.db?mode=ro"` → `Error: in prepare, unable to open database file (14)`; `lifecycle.db` present (532 KB, `rw-r--r--`, owner marklehn), `-shm` and `-wal` absent; `PRAGMA journal_mode` → `wal`; after the daemon's open `-shm` (32 KB) and `-wal` (0 B) exist and every reader works | the 30th baton block; thread 286 |
| P3 | ⛔ the mechanism | `lifecycle.py:28` `PRAGMA journal_mode=WAL` at `init_lifecycle_db`; SQLite: a WAL reader needs the `-shm` index; the last connection's clean close deletes `-wal` and `-shm`; `mode=ro` opens the file read-only and may not create either — SQLITE_CANTOPEN (14); a plain connection creates them; `PRAGMA query_only=1` makes a connection refuse every write statement | `sqlite3` documentation (`wal.html`, `uri.html`, `pragma.html#pragma_query_only`); P2's reproduction |
| P4 | ⛔ the tests to clone | `tests/test_status.py` (24 tests): the `status_db` fixture (`:17–`) builds a DB with `init_lifecycle_db` and inserts plans/steps; `tests/test_lifecycle.py` `TestMarkStepComplete` (#100073) — the row-reading shape; `conftest.isolate_lifecycle_db` (`:31`) | the files |
| P5 | in-flight; class; interpreter | queue empty at drafting; writes: `lifecycle.py`, `status.py`, `dashboard.py`, `depositor.py`, `tools/gate_watcher.py`, the test file, the manifest, run file, dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases; Python 3.9.6, the bellows venv | `python3 status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-readonly-wal-open-2026-09-11.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `c2dc785`; clone-diff against `Done/executable-100073.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every walk.

- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:  w1 dry; w2 dry
- ACID:                w1 dry; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 286's fix. Two walks: 2 → 0 (walk 1 gave the fallback spy a mechanism and moved the sidecar assertions inside the connection's lifetime; walk 2 dry on every lens). Every lens commit through `lens_commit.py`, the tool run bare, its exit read; the close through `close_cycle.py`. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases; after the merge the first restarts through the agents on both machines.

## Cycle Manifest
tier: T1
target: lifecycle.py
class: shop-infra
reads: lifecycle.py, status.py, dashboard.py, depositor.py, tools/gate_watcher.py, tests/test_status.py, tests/test_lifecycle.py, knowledge/decisions/Done/executable-100073.md
writes: lifecycle.py, status.py, dashboard.py, depositor.py, tools/gate_watcher.py, tests/test_lifecycle_readonly.py, knowledge/mutants/readonly-wal-open.json, knowledge/mutants/readonly-wal-open.run.txt, knowledge/development/dev-log-readonly-wal-open-2026-09-11.md, knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md, knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt
mutants: knowledge/mutants/readonly-wal-open.json
open_forks: 1. the Planner's own `mode=ro` diagnostics (#100071, #100072 opened the live DB that way from a worktree) — the same window applies; thread 281's session-start backup removes it for overnight runs; 2. the dashboard distinguishing "unreadable" from "absent" in its render is the smallest change here — a fuller viewer state model is thread 239's
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:4
coherence: 2/2 body walks named in the register (6 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-readonly-wal-open.md.foldcheck.json

---

## STEP 1 — DEV (one helper, four call sites, six tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never open the LIVE `lifecycle.db` from this step — every test builds its own under `tmp_path`; `T=$(mktemp -d /tmp/ro-wal.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `lifecycle.py`
> - `status.py`
> - `dashboard.py`
> - `depositor.py`
> - `tools/gate_watcher.py`
> - `tests/test_lifecycle_readonly.py`
> - `knowledge/mutants/readonly-wal-open.json`
> - `knowledge/mutants/readonly-wal-open.run.txt`
> - `knowledge/development/dev-log-readonly-wal-open-2026-09-11.md`
>
> **Item 1 — re-derive P1, P3 and P4 and HALT on a mechanism mismatch** (a line-number drift is not a mismatch; a `connect_readonly` already in `lifecycle.py`, or a reader that no longer opens `?mode=ro`, IS one). Reproduce P2 on a `tmp_path` DB — `init_lifecycle_db`, close, delete `-shm`/`-wal` if present, then `sqlite3.connect("file:…?mode=ro", uri=True).execute("SELECT count(*) FROM plans")` — and paste the `OperationalError` text; if it does NOT raise on this SQLite build, HALT (the mechanism is the plan's premise).
> **Item 2 — write the failing tests FIRST:** t1–t6 as *What this changes* 6 (red: t1 raises, t5 returns `None`, t6 finds four literals). Run the file; paste the red summary line.
> **Item 3 — the edits** as *What this changes* 1–5; then the file green, then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher`'s live-DB skip is the one); `tests/test_status.py`'s 24 unchanged and green.
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-readonly-wal-open-2026-09-11.md knowledge/mutants/readonly-wal-open.run.txt && git add lifecycle.py status.py dashboard.py depositor.py tools/gate_watcher.py tests/test_lifecycle_readonly.py knowledge/mutants/readonly-wal-open.json && git commit -F <msg-file> -- lifecycle.py status.py dashboard.py depositor.py tools/gate_watcher.py tests/test_lifecycle_readonly.py knowledge/mutants/readonly-wal-open.json` — seven files; the message tagged with the plan id and `thread 286`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/readonly-wal-open.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/readonly-wal-open.json > knowledge/mutants/readonly-wal-open.run.txt 2>&1`; the last line must read `MUTATION: 3 killed, 0 survived, 0 error`.
> **Item 6 — the dev-log** `knowledge/development/dev-log-readonly-wal-open-2026-09-11.md` under the four headings declared below; `## Pins re-derived (P1, P3, P4)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `and every reader works`; paste through those words, then stop. Under `## The window reproduced (Item 1)` the `OperationalError` text; under `## Failing-first (red, then green)` the red line and the green line; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare, path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P3, P4)`; `## The window reproduced (Item 1)`; `## Failing-first (red, then green)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P3, P4)` ← P2
>
> **Deposits:**
> - `knowledge/mutants/readonly-wal-open.json`
> - `knowledge/mutants/readonly-wal-open.run.txt`
> - `knowledge/development/dev-log-readonly-wal-open-2026-09-11.md`
>
> **Post-conditions:** t1–t6 green beside the 24 status tests; the full suite `N passed, 1 skipped` with no `failed`; the mutation run's last line `MUTATION: 3 killed, 0 survived, 0 error`; two DEV commits; the dev-log's four headings present as full lines with P2's cell whole; `git status --porcelain` empty after the second commit; the live DB never opened by the step.

## STEP 2 — QA (full suite; the window reproduced on a COPY and read through the new opener; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/ro-wal-qa.XXXXXX)`; the live DB is opened once, read-only, for the backup, and never otherwise.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the window on a copy:** `sqlite3 "file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro" ".backup $T/copy.db"` (a backup is a clean WAL file with no sidecars — the stopped state, by construction); then, in-process from the worktree root, `sqlite3.connect("file:$T/copy.db?mode=ro", uri=True).execute("SELECT count(*) FROM plans")` → paste the `OperationalError` (the window), and `lifecycle.connect_readonly("$T/copy.db").execute("SELECT count(*) FROM plans").fetchone()` → paste the count and, BEFORE closing that connection, `ls "$T"` showing `copy.db-shm` created (it is deleted again on close); then `status.query_in_flight("$T/copy.db")` → a list (possibly empty), no raise.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no live lifecycle row (the live DB was opened read-only once, for the backup), no daemon.
> **Item 4 — receipt** `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, nine files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: readonly-wal-open-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["readonly-wal-open-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (PT v4.108 §8).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and pauses for a verdict (PT v4.108 §8).
>
> **Deposits:**
> - `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's three outputs pasted (the window's error, the count with the `-shm` created, the list); the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
