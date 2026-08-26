# bellows — executable: the depositor cluster — `tools/gate_watcher.py` (session-independent, receipt-spawned) + four deposit-discipline surfaces verified (retires ~7 deposit memories at close)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO-approved batch-4 work order, item (2) — "the depositor cluster (one plan: duplicate-check, daemon-side minting, checker re-runs at deposit, shared-append serialization, auto-armed watchers — retires ~6 discipline memories)"; the audit rows L121-122, L130, L134, L149, L152, L159; the Planner's authoring scout (2026-08-26): four of the five features ALREADY SHIPPED — this plan builds the fifth (the auto-armed watcher, audit row L130's named shape: "deposit tooling could arm the watcher automatically") and VERIFIES the four, each with a live instrument.

## Why this exists

Seven memory entries carry deposit discipline the system now enforces or can enforce: the receipt layer refuses duplicate slug+hash deposits; the daemon is the only id minter (`lifecycle.py:255`); the depositor re-runs cycle_check + plan_lint at the deposit path before any claim; the shared-append feedback file went DB-mediated with an idempotency guard. The one gap: the deposit receipt only ATTESTS that a session-local watcher was armed — nothing arms one that survives the session. This plan ships that watcher, wires the receipt tool to spawn it detached, and records one verification pass per already-shipped surface so the memories retire on evidence, not recall.

## What this plan does NOT do

- **No depositor/daemon/gates changes.** The write set is two tools + one test file + logs. No memory writes (sandbox-denied to agents; the Planner retires at close under the 562 gate: `bellows-deposit-once-discipline`, `bellows-deposit-predict-never-mint`, `read-id-sequence-at-deposit`, `last-edit-before-deposit-is-least-reviewed`, `lint-expected-state-is-location-dependent`, `concurrent-sibling-deposits-conflict-on-shared-append-file`, `bellows-watcher-per-deposited-plan`).
- **The watcher never writes the DB** — read-only URI, its log is its only output. It is a reporter, not an actor.

## Numbers discipline

