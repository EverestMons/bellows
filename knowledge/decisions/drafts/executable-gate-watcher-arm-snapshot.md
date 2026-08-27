# bellows — executable: gate_watcher arm-time snapshot — a pause already present at arming is logged as PRE-EXISTING, not as a fresh transition (thread 20)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** tuyere thread 20 (opened 2026-08-27 from the exec-571 close); exec-571's shipped pause detection (`tools/gate_watcher.py`, closed 2026-08-27); LESSONS.md 2026-08-26 "a live canary must be fired in the STATE the tool exists to discriminate".

## Why this exists

A watcher armed while a verdict-request file is still on disk reports that pause as if it had just observed it. The file lingers between the Planner issuing a verdict and the daemon consuming it (seconds), so a watcher started in that window logs a pause that is already resolved. Measured live 2026-08-27 on the shop's shell watcher, which exits on pause and therefore terminated immediately on the stale file; the arm-time snapshot guard fixed it and produced an audit line (`arm-time pending ignored: verdict-request-570-step-1.md`, then `PAUSED … NEW verdict-request: verdict-request-570-step-2.md`).

⚠️ **Scope, stated honestly and NARROWER than thread 20's opening text** (which said "the same race on any re-arm" without pricing the consequence — corrected here by the Planner, per the price-inherited-severity-labels law; the thread text is corrected at close):
- The **shipped spawn path is NOT affected.** `deposit_receipt._spawn_watcher` (`tools/deposit_receipt.py:55-63`) starts the watcher at DEPOSIT, when no verdict-request for that plan can exist, and the loop's 120m default spans the whole plan.
- The loop **never exits on a pause** — `main` returns only on a TERMINAL phase (`tools/gate_watcher.py`, the `if cur.get("phase") in TERMINAL` arm) or timeout. So this defect can NOT cause a false termination or a missed pause.
- What it CAN do: a **hand-run** mid-plan (the docstring's documented "or run by hand") writes a first log line asserting a pause that was already resolved, then a phantom resume line when the daemon consumes the file. The damage is to the watcher's OWN RECORD — the log is the artifact the async-notifications-are-claims law points consumers at, so a phantom pause→resume cycle in it is a real honesty defect, and a small one.

## What this plan does NOT do

- **No change to `read_state` and no change to `--status` behavior.** Both must keep reporting the TRUE instantaneous state: if a request file is present, the plan IS awaiting a verdict at that instant and `--status` must say so. The arming semantics are a POLL-LOOP concern and belong only there.
- **No change to the exit contract** (terminal → 0, timeout → 3, usage → 2) and no new CLI argument.
- **No memory writes** (sandbox-denied to agents; the Planner closes thread 20 and corrects its scope text at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| A1 | loop exit arms | `main` returns 0 ONLY under `if cur.get("phase") in TERMINAL`; returns 3 after the `while` on timeout; no pause arm exists | read `tools/gate_watcher.py` `main` |
| A2 | spawn timing | `deposit_receipt._spawn_watcher` at `tools/deposit_receipt.py:55-63`, called at `:119` during receipt writing — i.e. at deposit, pre-claim | read both sites |
| A3 | first-poll framing | `prev = "UNSET"`; the first poll calls `judge_transition(None, cur)`, so ANY phase renders a line — including a stale `awaiting-verdict` | the `prev == "UNSET"` ternary in `main` |
| A4 | pause phase shape | `read_state` returns `{"phase": "awaiting-verdict", "plan_id", "gate_failures", "pending": [names]}`; `pending` ABSENT on every non-pause phase | read `read_state` |
| A5 | baselines | `tests/test_gate_watcher.py` collects **16**; full suite **1582 passed** (exec-570 QA) | `pytest … --collect-only`; the 570 evidence `.txt` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **THE SPLIT-PATH LAW:** `lifecycle.db`, `verdicts/`, `logs/` are untracked — resolved at RUNTIME from the tool's own location; tests inject paths explicitly.
- ⚠️ **`read_state` and `judge_transition` keep their current signatures and outputs** — all 16 existing tests stay green UNMODIFIED. The change lives in `main` only.
- ⚠️ **`--status` output is unchanged for every state**, pause included (assert with a test).
- ⚠️ **A genuine LATER pause must still be reported** after an armed-over one clears — the snapshot is cleared when the pending set empties, or the guard would swallow every subsequent pause. This is the failure mode that makes the guard worse than the bug; it gets its own test.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the guard + constructed-state tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/gate_watcher.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "pre-existing" tools/gate_watcher.py; true` → 0 = full run; ≥1 = resume at Task C.
>
> **Task B — edit `tools/gate_watcher.py`** (anchored edits in `main` ONLY; each anchor asserted unique before editing):
>
> 1. **Extract the loop body's decision into a testable pure helper** placed directly above `main`:
>    ```python
>    def judge_watch_line(prev, cur, arm_pending):
>        """Loop-only framing: (line, new_arm_pending).
>
>        A pause whose pending set is exactly the one present when this watcher
>        armed is PRE-EXISTING — already resolved and awaiting daemon cleanup —
>        so it is reported as armed-over, never as a freshly observed pause.
>        The snapshot clears as soon as the pending set empties, so the NEXT
>        genuine pause reports normally.
>        """
>    ```
>    Behavior, in this order:
>    - `cur is None` (db-unreadable) → `(judge_transition(prev, cur), arm_pending)` — the snapshot survives an unreadable poll UNCHANGED. Clearing it there would let the next readable poll re-report the armed-over pause as new.
>    - `cur` is a dict WITHOUT `pending` → `(judge_transition(prev, cur), None)` — snapshot cleared, the plan is no longer paused.
>    - `cur` is a dict WITH `pending` and `arm_pending is not None and set(cur["pending"]) == arm_pending` → armed-over: on the first poll (`prev is None`) the line is `f"WATCH: armed over pre-existing verdict-request: {','.join(cur['pending'])} (already resolved or awaiting daemon cleanup; not a new pause)"`, on later polls `None`; snapshot returned UNCHANGED.
>    - `cur` is a dict WITH `pending` otherwise (no snapshot, or a DIFFERENT set) → `(judge_transition(prev, cur), arm_pending)` — a genuine pause, reported normally.
>
>    ⚠️ The helper must NOT compare `set(...)` against a `None` snapshot (a `set() == None` test is False and would work by accident); branch on `arm_pending is not None` explicitly so the intent is readable and the empty-snapshot case cannot drift.
> 2. **Seed the snapshot in `main` from the first READABLE poll, not from the first iteration.** The loop's existing first read may return `None` (db-unreadable), and seeding from that would set the snapshot to `None` permanently, silently disabling the guard. Use an explicit `armed = False` flag: on each iteration, if `not armed and cur is not None`, set `arm_pending = set(cur["pending"]) if cur.get("pending") else None` and `armed = True` BEFORE computing the line; thereafter thread `arm_pending` through `judge_watch_line`, reassigning it from the returned value. `prev` bookkeeping is unchanged, so the first readable poll still passes `prev=None` into the helper and earns the armed-over line.
> 3. Replace the loop's `line = judge_transition(...)` call with the `judge_watch_line` call. The TERMINAL exit arm, the timeout arm, the `prev` bookkeeping, and `_log_line` are UNTOUCHED.
>
> **Task C — extend `tests/test_gate_watcher.py`** with a `TestArmTimeSnapshot` class (pure-function tests against `judge_watch_line`; no sleeping, no poll loop):
> 1. `test_pre_existing_pause_reported_as_armed_over` — `prev=None`, paused `cur`, `arm_pending={that file}` → line contains `armed over pre-existing` and does NOT contain `awaiting-verdict`.
> 2. `test_pre_existing_pause_silent_on_later_polls` — same but `prev=cur` → line is `None`.
> 3. `test_new_pause_after_snapshot_cleared_reports_normally` — the guard's own failure mode: paused `cur` with a DIFFERENT file, `arm_pending=None` → a normal `WATCH: awaiting-verdict … pending=…` line.
> 4. `test_snapshot_cleared_when_pending_empties` — `cur` without `pending`, `arm_pending={old}` → returned snapshot is `None`.
> 5. `test_different_pending_set_is_a_new_pause` — `arm_pending={step-1}`, `cur` pending `{step-2}` → normal awaiting-verdict line (the measured 570 case).
> 6. `test_arm_pending_none_is_transparent` — `arm_pending=None` on every non-pause phase → identical to `judge_transition`'s own output (the transparency control).
> 6b. `test_db_unreadable_preserves_snapshot` — `cur=None` with `arm_pending={file}` → the db-unreadable line is returned AND the snapshot comes back UNCHANGED (not `None`); a following poll with the same pending set is still treated as armed-over. Guards the clear-on-unreadable slip.
> 7. `test_status_mode_unchanged_for_pause` — `--status` on a constructed paused state still prints `WATCH: awaiting-verdict id=<N> pending=<file>` (the MUST-PRESERVE assertion). **CLONE the existing convention rather than inventing one:** `tests/test_gate_watcher.py:121-127` (`test_status_oneshot`) already calls `main(["gate_watcher.py", "<name>", "--status", "--db-path", db_path])` with the `capsys` fixture and asserts on `captured.out`; follow that call shape exactly, adding `"--pending-dir", str(pending_dir)`.
> **Targeted run:** `python3 -m pytest tests/test_gate_watcher.py -q` → 24 passed (16 baseline A5 + 8 new; re-derive if your baseline differs), 0 failed. DEV runs NO full suite.
>
> **Task D — dev log** `knowledge/dev-logs/gate-watcher-arm-snapshot-dev-2026-08-27.md`: the diff summary, each pin re-derivation (A1-A5, yours vs the table, say "supersedes" where they differ), the targeted-test tail pasted raw.
>
> **Task E — commit** (worktree; message `[<id>] gate-watcher-arm-snapshot: pre-existing pause logged as armed-over; 8 tests`): `cd "$(git rev-parse --show-toplevel)" && git add tools/gate_watcher.py tests/test_gate_watcher.py knowledge/dev-logs/gate-watcher-arm-snapshot-dev-2026-08-27.md && git commit`. Verify: `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `tools/gate_watcher.py` (modified — `judge_watch_line` + `main` threading)
> - `tests/test_gate_watcher.py` (extended — `TestArmTimeSnapshot`, 8 tests)
> - `knowledge/dev-logs/gate-watcher-arm-snapshot-dev-2026-08-27.md`
>
> **Scope:**
> - `tools/gate_watcher.py`
> - `tests/test_gate_watcher.py`
> - `knowledge/dev-logs/gate-watcher-arm-snapshot-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + a real armed-over run)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/pytest_full.txt` — 0 failed (record the count; derivation vs the 1582 A5 baseline).
> **Item 2 — a REAL armed-over run, full tails pasted to `probes-raw.txt`.** The discriminating condition must be CONSTRUCTED — do not wait for one. `SCRATCH=$(mktemp -d)`; resolve this plan's own id: `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id FROM plans WHERE deposit_placeholder_name='executable-gate-watcher-arm-snapshot.md' ORDER BY id DESC LIMIT 1;"` → `$PID`.
> ⚠️ **Both loop behaviors must be exercised in ONE run with the swap performed MID-RUN.** A second fresh run with `step-2` already on disk would arm OVER it and correctly print the armed-over line — proving nothing about later pauses. The discriminating sequence requires the file to change while the watcher is alive. **Delete the log before the run** so every assertion reads a clean window (a `grep -c` over an appended-to log cannot tell the two runs apart).
> 1. **Setup:** `LOG=logs/watch/executable-gate-watcher-arm-snapshot.md.log`; `rm -f "$LOG"`; `touch "$SCRATCH/verdict-request-$PID-step-1.md"`.
> 2. **One run, swap mid-flight:** start the loop in the background —
>    `python3 tools/gate_watcher.py executable-gate-watcher-arm-snapshot.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db --pending-dir "$SCRATCH" --timeout-min 1 --interval-sec 3 &`
>    then `sleep 10` (≥3 polls over the armed-over state), `rm "$SCRATCH/verdict-request-$PID-step-1.md"`, `sleep 8` (the pending set empties → the snapshot clears), `touch "$SCRATCH/verdict-request-$PID-step-2.md"`, `sleep 10`, then `wait` for the 1-minute timeout (exit 3, expected).
> 3. **Assert on the single clean log, pasting it whole:**
>    - `/usr/bin/grep -cF "armed over pre-existing verdict-request: verdict-request-$PID-step-1.md" "$LOG"` → **1** (the armed-over framing fired, once).
>    - `/usr/bin/grep -cF "pending=verdict-request-$PID-step-1.md" "$LOG"` → **0** (the stale pause was never reported as a fresh one).
>    - `/usr/bin/grep -cF "pending=verdict-request-$PID-step-2.md" "$LOG"` → **≥1** (the genuine LATER pause reported normally). **This is the assertion proving the guard did not simply mute pauses — if it reads 0, the guard is worse than the bug: HALT and report.**
> 4. **`--status` unchanged (the MUST-PRESERVE control):** with `step-2` still in place, `python3 tools/gate_watcher.py --status executable-gate-watcher-arm-snapshot.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db --pending-dir "$SCRATCH"` → `WATCH: awaiting-verdict id=$PID pending=verdict-request-$PID-step-2.md`, exit 0 — the loop's framing must NOT have leaked into `--status`.
> 5. Cleanup: `rm -rf "$SCRATCH"`; leave `$LOG` in place (untracked) and pasted into the evidence.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel asserted; reflog `-n 4` → 0 amends; per-item table; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 4 — commit the evidence** (worktree; message `[<id>] gate-watcher-arm-snapshot: QA — full suite + armed-over and later-pause runs`): `cd "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/ && git commit`. Verify: `git show --stat HEAD | cat` lists exactly the 3 evidence files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one pure helper extracted into `main`'s loop + additive tests; the defect is measured and its blast radius is one log line.

**Walk register:** `bellows/knowledge/research/walk-register-gate-watcher-arm-snapshot-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-5 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the loop-only seam held; no direction-class finding.
- Weak spots:          w1 1 folded (snapshot seeded from the first READABLE poll, not the first iteration); w2 1 folded (the appended-log ambiguity); w3 dry; w4 1 folded (test 7 cloned the existing main() convention at :121-127); w5 dry
- Destruction:         w1 dry; w2 dry; w3 dry; w4 dry; w5 dry
- Vulnerabilities:     w1 1 folded (the explicit `is not None` snapshot branch); w2 1 folded (⚠️ the QA later-pause probe would have armed OVER step-2 and proven nothing — rewritten as one run with a mid-flight swap); w3 dry; w4 dry; w5 dry
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 dry; w5 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry; w5 dry
**Cold panel: NOT convened, decided with reasoning** — T1 additive change to a read-only reporter, no money path, no destructive step; the 563/569/571 precedent.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block (fold grep-verifications, structure count, run_check cycle/lint/register all branched-on).
**Closing:** **walk 5 confirmed walk 3's and walk 4's residue clear — all five lenses dry twice (w3, w5) with w4's single fold between; BAR MET.** Instruction series **2 → 2 → 0 → 1 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/gate_watcher.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_gate_watcher.py
writes: tools/gate_watcher.py, tests/test_gate_watcher.py, knowledge/dev-logs/gate-watcher-arm-snapshot-dev-2026-08-27.md, knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/pytest_full.txt, knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/probes-raw.txt, knowledge/qa/evidence/gate-watcher-arm-snapshot-2026-08-27/qa-receipt.md
open_forks: whether the receipt should re-spawn a watcher after each verdict (NOT decided here — today's single deposit-time spawn spans the plan via the 120m default, and re-spawning is what would make this race routine); thread 20's scope text is corrected by the Planner at close
walks: 5
yields: 2, 2, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
