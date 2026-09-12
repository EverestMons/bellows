# bellows — THE READ-ONLY OPENER PROBES BEFORE IT RETURNS: `lifecycle.connect_readonly` runs one read (`PRAGMA schema_version`) on the `mode=ro` connection inside its try, so a SQLITE_CANTOPEN that SQLite 3.43.2 defers to the first query is caught like the one raised at connect — the read-only connection closed, the plain `query_only` connection returned; three tests with a stand-in connection that fails on its first query pin both forms on every SQLite (thread 299)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one function in `lifecycle.py`, three tests in one file, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — `lifecycle.py` is imported by most of the suite; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 299

**auto_close:** false

**Post-close:** daemon restart owed on BOTH machines — `lifecycle.py` is daemon-loaded (the depositor's in-flight resolution and the gate watcher read through the opener); `bellows.py restart` from each checkout, the Air over the tailnet. No doctrine. Then `tuyere.threads done 299 --commit bellows:<the DEV commit that touched lifecycle.py>` (a defect thread's `done` requires the commit, thread 184; thread 300's question — which commit a `done` names — is open, so name the DEV commit).

**Depends on:** thread 299 (found at the Planner's (b) read of #100083 STEP 2, 2026-09-11, from the QA receipt's own note) and #100083 (the opener, thread 289, Done 2026-09-11). Clone origin by kind and layout: `Done/executable-100083.md` (the plan that shipped the helper: the deterministic `sqlite3.connect` wrapper of t1, the version-gated live test, the two-commit DEV with the manifest riding the first commit, failing-first, the mutation run redirected into a deposit, the full-suite QA with a measurement on a COPY of the live DB under the system interpreter).

**Tier computed (§1):** **T1** — T-1 fires (the lifecycle module every reader and the daemon import); T-6 does not (no doctrine); T-2 does not (no live write; every test builds its own DB under `tmp_path`; the QA measures on a backup copy).

## CEO Context

#100083's opener catches the refusal only where `sqlite3.connect` raises it. Its own QA found the other form: on a backup copy of the live DB with the sidecars removed, under the mini's system `python3` (SQLite 3.43.2), the `mode=ro` connect sometimes RETURNS a connection and the same "unable to open database file" arrives at the first query — past the opener's `try`, so the caller raises anyway. The readers the opener exists for run under the venv since #100083 corrected the skills, where SQLite 3.53.4 reads, so today the residue bites only a bare `python3 status.py`; but a reader that exists to report the stopped state should not depend on which moment SQLite chooses to refuse. The fix is one read inside the `try` — `PRAGMA schema_version`, which makes SQLite open the file and its WAL index and writes nothing — and a close of the read-only connection before the fallback. The tests cannot patch a real connection's `execute` (it is a C method), so the connect wrapper returns a small stand-in object whose first `execute` raises; the stand-in records whether it was closed.

## What this changes

1. **`lifecycle.py`** — `connect_readonly` (:452) in its existing shape: `ro = None` before the `try`; inside it, `ro = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=timeout)`, then `ro.execute("PRAGMA schema_version").fetchone()`, then `return ro`; the `except sqlite3.OperationalError as exc:` arm first closes `ro` when it is not `None` (a nested `try`/`except Exception: pass` around `ro.close()`, so a failing close never masks the refusal), then applies the existing test unchanged — re-raise unless `"unable to open database file"` is in the message and the file exists; the fallback (a plain connection, `PRAGMA query_only = 1`, return) unchanged. The docstring gains one sentence: the refusal is caught whether SQLite raises it at open or at the first read (thread 299).
2. **`tests/test_lifecycle_readonly.py`** — a module-level stand-in `class _DeferredRefusal` (`__init__(self, message="unable to open database file")` storing the message and `self.closed = False`; `execute(self, *a, **kw)` raises `sqlite3.OperationalError(self.message)`; `close(self)` sets `self.closed = True`) and three tests in `TestConnectReadonly`, each with t1's wrapper shape (`real_connect = sqlite3.connect`, `monkeypatch.setattr(sqlite3, "connect", wrapper)`, the calls recorded): (t7) `test_fallback_on_deferred_refusal` — for a `file:` argument the wrapper returns a `_DeferredRefusal()` and keeps it; after `conn = lifecycle.connect_readonly(db_path)` on a DB built by `init_lifecycle_db`: the stand-in's `closed` is `True`, two calls were made (the first `file:`, the second not), `conn.execute("SELECT count(*) FROM plans").fetchone() == (0,)` and `conn.execute("PRAGMA query_only").fetchone() == (1,)`; (t8) `test_deferred_other_error_propagates` — the stand-in carries `"database is locked"`: `connect_readonly` raises `sqlite3.OperationalError` matching `locked`, the stand-in is closed, and ONE call was made (no fallback); (t9) `test_status_reads_through_deferred_refusal` — t7's wrapper, then `status.query_in_flight(db_path)` returns a list (the reader thread 299 is about). t1–t6 and the hooks test unchanged; t2 (a writer open, exactly one `file:` call) still holds, because the probe runs on the real read-only connection and succeeds.
3. **`knowledge/mutants/readonly-probe.json`** — four mutants, `target` `lifecycle.py`, each `expect_fail` a class-qualified node id: (m1) the probe line removed → t7 (the stand-in is returned and the test's first query raises); (m2) the `ro.close()` block removed → t7 (the `closed` assertion); (m3) the message test dropped, so every `OperationalError` falls back → t8 (the locked error falls back instead of propagating); (m4) the close moved below the message test, so it runs only on the fallback path → t8 (the locked stand-in is left open).
4. **Not changed:** the fallback's shape; the four callers (`status.py` :231/:251, `depositor.py` :564, `tools/gate_watcher.py` :68); t1–t6; the skills; every gate.

## Why this exists

A reader that reports the stopped state was fixed for one of the two ways SQLite 3.43.2 refuses it; the second way was found by the fix's own QA and recorded, not guessed. One read inside the guard closes it, and a stand-in pins it on the SQLite that never shows it.

## What this does NOT do

- Change the interpreter the readers run under, or add `immutable=1` (stale pages — the parent lesson's warning).
- Reproduce the deferred form deterministically on a real file: it appears "sometimes" on 3.43.2; the QA measures how often on copies and records it, and the stand-in is the deterministic proof.
- Import `lifecycle` from a scratch script anywhere in the plan: the QA's live measurement uses `sqlite3` alone, on copies.

## MUST-PRESERVE

- ⛔ **The probe is a read.** `PRAGMA schema_version` (or a `SELECT` over `sqlite_master`), never `PRAGMA journal_mode` and never a statement that writes.
- ⛔ **The read-only connection is closed before the fallback and before a re-raise** — no leaked handle on either path (t7, t8).
- ⛔ **The message test stays.** Only "unable to open database file" with the file present falls back; every other `OperationalError` propagates (t8).
- ⛔ **No live DB write, and `lifecycle` is never imported outside pytest.** Every test builds its DB under `tmp_path` (`conftest.isolate_lifecycle_db`); the QA's live measurement runs `sqlite3` alone on backup copies under `$T`.
- ⛔ **Every `expect_fail` is a class-qualified node id**, and the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict rather than committing.

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `36901bd`, governance `a4e49eb4`, daemon pid 3106 under the agent)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the opener and its callers | `lifecycle.py:452` `def connect_readonly(db_path, timeout=5.0):` — `try: return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=timeout)`; `except sqlite3.OperationalError as exc: if "unable to open database file" not in str(exc) or not os.path.exists(db_path): raise`; then `conn = sqlite3.connect(db_path, timeout=timeout)`, `conn.execute("PRAGMA query_only = 1")`, `return conn`; callers `status.py:231` and `:251` (`conn = connect_readonly(db_path)`), `depositor.py:564` (`conn = lifecycle.connect_readonly(self._db_path)`), `tools/gate_watcher.py:68` (`conn = connect_readonly(path, timeout=5)`) | `sed -n 448,474p lifecycle.py`; `grep -nF 'connect_readonly(' status.py depositor.py tools/gate_watcher.py` |
| P2 | ⛔ the measurement the thread rests on | #100083's QA receipt `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md`, its Item 2: a `.backup` of the live DB as `copy.db`, then `rm copy.db-shm copy.db-wal && sync && sleep 2`, then under `/usr/bin/python3` (SQLite 3.43.2) `sqlite3.connect("file:<copy>?mode=ro", uri=True).execute("SELECT count(*) FROM plans")` → `OperationalError: unable to open database file`; its note: the `mode=ro` connect "sometimes returns a Connection object that defers the CANTOPEN to `execute()` (the error text is identical)"; #100083's P2 (a tmp DB after `init_lifecycle_db`, sidecars removed, the same interpreter) raised at connect | the receipt, `## Item 2` and the note after it |
| P3 | ⛔ the tests to clone | `tests/test_lifecycle_readonly.py`, `class TestConnectReadonly`: t1 `test_fallback_on_file_uri_error` (the wrapper: `real_connect = sqlite3.connect`; raise `OperationalError("unable to open database file")` for `file:` arguments; `monkeypatch.setattr(sqlite3, "connect", wrapper)`), t1b `test_fallback_live_wal_window` (`skipif sqlite3.sqlite_version_info >= (3, 44)`), t2 `test_uri_reads_when_writer_open` (exactly one `file:` call), t3 `test_missing_file_propagates`, t4 `test_fallback_connection_is_readonly` (an INSERT raises `readonly`), t5 `test_resolve_in_flight_writes_returns_list`, t6 `test_no_mode_ro_outside_lifecycle`, `test_no_python3_status_in_hooks`; the module preamble loads the worktree's `status.py` by path (`importlib.util.spec_from_file_location`) because the full suite caches the main repo's | the file's first 160 lines |
| P4 | ⛔ the mutation tool and the manifest form | `tools/mutation_check.py <manifest> [--repo-root] [--keep-sandbox] [--python] [--timeout]`; `knowledge/mutants/readonly-wal-open.json` — `target: lifecycle.py`, three mutants (`fallback-removed`, `mode-ro-removed`, `query-only-dropped`), each `anchor` an exact multi-line string of the function and `expect_fail` a class-qualified node id; a clean run's last line `MUTATION: <n> killed, 0 survived, 0 error` | the file; `--help` |
| P5 | the interpreters | the bellows venv: Python 3.12.14, SQLite 3.53.4 (a `mode=ro` open of a writer-less WAL database reads, so the probe succeeds); the mini's `/usr/bin/python3`: 3.9.6, SQLite 3.43.2 (refuses, at connect or at the first query); the Air's `/usr/bin/python3`: SQLite 3.51.0 (reads) — the Air row is Planner-measured over the tailnet, not re-derived by the step | `<interpreter> -c "import sqlite3, sys; print(sys.version.split()[0], sqlite3.sqlite_version)"` |
| P6 | in-flight; class; interpreter | queue empty at drafting; the tools plan (thread 302) drafted beside this one and deposited first; writes: `lifecycle.py`, the test file, the manifest, the run file, the dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases; the bellows venv for everything but the QA's measurement, which runs `/usr/bin/python3` with `sqlite3` alone | `.venv/bin/python status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-readonly-probe-2026-09-11.md
**Walks:** walk 0 pinned (P1–P6 measured on bellows `36901bd`; clone-diff against `Done/executable-100083.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every walk.

- Weak spots:          w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 0 / record 1
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:   w1 dry; w2 dry
- ACID:                 w1 dry; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 299's fix. Two walks: 3 → 0 (walk 1 named t7's red reason as the run prints it, replaced a mutant no manifest could carry with the close-below-the-message-test mutant that t8 kills, and made the QA measure the opener's own probe statement rather than a different first query; walk 2 removed a drafting placeholder from the record and was dry on every lens). Every lens commit through `lens_commit.py`, the tool run bare, its exit read; the close through `close_cycle.py`. Deposit via `ready-` after thread 302's plan closes (P6); HOLDS on class shop-infra, the CEO releases; after the merge: both restarts, `threads done 299 --commit bellows:<the DEV sha>`.

## Cycle Manifest
tier: T1
target: lifecycle.py
class: shop-infra
reads: lifecycle.py, status.py, depositor.py, tools/gate_watcher.py, tests/test_lifecycle_readonly.py, tests/conftest.py, tools/mutation_check.py, tools/check_deposit.py, knowledge/decisions/Done/executable-100083.md, knowledge/mutants/readonly-wal-open.json, knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md
writes: lifecycle.py, tests/test_lifecycle_readonly.py, knowledge/mutants/readonly-probe.json, knowledge/mutants/readonly-probe.run.txt, knowledge/development/dev-log-readonly-probe-2026-09-11.md, knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md, knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt
mutants: knowledge/mutants/readonly-probe.json
open_forks: 1. a status reader that reports STOPPED on any refusal instead of falling back (the parent lesson's second option), if a third form of the refusal is ever measured; 2. the readers' interpreter asserted at their entry (a `sys.executable` check) so a bare `python3 status.py` warns instead of relying on the opener
walks: 2
yields: 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:13
coherence: 2/2 body walks named in the register (4 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-readonly-probe.md.foldcheck.json

---

## STEP 1 — DEV (one probe and one close in the opener, three tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim, `bellows.py stop|restart`; never import `lifecycle` outside pytest; the live `lifecycle.db` is never opened by this step; `T=$(mktemp -d /tmp/ro-probe.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `lifecycle.py`
> - `tests/test_lifecycle_readonly.py`
> - `knowledge/mutants/readonly-probe.json`
> - `knowledge/mutants/readonly-probe.run.txt`
> - `knowledge/development/dev-log-readonly-probe-2026-09-11.md`
>
> **Item 1 — re-derive P1 and P3 and HALT on a mechanism mismatch** (a line-number drift is not a mismatch; a read already inside the opener's `try`, a close of the read-only connection already present, or a `connect_readonly` that no longer exists, IS one: someone fixed it first). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing tests FIRST:** *What this changes* 2 — `_DeferredRefusal` and t7–t9 (red, each for its own reason: t7 fails on its first assertion — the stand-in was returned unprobed and never closed (`assert False is True` on its `closed`); t8 `DID NOT RAISE`, because the stand-in is returned unprobed; t9 raises inside `status.query_in_flight`). Run the file; paste the red summary line and the three reasons.
> **Item 3 — the edit** as *What this changes* 1; then the file green (t1–t9 with t1b's skip), then the FULL suite green (`N passed, 2 skipped` — `test_gate_watcher`'s live-DB skip and t1b's version gate).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-readonly-probe-2026-09-11.md knowledge/mutants/readonly-probe.run.txt && git add lifecycle.py tests/test_lifecycle_readonly.py knowledge/mutants/readonly-probe.json && git commit -F <msg-file> -- lifecycle.py tests/test_lifecycle_readonly.py knowledge/mutants/readonly-probe.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 299`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/readonly-probe.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/readonly-probe.json > knowledge/mutants/readonly-probe.run.txt 2>&1`; the last line must read `MUTATION: 4 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-readonly-probe-2026-09-11.md` under the four headings declared below; `## Pins re-derived (P1, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `raised at connect`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line with its three reasons and the green line; under `## The two forms caught (t7, t8)` the two tests' assertions quoted with their outcomes; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and dev-log now exist), path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P3)`; `## Failing-first (red, then green)`; `## The two forms caught (t7, t8)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P3)` ← P2
>
> **Deposits:**
> - `knowledge/mutants/readonly-probe.json`
> - `knowledge/mutants/readonly-probe.run.txt`
> - `knowledge/development/dev-log-readonly-probe-2026-09-11.md`
>
> **Post-conditions:** t1–t9 green with t1b's skip; the full suite `N passed, 2 skipped` with no `failed`; the mutation run's last line `MUTATION: 4 killed, 0 survived, 0 error`; two DEV commits — the first carrying the three files, the second the run file and the dev-log; the dev-log's four headings present as full lines with P2's cell whole; `git status --porcelain` empty after the second commit; the opener's probe is a read (`grep -cF 'PRAGMA schema_version' lifecycle.py` is 1 and no new `execute(` in the function names a write).

## STEP 2 — QA (full suite; how often 3.43.2 defers, measured on copies with `sqlite3` alone; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/ro-probe-qa.XXXXXX)`; the live DB is opened once, read-only, for the backup, and never otherwise; `lifecycle` is not imported by this step.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the two forms, measured on copies:** `sqlite3 "file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro" ".backup $T/base.db"` (the backup API — the one line in this plan that opens the live DB); then FIVE attempts, each on a fresh copy — `cp "$T/base.db" "$T/c<i>.db"`, remove any `-shm`/`-wal` beside it, `sync` — each run by `/usr/bin/python3` with `sqlite3` and `os` alone (no bellows import): open with `sqlite3.connect("file:$T/c<i>.db?mode=ro", uri=True)` inside one `try`, then `execute("PRAGMA schema_version").fetchone()` — the opener's own probe statement — inside a second, and on success `execute("SELECT count(*) FROM plans")`; print one line per attempt — `raised at connect`, `raised at first query`, or `read <count>` — and the interpreter's `sqlite3.sqlite_version`. Paste the five lines and the two counts beside P2's note. Any mix is a result, not a failure: the deterministic proof is t7–t9; this item records how often the deferred form appears on this machine.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no live lifecycle row, no daemon act.
> **Item 4 — receipt** `knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: readonly-probe-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["readonly-probe-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/readonly-probe-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/readonly-probe-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N ≥ the DEV's count and no `failed`; Item 2's five attempt lines and two counts pasted beside P2's note; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files; the live DB opened once, read-only, for the backup (`grep -cF 'lifecycle.db' <receipt>` counts that one command and nothing else).