⚠️ **Measured 2026-08-26 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| D1 | evaluate order | `_do_evaluate`: collisions → `_rerun_validation` (called at depositor.py:159; cycle_check must return BAR_MET, plan_lint non-benign FAILs hold, manifest `cycle_check=` cross-checked) → `_check_receipt` (fail-closed) → class | depositor.py:129-199, :471-527 |
| D2 | receipt duplicate refusal | same slug+content_hash in active receipts/ → `ERROR: receipt already exists … duplicate deposit`, exit 1 | tools/deposit_receipt.py (the duplicate-check block) |
| D3 | minting single-writer | `lifecycle.py:255` `UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1` is the ONLY id_sequence writer in the codebase (grep enumeration; the hit itself is the positive control) | `/usr/bin/grep -rnF "id_sequence" *.py tools/ scripts/ tests/` |
| D4 | shared-append mediation | feedback file is DB-mediated: `lifecycle.py:698` `record_prompt_feedback`, `:717` `generate_feedback_md`; the daemon writes/commits it centrally at bellows.py:1681-1722 with the `check_ledger_write_exists`/`record_ledger_write` idempotency pair (old-style agent write detected and skipped at :1681-1682) | read both; targeted tests `tests/test_lifecycle.py -k "Idempotency or ledger"` |
| D5 | receipt watcher wording | receipt field `"watcher": "gate-watcher armed in depositing session"` + an attestation_boundary note — attestation ONLY, nothing spawned | tools/deposit_receipt.py (the receipt dict) |
| D6 | tools/ inventory | 6 entries; `gate_watcher.py` ABSENT; `tests/test_gate_watcher.py` ABSENT | `ls tools/ tests/` |
| D7 | watcher keying | `plans.deposit_placeholder_name` holds the claimable filename (e.g. `diagnostic-verify-then-retire-sweep.md` for id 568); `gate_events.result` ∈ ('pass','fail') with `overridden`; `steps.plan_id` joins | lifecycle.db schema (mode=ro) |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **THE SPLIT-PATH LAW:** `lifecycle.db` and `logs/` are untracked — the watcher resolves them relative to its own installed location at RUNTIME (live checkout), and tests inject `db_path`/log-dir explicitly; `tools/` and `tests/` are tracked and in your worktree.
- ⚠️ **Existing `tests/test_deposit_receipt.py` must stay green** — the receipt modification is ADDITIVE (new fields/behavior behind the existing call shape; the default spawn failure degrades to the attestation-only wording, never blocks the receipt).
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the watcher + receipt wiring + tests + four verification probes)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -d tools && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `test -f tools/gate_watcher.py && echo 1 || echo 0`, (ii) `test -f tests/test_gate_watcher.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task D; (1,1) → Task F commit-check; (0,1) → HALT.
>
> **Task B — write `tools/gate_watcher.py` EXACTLY:**
>
> ```python
> #!/usr/bin/env python3
> """gate_watcher — session-independent watcher for one deposited plan.
>
> Spawned detached by tools/deposit_receipt.py at deposit time (or run by
> hand). Polls lifecycle.db READ-ONLY; appends state transitions and
> un-overridden gate failures to logs/watch/<name>.log; exits on a terminal
> lifecycle state or timeout. The watcher is a REPORTER, never an actor —
> it writes no DB row and touches no plan file.
>
> The deposit receipt attests ARMING; this process is the armed thing. Its
> log is the watcher's own output file: every line records a direct DB read
> (the async-notifications-are-claims law, mechanized — the log IS the
> stable state query).
>
> usage: gate_watcher.py <claimable-name.md> [--timeout-min N] [--interval-sec N]
>        gate_watcher.py --status <claimable-name.md>
>
> exit: 0 terminal state reached (or --status printed); 2 usage; 3 timeout.
> """
> import argparse
> import os
> import sqlite3
> import sys
> import time
> from datetime import datetime
>
> _HERE = os.path.dirname(os.path.abspath(__file__))
> _ROOT = os.path.dirname(_HERE)
> _DB = os.path.join(_ROOT, "lifecycle.db")
> _WATCH_DIR = os.path.join(_ROOT, "logs", "watch")
>
> TERMINAL = {"closed", "halted", "abandoned"}
>
>
> def read_state(name, db_path=None):
>     """One read-only DB query -> state dict, or None if the DB is unreadable."""
>     path = db_path or _DB
>     try:
>         conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
>     except sqlite3.Error:
>         return None
>     try:
>         row = conn.execute(
>             "SELECT id, lifecycle_state FROM plans "
>             "WHERE deposit_placeholder_name = ? ORDER BY id DESC LIMIT 1",
>             (name,),
>         ).fetchone()
>         if row is None:
>             return {"phase": "pre-claim"}
>         plan_id, state = row
>         fails = conn.execute(
>             "SELECT g.gate_name FROM gate_events g "
>             "JOIN steps s ON g.step_id = s.id "
>             "WHERE s.plan_id = ? AND g.result = 'fail' AND g.overridden = 0",
>             (plan_id,),
>         ).fetchall()
>         return {
>             "phase": state,
>             "plan_id": plan_id,
>             "gate_failures": sorted(f[0] for f in fails),
>         }
>     except sqlite3.Error:
>         return None
>     finally:
>         conn.close()
>
>
> def judge_transition(prev, cur):
>     """(prev_state, cur_state) -> log line, or None when nothing changed.
>
>     A db-unreadable poll is REPORTED (transient or not, silence would be
>     indistinguishable from 'no change' — silence is not success).
>     """
>     if cur is None:
>         return "WATCH: db-unreadable (will retry)"
>     if prev is not None and prev == cur:
>         return None
>     gf = cur.get("gate_failures") or []
>     tail = " gate_failures=" + ",".join(gf) if gf else ""
>     pid_part = f" id={cur['plan_id']}" if "plan_id" in cur else ""
>     return f"WATCH: {cur['phase']}{pid_part}{tail}"
>
>
> def _log_line(log_path, line):
>     stamped = f"{datetime.now().isoformat()} {line}\n"
>     with open(log_path, "a") as f:
>         f.write(stamped)
>
>
> def main(argv):
>     ap = argparse.ArgumentParser()
>     ap.add_argument("name")
>     ap.add_argument("--timeout-min", type=int, default=120)
>     ap.add_argument("--interval-sec", type=int, default=15)
>     ap.add_argument("--status", action="store_true")
>     ap.add_argument("--db-path", default=None,
>                     help="lifecycle.db path (default: beside this tool's bellows root; "
>                          "worktrees have no lifecycle.db — pass the live checkout's)")
>     try:
>         args = ap.parse_args(argv[1:])
>     except SystemExit:
>         return 2
>
>     if args.status:
>         cur = read_state(args.name, db_path=args.db_path)
>         line = judge_transition(None, cur) or "WATCH: (no state)"
>         print(line)
>         return 0
>
>     os.makedirs(_WATCH_DIR, exist_ok=True)
>     log_path = os.path.join(_WATCH_DIR, args.name + ".log")
>     _log_line(log_path, f"WATCH: armed for {args.name} "
>                         f"(timeout {args.timeout_min}m, interval {args.interval_sec}s)")
>     deadline = time.monotonic() + args.timeout_min * 60
>     prev = "UNSET"
>     while time.monotonic() < deadline:
>         cur = read_state(args.name, db_path=args.db_path)
>         line = judge_transition(None if prev == "UNSET" else prev, cur)
>         if line:
>             _log_line(log_path, line)
>         if cur is not None:
>             prev = cur
>             if cur.get("phase") in TERMINAL:
>                 _log_line(log_path, f"WATCH: terminal — {cur['phase']}; exiting")
>                 return 0
>         time.sleep(args.interval_sec)
>     _log_line(log_path, "WATCH: timeout; exiting")
>     return 3
>
>
> if __name__ == "__main__":
>     sys.exit(main(sys.argv))
> ```
>
> Post-probes: `/usr/bin/grep -cF "mode=ro" tools/gate_watcher.py` == 1; `/usr/bin/grep -cF "overridden = 0" tools/gate_watcher.py` == 1; `chmod +x tools/gate_watcher.py`.
>
> **Task C — wire `tools/deposit_receipt.py` (ADDITIVE).** Three edits, each anchored on text you first assert unique with `/usr/bin/grep -cF` == 1:
> 1. Add `import subprocess` beside the existing imports.
> 2. Add a module-level function (after `_is_in_watched_tree`):
>
> ```python
> def _spawn_watcher(claimable_name):
>     """Spawn the session-independent gate watcher, detached. Returns pid or None."""
>     watcher = os.path.join(_HERE, "gate_watcher.py")
>     try:
>         p = subprocess.Popen(
>             [sys.executable, watcher, claimable_name],
>             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
>             start_new_session=True,
>         )
>         return p.pid
>     except Exception:
>         return None
> ```
>
> 3. In `write_receipt`, add a keyword arg `spawn_watcher=True` and, immediately BEFORE the `receipt = {` dict build, insert:
>
> ```python
>     watcher_note = "gate-watcher armed in depositing session"
>     if spawn_watcher:
>         pid = _spawn_watcher(slug + ".md")
>         if pid is not None:
>             watcher_note = f"gate_watcher.py spawned detached (pid {pid}); log: logs/watch/{slug}.md.log"
> ```
>
>    and change the receipt dict's `"watcher":` value to `watcher_note`. In `__main__`, add `--no-spawn` (`action="store_true"`) passed through as `spawn_watcher=not args.no_spawn`. A failed spawn degrades to the old attestation wording — the receipt is NEVER blocked by the watcher (fail-open on the reporter, fail-closed on the attestation, stated).
>
> Post-probes: `/usr/bin/grep -cF "_spawn_watcher" tools/deposit_receipt.py` == 3 (def + call + nothing else); `/usr/bin/grep -cF "no-spawn" tools/deposit_receipt.py` == 1; existing tests still green: `python3 -m pytest tests/test_deposit_receipt.py -q 2>&1 | tail -2` → 0 failed (record the count).
>
> **Task D — tests `tests/test_gate_watcher.py`** (new): NINE tests, all against a tmp lifecycle DB built with `lifecycle.init_lifecycle_db(db_path)` + direct row inserts (provenance comments naming D7's schema read):
> 1. `read_state` with no plans row → `{"phase": "pre-claim"}`.
> 2. `read_state` with an in_progress row keyed by `deposit_placeholder_name` → phase + plan_id, empty gate_failures.
> 3. `read_state` with a step + one `result='fail', overridden=0` gate_event → that gate named.
> 4. `read_state` with the failure overridden (`overridden=1`) → gate_failures empty (the override is honored).
> 5. `read_state` on a nonexistent db path → None (fail-visible, not a crash).
> 6. `judge_transition(None-prev, cur)` → a line; same-state → None; changed gate list → a line (three asserts, one test).
> 7. `judge_transition(prev, None)` → the db-unreadable line (silence-is-not-success arm).
> 8. `--status` one-shot via `main()` against the tmp DB — passed with `--db-path <tmp db>` (no monkeypatching) — prints a WATCH line, exit 0.
> 9. `deposit_receipt.write_receipt(..., spawn_watcher=False)` (tmp plan file, tmp receipts dir via monkeypatch) → receipt written with the attestation-only wording; and with `spawn_watcher=True` + `_spawn_watcher` monkeypatched to return 4242 → the wording carries `pid 4242`. (No real process spawned in tests.)
>
> Targeted run: `python3 -m pytest tests/test_gate_watcher.py -q 2>&1 | tail -2` → 0 failed (record counts; supersede with derivation).
>
> **Task E — the four verification probes (recorded verbatim in the dev log; these license the retirements):**
> 1. **Checker re-runs at deposit (D1):** cite `_rerun_validation`'s call at depositor.py:159 with the two lines around it; paste the function's hold arms (cycle_check≠BAR_MET, non-benign lint FAILs, manifest mismatch) with line numbers.
> 2. **Duplicate-check (D2):** live probe with cleanup — `cp` any Done plan to `/tmp/dup_probe_569.md`; run `python3 tools/deposit_receipt.py /tmp/dup_probe_569.md probe-569 --no-spawn` TWICE; first → `Receipt written`, second → `ERROR: receipt already exists … duplicate deposit`, exit 1 (paste both, with `$?`); then `rm receipts/receipt-dup_probe_569-*.json` and prove cleanup with `ls receipts/ | /usr/bin/grep -cF dup_probe_569; true` → 0.
> 3. **Minting single-writer (D3):** run the D3 grep over `*.py tools/ scripts/ tests/`; paste every hit; assert exactly ONE writer line (`lifecycle.py:255`) — the CREATE/INSERT-seed lines at :30/:36 and read-only references are enumerated and classified, none a second minting path.
> 4. **Shared-append mediation (D4):** cite bellows.py:1681-1722 (the old-style detection, the idempotency check, the central regenerate+commit); run `python3 -m pytest tests/test_lifecycle.py -k "Idempotency or ledger" -q 2>&1 | tail -2` → 0 failed (record the selected count).
>
> **Task F — dev log + commit.** `knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md` (Task B/C post-probe raws, Task D targeted raw, Task E's four probe records verbatim). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add tools/gate_watcher.py tools/deposit_receipt.py tests/test_gate_watcher.py knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] depositor-cluster(depositor-cluster-2026-08-26): session-independent gate watcher, receipt-spawned; four deposit surfaces verified" -- tools/gate_watcher.py tools/deposit_receipt.py tests/test_gate_watcher.py knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `tools/gate_watcher.py`
> - `tools/deposit_receipt.py`
> - `tests/test_gate_watcher.py`
> - `knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md`
>
> **Scope:**
> - `tools/gate_watcher.py`
> - `tools/deposit_receipt.py`
> - `tests/test_gate_watcher.py`
> - `knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + live behavior)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/depositor-cluster-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs the pre-change baseline you measure first).
> **Item 2 — live behavior (three runs, full tails pasted):**
> 1. `python3 tools/gate_watcher.py --status executable-depositor-cluster.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db` → a `WATCH:` line naming the LIVE phase of THIS plan with its minted id (in_progress at QA time — the worktree-committed tool reading the live DB via the split-path law; capture `$?` = 0).
> 2. `python3 tools/gate_watcher.py --status no-such-plan.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db` → `WATCH: pre-claim`, exit 0 (the honest not-yet-claimed answer).
> 3. The Task-E duplicate probe's cleanup re-verified IN THE WORKTREE's receipts dir (the dir the probe actually wrote — checking the live root instead would pass vacuously): `cd "$(git rev-parse --show-toplevel)" && ls receipts/ | /usr/bin/grep -cF dup_probe_569; true` → 0, and `git status --porcelain -- receipts/` → empty.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/depositor-cluster-2026-08-26/qa-receipt.md`: numstat 4 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/depositor-cluster-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one small read-only tool + an additive wiring edit + tests; the four verification surfaces read from code at walk 0.

**Walk register:** `bellows/knowledge/research/walk-register-depositor-cluster-2026-08-26.md`

**Walks:** walk 0 pinned; **walks 1–3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the build-one-verify-four shape held; no direction-class finding.
- Weak spots:          w1 1 folded (instruction 1 / record 0) — the worktree-DB reachability hole (--db-path); w2 dry; w3 dry
- Destruction:         w1 dry; w2 dry; w3 dry
- Vulnerabilities:     w1 dry; w2 1 folded (instruction 1 / record 0) — QA 2.3's vacuous-dir ambiguity pinned; w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — T1 additive tooling (one read-only reporter + an additive receipt edit); no money path, no destructive step; the E-family/563 precedent.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block (run_check cycle/lint/register, all branched-on).
**Closing:** **walk 3 met the bar — all five lenses dry, instruction 0 / record 0, no restructuring fold.** Instruction series **1 → 1 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/gate_watcher.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/depositor.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_lifecycle.py
writes: tools/gate_watcher.py, tools/deposit_receipt.py, tests/test_gate_watcher.py, knowledge/dev-logs/depositor-cluster-dev-2026-08-26.md, knowledge/qa/evidence/depositor-cluster-2026-08-26/pytest_full.txt, knowledge/qa/evidence/depositor-cluster-2026-08-26/probes-raw.txt, knowledge/qa/evidence/depositor-cluster-2026-08-26/qa-receipt.md
open_forks: the seven memory retirements = the Planner's close-time act (sandbox split, stated); the plan_lint cluster (batch item 3) carries R-3/R-5's routed residues; whether the daemon should ALSO spawn a watcher at claim (belt-and-braces) — not decided here
walks: 3
yields: 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x2
coherence: N/A
